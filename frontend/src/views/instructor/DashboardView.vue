<template>
  <div class="container-fluid p-4">  
    <BRow class="mb-4">
      <BCol md="3" v-for="card in summaryCards" :key="card.title">
        <BCard :bg-variant="card.variant" text-variant="white" class="mb-2">
          <BCardTitle>{{ card.title }}</BCardTitle>
          <h2 class="mb-0">{{ card.value }}</h2>
          <!-- <small>{{ card.subtext }}</small> -->
        </BCard>
      </BCol>
    </BRow>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { BCard, BCardTitle, BRow, BCol } from 'bootstrap-vue-next';
import { apiFetch } from '@/apiFetch';
import { useLoginStore } from '@/stores/AuthStore';

const loginStore = useLoginStore()

const summaryCards = ref([
  { title: 'Total Quizzes', value: 15, variant: 'primary' },
  { title: 'Total Questions', value: 150, variant: 'info' },
]);

onMounted(async () => {
 const data = await apiFetch(`/instructors/${loginStore.get_user_data().id}/analytics`)

 summaryCards.value[0].value = data.total_quiz
 summaryCards.value[1].value = data.total_questions
  
});
</script>
