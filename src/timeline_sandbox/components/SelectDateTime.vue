<script setup>
import { ref } from 'vue'

// For assigning timezone offset as positive or negative
const offsetSignConst = ["+", "-"]
// Values follows ISO 8601 format used by plaso's csv output with microseconds precision
const datetimeISOString = ref("0000-00-00T00:00:00.000000+00:00") //Default invalid datetime placeholder
const year = ref(0)
const month = ref(0)
const day = ref(0)
const hour = ref(0)
const minute = ref(0)
const second = ref(0)
const microsecond = ref(0)
const offsetHour = ref(0)
const offsetMinute = ref(0)
const offsetSign = ref("+")

//Form ref
const formRef = ref()

// Form validation for time
// INPROGRESS
const ISORules = [
    () => (year.value >= 0 && year.value <= 9999) ? true : "Year outside of range!",
    () => (month.value >= 0 && month.value <= 12) ? true : "Month outside of range!",
    () => (day.value >= 0 && day.value <= 31) ? true : "Day outside of range!",
    () => (hour.value >= 0 && hour.value <= 23) ? true : "Hour outside of range!",
    () => (minute.value >= 0 && minute.value <= 59) ? true : "Minute outside of range!",
    () => (second.value >= 0 && second.value <= 59) ? true : "Second outside of range!",
    () => (microsecond.value >= 0 && microsecond.value <= 999999) ? true : "Microsecond outside of range!",
    () => (offsetHour.value >= 0 && offsetHour.value <= 23) ? true : "Timezone hour offset outside of range!",
    () => (offsetMinute.value >= 0 && offsetMinute.value <= 59) ? true : "Timezone minute offset outside of range!",
]

function generateISOString() {
    datetimeISOString.value = year.value.toString(10).padStart(4, "0") + "-" +
        month.value.toString(10).padStart(2, "0") + "-" +
        day.value.toString(10).padStart(2, "0") + "T" +
        hour.value.toString(10).padStart(2, "0") + ":" +
        minute.value.toString(10).padStart(2, "0") + ":" +
        second.value.toString(10).padStart(2, "0") + "." +
        microsecond.value.toString(10).padStart(6, "0") +
        offsetSign.value +
        offsetHour.value.toString(10).padStart(2, "0") + ":" +
        offsetMinute.value.toString(10).padStart(2, "0")
}

// Expose list of labels and function to activate component
defineExpose({
    datetimeISOString
});

function onSubmit(isActive) {
    formRef.value?.validate().then(({ valid: isValid }) => {
        if (isValid) {
            generateISOString()
            isActive.value = false
        }
    })
}

</script>
<template>
    <v-btn>
        {{ datetimeISOString }}
        <v-dialog persistent activator="parent">
            <template v-slot:default="{ isActive }">
                <v-form @submit.prevent="onSubmit(isActive)" ref="formRef">
                    <v-card class="pa-4">

                        <v-row>
                            <v-col align="center" justify="center">
                                <v-card title="Set date">
                                    <v-card subtitle="Year (0-9999)"><input type="number" v-model="year"
                                            class="w-75 border border-b-lg rounded-lg" name="year" min="0" max="9999"></v-card>
                                    <v-card subtitle="Month (0-12)"><input type="number" v-model="month" class="w-75 border border-b-lg rounded-lg"
                                            name="month" min="0" max="12"></v-card>
                                    <v-card subtitle="Day (0-31)"><input type="number" v-model="day" class="w-75 border border-b-lg rounded-lg"
                                            name="day" min="0" max="31"></v-card>
                                </v-card>
                            </v-col>
                            <v-col align="center" justify="center">
                                <v-card title="Set time and UTC offset">
                                    <v-card subtitle="Hour (0-23)"><input type="number" v-model="hour" class="w-75 border border-b-lg rounded-lg"
                                            name="hour" min="0" max="23"></v-card>
                                    <v-card subtitle="Minute (0-59)"><input type="number" v-model="minute" class="w-75 border border-b-lg rounded-lg"
                                            name="minute" min="0" max="59"></v-card>
                                    <v-card subtitle="Second (0-59)"><input type="number" v-model="second" class="w-75 border border-b-lg rounded-lg"
                                            name="second" min="0" max="59"></v-card>
                                    <v-card subtitle="Microsecond (0-999999)"><input type="number" v-model="microsecond"
                                            class="w-75 border border-b-lg rounded-lg" name="microsecond" min="0" max="999999"></v-card>
                                    <v-card subtitle="UTC Offset hour (0-23)"><input type="number" v-model="offsetHour"
                                            class="w-75 border border-b-lg rounded-lg" name="offsetHour" min="0" max="23"></v-card>
                                    <v-card subtitle="UTC Offset hour (0-59)"><input type="number"
                                            v-model="offsetMinute" class="w-75 border border-b-lg rounded-lg" name="offsetMinute" min="0"
                                            max="59"></v-card>
                                    <v-card>
                                        <v-select v-model="offsetSign" class="w-75" :items="offsetSignConst"
                                        label="Select offset type"
                                        hint="Is offset from UTC timezone positive or negative?"></v-select>
                                    </v-card>

                                </v-card>
                            </v-col>
                        </v-row>
                        <v-row><v-input :rules="ISORules"></v-input></v-row>
                        <v-row align="center" justify="center">

                            <v-btn type="submit" class="mx-2">
                                Set Datetime
                            </v-btn>

                            <v-btn @click="isActive.value = false;" class="mx-2">
                                Cancel
                            </v-btn>

                        </v-row>
                    </v-card>
                </v-form>
            </template>

        </v-dialog>
    </v-btn>
</template>