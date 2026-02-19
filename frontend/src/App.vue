<template>
  <v-app>
    <RouterView v-slot="{ Component }">
      <Transition name="vuvoz-page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </v-app>
</template>

<script setup lang="ts">
</script>
