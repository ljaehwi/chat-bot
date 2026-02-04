<template>
  <div class="agent-graph">
    <h3 class="graph-title">Agent Workflow</h3>
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
      
      <!-- Connections -->
      <svg class="connections" viewBox="0 0 800 400">
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                  refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
          </marker>
        </defs>
        <path v-for="connection in connections" 
              :key="`${connection.from}-${connection.to}`"
              :d="connection.path" 
              stroke="#666" 
              stroke-width="2" 
              fill="none" 
              marker-end="url(#arrowhead)" />
      </svg>
    </div>
    
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
import { ref, computed } from 'vue'
import { useAgentStore } from '../stores/agent'

const store = useAgentStore()
const selectedNode = ref(null)

const nodes = ref([
  { id: 'clarify_intent', label: '의도 파악', icon: 'pi pi-search', description: '사용자 요청의 의도를 명확히 파악합니다.' },
  { id: 'initial_planner', label: '초기 계획', icon: 'pi pi-map', description: '사용자 의도에 따라 초기 실행 계획을 수립합니다.' },
  { id: 'execute_tools', label: '도구 실행', icon: 'pi pi-wrench', description: '계획된 도구들을 실행합니다.' },
  { id: 'synthesize_answer', label: '답변 종합', icon: 'pi pi-comment', description: '도구 실행 결과를 바탕으로 최종 답변을 종합합니다.' },
  { id: 'check_with_8b', label: '로컬 LLM', icon: 'pi pi-cpu', description: '로컬 LLM으로 답변을 생성합니다.' },
  { id: 'validate_answer', label: '답변 검증', icon: 'pi pi-check-circle', description: 'Gemini로 답변 품질을 검증합니다.' },
  { id: 'call_gemini', label: 'Gemini 호출', icon: 'pi pi-sparkles', description: 'Gemini로 고품질 답변을 생성합니다.' },
  { id: 'give_final_answer', label: '최종 답변', icon: 'pi pi-send', description: '최종 답변을 사용자에게 전달합니다.' }
])

const connections = ref([
  // clarify_intent -> initial_planner
  { from: 'clarify_intent', to: 'initial_planner', path: 'M 100 50 L 250 50' },

  // initial_planner -> execute_tools (if plan exists)
  { from: 'initial_planner', to: 'execute_tools', path: 'M 250 50 L 400 50' },
  // initial_planner -> check_with_8b (if no plan - chat)
  { from: 'initial_planner', to: 'check_with_8b', path: 'M 250 65 L 250 150' }, // Split down to check_with_8b

  // execute_tools -> synthesize_answer
  { from: 'execute_tools', to: 'synthesize_answer', path: 'M 400 50 L 550 50' },

  // synthesize_answer -> validate_answer
  { from: 'synthesize_answer', to: 'validate_answer', path: 'M 550 65 L 400 150' }, // Down and left to validate

  // check_with_8b -> validate_answer
  { from: 'check_with_8b', to: 'validate_answer', path: 'M 250 150 L 400 150' },

  // validate_answer -> call_gemini (if not satisfactory)
  { from: 'validate_answer', to: 'call_gemini', path: 'M 400 150 L 550 150' },
  // validate_answer -> give_final_answer (if satisfactory)
  { from: 'validate_answer', to: 'give_final_answer', path: 'M 415 150 L 700 150' }, // Right to give_final_answer

  // call_gemini -> give_final_answer
  { from: 'call_gemini', to: 'give_final_answer', path: 'M 550 150 L 700 150' }
])

const getNodeStatus = (nodeId) => {
  const nodeState = store.nodeStates[nodeId]
  if (!nodeState) return 'pending'
  return nodeState.status
}

const getNodeLogs = (nodeId) => {
  return store.nodeLogs[nodeId] || []
}

const showNodeDetails = (node) => {
  selectedNode.value = node
}

const closeModal = () => {
  selectedNode.value = null
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}
</script>

<style scoped>
.agent-graph {
  background: #1a1a1a;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.graph-title {
  color: #e0e0e0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.graph-container {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 1rem;
  min-height: 200px;
}

.node {
  background: #2a2a2a;
  border: 2px solid #333;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
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

.node-icon {
  font-size: 1.5rem;
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

.node-label {
  font-size: 0.8rem;
  color: #e0e0e0;
  font-weight: 500;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #333;
  border-top: 2px solid #ffa500;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  position: absolute;
  top: 8px;
  right: 8px;
}

.check-mark {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #4caf50;
  font-weight: bold;
  font-size: 1rem;
}

.connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
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
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  color: #e0e0e0;
}

.modal-content h4 {
  margin-top: 0;
  color: #4facfe;
}

.node-logs {
  margin-top: 1rem;
  max-height: 200px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.timestamp {
  color: #888;
  font-family: monospace;
}

.log-message {
  color: #e0e0e0;
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