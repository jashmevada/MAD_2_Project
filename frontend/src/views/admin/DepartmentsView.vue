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
            <BFormInput id="subject-name" v-model="form.name" placeholder="Enter Title" required></BFormInput>
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
  </template>
  
  <script setup>
  import { ref, reactive, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { apiFetch } from '@/apiFetch'
  
  const router = useRouter()
  
  // Table fields definition
  const fields = [
    { key: 'name', label: 'Subject Name', sortable: true },
   //  { key: 'code', label: 'Code', sortable: true },
    { key: 'department', label: 'Department', sortable: true },
    {key:'description' , label:'Description', sortable:true},
    // { key: 'credits', label: 'Credits', sortable: true },
    // { key: 'status', label: 'Status', sortable: true },
    { key: 'actions', label: 'Actions' }
  ]
  
  // State variables
  const subjects = ref([])
  const isLoading = ref(true)
  const showModal = ref(false)
  const showDeleteModal = ref(false)
  const isEditing = ref(false)
  const selectedSubject = ref(null)
  
  // Form data
  const form = reactive({
    id: null,
    name: undefined,
    code: '',
    department: '',
    description: '',
  })
  
  // Department options
  const departmentOptions = [
    { value: '', text: 'Select department' },
    { value: 'computer-science', text: 'Computer Science' },
    { value: 'mathematics', text: 'Mathematics' },
    { value: 'physics', text: 'Physics' },
    { value: 'chemistry', text: 'Chemistry' },
    { value: 'biology', text: 'Biology' },
    { value: 'engineering', text: 'Engineering' }
  ]
  
  // Form validation
  const validation = computed(() => {
    return {
      name: form.name?.trim() !== '',
      code: form.code.trim() !== '',
      department: form.department !== ''
    }
  })
  
  // Check if form is valid
  const isFormValid = computed(() => {
    return Object.values(validation.value).every(valid => valid)
  })
  
  // Fetch subjects from API
  const fetchSubjects = async () => {
    isLoading.value = true
    try {
      // Replace with your actual API call
      subjects.value = await apiFetch('/subjects')
  
      // Simulated API response
      // await new Promise(resolve => setTimeout(resolve, 800))
      // subjects.value = [
      //   { id: 1, name: 'Introduction to Programming', code: 'CS101', department: 'computer-science', credits: 3, description: 'Basic programming concepts', status: true },
      //   { id: 2, name: 'Data Structures', code: 'CS201', department: 'computer-science', credits: 4, description: 'Advanced data structures', status: true },
      //   { id: 3, name: 'Calculus I', code: 'MATH101', department: 'mathematics', credits: 3, description: 'Limits, derivatives, and integrals', status: true },
      //   { id: 4, name: 'Organic Chemistry', code: 'CHEM301', department: 'chemistry', credits: 4, description: 'Study of carbon compounds', status: false }
      // ]
    } catch (error) {
      console.error('Error fetching subjects:', error)
    } finally {
      isLoading.value = false
    }
  }
  
  // Open add subject modal
  const openAddModal = () => {
    isEditing.value = false
    resetForm()
    showModal.value = true
  }
  
  // Edit subject
  const editSubject = (subject) => {
    isEditing.value = true
    selectedSubject.value = subject
  
    // Populate form with subject data
    Object.keys(form).forEach(key => {
      if (key in subject) {
        form[key] = subject[key]
      }
    })
  
    showModal.value = true
  }
  
  // Confirm delete
  const confirmDelete = (subject) => {
    selectedSubject.value = subject
    showDeleteModal.value = true
  }
  
  // Delete subject
  const deleteSubject = async () => {
    if (!selectedSubject.value) return
  
    try {
      // Replace with your actual API call
      await apiFetch(`/subjects/${selectedSubject.value.id}`, { method: 'DELETE' })
  
      // Update local state
      subjects.value = subjects.value.filter(s => s.id !== selectedSubject.value.id)
  
      // Show success message (you can implement a toast notification here)
      console.log(`Subject "${selectedSubject.value.name}" deleted successfully`)
    } catch (error) {
      console.error('Error deleting subject:', error)
    }
  }
  
  // Handle form submission
  const handleSubmit = async (event) => {
    // Prevent modal from closing if form is invalid
    if (!isFormValid.value) {
      event.preventDefault()
      return
    }
  
    try {
      if (isEditing.value) {
        // Update existing subject
        // Replace with your actual API call
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
        // Add new subject
        // Replace with your actual API call
  
        const response = await apiFetch('/subjects/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(form)
        })
        
        const newSubject = {
          ...form,
          id: Math.max(0, ...subjects.value.map(s => s.id)) + 1
        }
  
        subjects.value.push(newSubject)
  
        // console.log(`Subject "${form.name}" added successfully`)
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
  