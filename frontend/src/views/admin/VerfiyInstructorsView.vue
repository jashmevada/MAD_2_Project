<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="text-center my-4">
      <BSpinner label="Loading..."></BSpinner>
      <p class="mt-2">Loading instructor data...</p>
    </div>

    <!-- Error message -->
    <BAlert v-else-if="error" show variant="danger">
      {{ error }}
    </BAlert>

    <!-- Instructors table -->
    <BTable v-else hover responsive :items="instructors" :fields="fields" striped>
      <!-- Custom formatted name column -->
      <template #cell(name)="data">
        <div class="d-flex align-items-center">
          <img :src="data.item.profileImage || 'https://via.placeholder.com/40'" class="rounded-circle me-2" width="40"
            height="40" alt="Profile">
          <div>
            <strong>{{ data.item.name }}</strong>
            <div class="small text-muted">{{ data.item.qualification }}</div>
          </div>
        </div>
      </template>

      <!-- Status column with badge -->
      <template #cell(status)="data">
        <BBadge :variant="getStatusVariant(data.value)">
          {{ data.value }}
        </BBadge>
      </template>

      <!-- Actions column -->
      <template #cell(actions)="data">
        <div class="d-flex gap-2">
          <BButton size="sm" variant="success" @click="approveInstructor(data.item.id)"
            :disabled="data.item.status !== 'Pending'">
            <span v-if="processingId === data.item.id" class="spinner-border spinner-border-sm me-1"></span>
            Approve
          </BButton>

          <BButton size="sm" variant="danger" @click="rejectInstructor(data.item.id)"
            :disabled="data.item.status !== 'Pending'">
            Reject
          </BButton>

          <BButton size="sm" variant="info" @click="viewDetails(data.item)">
            Details
          </BButton>
        </div>
      </template>
    </BTable>

    <!-- Instructor details modal -->
    <BModal v-model="showModal" :title="`Instructor Details: ${selectedInstructor?.name || ''}`" size="lg" hide-footer>
      <div v-if="selectedInstructor" class="p-2">
        <div class="text-center mb-4">
          <img :src="selectedInstructor.profileImage || 'https://via.placeholder.com/100'" class="rounded-circle mb-2"
            width="100" height="100" alt="Profile">
          <h4>{{ selectedInstructor.name }}</h4>
          <p class="text-muted">{{ selectedInstructor.qualification }}</p>
        </div>

        <div class="row mb-2">
          <div class="col-md-4 fw-bold">Email:</div>
          <div class="col-md-8">{{ selectedInstructor.email }}</div>
        </div>

        <div class="row mb-2">
          <div class="col-md-4 fw-bold">Department:</div>
          <div class="col-md-8">{{ selectedInstructor.department }}</div>
        </div>

        <div class="row mb-2">
          <div class="col-md-4 fw-bold">Experience:</div>
          <div class="col-md-8">{{ selectedInstructor.experience }} years</div>
        </div>

        <div class="row mb-2">
          <div class="col-md-4 fw-bold">Status:</div>
          <div class="col-md-8">
            <BBadge :variant="getStatusVariant(selectedInstructor.status)">
              {{ selectedInstructor.status }}
            </BBadge>
          </div>
        </div>

        <div class="mt-4">
          <h5>Bio</h5>
          <p>{{ selectedInstructor.bio || 'No bio provided.' }}</p>
        </div>

        <div class="d-flex justify-content-end mt-4">
          <BButton @click="showModal = false" variant="secondary" class="me-2">Close</BButton>
          <BButton v-if="selectedInstructor.status === 'Pending'" @click="approveInstructor(selectedInstructor.id)"
            variant="success">
            Approve Access
          </BButton>
        </div>
      </div>
    </BModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  BTable,
  BButton,
  BBadge,
  BSpinner,
  BAlert,
  BModal
} from 'bootstrap-vue-next'
import { apiFetch } from '@/main'

// Table fields definition
const fields = [
  { key: 'name', label: 'Instructor Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'department', label: 'Department', sortable: true },
  { key: 'requestDate', label: 'Requested On', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'actions', label: 'Actions' }
]

// State variables
const instructors = ref([])
const loading = ref(true)
const error = ref(null)
const processingId = ref(null)
const showModal = ref(false)
const selectedInstructor = ref(null)

// Fetch instructors data from backend
const fetchInstructors = async () => {
  loading.value = true
  error.value = null

  try {
    instructors.value = await apiFetch('/instructors', {
      query: { approval: true }
    })
  } catch (err) {
    console.error('Error fetching instructors:', err)
    error.value = 'Failed to load instructor data. Please try again.'
  } finally {
    loading.value = false
  }
}

// Get appropriate badge variant based on status
const getStatusVariant = (status) => {
  switch (status) {
    case 'Approved': return 'success'
    case 'Rejected': return 'danger'
    case 'Pending': return 'warning'
    default: return 'secondary'
  }
}

// View instructor details
const viewDetails = (instructor) => {
  selectedInstructor.value = instructor
  showModal.value = true
}

// Approve instructor
const approveInstructor = async (id) => {
  processingId.value = id

  try {
    await apiFetch(`/instructors/${id}/approve`, { method: "POST" })

    // Update local state
    const index = instructors.value.findIndex(i => i.id === id)
    if (index !== -1) {
      instructors.value[index].status = 'Approved'
    }

    // Update modal if open
    if (selectedInstructor.value && selectedInstructor.value.id === id) {
      selectedInstructor.value.status = 'Approved'
    }
  } catch (err) {
    console.error('Error approving instructor:', err)
    error.value = 'Failed to approve instructor. Please try again.'
  } finally {
    processingId.value = null
  }
}

// Reject instructor
const rejectInstructor = async (id) => {
  if (!confirm('Are you sure you want to reject this instructor?')) return

  processingId.value = id

  try {
    await apiFetch(`/instructors/${id}/reject`, { method: "POST" })

    // Update local state
    const index = instructors.value.findIndex(i => i.id === id)
    if (index !== -1) {
      instructors.value[index].status = 'Rejected'
    }

    // Update modal if open
    if (selectedInstructor.value && selectedInstructor.value.id === id) {
      selectedInstructor.value.status = 'Rejected'
    }
  } catch (err) {
    console.error('Error rejecting instructor:', err)
    error.value = 'Failed to reject instructor. Please try again.'
  } finally {
    processingId.value = null
  }
}

// Fetch data on component mount
onMounted(() => {
  fetchInstructors()
})
</script>
