<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Add New Subject</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitForm" class="needs-validation" novalidate>
              <!-- Subject Name -->
              <div class="mb-3">
                <label for="subjectName" class="form-label">Subject Name</label>
                <input type="text" class="form-control" id="subjectName" v-model="form.name"
                  :class="{ 'is-invalid': errors.name }" required>
                <div class="invalid-feedback" v-if="errors.name">
                  {{ errors.name }}
                </div>
              </div>

              <!-- Subject Code -->
              <div class="mb-3">
                <label for="subjectCode" class="form-label">Subject Code</label>
                <input type="text" class="form-control" id="subjectCode" v-model="form.code"
                  :class="{ 'is-invalid': errors.code }" required>
                <div class="invalid-feedback" v-if="errors.code">
                  {{ errors.code }}
                </div>
              </div>

              <!-- Department -->
              <div class="mb-3">
                <label for="department" class="form-label">Department</label>
                <select class="form-select" id="department" v-model="form.department"
                  :class="{ 'is-invalid': errors.department }" required>
                  <option value="" disabled selected>Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
                <div class="invalid-feedback" v-if="errors.department">
                  {{ errors.department }}
                </div>
              </div>

              <!-- Credits -->
              <div class="mb-3">
                <label for="credits" class="form-label">Credits</label>
                <input type="number" class="form-control" id="credits" v-model="form.credits" min="1" max="10"
                  :class="{ 'is-invalid': errors.credits }" required>
                <div class="invalid-feedback" v-if="errors.credits">
                  {{ errors.credits }}
                </div>
              </div>

              <!-- Description -->
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" rows="3" v-model="form.description"
                  :class="{ 'is-invalid': errors.description }"></textarea>
                <div class="invalid-feedback" v-if="errors.description">
                  {{ errors.description }}
                </div>
              </div>

              <!-- Active Status -->
              <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="isActive" v-model="form.isActive">
                <label class="form-check-label" for="isActive">Active Subject</label>
              </div>

              <!-- Submit Buttons -->
              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="button" class="btn btn-secondary me-md-2" @click="resetForm">Reset</button>
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                  {{ isSubmitting ? 'Saving...' : 'Save Subject' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Success Alert -->
        <div class="alert alert-success mt-3" v-if="showSuccess">
          <i class="bi bi-check-circle-fill me-2"></i>
          Subject has been added successfully!
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { apiFetch } from '@/apiFetch';
import { ref, reactive, onMounted } from 'vue';

// Form data
const form = reactive({
  name: '',
  code: '',
  department: '',
  credits: 3,
  description: '',
  isActive: true
});

// Form state
const errors = reactive({});
const isSubmitting = ref(false);
const showSuccess = ref(false);
const departments = ref([]);

// Fetch departments from API
onMounted(async () => {
  try {
    const response = await apiFetch('/api/departments');
    departments.value = response.data;
  } catch (error) {
    console.error('Failed to load departments:', error);
  }
});

// Validate form
const validateForm = () => {
  errors.name = !form.name ? 'Subject name is required' : '';
  errors.code = !form.code ? 'Subject code is required' : '';
  errors.department = !form.department ? 'Please select a department' : '';
  errors.credits = !form.credits ? 'Credits are required' : '';

  if (form.description && form.description.length > 500) {
    errors.description = 'Description must be less than 500 characters';
  } else {
    errors.description = '';
  }

  return !Object.values(errors).some(error => error);
};

// Submit form
const submitForm = async () => {
  if (!validateForm()) return;

  isSubmitting.value = true;

  try {
    await apiFetch('/api/subjects', form);

    // Show success message
    showSuccess.value = true;

    // Reset form after successful submission
    resetForm();

    // Hide success message after 3 seconds
    setTimeout(() => {
      showSuccess.value = false;
    }, 3000);
  } catch (error) {
    console.error('Error submitting form:', error);

    // Handle validation errors from server
    if (error.response && error.response.data.errors) {
      Object.assign(errors, error.response.data.errors);
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Reset form
const resetForm = () => {
  Object.keys(form).forEach(key => {
    if (key === 'isActive') {
      form[key] = true;
    } else if (key === 'credits') {
      form[key] = 3;
    } else {
      form[key] = '';
    }
  });

  // Clear errors
  Object.keys(errors).forEach(key => {
    errors[key] = '';
  });
};
</script>

<style scoped>
.card {
  border-radius: 10px;
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #4a6bff, #2541b2);
}

.form-control:focus,
.form-select:focus {
  border-color: #4a6bff;
  box-shadow: 0 0 0 0.25rem rgba(74, 107, 255, 0.25);
}

.btn-primary {
  background-color: #4a6bff;
  border-color: #4a6bff;
}

.btn-primary:hover {
  background-color: #2541b2;
  border-color: #2541b2;
}
</style>
