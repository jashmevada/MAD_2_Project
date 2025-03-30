<template>
  <div class="quiz-container">
    
    <!-- Loading State -->
    <BOverlay :show="loading" rounded="sm" spinner-variant="primary">
     
      <!-- Quiz Not Started Yet -->
      <div v-if="!quizStarted && !quizCompleted" class="text-center my-5">
        <h2>{{ quiz.title }}</h2>
        <h4 class="text-secondary">{{ quiz.subject }}</h4>
        <div class="countdown-container my-4">
          <h4>Quiz will start on: {{ formatDate(quiz.date_of_quiz) }}</h4>
          <p class="text-primary fw-bold">{{ timeRemaining }}</p>
          <BProgress :value="countdownProgress" :max="100" animated></BProgress>
        </div>
        <BButton v-if="canStartNow" variant="primary" size="lg" @click="startQuiz">
          Start Quiz Now
        </BButton>
      </div>

      <!-- Quiz In Progress -->
      <div v-else-if="quizStarted && !quizCompleted" class="quiz-active">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2>{{ quiz.title }}</h2>
          <div class="quiz-timer">
            <span class="badge bg-danger p-2" v-if="timeLeft !== null">
              Time Remaining: {{ formatTime(timeLeft) }}
            </span>
          </div>
        </div>
        <h5 class="text-secondary mb-3">{{ quiz.subject }}</h5>

        <BProgressBar :value="currentQuestionIndex + 1" :max="quiz.no_of_questions" class="mb-4" show-value
          :label="`Question ${currentQuestionIndex + 1} of ${quiz.no_of_questions}`"></BProgressBar>

        <BCard v-if="currentQuestion" class="question-card mb-4">
          <BCardTitle>{{ currentQuestion.question_statement }}</BCardTitle>
          <BCardBody>
            <BListGroup>
              <BListGroupItem v-for="(optionText, optionIndex) in currentQuestion.options" :key="optionIndex" button
                :active="selectedOption === optionIndex" @click="selectOption(optionIndex)"
                class="d-flex align-items-center my-1">
                {{ optionText }}
              </BListGroupItem>
            </BListGroup>
          </BCardBody>

          <BCardFooter class="d-flex justify-content-between">
            <BButton variant="outline-secondary" :disabled="currentQuestionIndex === 0" @click="previousQuestion">
              Previous
            </BButton>

            <BButton v-if="!isLastQuestion" variant="primary" @click="nextQuestion()">
              Next Question
            </BButton>

            <BButton v-else variant="success" @click="finishQuiz()">
              Finish Quiz
            </BButton>
          </BCardFooter>
        </BCard>
      </div>

      <!-- Quiz Completed -->
      <div v-else-if="quizCompleted" class="text-center my-5">
        <h2>Quiz Completed!</h2>
        <BCard class="mt-4">
          <BCardTitle>Quiz Submitted</BCardTitle>
          <BCardBody>
            <p class="lead">Your quiz has been submitted successfully.</p>
            <p>Your results will be available on the student quiz portal.</p>

            <BButton variant="primary" @click="goToQuizPortal" class="mt-3">
              Return to Quiz Portal
            </BButton>
          </BCardBody>
        </BCard>
      </div>
    </BOverlay>
  </div>
</template>

<script setup>
import { apiFetch } from '@/apiFetch';
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';

const route = useRoute()
const router = useRouter();


const quiz = ref({ 
  id: null,
  title: '',
  subject: '',
  date_of_quiz: null,
  time_duration: 0,
  no_of_questions: 0,
  remarks: '',
  question: [],
  chapter_id: null
});
const loading = ref(true);
const quizStarted = ref(false);
const quizCompleted = ref(false);
const currentQuestionIndex = ref(0);
const selectedOption = ref(null);
const userAnswers = ref([]);
const timeRemaining = ref('');
const countdownProgress = ref(0);
const timeLeft = ref(null);
const localTimeLeft = ref(null);
const timerSessionId = ref(null);
const eventSource = ref(null);

let countdownTimer = null;
let localTimerInterval = null;


