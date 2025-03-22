<template>
    <div class="container mt-5">
  
      <div class="row mb-4">
        <div class="col-md-6">
          <BFormInput v-model="searchQuery" placeholder="Search quizzes..." type="search" class="mb-2" />
        </div>
        <div class="col-md-3">
          <BFormSelect v-model="subjectFilter" :options="subjectOptions" class="mb-2">
            <template #first>
              <option value="">All Subjects</option>
            </template>
          </BFormSelect>
        </div>
        <div class="col-md-2">
          <BFormSelect v-model="departmentFilter" :options="departmentOptions" class="mb-2">
            <template #first>
              <option value="">All Department</option>
            </template>
          </BFormSelect>
        </div>
      </div>
  
      <BCard>
        <BTable :items="filteredQuizzes" :fields="fields" hover responsive empty-text="No subjects found">
  
          <template #table-busy>
            <div class="text-center my-2">
              <BSpinner class="align-middle"></BSpinner>
              <strong class="ms-2">Loading...</strong>
            </div>
          </template>
  
          <template #cell(date)="data">
            {{ formatDate(data.value) }}
          </template>
  
          <template #cell(duration)="data">
            {{ data.value }} minutes
          </template>
        </BTable>
      </BCard>
  
      <BModal v-model="showDeleteModal" title="Confirm Deletion" @ok="deleteQuiz">
        <p>Are you sure you want to delete the quiz "{{ quizToDelete?.title }}"?</p>
      </BModal>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { Icon } from '@iconify/vue'
import { apiFetch } from '@/main'
  
  const fields = [
    { key: 'title', label: 'Quiz Title', sortable: true },
    { key: 'subject', label: 'Subject', sortable: true },
    { key: 'date', label: 'Date', sortable: true },
    { key: 'duration', label: 'Duration', sortable: true },
    { key: 'totalQuestions', label: 'Questions', sortable: true },
  ]
  
  const quizzes = ref([])
  
onMounted(async () => {
    quizzes.value = await apiFetch('/quizzes')
})
  
  const searchQuery = ref('')
  const subjectFilter = ref('')
  
  
  const showDeleteModal = ref(false)
  const quizToDelete = ref(null)
  
  
  const subjectOptions = computed(() => {
    const subjects = new Set(quizzes.value.map(quiz => quiz.subject))
    return Array.from(subjects).map(subject => ({ value: subject, text: subject }))
  })
  
  
  const filteredQuizzes = computed(() => {
    let result = quizzes.value
  
  
    if (subjectFilter.value) {
      result = result.filter(quiz => quiz.subject === subjectFilter.value)
    }
  
  
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(quiz =>
        quiz.title.toLowerCase().includes(query) ||
        quiz.subject.toLowerCase().includes(query)
      )
    }
  
    return result
  })
  
  
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
  
  </script>
  