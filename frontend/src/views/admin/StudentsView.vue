<template>
  <div class="subjects-container p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <!-- <h2>Subjects Management</h2> -->
      <BButton variant="primary" @click="openAddModal">
        <i class="bi bi-plus-circle me-2"></i> Add Student
      </BButton>
    </div>

    <!-- Subjects Table -->
    <BCard>
      <BTable hover responsive :items="subjects" :fields="fields" :busy="isLoading" show-empty
        empty-text="No subjects found" @row-clicked="navigateToSubjectDetail">
        <!-- Loading state -->
        <template #table-busy>
          <div class="text-center my-2">
            <BSpinner class="align-middle"></BSpinner>
            <strong class="ms-2">Loading...</strong>
          </div>
        </template>

        <template #cell(actions)="{ item }">
          <div class="d-flex gap-2">
            <BButton size="sm" variant="outline-primary" @click="editSubject(item)">
              <i class="bi bi-pencil"></i> Edit
            </BButton>
            <BButton size="sm" variant="outline-danger" @click="confirmDelete(item)">
              <i class="bi bi-trash"></i> Delete
            </BButton>
          </div>
        </template>
      </BTable>
    </BCard>
  </div>
</template>

<script setup>

import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/main'


const router = useRouter()
const subjects = ref([])
const isLoading = ref(true)

// Table fields definition
const fields = [
  { key: 'full_name', label: 'Name', sortable: true },
  { key: 'code', label: 'Code', sortable: true },
  { key: 'department', label: 'Department', sortable: true },
  { key: 'actions', label: 'Actions' }
]

const fetchSubjects = async () => {
  isLoading.value = true
  try {
    subjects.value = await apiFetch('/students')
  } catch (error) {
    console.error('Error fetching subjects:', error)
  } finally {
    isLoading.value = false
  }
}


onMounted(async () => {
  await fetchSubjects()
})

</script>

<style scoped>
</style>