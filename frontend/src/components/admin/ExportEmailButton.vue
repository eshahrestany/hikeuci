<script setup>
import Button from "@/components/ui/button/Button.vue"
import {toast} from "vue-sonner";
import {Copy} from "lucide-vue-next"
import {useAuth} from "@/lib/auth.js"

const {fetchWithAuth} = useAuth()
const props = defineProps({
  mode: {type: String, required: true}, // "signup" or "all"
})

async function get_and_copy(){
  try {
    const res = await fetchWithAuth('/api/admin/' + (props.mode === 'signup' ? 'list-emails-in-hike' : 'list-emails'))
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(errText || 'Unknown error')
    }
    if (res.status === 200) {
      const emails = await res.json()
      let newline_separated = ""
      for (const email of emails) {
        newline_separated += email + "\n"
      }
      await navigator.clipboard.writeText(newline_separated)
      toast.success(`List of ${props.mode === 'signup' ? 'signed up' : 'all'} members' emails successfully copied to clipboard!`)
    }
  } catch (error) {
    toast.error(`Failed to fetch list of emails, ${error.message}`)
  }
}

</script>

<template>
  <Button @click="get_and_copy">
    <Copy class="w-4 h-4"/>
    Copy Emails
  </Button>
</template>