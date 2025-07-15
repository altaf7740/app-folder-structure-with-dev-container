<template>
  <div class="container">
    <h1>AI Model Manager</h1>

    <form @submit.prevent="handleSubmit" class="upload-form">
      <input v-model="comment" type="text" placeholder="Comment" required />
      <label>
        <input type="checkbox" v-model="isActivated" />
        Activate this model
      </label>
      <input ref="folderInput" type="file" webkitdirectory multiple required />
      <button type="submit">{{ editingId ? 'Update' : 'Upload' }}</button>
    </form>
    <hr />

    <table>
      <thead>
        <tr>
          <th>Comment</th>
          <th>Active</th>
          <th>Created</th>
          <th>Updated</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="model in models" :key="model.id" :class="{ active: model.is_activated_aimodel }">
          <td>{{ model.comment }}</td>
          <td>{{ model.is_activated_aimodel ? '✅' : '' }}</td>
          <td>{{ new Date(model.created_at).toLocaleString() }}</td>
          <td>{{ new Date(model.updated_at).toLocaleString() }}</td>
          <td>
            <button @click="editModel(model)">Edit</button>
            <button @click="deleteModel(model.id)">Delete</button>
            <button v-if="!model.is_activated_aimodel" @click="activateModel(model)">Activate</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface AIModel {
  id: string
  comment: string
  is_activated_aimodel: boolean
  model_folder_path: string
  created_at: string
  updated_at: string
}

const comment = ref('')
const isActivated = ref(false)
const folderInput = ref<HTMLInputElement | null>(null)
const models = ref<AIModel[]>([])
const editingId = ref<string | null>(null)

const fetchModels = async () => {
  const res = await fetch('http://localhost:8000/aimodels')
  models.value = await res.json()
}

const resetForm = () => {
  comment.value = ''
  isActivated.value = false
  folderInput.value!.value = ''
  editingId.value = null
}

const handleSubmit = async () => {
  const formData = new FormData()
  formData.append('comment', comment.value)
  formData.append('is_activated_aimodel', isActivated.value.toString())

  if (editingId.value) {
    // update (no files involved)
    const res = await fetch(`http://localhost:8000/aimodels/${editingId.value}`, {
      method: 'PUT',
      body: formData
    })
    await res.json()
  } else {
    // upload (files involved)
    if (!folderInput.value?.files?.length) return
    Array.from(folderInput.value.files).forEach(file => {
      formData.append('folder', file, file.webkitRelativePath)
    })
    const res = await fetch('http://localhost:8000/aimodels', {
      method: 'POST',
      body: formData
    })
    await res.json()
  }

  await fetchModels()
  resetForm()
}

const deleteModel = async (id: string) => {
  if (!confirm('Are you sure you want to delete this model?')) return
  await fetch(`http://localhost:8000/aimodels/${id}`, { method: 'DELETE' })
  await fetchModels()
}

const editModel = (model: AIModel) => {
  comment.value = model.comment
  isActivated.value = model.is_activated_aimodel
  editingId.value = model.id
}

const activateModel = async (model: AIModel) => {
  const formData = new FormData()
  formData.append('comment', model.comment)
  formData.append('is_activated_aimodel', 'true')
  await fetch(`http://localhost:8000/aimodels/${model.id}`, {
    method: 'PUT',
    body: formData
  })
  await fetchModels()
}

onMounted(fetchModels)
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: auto;
  font-family: Arial, sans-serif;
}

.upload-form {
  margin-bottom: 30px;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.upload-form input[type="text"] {
  flex: 1;
  padding: 6px;
}

.upload-form input[type="file"] {
  flex: 1;
}

.upload-form button {
  padding: 6px 12px;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

.upload-form button:hover {
  background: #0056b3;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

thead {
  background-color: #f0f0f0;
}

td, th {
  padding: 10px;
  border: 1px solid #ddd;
}

tr.active {
  background-color: #e0ffe0;
}

button {
  margin-right: 5px;
}
</style>
