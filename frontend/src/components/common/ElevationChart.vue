<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'

const props = defineProps({
  elevationData: {
    type: Array,
    required: true,
  },
})

const METERS_TO_FEET = 3.28084
const PADDING = { top: 16, right: 16, bottom: 24, left: 48 }

const canvasRef = ref(null)
let resizeObserver = null

function draw() {
  const canvas = canvasRef.value
  if (!canvas || !props.elevationData?.length) return

  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr

  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  const w = rect.width
  const h = rect.height

  const chartW = w - PADDING.left - PADDING.right
  const chartH = h - PADDING.top - PADDING.bottom

  const elevFeet = props.elevationData.map(p => p.ele * METERS_TO_FEET)
  const rawMin = Math.min(...elevFeet)
  const rawMax = Math.max(...elevFeet)

  // Add some breathing room and round to nice numbers
  const range = rawMax - rawMin || 1
  const padding = range * 0.1
  const minElev = Math.floor((rawMin - padding) / 50) * 50
  const maxElev = Math.ceil((rawMax + padding) / 50) * 50
  const elevRange = maxElev - minElev || 1

  // Clear
  ctx.clearRect(0, 0, w, h)

  // Compute cumulative distance along the track for X axis
  const distances = [0]
  for (let i = 1; i < props.elevationData.length; i++) {
    const prev = props.elevationData[i - 1]
    const curr = props.elevationData[i]
    const dlat = (curr.lat - prev.lat) * 111320
    const dlon = (curr.lon - prev.lon) * 111320 * Math.cos((curr.lat * Math.PI) / 180)
    distances.push(distances[i - 1] + Math.sqrt(dlat * dlat + dlon * dlon))
  }
  const totalDist = distances[distances.length - 1] || 1

  function xPos(i) {
    return PADDING.left + (distances[i] / totalDist) * chartW
  }
  function yPos(elev) {
    return PADDING.top + chartH - ((elev - minElev) / elevRange) * chartH
  }

  // Gridlines and Y-axis labels
  const tickCount = 4
  const tickStep = elevRange / tickCount
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1
  ctx.fillStyle = '#6b7280'
  ctx.font = '11px system-ui, sans-serif'
  ctx.textAlign = 'right'
  ctx.textBaseline = 'middle'

  for (let i = 0; i <= tickCount; i++) {
    const elev = minElev + i * tickStep
    const y = yPos(elev)
    ctx.beginPath()
    ctx.moveTo(PADDING.left, y)
    ctx.lineTo(w - PADDING.right, y)
    ctx.stroke()
    ctx.fillText(`${Math.round(elev)} ft`, PADDING.left - 6, y)
  }

  // Filled area
  ctx.beginPath()
  ctx.moveTo(xPos(0), yPos(elevFeet[0]))
  for (let i = 1; i < elevFeet.length; i++) {
    ctx.lineTo(xPos(i), yPos(elevFeet[i]))
  }
  ctx.lineTo(xPos(elevFeet.length - 1), PADDING.top + chartH)
  ctx.lineTo(xPos(0), PADDING.top + chartH)
  ctx.closePath()
  ctx.fillStyle = 'rgba(34, 139, 34, 0.15)'
  ctx.fill()

  // Line
  ctx.beginPath()
  ctx.moveTo(xPos(0), yPos(elevFeet[0]))
  for (let i = 1; i < elevFeet.length; i++) {
    ctx.lineTo(xPos(i), yPos(elevFeet[i]))
  }
  ctx.strokeStyle = '#228B22'
  ctx.lineWidth = 2
  ctx.lineJoin = 'round'
  ctx.stroke()
}

onMounted(() => {
  draw()
  resizeObserver = new ResizeObserver(() => draw())
  if (canvasRef.value) resizeObserver.observe(canvasRef.value)
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})

watch(() => props.elevationData, draw, { deep: true })
</script>

<template>
  <div class="w-full">
    <canvas ref="canvasRef" class="w-full h-32" />
  </div>
</template>
