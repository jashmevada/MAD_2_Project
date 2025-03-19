<template>
  <div class="registration-container">
    <BContainer>
      <BRow class="justify-content-center">
        <BCol cols="12" md="8" lg="6">
          <BCard class="shadow-sm border-0 registration-card">
            <BCardHeader class="bg-primary text-white text-center py-3">
              <h3 class="mb-0">{{ currentStep === 1 ? 'Account Information' : 'Additional Information' }}</h3>
            </BCardHeader>

            <BCardBody class="p-4">
              <!-- Account Information Form (Step 1) -->
              <div v-if="currentStep === 1">
                <BForm @submit.prevent="nextStep" novalidate>
                  <BFormGroup label="Username" label-for="username" :state="validation.username"
                    :invalid-feedback="errors.username">
                    <BFormInput id="username" v-model="form.username" :state="validation.username"
                      placeholder="Choose a username" required trim></BFormInput>
                  </BFormGroup>

                  <BFormGroup label="Email" label-for="_email" :state="validation.email"
                    :invalid-feedback="errors.username">
                    <BFormInput id="_email" v-model="form.email" :state="validation.email"
                      placeholder="Enter your Email." required trim></BFormInput>
                  </BFormGroup>



                  <BFormGroup label="Password" label-for="password" :state="validation.password"
                    :invalid-feedback="errors.password">
                    <BInputGroup>
                      <BFormInput id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'"
                        :state="validation.password" placeholder="Create a password" required
                        aria-describedby="password-strength"></BFormInput>
                      <BButton @click="showPassword = !showPassword" variant="outline-secondary">
                        <Icon :icon="showPassword ? 'heroicons:eye-slash' : 'heroicons:eye'" width="20" />
                      </BButton>
                    </BInputGroup>
                    <div id="password-strength" class="form-text mt-1"
                      :class="{ 'text-danger': passwordStrength < 2, 'text-warning': passwordStrength === 2, 'text-success': passwordStrength > 2 }">
                      <small>Password strength: {{ passwordStrengthText }}</small>
                      <BProgress :value="passwordStrength * 25" :variant="passwordStrengthVariant" height="5px"
                        class="mt-1"></BProgress>
                    </div>
                  </BFormGroup>

                  <BFormGroup label="Role" label-for="role" :state="validation.role" :invalid-feedback="errors.role">
                    <BFormSelect id="role" v-model="form.role" :options="roleOptions" :state="validation.role" required>
                    </BFormSelect>
                  </BFormGroup>

                  <div class="d-grid gap-2 mt-4">
                    <BButton type="submit" variant="primary">Next</BButton>
                  </div>
                </BForm>
              </div>

              <!-- Additional Information Form (Step 2) -->
              <div v-if="currentStep === 2">
                <!-- Student Form -->
                <div v-if="form.role === 'student'">
                  <h5 class="border-bottom pb-2 mb-3">Student Information</h5>
                  <BForm @submit.prevent="submitForm" novalidate>
                    <BFormGroup label="First Name" label-for="studentFirstName" :state="validation.studentFirstName"
                      :invalid-feedback="errors.studentFirstName">
                      <BFormInput id="studentFirstName" v-model="form.studentFirstName"
                        :state="validation.studentFirstName" placeholder="Enter your first name" required trim>
                      </BFormInput>
                    </BFormGroup>

                    <BFormGroup label="Last Name" label-for="studentLastName" :state="validation.studentLastName"
                      :invalid-feedback="errors.studentLastName">
                      <BFormInput id="studentLastName" v-model="form.studentLastName"
                        :state="validation.studentLastName" placeholder="Enter your last name" required trim>
                      </BFormInput>
                    </BFormGroup>

                    <BFormGroup label="Qualification" label-for="studentq" :state="validation.studentQualification"
                      :invalid-feedback="errors.studentLastName">
                      <BFormInput id="studentq" v-model="form.studentQualification"
                        :state="validation.studentQualification" placeholder="Enter your Qualification" required trim>
                      </BFormInput>
                    </BFormGroup>

                    <BFormGroup label="Date of Birth" label-for="studentDob">
                      <BFormInput id="studentDob" v-model="form.studentDob" type="date"></BFormInput>
                    </BFormGroup>

                    <div class="d-grid gap-2 mt-4">
                      <BButton variant="secondary" @click="prevStep">Previous</BButton>
                      <BButton type="submit" variant="primary" :disabled="isSubmitting">
                        <BSpinner small v-if="isSubmitting" class="me-2"></BSpinner>
                        {{ isSubmitting ? 'Registering...' : 'Register' }}
                      </BButton>
                    </div>
                  </BForm>
                </div>

                <!-- Instructor Form -->
                <div v-if="form.role === 'instructor'">
                  <h5 class="border-bottom pb-2 mb-3">Instructor Information</h5>
                  <BForm @submit.prevent="submitForm" novalidate>
                    <BFormGroup label="Full Name" label-for="instructorName" :state="validation.instructorName"
                      :invalid-feedback="errors.instructorName">
                      <BFormInput id="instructorName" v-model="form.instructorName" :state="validation.instructorName"
                        placeholder="Enter your full name" required trim></BFormInput>
                    </BFormGroup>

                    <BFormGroup label="Email" label-for="instructorEmail" :state="validation.instructorEmail"
                      :invalid-feedback="errors.instructorEmail">
                      <BFormInput id="instructorEmail" v-model="form.instructorEmail" type="email"
                        :state="validation.instructorEmail" placeholder="Enter your email" required trim></BFormInput>
                    </BFormGroup>

                    <BFormGroup label="Qualifications" label-for="instructorQualifications">
                      <BFormInput id="instructorQualifications" v-model="form.instructorQualifications"
                        placeholder="Enter your qualifications"></BFormInput>
                    </BFormGroup>

                    <div class="d-grid gap-2 mt-4">
                      <BButton variant="secondary" @click="prevStep">Previous</BButton>
                      <BButton type="submit" variant="primary" :disabled="isSubmitting">
                        <BSpinner small v-if="isSubmitting" class="me-2"></BSpinner>
                        {{ isSubmitting ? 'Registering...' : 'Register' }}
                      </BButton>
                    </div>
                  </BForm>
                </div>
              </div>

              <BAlert v-if="formSubmitted" variant="success" show dismissible @dismissed="formSubmitted = false">
                Registration successful! Please check your email to verify your account.
              </BAlert>
            </BCardBody>
          </BCard>
        </BCol>
      </BRow>
    </BContainer>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Icon } from '@iconify/vue'
