import { reactive } from 'vue'
import { useRouter } from 'vue-router'

const API_URL = import.meta.env.VITE_API_URL || ''

// Simple auth store using the Composition API.
const state = reactive({
  user: JSON.parse(localStorage.getItem('auth_user')) || null,
})

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

  function signOut() {
    setUser(null)
    router.replace('/login')   // send them back to login
  }

  // Helper: returns { Authorization: "Bearer …" } or {}
  function getAuthHeaders() {
    return state.user?.token
      ? { Authorization: `Bearer ${state.user.token}` }
      : {}
  }

  /**
   * Fetch wrapper that:
   *  - prefixes API_URL
   *  - sets Content-Type: application/json
   *  - injects Authorization header if logged in
   *  - auto signs out on 401
   */
  async function fetchWithAuth(path, opts = {}) {
    const url = `${API_URL}${path}`
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...opts.headers,
    }
    const res = await fetch(url, {
      ...opts,
      headers,
    })
    if (res.status === 401) {
      signOut()
      throw new Error('Unauthorized')
    }
    return res
  }

  async function postWithAuth(path, data = {}, opts = {}) {
    const url = `${API_URL}${path}`;
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...opts.headers,
    };

    const res = await fetch(url, {
      ...opts,               // allow overriding mode, credentials, etc.
      method: 'POST',        // force POST
      headers,
      body: JSON.stringify(data),
    });

    if (res.status === 401) {
      signOut();
      throw new Error('Unauthorized');
    }

    return res;
  }

  return { state, setUser, signOut, fetchWithAuth, postWithAuth }
}
