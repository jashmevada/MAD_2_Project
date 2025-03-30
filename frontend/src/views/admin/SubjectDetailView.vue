<script setup>
import { apiFetch } from '@/apiFetch';
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToastController } from 'bootstrap-vue-next'

const route = useRoute();
const router = useRouter();
const toast = useToastController()


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
  name: '',
  description: ''
});


const chapterFields = [
  { key: 'name', label: 'Title', sortable: true },
  { key: 'description', label: 'Description' },
  { key: 'actions', label: 'Actions' }
];


const chapterValidation = computed(() => {
  return {
    title: chapterForm.name.trim() !== ''
  };
});


const fetchSubjectDetails = async () => {
  const subjectId = route.params.id;

  try {

    const subjectData = await apiFetch(`/subjects/${subjectId}`);
    subject.value = await subjectData

    loadingChapters.value = true;
    const chaptersData = await apiFetch(`/subjects/${subjectId}/chapters`);
    chapters.value = await chaptersData

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
  console.log(chapter);

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
    await apiFetch("/chapters", { method: 'DELETE', query: { id: selectedChapter.value.id } });

    // Update local state
    chapters.value = chapters.value.filter(c => c.id !== selectedChapter.value.id);

    console.log(`Chapter "${selectedChapter.value.title}" deleted successfully`);
    toast.show?.({ props: { title: 'Delete Chapter', value: true, variant: 'success', body: `Chapter "${chapterForm.title}" added successfully.` } })
  } catch (error) {
    console.error('Error deleting chapter:', error);
    toast.show?.({ props: { title: 'Delete Chapter', value: true, variant: 'danger', body: `Chapter "${chapterForm.title}" Not Delete.` } })
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

      await apiFetch(`/chapters/${chapterForm.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chapterForm)
      });

      // Update local state
      const index = chapters.value.findIndex(c => c.id === chapterForm.id);
      if (index !== -1) {
        chapters.value[index] = { ...chapterForm };
      }

      console.log(`Chapter "${chapterForm.title}" updated successfully`);
      toast.show?.({ props: { title: 'Edit Chapter', value: true, variant: 'success', body: `Chapter "${chapterForm.title}" edit successfully.` } })

    } else {

      const response = await apiFetch(`/subjects/${subject.value.id}/chapters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chapterForm)
      });

      const newChapter = {
        ...chapterForm,
        id: Math.max(0, ...chapters.value.map(c => c.id)) + 1
      };

      // Update local state
      chapters.value.push(newChapter);

      toast.show?.({ props: { title: 'New Chapter', value: true, variant: 'success', body: `Chapter "${chapterForm.title}" added successfully.` } })

    }
  } catch (error) {
    console.error('Error saving chapter:', error);
    toast.show?.({ props: { title: 'Chapter', value: true, variant: 'danger', body: `Failed to Update` } })
    event.preventDefault();
  }
};

const resetChapterForm = () => {
  chapterForm.id = null;
  chapterForm.title = '';
  // chapterForm.order = chapters.value.length + 1;
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

      <BCardHeader class="d-flex justify-content-between align-items-center">
        <h3>{{ subject.name }}</h3>
        <BButton variant="outline-secondary" @click="$router.go(-1)">
          <i class="bi bi-arrow-left"></i> Back
        </BButton>
      </BCardHeader>

      <BCardBody>

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

    <BModal v-model="showChapterModal" :title="isEditingChapter ? 'Edit Chapter' : 'Add New Chapter'"
      @hidden="resetChapterForm" @ok="handleChapterSubmit">
      <BForm @submit.prevent>
        <BFormGroup label="Chapter Title" label-for="chapter-title">
          <BFormInput id="chapter-title" v-model="chapterForm.name" :state="chapterValidation.title"
            placeholder="Enter chapter title" required></BFormInput>
          <BFormInvalidFeedback v-if="!chapterValidation.title">
            Chapter title is required
          </BFormInvalidFeedback>
        </BFormGroup>

        <BFormGroup label="Description" label-for="chapter-description">
          <BFormTextarea id="chapter-description" v-model="chapterForm.description"
            placeholder="Enter chapter description" rows="3"></BFormTextarea>
        </BFormGroup>
      </BForm>
    </BModal>

    <BModal v-model="showDeleteChapterModal" title="Confirm Delete" ok-variant="danger" ok-title="Delete"
      @ok="deleteChapter">
      <p class="my-4">Are you sure you want to delete the chapter "{{ selectedChapter?.title }}"?</p>
      <p class="text-danger">This action cannot be undone.</p>
    </BModal>
  </div>

  <BToastOrchestrator />
</template>
