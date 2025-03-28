<template>
  <BCard>
    <BCardHeader class="d-flex justify-content-between align-items-center">
      <BButton variant="outline-secondary" @click="$router.go(-1)">Back</BButton>
    </BCardHeader>

    <BForm @submit.prevent="submitQuiz" novalidate>

      <BFormGroup id="quiz-title" label="Quiz Title:" label-for="input-title">
        <BFormInput id="input-title" v-model="quiz.title" placeholder="Enter quiz title" required />
      </BFormGroup>

      <BFormGroup id="quiz-subject" label="Subject:" label-for="input-subject">
        <BFormSelect id="input-subject" v-model="quiz.subject_id" placeholder="Enter subject" :options="subjectList"
          text-field="name" value-field="id" @change="updateChapterList" required />
      </BFormGroup>

      <BFormGroup id="quiz-chapters" label="Chapters:" label-for="input-chapters">
        <BFormSelect id="input-chapters" v-model="quiz.chapter_id" placeholder="Enter chapters covered"
          :options="chapterList" text-field="name" value-field="id" required />
      </BFormGroup>

      <!-- Date and Time -->
      <BRow>
        <BCol md="6">
          <BFormGroup id="quiz-date" label="Quiz Date:" label-for="input-date">
            <BFormInput id="input-date" v-model="quiz.date" type="date" required />
          </BFormGroup>
        </BCol>
        <BCol md="6">
          <BFormGroup id="quiz-time" label="Quiz Time:" label-for="input-time">
            <BFormInput id="input-time" v-model="quiz.time" type="time" required />
          </BFormGroup>
        </BCol>
      </BRow>

      <!-- Duration and Question Count -->
      <BRow>
        <BCol md="6">
          <BFormGroup id="quiz-duration" label="Duration (minutes):" label-for="input-duration">
            <BFormInput id="input-duration" v-model="quiz.time_duration" type="number" min="1" required />
          </BFormGroup>
        </BCol>
        <BCol md="6">
          <BFormGroup id="quiz-question-count" label="Number of Questions:" label-for="input-question-count">
            <BFormInput id="input-question-count" v-model="questionCount" type="number" min="1"
              @change="updateQuestionCount" required />
          </BFormGroup>
        </BCol>
      </BRow>

      <!-- Questions Section -->
      <h3 class="mt-4">Questions</h3>
      <div v-for="(question, qIndex) in quiz.questions" :key="qIndex"
        class="question-container mb-4 p-3 border rounded">
        <BFormGroup :label="`Question ${qIndex + 1}:`" :label-for="`question-${qIndex}`">
          <BFormInput class="mb-2" :id="`question-${qIndex}`" v-model="question.question_statement"
            placeholder="Enter question" required />
        </BFormGroup>

        <!-- Options -->
        <div v-for="(option, oIndex) in question.options" :key="`${qIndex}-${oIndex}`" class="d-flex mb-2">
          <BFormInput v-model="question.options[oIndex]" :placeholder="`Option ${oIndex + 1}`" class="me-2" required />
          <BFormRadio v-model="question.correct_option" :value="oIndex" :name="`correct-answer-${oIndex}-${qIndex}`">
            Correct
          </BFormRadio>
        </div>

        <div class="d-flex mt-2">
          <BButton variant="outline-primary" size="sm" @click="addOption(qIndex)" class="me-2">
            Add Option
          </BButton>
          <BButton variant="outline-danger" size="sm" @click="removeOption(qIndex)"
            :disabled="question.options.length <= 2">
            Remove Option
          </BButton>
        </div>
      </div>

      <div class="d-flex justify-content-end mt-4">
        <BButton type="submit" variant="primary">Create Quiz</BButton>
      </div>
    </BForm>
  </BCard>

  {{ quiz }}
</template>

