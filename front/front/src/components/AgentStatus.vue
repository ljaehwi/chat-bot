<template>
  <div class="agent-status-container">
    <Panel header="System Health" :toggleable="true">
      <SystemHealth />
    </Panel>
    
    <Panel header="Agent Workflow" :toggleable="true" class="p-mt-4">
      <div class="graph-container">
        <div 
          v-for="node in nodes" 
          :key="node.id"
          :class="['node', getNodeStatus(node.id)]"
          @click="showNodeDetails(node)"
        >
          <div class="node-icon">
            <i :class="node.icon"></i>
          </div>
          <div class="node-label">{{ node.label }}</div>
          <div v-if="getNodeStatus(node.id) === 'running'" class="spinner"></div>
          <div v-if="getNodeStatus(node.id) === 'completed'" class="check-mark">✓</div>
        </div>
      </div>
    </Panel>

    <Panel header="Logs" :toggleable="true" class="p-mt-4 terminal-panel">
      <div class="logs-container">
        <div v-for="(log, index) in store.logs" :key="index" class="log-entry">
          {{ log }}
        </div>
      </div>
    </Panel>
    
    <!-- Node Details Modal -->
    <div v-if="selectedNode" class="node-details-modal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h4>{{ selectedNode.label }}</h4>
        <p>{{ selectedNode.description }}</p>
        <div v-if="getNodeLogs(selectedNode.id).length > 0" class="node-logs">
          <h5>실행 로그:</h5>
          <div v-for="log in getNodeLogs(selectedNode.id)" :key="log.timestamp" class="log-entry">
            <span class="timestamp">{{ formatTime(log.timestamp) }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
        <button @click="closeModal" class="close-btn">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAgentStore } from '../stores/agent';
import Panel from 'primevue/panel';
import SystemHealth from './SystemHealth.vue';

const store = useAgentStore();
const selectedNode = ref(null);

const nodes = ref([
  { id: 'clarify_intent', label: '의도 파악', icon: 'pi pi-search', description: '사용자 요청의 의도를 명확히 파악합니다.' },
  { id: 'initial_planner', label: '초기 계획', icon: 'pi pi-map', description: '사용자 의도에 따라 초기 실행 계획을 수립합니다.' }, // 변경
  { id: 'execute_tools', label: '도구 실행', icon: 'pi pi-wrench', description: '계획된 도구들을 실행합니다.' },
  { id: 'synthesize_answer', label: '답변 종합', icon: 'pi pi-comment', description: '도구 실행 결과를 바탕으로 최종 답변을 종합합니다.' }, // 추가
  { id: 'check_with_8b', label: '로컬 LLM', icon: 'pi pi-cpu', description: '로컬 LLM으로 답변을 생성합니다.' },
  { id: 'validate_answer', label: '답변 검증', icon: 'pi pi-check-circle', description: 'Gemini로 답변 품질을 검증합니다.' },
  { id: 'call_gemini', label: 'Gemini 호출', icon: 'pi pi-sparkles', description: 'Gemini로 고품질 답변을 생성합니다.' },
  { id: 'give_final_answer', label: '최종 답변', icon: 'pi pi-send', description: '최종 답변을 사용자에게 전달합니다.' }
]);

const getNodeStatus = (nodeId) => {
  const nodeState = store.nodeStates[nodeId];
  if (!nodeState) return 'pending';
  return nodeState.status;
};

const getNodeLogs = (nodeId) => {
  return store.nodeLogs[nodeId] || [];
};

const showNodeDetails = (node) => {
  selectedNode.value = node;
};

const closeModal = () => {
  selectedNode.value = null;
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString();
};
</script>

<style scoped>
.agent-status-container {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.p-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.terminal-panel {
  flex-grow: 1;
}

.graph-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  padding: 1rem 0;
}

.node {
  background: #2a2a2a;
  border: 2px solid #333;
  border-radius: 8px;
  padding: 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.node:hover {
  border-color: #4facfe;
  transform: translateY(-2px);
}

.node.pending {
  border-color: #666;
  opacity: 0.6;
}

.node.running {
  border-color: #ffa500;
  background: #2a2a2a;
  animation: pulse 1.5s infinite;
}

.node.completed {
  border-color: #4caf50;
  background: #1a3a1a;
}

.node.error {
  border-color: #f44336;
  background: #3a1a1a;
}

.node.skipped {
  border-color: #888;
  background: #2a2a2a;
  opacity: 0.5;
}

.node-icon {
  font-size: 1.2rem;
  color: #4facfe;
}

.node.running .node-icon {
  color: #ffa500;
}

.node.completed .node-icon {
  color: #4caf50;
}

.node.error .node-icon {
  color: #f44336;
}

.node.skipped .node-icon {
  color: #888;
}

.node-label {
  font-size: 0.7rem;
  color: #e0e0e0;
  font-weight: 500;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #333;
  border-top: 2px solid #ffa500;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  position: absolute;
  top: 4px;
  right: 4px;
}

.check-mark {
  position: absolute;
  top: 4px;
  right: 4px;
  color: #4caf50;
  font-weight: bold;
  font-size: 0.8rem;
}

.logs-container {
  background: #1a1a1a;
  border-radius: 4px;
  padding: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 0.8rem;
}

.log-entry {
  color: #e0e0e0;
  margin-bottom: 0.25rem;
  word-break: break-all;
}

.node-details-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  color: #e0e0e0;
}

.modal-content h4 {
  margin-top: 0;
  color: #4facfe;
}

.node-logs {
  margin-top: 1rem;
  max-height: 150px;
  overflow-y: auto;
}

.timestamp {
  color: #888;
  font-family: monospace;
  font-size: 0.8rem;
}

.log-message {
  color: #e0e0e0;
  font-size: 0.8rem;
}

.close-btn {
  background: #4facfe;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(255, 165, 0, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(255, 165, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 165, 0, 0); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
