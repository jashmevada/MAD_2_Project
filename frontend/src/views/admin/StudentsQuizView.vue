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
        <BFormSelect v-model="departmentFilter" :options="departmentOptions" class="mb-2" value-field="id"
          text-field="title">
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

        <template #cell(actions)="data">
          <div class="d-flex gap-2">
            <BButton size="sm" variant="outline-primary" :to="`/admin/students/${data.item.id}/score`">
              Scores
            </BButton>
          </div>
        </template>
      </BTable>
    </BCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, shallowRef } from 'vue'
import { apiFetch } from '@/apiFetch'
import { useLoginStore } from '@/stores/AuthStore'
import router from '@/router'
import { useRoute } from 'vue-router'

const loginStore = useLoginStore()
const route = useRoute()

const fields = [
  { key: 'title', label: 'Quiz Title', sortable: true },
  { key: 'subject', label: 'Subject', sortable: true },
  { key: 'date_of_quiz', label: 'Date', sortable: true },
  { key: 'time_duration', label: 'Duration', sortable: true },
  { key: 'no_of_questions', label: 'Questions', sortable: true },
  { key: 'actions', label: 'Actions' }
]

const quizzes = ref([])
const departmentOptions = shallowRef([])

onMounted(async () => {
  quizzes.value = await apiFetch(`/students/${route.params.id}/quizzes`)
  departmentOptions.value = await apiFetch("/departments")
})

const searchQuery = ref('')
const subjectFilter = ref('')
const departmentFilter = ref('')

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