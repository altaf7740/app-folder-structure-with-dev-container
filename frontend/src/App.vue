<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="name" type="text" name="name" placeholder="Name" required />
    <input v-model.number="age" type="number" name="age" placeholder="Age" required />
    <input ref="folderInput" type="file" name="folder" webkitdirectory multiple required />
    <button type="submit">Upload</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const name = ref('')
const age = ref<number | null>(null)
const folderInput = ref<HTMLInputElement | null>(null)

const handleSubmit = async () => {
  if (!folderInput.value?.files?.length) return

  const formData = new FormData()
  formData.append('name', name.value)
  formData.append('age', age.value?.toString() || '')

  Array.from(folderInput.value.files).forEach(file => {
    formData.append('folder', file, file.webkitRelativePath)
  })

  const res = await fetch('http://localhost:8000/upload', {
    method: 'POST',
    body: formData,
  })

  const result = await res.json()
  console.log(result)
}
</script>