import {
  BContainer,
  BRow,
  BCol,
  BCard,
  BCardHeader,
  BCardBody,
  BForm,
  BFormGroup,
  BFormInput,
  BFormSelect,
  BButton,
  BAlert,
  BInputGroup,
  BProgress,
  BSpinner
} from 'bootstrap-vue-next'
import { apiFetch } from '@/main'
import { useRouter } from 'vue-router'

const router = useRouter()

// Form data
const form = reactive({
  username: '',
  password: '',
  role: '',
  email: '',
  studentFirstName: '',
  studentLastName: '',
  studentDob: '',
  studentQualification: '',
  instructorName: '',
  instructorEmail: '',
  instructorQualifications: ''
})

// UI state
const currentStep = ref(1)
const isSubmitting = ref(false)
const formSubmitted = ref(false)
const showPassword = ref(false)

// Form validation errors
const errors = reactive({
  username: '',
  email: '',
  password: '',
  role: '',
  studentFirstName: '',
  studentLastName: '',
  instructorName: '',
  instructorEmail: ''
})

// Role options
const roleOptions = [
  { value: '', text: 'Select role' },
  { value: 'student', text: 'Student' },
  { value: 'instructor', text: 'Instructor' }
]

const passwordStrength = computed(() => {
  const password = form.password
  if (!password) return 0

  let strength = 0

  if (password.length >= 8) strength++

  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++

  if (/[0-9]/.test(password)) strength++

  if (/[^A-Za-z0-9]/.test(password)) strength++

  return strength
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return 'Very Weak'
  if (strength === 1) return 'Weak'
  if (strength === 2) return 'Medium'
  if (strength === 3) return 'Strong'
  return 'Very Strong'
})

const passwordStrengthVariant = computed(() => {
  const strength = passwordStrength.value
  if (strength < 2) return 'danger'
  if (strength === 2) return 'warning'
  if (strength === 3) return 'info'
  return 'success'
})

const validateStep1 = () => {
  let isValid = true

  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })

  if (!form.username.trim()) {
    errors.username = 'Username is required'
    isValid = false
  } else if (form.username.length < 4) {
    errors.username = 'Username must be at least 4 characters'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    isValid = false
  } else if (passwordStrength.value < 2) {
    errors.password = 'Password is too weak. Include uppercase, lowercase, numbers, and special characters'
    isValid = false
  }

  if (!form.role) {
    errors.role = 'Role is required'
    isValid = false
  }

  return isValid
}

const validateStep2 = () => {
  let isValid = true

  if (form.role === 'student') {
    if (!form.studentFirstName) {
      errors.studentFirstName = 'First name is required'
      isValid = false
    }
    if (!form.studentLastName) {
      errors.studentLastName = 'Last name is required'
      isValid = false
    }
  } else if (form.role === 'instructor') {
    if (!form.instructorName) {
      errors.instructorName = 'Full name is required'
      isValid = false
    }
    if (!form.instructorEmail) {
      errors.instructorEmail = 'Email is required'
      isValid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.instructorEmail)) {
      errors.instructorEmail = 'Invalid email format'
      isValid = false
    }
  }

  return isValid
}

const validation = computed(() => {
  return {
    username: errors.username ? false : null,
    email: errors.email ? false : null,
    password: errors.password ? false : null,
    role: errors.role ? false : null,
    studentFirstName: errors.studentFirstName ? false : null,
    studentLastName: errors.studentLastName ? false : null,
    studentQualification: errors.studentQualification ? false : null,
    instructorName: errors.instructorName ? false : null,
    instructorEmail: errors.instructorEmail ? false : null
  }
})

const nextStep = () => {
  if (validateStep1()) {
    currentStep.value = 2
  }
}

const prevStep = () => {
  currentStep.value = 1
}

const submitForm = async () => {
  if (validateStep2()) {
    isSubmitting.value = true

    try {

      const formattedData = {
        data: {
          user_role: form.role,
          ...(form.role === 'student' ? {
            full_name: form.studentFirstName + form.studentLastName,
            dob: form.studentDob,
            qualification: form.studentQualification
          } : {}),
          ...(form.role === 'instructor' ? {
            full_name: form.instructorName,
            qualifications: form.instructorQualifications
          } : {})
        },
        email: form.role === 'student' ? form.email : form.instructorEmail,
        username: form.username,
        email: form.email,
        password: form.password
      }

      await apiFetch("/register", {
        method: 'POST',
        body: formattedData,
        onResponse({ response }) {
          if (response.status === 201) {
            router.push("/")
          }
        }
      })

      formSubmitted.value = true

      console.log('Registration successful!')
    } catch (error) {
      console.error('Registration failed:', error)
      // Handle error
    } finally {
      isSubmitting.value = false
    }
  }
}
</script>

<style scoped>
.registration-container {
  padding: 3rem 1rem;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.registration-card {
  border-radius: 10px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .registration-container {
    padding: 1rem;
  }
}
</style>
