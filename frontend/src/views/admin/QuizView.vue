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
      <div class="col-md-3">
        <BButton variant="success" @click='$router.push("quiz/create")'>
          <Icon icon="heroicons:plus-circle" class="me-2" width="24" />Quiz
        </BButton>
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

        <template #cell(actions)="data">
          <div class="d-flex gap-2">
            <BButton size="sm" variant="outline-primary" @click="editQuiz(data.item)">
              Edit
            </BButton>
            <BButton size="sm" variant="outline-danger" @click="confirmDelete(data.item)">
              Delete
            </BButton>
          </div>
        </template>
      </BTable>
    </BCard>

    <BModal v-model="showModal" :title="isEditing ? 'Edit Quiz' : 'Add New Quiz'" @ok="saveQuiz">
      <BForm>
        <BFormGroup label="Title">
          <BFormInput v-model="currentQuiz.title" required />
        </BFormGroup>

        <BFormGroup label="Subject">
          <BFormInput v-model="currentQuiz.subject" required />
        </BFormGroup>

        <BFormGroup label="Date">
          <BFormInput v-model="currentQuiz.date" type="date" required />
        </BFormGroup>

        <BFormGroup label="Duration (minutes)">
          <BFormInput v-model="currentQuiz.duration" type="number" required />
        </BFormGroup>

        <BFormGroup label="Total Questions">
          <BFormInput v-model="currentQuiz.totalQuestions" type="number" required />
        </BFormGroup>
      </BForm>
    </BModal>

    <BModal v-model="showDeleteModal" title="Confirm Deletion" @ok="deleteQuiz">
      <p>Are you sure you want to delete the quiz "{{ quizToDelete?.title }}"?</p>
    </BModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'

const fields = [
  { key: 'title', label: 'Quiz Title', sortable: true },
  { key: 'subject', label: 'Subject', sortable: true },
  { key: 'date', label: 'Date', sortable: true },
  { key: 'duration', label: 'Duration', sortable: true },
  { key: 'totalQuestions', label: 'Questions', sortable: true },
  { key: 'actions', label: 'Actions' }
]

const quizzes = ref([
  {
    id: 1,
    title: 'Introduction to Vue.js',
    subject: 'Web Development',
    date: '2025-03-25',
    duration: 45,
    totalQuestions: 20
  },
  {
    id: 2,
    title: 'Advanced JavaScript Concepts',
    subject: 'Programming',
    date: '2025-04-10',
    duration: 60,
    totalQuestions: 25
  },
  {
    id: 3,
    title: 'Database Design Principles',
    subject: 'Database',
    date: '2025-03-15',
    duration: 30,
    totalQuestions: 15
  },
  {
    id: 4,
    title: 'CSS Frameworks Comparison',
    subject: 'Web Development',
    date: '2025-05-05',
    duration: 40,
    totalQuestions: 18
  }
])


const searchQuery = ref('')
const subjectFilter = ref('')


const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const currentQuiz = ref({})
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

const showAddQuizModal = () => {
  currentQuiz.value = {
    id: Math.max(0, ...quizzes.value.map(q => q.id)) + 1,
    title: '',
    subject: '',
    date: new Date().toISOString().split('T')[0],
    duration: 30,
    totalQuestions: 10
  }
  isEditing.value = false
  showModal.value = true
}

const editQuiz = (quiz) => {
  currentQuiz.value = { ...quiz }
  isEditing.value = true
  showModal.value = true
}

const saveQuiz = () => {
  if (isEditing.value) {
    const index = quizzes.value.findIndex(q => q.id === currentQuiz.value.id)
    if (index !== -1) {
      quizzes.value[index] = { ...currentQuiz.value }
    }
  } else {
    // Add new quiz
    quizzes.value.push({ ...currentQuiz.value })
  }
  showModal.value = false
}

const confirmDelete = (quiz) => {
  quizToDelete.value = quiz
  showDeleteModal.value = true
}

const deleteQuiz = () => {
  if (quizToDelete.value) {
    quizzes.value = quizzes.value.filter(q => q.id !== quizToDelete.value.id)
    quizToDelete.value = null
  }
  showDeleteModal.value = false
}
</script>
