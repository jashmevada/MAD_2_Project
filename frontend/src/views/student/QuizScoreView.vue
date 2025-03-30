<template>
    <div class="container mt-4">
      <h1>Quiz Score History</h1>
      
      <!-- Quiz Info Card -->
      <BCard class="mb-4">
        <BCardTitle>{{ quizInfo.title }}</BCardTitle>
        <BCardText> 
          <strong>Chapter:</strong> {{ quizInfo.chapter }}<br>
          <strong>Department:</strong> {{ quizInfo.department }}<br>
          <strong>Total Questions:</strong> {{ quizInfo.total_questions }}<br>
          <strong>Attempts:</strong> {{ quizScores.length }}
        </BCardText>
      </BCard>
      
      <!-- Latest Score Card -->
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
      
      <!-- Score History Chart -->
      <BCard class="mb-4">
        <BCardTitle>Score History</BCardTitle>
        <div style="height: 300px;">
          <canvas id="score-history-chart"></canvas>
        </div>
      </BCard>
      
      <!-- All Attempts Table -->
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
      
      <!-- Score Details Modal -->
      <BModal v-model="score_details" id="score-details-modal" title="Attempt Details" size="lg" hide-footer>
        <div v-if="selectedAttempt">
          <h4>Score: {{ selectedAttempt.marks }}%</h4>
          <p>Date: {{ formatDate(selectedAttempt.date) }}</p>
          
          <h5 class="mt-4">Question Breakdown</h5>
          <BTable striped :items="selectedAttempt.questions" :fields="questionFields">
            <!-- <template #cell(correct)="data">
                
              <BIcon v-if="data.value" icon="check-circle-fill" variant="success"></BIcon>
              <BIcon v-else icon="x-circle-fill" variant="danger"></BIcon>
            </template> -->
          </BTable>

          <!-- <div class="d-flex justify-content-end mt-4">
            <BButton variant="secondary" @click="$bvModal.hide('score-details-modal')">
              Close
            </BButton>
          </div> -->
        </div>
      </BModal>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import Chart from 'chart.js/auto';
import { apiFetch } from '@/apiFetch';
import { useRoute } from 'vue-router';
import { useLoginStore } from '@/stores/AuthStore';
  
  // Quiz information
  const quizInfo = ref({
    id: -1,
    title: '',
    chapter: '',
    department: '',
    total_questions: 0
  });
  
  // Score data
  const quizScores = ref([
    {
      id: -1,
      score: 0,
      date: undefined,
      questions: [{ id: -1, question: '', correct: true},]
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

    quizScores.value = quiz_data.quiz_scores.map((d) => ({...d, date: new Date(d.date)}))

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
  // Show details modal
  const showDetails = (attempt) => {
    selectedAttempt.value = attempt;
    // renderCategoryChart();
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
  
  // Render category performance chart in modal
//   const renderCategoryChart = () => {
//     if (!selectedAttempt.value) return;
    
//     // Clear previous chart if exists
//     const existingChart = Chart.getChart('category-chart');
//     if (existingChart) existingChart.destroy();
    
//     const ctx = document.getElementById('category-chart');
    
//     // Group questions by category and calculate performance
//     const categories = {};
//     selectedAttempt.value.questions.forEach(q => {
//       if (!categories[q.category]) {
//         categories[q.category] = { total: 0, correct: 0 };
//       }
//       categories[q.category].total++;
//       if (q.correct) categories[q.category].correct++;
//     });
    
//     const categoryLabels = Object.keys(categories);
//     const categoryData = categoryLabels.map(cat => 
//       (categories[cat].correct / categories[cat].total) * 100
//     );
    
//     new Chart(ctx, {
//       type: 'bar',
//       data: {
//         labels: categoryLabels,
//         datasets: [{
//           label: 'Performance by Category (%)',
//           data: categoryData,
//           backgroundColor: 'rgba(54, 162, 235, 0.7)'
//         }]
//       },
//       options: {
//         responsive: true,
//         maintainAspectRatio: false,
//         scales: {
//           y: {
//             beginAtZero: true,
//             max: 100
//           }
//         }
//       }
//     });
//   };
  </script>
  