<script setup>
import { apiFetch } from '@/apiFetch'
import router from '@/router'
import { useLoginStore } from '@/stores/AuthStore'
// import { BFormSelect } from 'bootstrap-vue-next'
import { ref, reactive, onMounted, shallowRef, watch } from 'vue'
import { useRoute } from 'vue-router'

const subjectList = shallowRef()
const initQuestionList = ref()
const route = useRoute()

const quiz_id = route.params?.id
const quiz = ref({
  title: '',
  subject_id: '',
  chapter_id: '',
  date: '',
  time_duration: 30,
  remarks: '',
  created_by: 0,
  questions: []
})

watch(quiz, (old, ne) => {
  console.log(ne);
})

const questionCount = ref(1)
const chapterList = shallowRef()

onMounted(async () => {
  if (useLoginStore().get_user_data().subject) {
    subjectList.value = [await apiFetch(`/subjects/${useLoginStore().get_user_data().subject}`)]
  }
  else {
    subjectList.value = await apiFetch(`/subjects`)
  }

  if (quiz_id) {
    quiz.value = await apiFetch(`/quizzes/${quiz_id}`)
    const date = new Date(quiz.value.date_of_quiz)
    quiz.value.date = date.toISOString().slice(0, 10);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    quiz.value.time = `${hours}:${minutes}`;

    initQuestionList.value = await apiFetch(`/quizzes/${quiz_id}/questions`)
    questionCount.value = quiz.value.no_of_questions
    updateChapterList()
  }
  // quiz.value.questions.push(...initQuestionList.value)
  initializeQuestions(0)
})



const updateChapterList = async () => {
  chapterList.value = await apiFetch(`/subjects/${quiz.value.subject_id}/chapters`).catch(() => { return [{ id: -1, name: 'Please Select Subject First' }] })
}

const initializeQuestions = (count) => {
  quiz.value.questions = []

  quiz.value.questions.push(...initQuestionList.value.map((e) => {e.options = Object.values(e.options); return e}))
  
  for (let i = 0; i < count; i++) {
    quiz.value.questions.push({
      question_statement: '',
      options: ['', ''],
      correct_option: 0
    })
  }
  
  // console.log(quiz.value.questions);
}

const updateQuestionCount = () => {
  const count = parseInt(questionCount.value) || 1
  initializeQuestions(count - 1)
}

const addOption = (questionIndex) => {
  if (quiz.value.questions[questionIndex].options.length < 6) {
    quiz.value.questions[questionIndex].options.push('')
  }
}

const removeOption = (questionIndex) => {
  if (quiz.value.questions[questionIndex].options.length > 2) {
    quiz.value.questions[questionIndex].options.pop()

    // Reset correct answer if it was pointing to a removed option
    if (quiz.value.questions[questionIndex].correct_option >= quiz.value.questions[questionIndex].options.length) {
      quiz.value.questions[questionIndex].correct_option = 0
    }
  }
}

const submitQuiz = async () => {
  try {

    const formattedQuiz = {
      ...quiz.value,
      created_by: quiz_id,
      date_of_quiz: `${quiz.value.date}T${quiz.value.time}`,
      questions: quiz.value.questions.map(q => ({
        question_statement: q.question_statement,
        options: q.options,
        correct_option: q.correct_option
      }))
    }

    console.log(formattedQuiz);

    const response = await apiFetch(`/quizzes/${quiz_id}`, {
      method: 'PUT',
      body: JSON.stringify(formattedQuiz)
    })
    router.go(-1)
  } catch (error) {
    console.error('Error submitting quiz:', error)
    alert('An error occurred. Please try again.')
  }
}

const resetForm = () => {
  quiz.value.title = ''
  quiz.value.subject = ''
  quiz.value.chapters = ''
  quiz.value.date = ''
  quiz.value.time = ''
  quiz.value.duration = 30
  questionCount.value = 1
  initializeQuestions(1)
}


</script>

<style scoped>
.question-container {
  background-color: #f8f9fa;
}
</style>