const currentQuestion = computed(() => {
  if (!quiz.value.question || !quiz.value.question.length) return null;
  return quiz.value.question[currentQuestionIndex.value];
});

const isLastQuestion = computed(() => {
  return currentQuestionIndex.value === quiz.value.question.length - 1;
});

const canStartNow = computed(() => {
  if (!quiz.value.date_of_quiz) return false;
  const now = new Date();
  const startDate = new Date(quiz.value.date_of_quiz);
  return now >= startDate;
});


const loadQuiz = async () => {
  try {
    loading.value = true;
    quiz.value = await apiFetch(`quizzes/${route.params.id}`);


    try {
      quiz.value.question = await apiFetch(`quizzes/${route.params.id}/questions` )
      userAnswers.value = new Array(quiz.value.question.length).fill(null);
    } catch {
      userAnswers.value = []
    }
    

    const now = new Date();
    const startDate = new Date(quiz.value.date_of_quiz);
    console.log(startDate);
    console.log(now);
    
    
    if (now >= startDate) {
      quizStarted.value = true;
      // Connect to SSE for timer updates
      connectToTimerStream();
    } else {
      // Start countdown
      console.log("Countdown");
      
      startCountdown(startDate);
    }
  } catch (error) {
    console.error('Error loading quiz:', error);
  } finally {
    loading.value = false;
  }
};

const connectToTimerStream = () => {
  // Close any existing connection
  if (eventSource.value) {
    eventSource.value.close();
  }
  
  // Create new SSE connection
  const url = `http://localhost:5000/api/quizzes/${route.params.id}/timer-stream/1`;
  eventSource.value = new EventSource(url);
  
  // Set up event listeners
  eventSource.value.addEventListener('connection', (event) => {
    const data = JSON.parse(event.data);
    console.log('SSE Connection established:', data);
  });
  
  eventSource.value.addEventListener('timer_update', (event) => {
    const data = JSON.parse(event.data);
    timerSessionId.value = data.timer_session_id;
    timeLeft.value = data.time_remaining;
    
    // Start or update the local timer
    startLocalTimer(data.time_remaining);
    
    // If timer has completed, finish the quiz
    if (data.status === 'completed' || timeLeft.value <= 0) {
      finishQuiz();
    }
  });
  
  eventSource.value.addEventListener('timer_status', (event) => {
    const data = JSON.parse(event.data);
    if (data.status === 'not_started' && canStartNow.value) {
      // Quiz can be started but hasn't been yet
      quizStarted.value = false;
    }
  });
  
  eventSource.value.onerror = (error) => {
    console.error('SSE Error:', error);
    // Try to reconnect after a delay
    setTimeout(() => {
      connectToTimerStream();
    }, 5000);
  };
};

const startLocalTimer = (initialTime) => {
  localTimeLeft.value = initialTime;
  if (localTimerInterval) {
    clearInterval(localTimerInterval);
  }
  localTimerInterval = setInterval(() => {
    if (localTimeLeft.value > 0) {
      localTimeLeft.value -= 0.1;  // Decrease by 0.1 seconds for smoother animation
    } else {
      clearInterval(localTimerInterval);
      localTimeLeft.value = 0;
    }
  }, 100); // Update every 100ms for smoother countdown
};

const startCountdown = (startDate) => {
  // Store the initial time difference when countdown starts
  const initialTotalDiff = startDate - new Date();
  
  const updateCountdown = () => {
    const now = new Date();
    const diff = startDate - now;
    
    if (diff <= 0) {
      clearInterval(countdownTimer);
      quizStarted.value = true;
      // Connect to SSE for timer updates once countdown is complete
      connectToTimerStream();
      return;
    }
    
    // Calculate progress based on how much time has elapsed compared to initial difference
    const elapsedTime = initialTotalDiff - diff;
    countdownProgress.value = (elapsedTime / initialTotalDiff) * 100;
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    timeRemaining.value = `${days}d ${hours}h ${minutes}m ${seconds}s`;
  };
  
  updateCountdown();
  countdownTimer = setInterval(updateCountdown, 1000);
};

