<template>
  <div class="app-container">
    <Toolbar class="app-toolbar">
      <template #start>
        <div class="logo">
          <h1>AI Agent Cockpit</h1>
        </div>
      </template>
      <template #end>
        <Button icon="pi pi-cog" class="p-button-text" />
      </template>
    </Toolbar>

    <Splitter class="app-splitter">
      <SplitterPanel class="p-splitterpanel scroll-panel" :size="20" :min-size="15">
        <SessionSidebar />
      </SplitterPanel>
      <SplitterPanel class="p-splitterpanel chat-splitter-panel" :size="50" :min-size="40">
        <Splitter layout="vertical" class="chat-vertical-splitter">
          <SplitterPanel class="p-splitterpanel chat-messages-panel" :size="80" :min-size="60">
            <ChatWindow class="chat-window-panel" />
          </SplitterPanel>
          <SplitterPanel class="p-splitterpanel chat-input-panel" :size="20" :min-size="10">
            <ChatInput class="chat-input-panel-inner" />
          </SplitterPanel>
        </Splitter>
      </SplitterPanel>
      <SplitterPanel class="p-splitterpanel scroll-panel" :size="30" :min-size="20">
        <AgentStatus />
      </SplitterPanel>
    </Splitter>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAgentStore } from './stores/agent';
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';

import SessionSidebar from './components/SessionSidebar.vue';
import ChatWindow from './components/ChatWindow.vue';
import ChatInput from './components/ChatInput.vue';
import AgentStatus from './components/AgentStatus.vue';

// Initialize the agent store
const store = useAgentStore();

// Establish WebSocket connection when the component mounts
onMounted(() => {
  store.initConnection();
});
</script>

<style>
/* Global Styles */
html, body, #app {
  height: 100%;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: #1e1e1e; /* Dark background */
  color: #d4d4d4;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-toolbar {
  border-bottom: 1px solid #333;
  background: #252526;
  padding: 0.5rem 1rem;
}

.logo {
  display: flex;
  align-items: center;
}

.logo h1 {
  font-size: 1.5rem;
  margin-left: 1rem;
  font-weight: 600;
}

/* Make splitter fill remaining height */
.app-splitter {
  flex-grow: 1;
  min-height: 0;
  height: 100%;
  border: none;
}

/* Style splitter panels to have a dark background */
.p-splitter-panel {
  background-color: #1e1e1e;
  min-height: 0;
}

.p-splitter {
  min-height: 0;
  height: 100%;
}

.scroll-panel {
  overflow: auto;
}

.chat-splitter-panel {
  overflow: hidden;
}

.chat-vertical-splitter {
  height: 100%;
  min-height: 0;
}

.chat-messages-panel,
.chat-input-panel {
  min-height: 0;
  overflow: hidden;
}

.chat-window-panel {
  height: 100%;
  min-height: 0;
}

.chat-input-panel-inner {
  height: 100%;
}

/* PrimeVue Component Overrides */
.p-toolbar {
  border-radius: 0;
}

.p-splitter-gutter {
  background: #333 !important;
}

.p-splitter-gutter-handle {
  background: #555 !important;
}
</style>
