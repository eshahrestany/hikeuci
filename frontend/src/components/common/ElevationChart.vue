<script setup lang="ts">
import { computed } from 'vue'
import { VisArea, VisAxis, VisLine, VisXYContainer } from '@unovis/vue'
import {
  ChartContainer,
  ChartCrosshair,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
  type ChartConfig,
} from '@/components/ui/chart'

const props = defineProps<{
  elevationData: Array<{ lat: number; lon: number; ele: number }>
}>()

const METERS_TO_FEET = 3.28084
const METERS_TO_MILES = 0.000621371

type DataPoint = { distanceMi: number; elevation: number }

const chartData = computed<DataPoint[]>(() => {
  if (!props.elevationData?.length) return []

  const distances = [0]
  for (let i = 1; i < props.elevationData.length; i++) {
    const prev = props.elevationData[i - 1]
    const curr = props.elevationData[i]
    const dlat = (curr.lat - prev.lat) * 111320
    const dlon =
      (curr.lon - prev.lon) * 111320 * Math.cos((curr.lat * Math.PI) / 180)
    distances.push(distances[i - 1] + Math.sqrt(dlat * dlat + dlon * dlon))
  }

  return props.elevationData.map((point, i) => ({
    distanceMi: parseFloat((distances[i] * METERS_TO_MILES).toFixed(3)),
    elevation: Math.round(point.ele * METERS_TO_FEET),
  }))
})

const yDomain = computed<[number, number]>(() => {
  if (!chartData.value.length) return [0, 1000]
  const elevations = chartData.value.map((d) => d.elevation)
  const rawMin = Math.min(...elevations)
  const rawMax = Math.max(...elevations)
  const range = rawMax - rawMin || 1
  const padding = range * 0.1
  return [
    Math.floor((rawMin - padding) / 50) * 50,
    Math.ceil((rawMax + padding) / 50) * 50,
  ]
})

const chartConfig: ChartConfig = {
  elevation: {
    label: 'Elevation (ft)',
    color: '#3f9c35',
  },
}

const tooltipTemplate = componentToString(chartConfig, ChartTooltipContent, {
  labelFormatter: (d: number | Date) => `${Number(d).toFixed(2)} mi`,
})
</script>

<template>
  <div class="w-full">
    <ChartContainer :config="chartConfig" class="h-32 aspect-auto" cursor>
      <VisXYContainer :data="chartData" :y-domain="yDomain">
        <VisArea
          :x="(d: DataPoint) => d.distanceMi"
          :y="(d: DataPoint) => d.elevation"
          color="#3f9c35"
          :opacity="0.15"
        />
        <VisLine
          :x="(d: DataPoint) => d.distanceMi"
          :y="(d: DataPoint) => d.elevation"
          color="#3f9c35"
          :line-width="2"
        />
        <VisAxis
          type="x"
          :tick-line="false"
          :domain-line="false"
          :grid-line="false"
          :num-ticks="4"
          :tick-format="(d: number) => `${d.toFixed(1)} mi`"
        />
        <VisAxis
          type="y"
          :num-ticks="4"
          :tick-line="false"
          :domain-line="false"
          :tick-format="(d: number) => `${d.toLocaleString()} ft`"
        />
        <ChartTooltip />
        <ChartCrosshair
          :template="tooltipTemplate"
          color="#3f9c35"
        />
      </VisXYContainer>
    </ChartContainer>
  </div>
</template>
