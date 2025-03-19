<script setup>
import { apiFetch } from '@/main';
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Get route and router
const route = useRoute();
const router = useRouter();

// Subject data
const subject = ref({});
const chapters = ref([]);
const loadingChapters = ref(true);

// Chapter form
const showChapterModal = ref(false);
const isEditingChapter = ref(false);
const selectedChapter = ref(null);
const showDeleteChapterModal = ref(false);

const chapterForm = reactive({
  id: null,
  title: '',
  order: 1,
  description: ''
});

// Chapter fields
const chapterFields = [
  { key: 'order', label: '#', sortable: true },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'description', label: 'Description' },
  { key: 'actions', label: 'Actions' }
];

// Form validation
const chapterValidation = computed(() => {
  return {
    title: chapterForm.title.trim() !== ''
  };
});

// Fetch subject and its chapters
const fetchSubjectDetails = async () => {
  const subjectId = route.params.id;

  try {
    // Fetch subject details
    const subjectData = await apiFetch(`/subjects/${subjectId}`);
    subject.value = await subjectData

    // Simulate API response
    // subject.value = {
    //   id: subjectId,
    //   name: 'Introduction to Programming',
    //   code: 'CS101',
    //   department: 'Computer Science',
    //   credits: 3,
    //   description: 'Basic programming concepts and problem-solving techniques.'
    // };

    // Fetch chapters
    loadingChapters.value = true;
    const chaptersData = await apiFetch(`/subjects/${subjectId}/chapters`);
    chapters.value = await chaptersData

    // Simulate API response
    chapters.value = [
      { id: 1, title: 'Introduction to Algorithms', order: 1, description: 'Basic algorithm concepts' },
      { id: 2, title: 'Variables and Data Types', order: 2, description: 'Understanding different data types' },
      { id: 3, title: 'Control Structures', order: 3, description: 'Loops and conditional statements' }
    ];
  } catch (error) {
    console.error('Error fetching subject details:', error);
  } finally {
    loadingChapters.value = false;
  }
};

// Chapter management functions
const openAddChapterModal = () => {
  isEditingChapter.value = false;
  resetChapterForm();
  showChapterModal.value = true;
};

const editChapter = (chapter) => {
  isEditingChapter.value = true;
  selectedChapter.value = chapter;

  // Populate form with chapter data
  Object.keys(chapterForm).forEach(key => {
    if (key in chapter) {
      chapterForm[key] = chapter[key];
    }
  });

  showChapterModal.value = true;
};

const confirmDeleteChapter = (chapter) => {
  selectedChapter.value = chapter;
  showDeleteChapterModal.value = true;
};

const deleteChapter = async () => {
  if (!selectedChapter.value) return;

  try {
    // Delete chapter
    // await fetch(`/api/chapters/${selectedChapter.value.id}`, { method: 'DELETE' });

    // Update local state
    chapters.value = chapters.value.filter(c => c.id !== selectedChapter.value.id);

    console.log(`Chapter "${selectedChapter.value.title}" deleted successfully`);
  } catch (error) {
    console.error('Error deleting chapter:', error);
  }
};

const handleChapterSubmit = async (event) => {
  // Validate form
  if (!chapterValidation.value.title) {
    event.preventDefault();
    return;
  }

  try {
    if (isEditingChapter.value) {
      // Update existing chapter
      // await fetch(`/api/chapters/${chapterForm.id}`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(chapterForm)
      // });

      // Update local state
      const index = chapters.value.findIndex(c => c.id === chapterForm.id);
      if (index !== -1) {
        chapters.value[index] = { ...chapterForm };
      }

      console.log(`Chapter "${chapterForm.title}" updated successfully`);
    } else {
      // Add new chapter
      // const response = await fetch(`/api/subjects/${subject.value.id}/chapters`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(chapterForm)
      // });
      // const newChapter = await response.json();

      // Simulate API response
      const newChapter = {
        ...chapterForm,
        id: Math.max(0, ...chapters.value.map(c => c.id)) + 1
      };

      // Update local state
      chapters.value.push(newChapter);

      console.log(`Chapter "${chapterForm.title}" added successfully`);
    }
  } catch (error) {
    console.error('Error saving chapter:', error);
    event.preventDefault();
  }
};

