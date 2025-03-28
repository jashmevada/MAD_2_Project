<template>
    <BCard>    
        <BCardHeader class="d-flex justify-content-between align-items-center">
            <span></span>
            <BButton variant="outline-secondary" @click="$router.go(-1)">Back</BButton>
        </BCardHeader>

      <BForm @submit.prevent="submitQuiz" novalidate>
      
        <BFormGroup id="quiz-title" label="Quiz Title:" label-for="input-title">
          <BFormInput
            id="input-title"
            v-model="quiz.title"
            placeholder="Enter quiz title"
            required
          />
        </BFormGroup>
  
        <BFormGroup id="quiz-subject" label="Subject:" label-for="input-subject">
          <BFormSelect
            id="input-subject"
            v-model="quiz.subject_id"
            placeholder="Enter subject"
            :options="subjectList"
            text-field="name"
            value-field="id"
            @change="updateChapterList"
            required
          />
        </BFormGroup>
  
        <BFormGroup id="quiz-chapters" label="Chapters:" label-for="input-chapters">
          <BFormSelect
            id="input-chapters"
            v-model="quiz.chapter_id"
            placeholder="Enter chapters covered"
            :options="chapterList"
            text-field="name"
            value-field="id"
            required
          />
        </BFormGroup>
  
        <!-- Date and Time -->
        <BRow>
          <BCol md="6">
            <BFormGroup id="quiz-date" label="Quiz Date:" label-for="input-date">
              <BFormInput
                id="input-date"
                v-model="quiz.date"
                type="date"
                required
              />
            </BFormGroup>
          </BCol>
          <BCol md="6">
            <BFormGroup id="quiz-time" label="Quiz Time:" label-for="input-time">
              <BFormInput
                id="input-time"
                v-model="quiz.time"
                type="time"
                required
              />
            </BFormGroup>
          </BCol>
        </BRow>
  
        <!-- Duration and Question Count -->
        <BRow>
          <BCol md="6">
            <BFormGroup id="quiz-duration" label="Duration (minutes):" label-for="input-duration">
              <BFormInput
                id="input-duration"
                v-model="quiz.time_duration"
                type="number"
                min="1"
                required
              />
            </BFormGroup>
          </BCol>
          <BCol md="6">
            <BFormGroup id="quiz-question-count" label="Number of Questions:" label-for="input-question-count">
              <BFormInput
                id="input-question-count"
                v-model="questionCount"
                type="number"
                min="1"
                @change="updateQuestionCount"
                required
              />
            </BFormGroup>
          </BCol>
        </BRow>
  
        <!-- Questions Section -->
        <h3 class="mt-4">Questions</h3>
        <div v-for="(question, qIndex) in quiz.questions" :key="qIndex" class="question-container mb-4 p-3 border rounded">
          <BFormGroup :label="`Question ${qIndex + 1}:`" :label-for="`question-${qIndex}`">
            <BFormInput
              class="mb-2"
              :id="`question-${qIndex}`"
              v-model="question.text"
              placeholder="Enter question"
              required
            />
          </BFormGroup>
  
          <!-- Options -->
          <div v-for="(option, oIndex) in question.options" :key="`${qIndex}-${oIndex}`" class="d-flex mb-2">
            <BFormInput
              v-model="question.options[oIndex]"
              :placeholder="`Option ${oIndex + 1}`"
              class="me-2"
              required
            />
            <BFormRadio
              v-model="question.correctAnswer"
              :value="oIndex"
              :name="`c-ans-${oIndex}-${qIndex}`"
              >
              Correct
            </BFormRadio>
          </div>
  
          <!-- Add/Remove Option Buttons -->
          <div class="d-flex mt-2">
            <BButton 
              variant="outline-primary" 
              size="sm" 
              @click="addOption(qIndex)" 
              class="me-2"
            >
              Add Option
            </BButton>
            <BButton 
              variant="outline-danger" 
              size="sm" 
              @click="removeOption(qIndex)" 
              :disabled="question.options.length <= 2"
            >
              Remove Option
            </BButton>
          </div>
        </div>
  
        <!-- Submit Button -->
        <div class="d-flex justify-content-end mt-4">
          <BButton type="submit" variant="primary">Create Quiz</BButton>
        </div>
      </BForm>
    </BCard>
</template>
  
<script setup>
  import { apiFetch } from '@/apiFetch'
  import router from '@/router'
import { useLoginStore } from '@/stores/AuthStore'
  // import { BFormSelect } from 'bootstrap-vue-next'
  import { ref, reactive, onMounted, shallowRef, computed } from 'vue'
import { useRoute } from 'vue-router'
  
  const subjectList = shallowRef()
  const route = useRoute()

  const quiz_id = route.params?.id
  let quiz = reactive({
    title: '',
    subject_id: '',
    chapter_id: '',
    date: '',
    time_duration: 30,
    remarks: '',
    created_by: 0,
    questions: []
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
       const data = await apiFetch(`/quizzes/${quiz_id}`)

       quiz = reactive({
        title: data.title, 
        subject_id: data.subject_id,
        chapter_id: data.chapter_id,
        date: new Date(data.date).getDate(),
        time_duration: data.time_duration,
        remakrs: '',
        created_by: data.created_by,
        quistions: []
       })
       console.log(data);
        
    }
  })

  
  const updateChapterList = async () => {
    chapterList.value = await apiFetch(`/subjects/${quiz.subject_id}/chapters`).catch(() => {return [{id: -1, name: 'Please Select Subject First'}]})
  }

  // Initialize with one question
  const initializeQuestions = (count) => {
    quiz.questions = []
    for (let i = 0; i < count; i++) {
      quiz.questions.push({
        text: '',
        options: ['', ''],
        correctAnswer: 0
      })
    }
  }
  
  const updateQuestionCount = () => {
    const count = parseInt(questionCount.value) || 1
    initializeQuestions(count)
  }
  
  const addOption = (questionIndex) => {
    if (quiz.questions[questionIndex].options.length < 6) {
      quiz.questions[questionIndex].options.push('')
    }
  }

  const removeOption = (questionIndex) => {
    if (quiz.questions[questionIndex].options.length > 2) {
      quiz.questions[questionIndex].options.pop()
      
      // Reset correct answer if it was pointing to a removed option
      if (quiz.questions[questionIndex].correctAnswer >= quiz.questions[questionIndex].options.length) {
        quiz.questions[questionIndex].correctAnswer = 0
      }
    }
  }
  
  const submitQuiz = async () => {
    try {

      const formattedQuiz = {
        ...quiz,
        date_of_quiz: `${quiz.date}T${quiz.time}`,
        questions: quiz.questions.map(q => ({
          question_statement: q.text,
          options: q.options,
          correct_option: q.correctAnswer
        }))
      }

      console.log(formattedQuiz);
      
      // API call
      const response = await apiFetch('/quizzes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formattedQuiz)
      })
      router.go(-1)
      // if (response.status === 200) {
        // alert('Quiz created successfully!')
        // resetForm()
      // } else {
      //   alert('Failed to create quiz. Please try again.')
      // }
    } catch (error) {
      console.error('Error submitting quiz:', error)
      alert('An error occurred. Please try again.')
    }
  }
  
  const resetForm = () => {
    quiz.title = ''
    quiz.subject = ''
    quiz.chapters = ''
    quiz.date = ''
    quiz.time = ''
    quiz.duration = 30
    questionCount.value = 1
    initializeQuestions(1)
  }
  
  initializeQuestions(1)
</script>
  
<style scoped>
  .question-container {
    background-color: #f8f9fa;
  }
</style>
  