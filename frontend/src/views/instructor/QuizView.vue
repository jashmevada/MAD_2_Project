<template>
  <div class="container mt-5">

    <div class="row mb-4">
      <div class="col-md-6">
        <BFormInput v-model="searchQuery" placeholder="Search quizzes..." type="search" class="mb-2" />
      </div>
      <!-- <div class="col-md-3">
          <BFormSelect v-model="subjectFilter" :options="subjectOptions" class="mb-2">
            <template #first>
              <option value="">All Subjects</option>
            </template>
</BFormSelect>
</div> -->
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

    <BModal v-model="showDeleteModal" title="Confirm Deletion" @ok="deleteQuiz">
      <p>Are you sure you want to delete the quiz "{{ quizToDelete?.title }}"?</p>
    </BModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { apiFetch } from '@/apiFetch'
import router from '@/router'
import { useLoginStore } from '@/stores/AuthStore'

const fields = [
  { key: 'title', label: 'Quiz Title', sortable: true },
  // { key: 'subject', label: 'Subject', sortable: true },
  { key: 'date_of_quiz', label: 'Date', sortable: true },
  { key: 'time_duration', label: 'Duration', sortable: true },
  { key: 'no_of_questions', label: 'Questions', sortable: true },
  { key: 'actions', label: 'Actions' }
]

const quizzes = ref([])


const searchQuery = ref('')
const subjectFilter = ref('')

const loginStore = useLoginStore()
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const currentQuiz = ref({})
const quizToDelete = ref(null)

onMounted(async () => {
  quizzes.value = await apiFetch("/quizzes", {
    query: { subject_id: loginStore.get_user_data().subject }
  })
})

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
  router.push(`quiz/${quiz.id}/edit`)
  // showModal.value = true
}

const saveQuiz = () => {
  if (isEditing.value) {
    const index = quizzes.value.findIndex(q => q.id === currentQuiz.value.id)
    if (index !== -1) {
      quizzes.value[index] = { ...currentQuiz.value }
    }
  } else {
    quizzes.value.push({ ...currentQuiz.value })
  }
  showModal.value = false
}

const confirmDelete = (quiz) => {
  quizToDelete.value = quiz
  showDeleteModal.value = true
}

const deleteQuiz = async () => {

  try {
    if (quizToDelete.value) {
      const resp = await apiFetch(`/quizzes/${quizToDelete.value.id}`, { method: 'DELETE' })
      quizzes.value = quizzes.value.filter(q => q.id !== quizToDelete.value.id)
      quizToDelete.value = null
    }
    showDeleteModal.value = false
  }
  catch (e) {
    console.log(e);

  }
}
</script>