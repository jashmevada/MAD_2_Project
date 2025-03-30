<template>
  <div class="container-fluid p-4">
    <!-- <h1 class="mb-4">Quiz Admin Dashboard</h1> -->

    <!-- Summary Cards -->

    <BRow class="mb-4">
      <BCol md="3">
        <BCard bg-variant="primary" text-variant="white" class="mb-2">
          <BCardTitle>Total Students</BCardTitle>
          <h2 class="mb-0">{{ api_data?.student_count }}</h2>
        </BCard>
      </BCol>
      <BCol md="3">
        <BCard bg-variant="primary" text-variant="white" class="mb-2">
          <BCardTitle>Total Instructors</BCardTitle>
          <h2 class="mb-0">{{ api_data?.instructor_count }}</h2>
       
        </BCard>
      </BCol>

      <BCol md="3">
        <BCard bg-variant="info" text-variant="white" class="mb-2">
          <BCardTitle>Total Quizzes</BCardTitle>
          <h2 class="mb-0">{{ totalQuizzes }}</h2>
       
        </BCard>
      </BCol>

      <BCol md="3">
        <BCard bg-variant="success" text-variant="white" class="mb-2">
          <BCardTitle>Total Questions</BCardTitle>
          <h2 class="mb-0">{{ totalQuestions }}</h2>
        
        </BCard>
      </BCol>
    </BRow>

    <!-- Charts -->
    <BRow>
      <BCol md="6" class="mb-4">
        <BCard title="Quiz Completions (Last 6 Months)">
          <div>
            <canvas id="quiz-completions-chart"></canvas>
          </div>
        </BCard>
      </BCol>

      <BCol md="8" class="mb-4">
        <BCard title="Top Performing Quizzes">
          <div>
            <canvas id="quiz-performance-chart"></canvas>
          </div>
        </BCard>
      </BCol>
<!-- 
      <BCol md="4" class="mb-4">
        <BCard title="User Engagement">
          <div>
            <canvas id="user-engagement-chart"></canvas>
          </div>
        </BCard>
      </BCol> -->
    </BRow>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { BCard, BCardTitle, BRow, BCol } from 'bootstrap-vue-next';
import Chart from 'chart.js/auto';
import { apiFetch } from '@/apiFetch';

// Summary card data
const totalQuizzes = ref(0);
// const newQuizzesThisMonth = ref(23);
const totalQuestions = ref(0);

const api_data = ref()

// Initialize charts when component is mounted
onMounted(async () => {
  // Quiz Completions Chart (Line chart)

  api_data.value = await apiFetch("/admin/analytics")

  totalQuizzes.value = api_data.value.total_quizzes
  totalQuestions.value = api_data.value.total_questions

  const completionsCtx = document.getElementById('quiz-completions-chart');

  new Chart(completionsCtx, {
    type: 'line',
    data: {
      labels: ['October', 'November', 'December', 'January', 'February', 'March'],
      datasets: [{
        label: 'Quiz Completions',
        data: [1250, 1380, 1120, 1450, 1680, 1820],
        borderColor: '#4bc0c0',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: false
        }
      }
    }
  });

  // Question Difficulty Distribution (Pie chart)
  const difficultyCtx = document.getElementById('question-difficulty-chart');
  new Chart(difficultyCtx, {
    type: 'pie',
    data: {
      labels: ['Easy', 'Medium', 'Hard', 'Expert'],
      datasets: [{
        data: [35, 45, 15, 5],
        backgroundColor: [
          'rgba(75, 192, 192, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(255, 99, 132, 0.7)'
        ]
      }]
    },
    options: {
      responsive: true
    }
  });

  // Top Performing Quizzes (Bar chart)
  const performanceCtx = document.getElementById('quiz-performance-chart');
  new Chart(performanceCtx, {
    type: 'bar',
    data: {
      labels: ['JavaScript Basics', 'HTML Fundamentals', 'CSS Mastery', 'Vue.js Essentials', 'React Fundamentals'],
      datasets: [{
        label: 'Completion Rate (%)',
        data: [92, 88, 76, 84, 79],
        backgroundColor: 'rgba(54, 162, 235, 0.7)'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });

  // User Engagement (Doughnut chart)
  const engagementCtx = document.getElementById('user-engagement-chart');
  new Chart(engagementCtx, {
    type: 'doughnut',
    data: {
      labels: ['Mobile', 'Desktop', 'Tablet'],
      datasets: [{
        data: [65, 30, 5],
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)'
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
});
</script>

<style scoped>
.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
