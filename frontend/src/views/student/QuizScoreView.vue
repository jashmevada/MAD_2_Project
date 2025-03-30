<template>
  <div class="container mt-4">
    <h1>Quiz Score History</h1>

    <BCard class="mb-4">
      <BCardTitle>{{ quizInfo.title }}</BCardTitle>
      <BCardText>
        <strong>Chapter:</strong> {{ quizInfo.chapter }}<br>
        <strong>Department:</strong> {{ quizInfo.department }}<br>
        <strong>Total Questions:</strong> {{ quizInfo.total_questions }}<br>
        <strong>Attempts:</strong> {{ quizScores.length }}
      </BCardText>
      <BCardFooter>
        <BButton variant="primary" @click="exportCSV">Export as CSV</BButton>
      </BCardFooter>
    </BCard>

    <BCard bg-variant="primary" text-variant="white" class="mb-4" v-if="latestScore">
      <BCardTitle>Latest Attempt</BCardTitle>
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h2 class="mb-0">{{ latestScore.marks }}%</h2>
          <small>{{ formatDate(latestScore.date) }}</small>
        </div>
        <div>
          <BButton variant="light" size="sm" @click="showDetails(latestScore)">
            View Details
          </BButton>
        </div>
      </div>
    </BCard>

    <BCard class="mb-4">
      <BCardTitle>Score History</BCardTitle>
      <div style="height: 300px;">
        <canvas id="score-history-chart"></canvas>
      </div>
    </BCard>


    <BCard>
      <BCardTitle>All Attempts</BCardTitle>
      <BTable striped hover :items="quizScores" :fields="fields">

        <template #cell(score)="data">
          <span :class="getScoreClass(data.value)">{{ data.value }}%</span>
        </template>
        <template #cell(date)="data">
          {{ formatDate(data.value) }}
        </template>
        <template #cell(actions)="data">
          <BButton size="sm" variant="primary" @click="showDetails(data.item)">
            Details
          </BButton>
        </template>
      </BTable>
    </BCard>

    <BModal v-model="score_details" id="score-details-modal" title="Attempt Details" size="lg" hide-footer>
      <div v-if="selectedAttempt">
        <h4>Score: {{ selectedAttempt.marks }}%</h4>
        <p>Date: {{ formatDate(selectedAttempt.date) }}</p>

        <h5 class="mt-4">Question Breakdown</h5>
        <BTable striped :items="selectedAttempt.questions" :fields="questionFields">
        </BTable>
      </div>
    </BModal>
  </div>

  
  <BToastOrchestrator />

</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import Chart from 'chart.js/auto';
import { apiFetch } from '@/apiFetch';
import { useRoute } from 'vue-router';
import { useLoginStore } from '@/stores/AuthStore';
import { useToastController } from 'bootstrap-vue-next'

// Quiz information
const quizInfo = ref({
  id: -1,
  title: '',
  chapter: '',
  department: '',
  total_questions: 0
});


const toast = useToastController()

const quizScores = ref([
  {
    id: -1,
    score: 0,
    date: undefined,
    questions: [{ id: -1, question: '', correct: true },]
  },
]);

// Table fields
const fields = [
  { key: 'id', label: 'Attempt #' },
  { key: 'marks', label: 'Score' },
  { key: 'date', label: 'Date' },
  { key: 'actions', label: 'Actions' }
];

const questionFields = [
  { key: 'question', label: 'Question' },
  { key: 'correct', label: 'Correct' }
];

const route = useRoute()
const loginStore = useLoginStore()

onMounted(async () => {
  const quiz_data = await apiFetch(`/students/${loginStore.get_user_data().id}/quizzes/${route.params.id}/scores`)

  quizInfo.value = quiz_data.quiz_info

  quizScores.value = quiz_data.quiz_scores.map((d) => ({ ...d, date: new Date(d.date) }))

  renderScoreHistoryChart();
});


const latestScore = computed(() => {
  if (quizScores.value.length === 0) return null;
  return [...quizScores.value].sort((a, b) => b.date - a.date)[0];
});

const selectedAttempt = ref(null);

const formatDate = (date) => {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getScoreClass = (score) => {
  if (score >= 80) return 'text-success';
  if (score >= 60) return 'text-warning';
  return 'text-danger';
};

const score_details = ref(false)

const showDetails = (attempt) => {
  selectedAttempt.value = attempt;

  score_details.value = true
};

// Render score history chart
const renderScoreHistoryChart = () => {
  const ctx = document.getElementById('score-history-chart');

  // Sort scores by date (oldest to newest)
  const sortedScores = [...quizScores.value].sort((a, b) => a.date - b.date);
  console.log(sortedScores);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: sortedScores.map(score => formatDate(score.date)),
      datasets: [{
        label: 'Score (%)',
        data: sortedScores.map(score => score.marks),
        borderColor: '#4bc0c0',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
};

const exportCSV = async () => {

  try {
    const response = await apiFetch('/export-csv', {
      method: 'POST',
      query: { q: 's_quiz_score', quiz_id:route.params.id },
      responseType: 'blob'
    });

    const url = URL.createObjectURL(response);

    const link = document.createElement('a');
    link.href = url;
    link.download = `data-export-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

  } catch (error) {
    console.error('Error exporting CSV:', error);
  }
};

</script>