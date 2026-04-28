// useRealtime — subscribe to admin SSE topics and dispatch events to handlers.
//
// Usage:
//   const topics = computed(() => hikeId.value ? [`hike:${hikeId.value}`] : [])
//   useRealtime(topics, {
//     checkin_updated: () => loadUpcoming(),
//     roster_updated:  () => loadUpcoming(),
//   })
//
// Behavior:
//   - Opens a fetch-event-source connection with the user's JWT.
//   - Auto-reconnects with exponential backoff (1s → 15s).
//   - Pauses on document visibility=hidden, resumes (and refires every
//     handler once with null for backfill) on visible.
//   - Coalesces bursts: each handler is debounced 250ms.
//   - On 401, refreshes the access token via useAuth and reconnects.
//   - Cleans up on component unmount.

import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { useAuth } from './auth.js'

const DEBOUNCE_MS = 250
const INITIAL_BACKOFF_MS = 1000
const MAX_BACKOFF_MS = 15000

export function useRealtime(topicsRef, handlers) {
  const { state, refreshAccessToken } = useAuth()
  const connected = ref(false)
  let abortController = null
  let backoff = INITIAL_BACKOFF_MS
  let reopenTimer = null
  let visibilityHandler = null

  // Wrap each handler in a debounce so bursts collapse into a single refetch.
  // Handler values may be a plain function (uses DEBOUNCE_MS) or
  // { fn, debounceMs } to override the delay per-event.
  const debounced = {}
  for (const [name, entry] of Object.entries(handlers)) {
    const fn = typeof entry === 'function' ? entry : entry.fn
    const delay = typeof entry === 'function' ? DEBOUNCE_MS : entry.debounceMs
    let t = null
    let lastData = null
    debounced[name] = (data) => {
      lastData = data
      if (t) clearTimeout(t)
      t = setTimeout(() => {
        t = null
        try { fn(lastData) } catch (e) { console.error(`realtime handler ${name} threw`, e) }
      }, delay)
    }
  }

  function close() {
    if (reopenTimer) {
      clearTimeout(reopenTimer)
      reopenTimer = null
    }
    if (abortController) {
      try { abortController.abort() } catch {}
      abortController = null
    }
    connected.value = false
  }

  function scheduleReopen(delayMs) {
    if (reopenTimer) clearTimeout(reopenTimer)
    reopenTimer = setTimeout(() => {
      reopenTimer = null
      open()
    }, delayMs)
  }

  function backfill() {
    // Fire each handler once with null so consumers refetch — covers
    // any events missed during a disconnect or visibility-pause.
    for (const fn of Object.values(debounced)) {
      try { fn(null) } catch {}
    }
  }

  async function open() {
    close()
    const topics = topicsRef.value || []
    if (!topics.length) return
    if (typeof document !== 'undefined' && document.visibilityState === 'hidden') return
    if (!state.user?.token) return

    abortController = new AbortController()
    const url = `/api/admin/stream?topics=${encodeURIComponent(topics.join(','))}`
    const ctrl = abortController

    try {
      await fetchEventSource(url, {
        signal: ctrl.signal,
        headers: { Authorization: `Bearer ${state.user.token}` },
        // We manage visibility ourselves — the library's default would
        // pause silently and accumulate stale state.
        openWhenHidden: false,
        async onopen(response) {
          const ct = response.headers.get('content-type') || ''
          if (response.ok && ct.includes('text/event-stream')) {
            connected.value = true
            backoff = INITIAL_BACKOFF_MS
            return
          }
          if (response.status === 401) {
            // Refresh and reopen with the new token.
            try { ctrl.abort() } catch {}
            const ok = await refreshAccessToken()
            if (ok) scheduleReopen(50)
            return
          }
          // Any other non-stream response → retry with backoff.
          throw new Error(`stream open failed: ${response.status}`)
        },
        onmessage(ev) {
          const fn = debounced[ev.event]
          if (!fn) return
          let parsed = null
          try { parsed = ev.data ? JSON.parse(ev.data) : null } catch {}
          fn(parsed)
        },
        onerror(err) {
          // Returning a number tells fetch-event-source to retry after that
          // many ms. Throwing aborts. We always want to retry unless our
          // own AbortController fired (which manifests as ctrl.signal.aborted).
          connected.value = false
          if (ctrl.signal.aborted) throw err
          const d = backoff
          backoff = Math.min(backoff * 2, MAX_BACKOFF_MS)
          return d
        },
        onclose() {
          connected.value = false
          // Server-initiated close → reconnect after backoff (unless we
          // intentionally aborted, in which case ctrl.signal.aborted is true).
          if (!ctrl.signal.aborted) scheduleReopen(backoff)
        },
      })
    } catch {
      connected.value = false
    }
  }

  watch(topicsRef, () => { open() }, { deep: true })

  onMounted(() => {
    if (typeof document !== 'undefined') {
      visibilityHandler = () => {
        if (document.visibilityState === 'visible') {
          backfill()
          open()
        } else {
          close()
        }
      }
      document.addEventListener('visibilitychange', visibilityHandler)
    }
    open()
  })

  onBeforeUnmount(() => {
    if (visibilityHandler) {
      document.removeEventListener('visibilitychange', visibilityHandler)
      visibilityHandler = null
    }
    close()
  })

  return { connected, close, open }
}
