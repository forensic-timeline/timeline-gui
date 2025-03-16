<script setup>
import { ref, defineProps, defineEmits } from 'vue'

// Emit form submition event and values
const emit = defineEmits(['submit_event'])

const props = defineProps(['is_sign_up', 'username', 'password', 'confirm'])
const is_sign_up = ref(props.is_sign_up)

const username = ref(props.username)
const password = ref(props.password)
const confirm = ref(props.confirm)

//   const username = ref(null)
//   const password = ref(null)
//   const confirm = ref(null)
function on_submit() {
    emit('submit_event', username.value, password.value, confirm.value)
}

const visible1 = ref(false)
const visible2 = ref(false)
</script>

<!-- TODO: Implement client-side validation + confirm password field for sign-up -->
<!-- TODO: Prefill fields if user failed server-side validation -->

<template>
    <v-form>
        <v-container fluid>
            <v-row>
                <v-col cols="12" sm="6">
                    <div class="text-subtitle-1 text-medium-emphasis">Username</div>

                    <v-text-field v-model="username" density="compact" placeholder="Username"
                        prepend-inner-icon="mdi-email-outline" variant="outlined"></v-text-field>

                    <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
                        Password

                        <a class="text-caption text-decoration-none text-blue" href="#" rel="noopener noreferrer"
                            target="_blank">
                            Forgot login password?</a>
                    </div>

                    <v-text-field v-model="password" :append-inner-icon="visible1 ? 'mdi-eye-off' : 'mdi-eye'"
                        :type="visible1 ? 'text' : 'password'" density="compact" placeholder="Enter your password"
                        prepend-inner-icon="mdi-lock-outline" variant="outlined"
                        @click:append-inner="visible1 = !visible1"></v-text-field>

                    <v-text-field v-if="is_sign_up" v-model="confirm"
                        :append-inner-icon="visible2 ? 'mdi-eye-off' : 'mdi-eye'" :type="visible2 ? 'text' : 'password'"
                        density="compact" placeholder="Confirm your password" prepend-inner-icon="mdi-lock-outline"
                        variant="outlined" @click:append-inner="visible2 = !visible2"></v-text-field>
                    <!-- Depends on is_sign_in -->
                    <v-btn  v-if="is_sign_up" @click="on_submit" type="submit" class="mb-8" color="blue" size="large" variant="tonal" block>
                        Sign Up
                    </v-btn>
                    <v-btn  v-else @click="on_submit" type="submit" class="mb-8" color="blue" size="large" variant="tonal" block>
                        Sign In
                    </v-btn>
                </v-col>
            </v-row>
        </v-container>
    </v-form>
</template>