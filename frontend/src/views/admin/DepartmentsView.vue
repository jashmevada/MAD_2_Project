<template>
    <div class="subjects-container p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <!-- <h2>Subjects Management</h2> -->
        <BButton variant="primary" @click="openAddModal">
          <i class="bi bi-plus-circle me-2"></i> Add Department
        </BButton>
      </div>
  
      <BCard>
        <BTable hover responsive :items="departments" :fields="fields" :busy="isLoading" show-empty
          empty-text="No Department found" @row-clicked="navigateToSubjectDetail">
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
                Edit
              </BButton>
              <BButton size="sm" variant="outline-danger" @click="confirmDelete(item)">
                 Delete
              </BButton>
            </div>
          </template>
        </BTable>
      </BCard>
  
      <BModal v-model="showModal" :title="isEditing ? 'Edit Department' : 'Add New Department'" @hidden="resetForm"
        @ok="handleSubmit" :ok-title="isEditing ? 'Update' : 'Save'">
        <BForm @submit.prevent>
          <BFormGroup label="Title" label-for="subject-name">
            <BFormInput id="subject-name" v-model="form.title" placeholder="Enter Title" required></BFormInput>
          </BFormGroup>
  
          <BFormGroup label="Description" label-for="description">
            <BFormTextarea id="description" v-model="form.description" placeholder="Enter subject description" rows="3">
            </BFormTextarea>
          </BFormGroup>
        </BForm>
      </BModal>
  
      <BModal v-model="showDeleteModal" title="Confirm Delete" ok-variant="danger" ok-title="Delete" @ok="deleteSubject">
        <p class="my-4">Are you sure you want to delete the subject "{{ selectedDepartment?.name }}"?</p>
        <p class="text-danger">This action cannot be undone.</p>
      </BModal>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { apiFetch } from '@/apiFetch'
  
  const router = useRouter()
  
  // Table fields definition
  const fields = [
    { key: 'title', label: 'Title', sortable: true },
    {key:'description' , label:'Description', sortable:true},
    { key: 'actions', label: 'Actions' }
  ]
  
  // State variables
  const departments = ref([])
  const isLoading = ref(true)
  const showModal = ref(false)
  const showDeleteModal = ref(false)
  const isEditing = ref(false)
  const selectedDepartment = ref(null)
  
  // Form data
  const form = reactive({
    id: null,
    title: '',
    description: '',
  })


  const validation = computed(() => {
    return {
      title: form.title?.trim() !== '',
      description: form.description !== ''
    }
  })
  
  const isFormValid = computed(() => {
    return Object.values(validation.value).every(valid => valid)
  })
  
  const fetchDepartments = async () => {
    isLoading.value = true
    try {
        departments.value = await apiFetch('/departments')
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
    selectedDepartment.value = subject
  
    
    Object.keys(form).forEach(key => {
      if (key in subject) {
        form[key] = subject[key]
      }
    })
  
    showModal.value = true
  }
  
  // Confirm delete
  const confirmDelete = (subject) => {
    selectedDepartment.value = subject
    showDeleteModal.value = true
  }
  
  const deleteSubject = async () => {
    if (!selectedDepartment.value) return
  
    try {
      await apiFetch(`/departments/${selectedDepartment.value.id}`, { method: 'DELETE' })
  
      departments.value = departments.value.filter(s => s.id !== selectedDepartment.value.id)
  
      // Show success message (you can implement a toast notification here)
      console.log(`Subject "${selectedDepartment.value.name}" deleted successfully`)
    } catch (error) {
      console.error('Error deleting subject:', error)
    }
  }
  
  const handleSubmit = async (event) => {
    if (!isFormValid.value) {
      event.preventDefault()
      return
    }
  
    try {
      if (isEditing.value) {
        await apiFetch(`/departments/${form.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form)
        })
  
        // Update local state
        const index = departments.value.findIndex(s => s.id === form.id)
        if (index !== -1) {
            departments.value[index] = { ...form }
        }
  
        console.log(`Subject "${form.name}" updated successfully`)
      } else {
        // Add new subject
        // Replace with your actual API call
  
        const t = await apiFetch('/departments', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form)
        })
        
        const newDepartment = {
          ...form,
        //   id: Math.max(0, ...departments.value.map(s => s.id)) + 1
        }
  
        departments.value.push(newDepartment)
      }
    } catch (error) {
      console.error('Error saving subject:', error)
      event.preventDefault()
    }
  }
  
  const resetForm = () => {
    form.title = ''
    form.description = ''
    selectedDepartment.value = null
  }
  
  onMounted(async () => {
    await fetchDepartments() 
  })
  
  const navigateToSubjectDetail = (item) => {
    router.push(`/admin/departments/${item.id}`)
  }
  </script>
  
  <style scoped>
  .subjects-container {
    max-width: 1200px;
    margin: 0 auto;
  }
  </style>
  