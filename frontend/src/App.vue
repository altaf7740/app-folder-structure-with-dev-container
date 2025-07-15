<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="comment" type="text" name="comment" placeholder="Comment" required />
    <label>
      <input type="checkbox" v-model="isActivated" />
      Activate this model
    </label>
    <input ref="folderInput" type="file" name="folder" webkitdirectory multiple required />
    <button type="submit">Upload</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const comment = ref('')
const isActivated = ref(false)
const folderInput = ref<HTMLInputElement | null>(null)

const handleSubmit = async () => {
  if (!folderInput.value?.files?.length) return

  const formData = new FormData()
  formData.append('comment', comment.value)
  formData.append('is_activated_aimodel', isActivated.value.toString())

  Array.from(folderInput.value.files).forEach(file => {
    formData.append('folder', file, file.webkitRelativePath)
  })

  const res = await fetch('http://localhost:8000/aimodels', {
    method: 'POST',
    body: formData,
  })

  const result = await res.json()
  console.log(result)
}
</script>
