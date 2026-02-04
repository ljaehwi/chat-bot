<template>
  <div class="approval-request">
    <h3>Human-in-the-loop</h3>
    <p>The agent is requesting approval for the following action:</p>
    <pre>{{ action }}</pre>
    <Button label="Approve" class="p-button-success" @click="approve" />
    <Button label="Reject" class="p-button-danger" @click="reject" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from 'primevue/button';

const action = ref({ tool: 'filesystem', action: 'delete', path: '/path/to/important/file.txt' });

const approve = () => {
  console.log('Action approved');
};

const reject = () => {
  console.log('Action rejected');
};
</script>

<style scoped>
.approval-request {
  padding: 1rem;
  border: 1px solid #ddd;
  margin: 1rem;
}
pre {
  background-color: #eee;
  padding: 1rem;
}
</style>
