<template>
  <div class="subjects-container p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <!-- <h2>Subjects Management</h2> -->
      <BButton variant="primary" @click="openAddModal">
        <i class="bi bi-plus-circle me-2"></i> Add New Subject
      </BButton>
    </div>


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
              <!-- <i class="bi bi-pencil">d</i>  -->
              Edit
            </BButton>
            <BButton size="sm" variant="outline-danger" @click="confirmDelete(item)">

              Delete
            </BButton>
          </div>
        </template>
      </BTable>
    </BCard>

    <BModal v-model="showModal" :title="isEditing ? 'Edit Subject' : 'Add New Subject'" @hidden="resetForm"
      @ok="handleSubmit" :ok-title="isEditing ? 'Update' : 'Save'">
      <BForm @submit.prevent>
        <BFormGroup label="Name" label-for="subject-name">
          <BFormInput id="subject-name" v-model="form.name" placeholder="Enter subject name" required></BFormInput>
        </BFormGroup>

        <BFormGroup label="Department" label-for="department">
          <BFormSelect id="department" v-model="form.department" :options="departmentOptions"
            :state="validation.department" required text-field="title" value-field="id"></BFormSelect>
          <BFormInvalidFeedback v-if="!validation.department">
            Please select a department
          </BFormInvalidFeedback>
        </BFormGroup>

        <BFormGroup label="Description" label-for="description">
          <BFormTextarea id="description" v-model="form.description" placeholder="Enter subject description" rows="3">
          </BFormTextarea>
        </BFormGroup>

      </BForm>
    </BModal>


    <BModal v-model="showDeleteModal" title="Confirm Delete" ok-variant="danger" ok-title="Delete" @ok="deleteSubject">
      <p class="my-4">Are you sure you want to delete the subject "{{ selectedSubject?.name }}"?</p>
      <p class="text-danger">This action cannot be undone.</p>
    </BModal>
  </div>

  <BToastOrchestrator />

</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '@/apiFetch'
import { useToastController } from 'bootstrap-vue-next'

const router = useRouter()
const toast = useToastController()

const fields = [
  { key: 'name', label: 'Subject Name', sortable: true },
  { key: 'department', label: 'Department', sortable: true },
  { key: 'description', label: 'Description', sortable: true },
  { key: 'actions', label: 'Actions' }
]

// State variables
const subjects = ref([])
const isLoading = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedSubject = ref(null)
const departmentOptions = ref([])

// Form data
const form = reactive({
  id: null,
  name: undefined,
  department: '',
  description: '',
})

const validation = computed(() => {
  return {
    name: form.name?.trim() !== '',
    department: form.department !== ''
  }
})

const isFormValid = computed(() => {
  return Object.values(validation.value).every(valid => valid)
})

const fetchSubjects = async () => {
  isLoading.value = true
  try {
    subjects.value = await apiFetch('/subjects')

  } catch (error) {
    console.error('Error fetching subjects:', error)
  } finally {
    isLoading.value = false
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showModal.value = true
}


const editSubject = (subject) => {
  isEditing.value = true
  selectedSubject.value = subject

  Object.keys(form).forEach(key => {
    if (key in subject) {
      form[key] = subject[key]
    }
  })

  showModal.value = true
}

const confirmDelete = (subject) => {
  selectedSubject.value = subject
  showDeleteModal.value = true
}

const deleteSubject = async () => {
  if (!selectedSubject.value) return

  try {
    await apiFetch(`/subjects/${selectedSubject.value.id}`, { method: 'DELETE' })

    subjects.value = subjects.value.filter(s => s.id !== selectedSubject.value.id)

    console.log(`Subject "${selectedSubject.value.name}" deleted successfully`)
    toast.show?.({ props: { title: 'Delete Department', value: true, variant: 'success', body: `Department "${selectedSubject.value.name}" deleted successfully` } })

  } catch (error) {
    console.error('Error deleting subject:', error)
    toast.show?.({ props: { title: 'Delete Department', value: true, variant: 'success', body: `Department "${selectedSubject.value.name}" deleted successfully` } })

  }
}

const handleSubmit = async (event) => {
  if (!isFormValid.value) {
    event.preventDefault()
    return
  }

  try {
    if (isEditing.value) {

      await apiFetch(`/subjects/${form.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })

      // Update local state
      const index = subjects.value.findIndex(s => s.id === form.id)
      if (index !== -1) {
        subjects.value[index] = { ...form }
      }

      console.log(`Subject "${form.name}" updated successfully`)
    } else {
      const response = await apiFetch('/subjects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })

      const newSubject = {
        ...form,
        id: Math.max(0, ...subjects.value.map(s => s.id)) + 1
      }

      subjects.value.push(newSubject)

      toast.show?.({ props: { title: 'New Subject', value: true, variant: 'success', body: `Subject "${selectedSubject.value.name}" new successfully` } })
    }
  } catch (error) {
    console.error('Error saving subject:', error)
    event.preventDefault()
  }
}

// Reset form
const resetForm = () => {
  form.id = null
  form.name = ''
  form.code = ''
  form.department = ''
  form.credits = 3
  form.description = ''
  form.status = true
  selectedSubject.value = null
}

// Fetch subjects on component mount
onMounted(async () => {
  await fetchSubjects()
  // subjects.value = await apiFetch("/subjects")
  departmentOptions.value = await apiFetch("/departments")
})

const navigateToSubjectDetail = (item) => {
  router.push(`/admin/subjects/${item.id}`)
}
</script>

<style scoped>
.subjects-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
