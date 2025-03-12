<script setup>
import { ref, onMounted, nextTick } from "vue";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-dark.css"; 

const logs = ref([]);
const activeDropdown = ref(null);

const fetchLogs = async () => {
  try {
    // const response = await fetch("http://localhost:8000/logs");
    const response = await fetch("http://localhost:8000/fetch_logs");
    const data = await response.json();
    logs.value = data;

    await nextTick(); 
    highlightCode();
  } catch (error) {
    console.error("ログ取得に失敗しました", error);
  }
};



const formatJSON = (jsonString) => {
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2);
  } catch (e) {
    return jsonString; 
  }
};

const highlightCode = () => {
  document.querySelectorAll("pre code").forEach((el) => {
    hljs.highlightElement(el);
  });
};


const toggleDropdown = (id) => {
  activeDropdown.value = activeDropdown.value === id ? null : id;
};

onMounted(fetchLogs);
</script>

<template>
  <div class="container">
    <h2>📜 ログデータ</h2>
    <button class="fetch-btn" @click="fetchLogs">Fetch Logs</button>

    <ul class="log-list">
      <li v-for="log in logs" :key="log.id" class="log-item">
        <div class="log-header">
          <span><strong>📌 IPアドレス：</strong> {{ log.ip_address }}</span>
          <span><strong>🕒 時間：</strong> {{ log.log_date }}</span>
          <button @click="toggleDropdown(log.id)" class="toggle-btn">
            {{ activeDropdown === log.id ? "🔼 折りたたむ" : "🔽 展開する" }}
          </button>
        </div>

        <div v-if="activeDropdown === log.id" class="log-details">
          <pre><code class="json">{{ formatJSON(log.details) }}</code></pre>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>

.container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background: #121212; 
  color: #f8f8f2; 
  border-radius: 10px;
}

.fetch-btn {
  background: #ff9800; 
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin-bottom: 10px;
}
.fetch-btn:hover {
  background: #e68900;
}

.log-list {
  list-style: none;
  padding: 0;
}
.log-item {
  border-bottom: 1px solid #333;
  padding: 10px;
  margin-bottom: 10px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.toggle-btn {
  background: #00acc1; 
  color: #fff;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 5px;
}
.toggle-btn:hover {
  background: #008ba3;
}

pre {
  background: #1e1e1e; 
  padding: 10px;
  border-radius: 5px;
  overflow: auto;
}
code {
  font-family: "Courier New", monospace;
}
</style>
