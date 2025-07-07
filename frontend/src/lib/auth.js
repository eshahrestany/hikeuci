import { reactive } from 'vue'

// Simple auth store using the Composition API. This keeps the signed-in user
// (email, name, picture, idToken) reactive across the application.

const state = reactive({
  user: JSON.parse(localStorage.getItem('auth_user')) || null,
})

export function useAuth() {
  function setUser(user) {
    state.user = user
    if (user) {
      localStorage.setItem('auth_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('auth_user')
    }
  }

  function signOut() {
    // Invalidate the session locally. If needed, revoke token server-side.
    setUser(null)
  }

  return { state, setUser, signOut }
}

export default { useAuth } 