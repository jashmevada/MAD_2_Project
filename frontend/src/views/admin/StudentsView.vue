<template>
  <div class="container mt-2">
    <div class="row mb-4">
      <div class="col-md-6">
        <BFormInput v-model="searchQuery" placeholder="Search Students..." type="search" class="mb-2" />
      </div>
    </div>

    <BCard>
      <BTable  hover responsive :items="filteredStudents" :fields="fields" :busy="isLoading" show-empty
        empty-text="No Student found" @row-clicked="navigateToStudentDetail">

        <template #table-busy>
          <div class="text-center my-2">
            <BSpinner class="align-middle"></BSpinner>
            <strong class="ms-2">Loading...</strong>
          </div>
        </template>

        <template #cell(full_name)="{item}">
          <div class="user-info">
          <div class="user-name"><strong>{{ item.full_name }}</strong></div>
          <div class="user-username text-muted">@{{ item.username }}</div>
          </div>
        </template>

        <template #cell(actions)="{ item }">
          <div class="d-flex gap-2">
            <!-- <BButton size="sm" variant="outline-primary" @click="editSubject(item)">
              <i class="bi bi-pencil"></i> Edit
            </BButton> -->
            <BButton size="sm" variant="outline-danger" @click="confirmDelete(item)">
              <i class="bi bi-trash"></i> Delete
            </BButton>
          </div>
        </template>

        
        <template #cell(dob)="{item}">
          {{ formatDate(item.dob) }}
        </template>


      </BTable>
    </BCard>
  </div>

  <BModal v-model="showDeleteModal" title="Confirm Delete" ok-variant="danger" ok-title="Delete" @ok="deleteSubject">
      <p class="my-4">Are you sure you want to delete the Student "{{ selectedStudent?.full_name }}"?</p>
      <p class="text-danger">This action cannot be undone.</p>
  </BModal>

</template>

<script setup>

import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/apiFetch'
import router from '@/router'

const students = ref([])
const isLoading = ref(true)

const fields = [
  { key: 'full_name', label: 'Name', sortable: true },
  {key: 'qualification', label: 'Qulification'},
  {key: 'dob', label: 'DOB'},
  { key: 'actions', label: 'Actions' }
]

const fetchStudents = async () => {
  isLoading.value = true
  try {
    students.value = await apiFetch('/students')
  } catch (error) {
    console.error('Error fetching subjects:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await fetchStudents()
})

// Filters 
const searchQuery = ref('')
const subjectFilter = ref('')

const filteredStudents = computed(() => {
  let result = students.value

  if (subjectFilter.value) {
    result = result.filter(quiz => quiz.subject === subjectFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(quiz =>
      quiz.full_name.toLowerCase().includes(query) 
      // quiz.subject.toLowerCase().includes(query)
    )
  }

  return result
})
// End


// Delete Modal 
const showDeleteModal = ref(false)
const selectedStudent = ref(null)

const confirmDelete = (student) => {
  selectedStudent.value = student
  showDeleteModal.value = true
}

const deleteSubject = async () => {
  if (!selectedStudent.value) return

  try {
    await apiFetch(`/students/${selectedStudent.value.id}`, { method: 'DELETE' })

    students.value = students.value.filter(s => s.id !== selectedStudent.value.id)

    console.log(`Subject "${selectedStudent.value.name}" deleted successfully`)
  } catch (error) {
    console.error('Error deleting subject:', error)
  }
}

const formatDate = (dateString) => {
    try {
      let t = new Date(dateString)
      return t.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      })
    } catch (e) {
      console.log("error");
  
      return dateString
    }
  }

function navigateToStudentDetail(item) {
  router.push(`/admin/students/${item.id}`)
}
</script>

<style scoped>
</style>