<template>
    <div class="container-fluid p-4">
      <!-- <h1 class="mb-4">Student Quiz Dashboard</h1> -->
      
      <!-- Summary Cards -->
      <BRow class="mb-4">
        <BCol md="3" v-for="card in summaryCards" :key="card.title">
          <BCard :bg-variant="card.variant" text-variant="white" class="mb-2">
            <BCardTitle>{{ card.title }}</BCardTitle>
            <h2 class="mb-0">{{ card.value }}</h2>
            <small>{{ card.subtext }}</small>
          </BCard>
        </BCol>
      </BRow>
      
      <!-- Charts -->
      <BRow>
        <BCol md="6" class="mb-4">
          <BCard title="Quiz Performance Over Time">
            <canvas id="performance-chart"></canvas>
          </BCard>
        </BCol>
        <BCol md="6" class="mb-4">
          <BCard title="Subject Proficiency">
            <canvas id="subject-chart"></canvas>
          </BCard>
        </BCol>
      </BRow>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { BCard, BCardTitle, BRow, BCol } from 'bootstrap-vue-next';
  import Chart from 'chart.js/auto';
  
  const summaryCards = ref([
    { title: 'Quizzes Taken', value: 15, subtext: '3 this week', variant: 'primary' },
    { title: 'Average Score', value: '78%', subtext: '5% improvement', variant: 'success' },
    { title: 'Total Questions', value: 150, subtext: 'Answered correctly', variant: 'info' },
    { title: 'Study Streak', value: '7 days', subtext: 'Keep it up!', variant: 'warning' }
  ]);
  
  onMounted(() => {
    // Performance Chart
    const perfCtx = document.getElementById('performance-chart');
    new Chart(perfCtx, {
      type: 'line',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
        datasets: [{
          label: 'Quiz Scores',
          data: [65, 70, 68, 75, 82, 80],
          borderColor: '#4bc0c0',
          tension: 0.1
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
  
    // Subject Proficiency Chart
    const subjectCtx = document.getElementById('subject-chart');
    new Chart(subjectCtx, {
      type: 'radar',
      data: {
        labels: ['Math', 'Science', 'History', 'Literature', 'Languages'],
        datasets: [{
          label: 'Your Proficiency',
          data: [80, 70, 65, 85, 75],
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgb(54, 162, 235)',
          pointBackgroundColor: 'rgb(54, 162, 235)'
        }]
      },
      options: {
        responsive: true,
        scales: {
          r: {
            angleLines: {
              display: false
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        }
      }
    });
  });
  </script>
  