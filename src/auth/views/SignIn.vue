<script setup>
import AccountForm from '../components/AccountForm.vue';
</script>

<template>
    <h1>Sign In</h1>
    <AccountForm></AccountForm>
    <v-btn to='sign-up' variant="tonal">
        Create new account
    </v-btn>
</template>