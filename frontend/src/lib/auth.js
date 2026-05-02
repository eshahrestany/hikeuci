import { reactive } from 'vue'
import { useRouter } from 'vue-router'

// Simple auth store using the Composition API.
const state = reactive({
  user: JSON.parse(localStorage.getItem('auth_user')) || null,
})

// Track in-flight refresh to avoid duplicate calls
let refreshPromise = null

export function useAuth() {
  const router = useRouter()

  function setUser(user) {
    state.user = user
    if (user) {
      localStorage.setItem('auth_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('auth_user')
    }
  }

  // Single source of truth for shaping user state from any auth response
  // (sign-in, refresh). Merges with existing user so partial responses
  // (e.g. refresh, which omits refreshToken) don't blow away identity.
  function setAuthFromResponse(body) {
    const next = { ...(state.user || {}) }
    if (body.token) next.token = body.token
    if (body.refreshToken) next.refreshToken = body.refreshToken
    if (typeof body.is_owner === 'boolean') next.is_owner = body.is_owner
    if (body.name) next.name = body.name
    if (body.email) next.email = body.email
    setUser(next)
  }

  function signOut() {
    setUser(null)
    router.replace('/login')
  }

  // Helper: returns { Authorization: "Bearer …" } or {}
  function getAuthHeaders() {
    return state.user?.token
      ? { Authorization: `Bearer ${state.user.token}` }
      : {}
  }

  /**
   * Attempt to get a new access token using the stored refresh token.
   * Returns true if successful, false otherwise.
   */
  async function refreshAccessToken() {
    const refreshToken = state.user?.refreshToken
    if (!refreshToken) return false

    // Deduplicate concurrent refresh attempts
    if (refreshPromise) return refreshPromise

    refreshPromise = (async () => {
      try {
        const res = await fetch('/api/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refreshToken }),
        })

        if (!res.ok) return false

        const body = await res.json()
        setAuthFromResponse(body)
        return true
      } catch {
        return false
      } finally {
        refreshPromise = null
      }
    })()

    return refreshPromise
  }

  /**
   * Fetch wrapper that:
   *  - sets Content-Type: application/json
   *  - injects Authorization header if logged in
   *  - on 401, attempts a silent token refresh and retries once
   *  - signs out if the refresh also fails
   */
  async function fetchWithAuth(path, opts = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...opts.headers,
    }
    let res = await fetch(path, { ...opts, headers })

    if (res.status === 401) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        const retryHeaders = {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
          ...opts.headers,
        }
        res = await fetch(path, { ...opts, headers: retryHeaders })
      }
      if (!refreshed || res.status === 401) {
        signOut()
        throw new Error('Unauthorized')
      }
    }
    return res
  }

  async function postWithAuth(path, data = {}, opts = {}) {
    return fetchWithAuth(path, {
      ...opts,
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  return { state, setUser, setAuthFromResponse, signOut, fetchWithAuth, postWithAuth, getAuthHeaders, refreshAccessToken }
}
