// stores/agent.js
import { defineStore } from 'pinia';
import { connectWebSocket, sendMessage, disconnectWebSocket } from '../services/socket';

export const useAgentStore = defineStore('agent', {
  state: () => ({
    messages: [],
    currentNode: 'idle',
    status: 'waiting', // 'waiting', 'thinking', 'streaming', 'finished', 'error'
    logs: [],
    isConnected: false,
    nodeStates: {}, // 각 노드의 상태 (pending, running, completed, error)
    nodeLogs: {}, // 각 노드별 로그
  }),
  actions: {
    initConnection() {
      connectWebSocket((data) => this.handleWebSocketMessage(data));
    },

    resetNodeStates() {
      this.nodeStates = {};
      this.nodeLogs = {};
    },

    updateNodeState(nodeId, status, message = '') {
      this.nodeStates[nodeId] = { status, timestamp: Date.now() };
      if (message) {
        if (!this.nodeLogs[nodeId]) this.nodeLogs[nodeId] = [];
        this.nodeLogs[nodeId].push({ message, timestamp: Date.now() });
      }
    },

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'connection_status':
                this.isConnected = data.status === 'connected';
                break;
            case 'node_start':
                this.updateNodeState(data.node, 'running', data.content);
                break;
            case 'node_end':
                this.updateNodeState(data.node, 'completed', data.content);
                break;
            case 'tool_start':
                this.logs.unshift(data.content);
                break;
            case 'tool_end':
                this.logs.unshift(data.content);
                break;
            case 'thinking':
                this.status = 'thinking';
                break;
            case 'final_answer':
                this.status = 'streaming';
                let lastMessage = this.messages[this.messages.length - 1];
                if (lastMessage && lastMessage.role === 'assistant') {
                    lastMessage.content = data.content;
                }
                break;
            case 'log':
                this.logs.unshift(data.content);
                break;
            case 'end':
                this.status = 'finished';
                break;
            case 'error':
                this.status = 'error';
                this.logs.unshift(`[ERROR] ${data.content}`);
                let lastMsg = this.messages[this.messages.length - 1];
                 if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content === '...') {
                    lastMsg.content = `An error occurred: ${data.content}`;
                }
                break;
        }
    },
    
    async fetchSystemHealth() {
      try {
        const response = await fetch('http://localhost:8000/api/system/health');
        if (!response.ok) { throw new Error('Network response was not ok'); }
        const data = await response.json();
        return data.components;
      } catch (error) {
        console.error("Error fetching system health:", error);
        return {
          db: { status: 'error', message: 'Connection failed' },
          mcp: { status: 'error', message: 'Connection failed' },
          local_llm: { status: 'error', message: 'Connection failed' },
          gemini_llm: { status: 'error', message: 'Connection failed' },
        };
      }
    },

    sendMessage(userId, message) {
      if (!this.isConnected) {
          this.logs.unshift("[ERROR] Cannot send message: Not connected to the server.");
          return;
      }
        
      this.messages.push({ id: Date.now(), role: 'user', content: message });
      this.messages.push({ id: Date.now() + 1, role: 'assistant', content: '...' });
      this.status = 'thinking';
      this.logs = [];
      this.resetNodeStates();

      const payload = {
        user_id: parseInt(userId, 10) || 1,
        message: message,
      };
      
      sendMessage(payload);
    },
  },
});