const resetChapterForm = () => {
  chapterForm.id = null;
  chapterForm.title = '';
  chapterForm.order = chapters.value.length + 1;
  chapterForm.description = '';
  selectedChapter.value = null;
};

// Fetch data on component mount
onMounted(() => {
  fetchSubjectDetails();
});

</script>

<template>
  <div class="subject-detail-container p-4">
    <BCard no-body>
      <!-- Subject Header -->
      <BCardHeader class="d-flex justify-content-between align-items-center">
        <h3>{{ subject?.name }} <small class="text-muted">({{ subject?.code }})</small></h3>
        <BButton variant="outline-secondary" @click="$router.go(-1)">
          <i class="bi bi-arrow-left"></i> Back
        </BButton>
      </BCardHeader>

      <BCardBody>
        <!-- Subject Details -->
        <div class="mb-4">
          <h5 class="border-bottom pb-2">Subject Information</h5>
          <BRow>
            <BCol md="3" class="fw-bold">Department:</BCol>
            <BCol md="9">{{ subject?.department }}</BCol>
          </BRow>
          <BRow>
            <BCol md="3" class="fw-bold">Credits:</BCol>
            <BCol md="9">{{ subject?.credits }}</BCol>
          </BRow>
          <BRow>
            <BCol md="3" class="fw-bold">Description:</BCol>
            <BCol md="9">{{ subject?.description }}</BCol>
          </BRow>
        </div>

        <!-- Chapters Section -->
        <div>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="border-bottom pb-2 mb-0">Chapters</h5>
            <BButton variant="primary" size="sm" @click="openAddChapterModal">
              <i class="bi bi-plus-circle"></i> Add Chapter
            </BButton>
          </div>

          <BTable hover :items="chapters" :fields="chapterFields" :busy="loadingChapters" show-empty
            empty-text="No chapters found for this subject">
            <template #cell(actions)="{ item }">
              <div class="d-flex gap-2">
                <BButton size="sm" variant="outline-primary" @click="editChapter(item)">
                  <i class="bi bi-pencil"></i> Edit
                </BButton>
                <BButton size="sm" variant="outline-danger" @click="confirmDeleteChapter(item)">
                  <i class="bi bi-trash"></i> Delete
                </BButton>
              </div>
            </template>
          </BTable>
        </div>
      </BCardBody>
    </BCard>

    <!-- Add/Edit Chapter Modal -->
    <BModal v-model="showChapterModal" :title="isEditingChapter ? 'Edit Chapter' : 'Add New Chapter'"
      @hidden="resetChapterForm" @ok="handleChapterSubmit">
      <BForm @submit.prevent>
        <BFormGroup label="Chapter Title" label-for="chapter-title">
          <BFormInput id="chapter-title" v-model="chapterForm.title" :state="chapterValidation.title"
            placeholder="Enter chapter title" required></BFormInput>
          <BFormInvalidFeedback v-if="!chapterValidation.title">
            Chapter title is required
          </BFormInvalidFeedback>
        </BFormGroup>

        <BFormGroup label="Order" label-for="chapter-order">
          <BFormInput id="chapter-order" v-model.number="chapterForm.order" type="number" min="1"
            placeholder="Enter chapter order"></BFormInput>
        </BFormGroup>

        <BFormGroup label="Description" label-for="chapter-description">
          <BFormTextarea id="chapter-description" v-model="chapterForm.description"
            placeholder="Enter chapter description" rows="3"></BFormTextarea>
        </BFormGroup>
      </BForm>
    </BModal>

    <!-- Delete Chapter Confirmation Modal -->
    <BModal v-model="showDeleteChapterModal" title="Confirm Delete" ok-variant="danger" ok-title="Delete"
      @ok="deleteChapter">
      <p class="my-4">Are you sure you want to delete the chapter "{{ selectedChapter?.title }}"?</p>
      <p class="text-danger">This action cannot be undone.</p>
    </BModal>
  </div>
</template>
