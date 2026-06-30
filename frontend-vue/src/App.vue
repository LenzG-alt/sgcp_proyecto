<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* ============================================
   ESTILOS GLOBALES — SGCP
   ============================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: #0c0c0c;
  color: #ccc;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: inherit;
  text-decoration: none;
}

/* Scrollbar personalizada */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #111;
}
::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>