const startQuiz = async () => {
  try {
    loading.value = true;
    
    // Start the timer via API
    const data = await apiFetch(`quizzes/${route.params.id}/start-timer`, {
      method:'POST',
      body: {
      quiz_id: route.params.id,
      user_id: 1,
      duration: parseFloat(quiz.value.time_duration) * 60 
    }
    });
    
    timerSessionId.value = data.timer_session_id;
    
    connectToTimerStream();

    quizStarted.value = true;
  } catch (error) {
    console.error('Error starting quiz:', error);
  } finally {
    loading.value = false;
  }
};

const formatTime = (seconds) => {
  if (seconds === null) return "--:--";
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
};

const selectOption = (optionIndex) => {
  selectedOption.value = optionIndex;
  userAnswers.value[currentQuestionIndex.value] = optionIndex;
  
  // Optionally, send the answer to the backend immediately
  saveCurrentAnswer();
};

const saveCurrentAnswer = async () => {
  try {
    await apiFetch(`/quizzes/${route.params.id}/save-answer`, {
      method: "POST",
      body: {
        question_id: currentQuestion.value.id,
        selected_option: selectedOption.value.toString(),
        user_id: 1
      }
    });
  } catch (error) {
    console.error('Error saving answer:', error);
  }
};

const nextQuestion = () => {
  currentQuestionIndex.value++;
  selectedOption.value = userAnswers.value[currentQuestionIndex.value];
};

const previousQuestion = () => {
  currentQuestionIndex.value--;
  selectedOption.value = userAnswers.value[currentQuestionIndex.value];
};

const finishQuiz = async () => {
  try {
    loading.value = true;
    
    if (localTimerInterval) {
      clearInterval(localTimerInterval);
    }
    
    // Close SSE connection
    if (eventSource.value) {
      eventSource.value.close();
      eventSource.value = null;
    }
    
    // End the timer via API
    if (timerSessionId.value) {
      await apiFetch(`/quizzes/${route.params.id}/end-timer`, {
        method: 'POST',
        body: {
        timer_session_id: timerSessionId.value}
      });
    }
    
    // Submit all answers to backend
    await apiFetch(`/quizzes/${route.params.id}/submit`, {
      method: 'POST',
      body: {
      answers: userAnswers.value.map((optionIndex, questionIndex) => ({
        question_id: quiz.value.question[questionIndex].id,
        selected_option: optionIndex !== null ? optionIndex.toString() : null
      })),
      user_id: 1,
      quiz_id: route.params.id, 
      timer_session_id: timerSessionId.value} 
    });
    
    quizCompleted.value = true;
  } catch (error) {
    console.error('Error submitting quiz:', error);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

const goToQuizPortal = () => {
  if (localTimerInterval) {
      clearInterval(localTimerInterval);
    }
  
  if (eventSource.value) {
      eventSource.value.close();
      eventSource.value = null;
  }
  router.push('/student/quiz/my-quizzes');
};

onMounted(() => {
  loadQuiz();
});

onUnmounted(() => {
  // Clean up timers and SSE connection
  if (countdownTimer) {
    clearInterval(countdownTimer);
  }
  
  if (localTimerInterval) {
    clearInterval(localTimerInterval);
  }
  
  if (eventSource.value) {
    eventSource.value.close();
    eventSource.value = null;
  }
}); 

// Watch for changes to the quiz ID
watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId) {
    // Clean up existing timers and SSE connection
    if (countdownTimer) {
      clearInterval(countdownTimer);
    }
    
    if (localTimerInterval) {
      clearInterval(localTimerInterval);
    }
    
    if (eventSource.value) {
      eventSource.value.close();
      eventSource.value = null;
    }

    selectedOption.value = null;
    currentQuestionIndex.value = 0;
    quizStarted.value = false;
    quizCompleted.value = false;
    timerSessionId.value = null;
    timeLeft.value = null;
    localTimeLeft.value = null;

    loadQuiz();
  }
});

</script>


<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.countdown-container {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.question-card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.quiz-timer {
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
