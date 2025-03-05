<script setup>
import { ref, onMounted, nextTick } from "vue";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-dark.css"; // 🔥黑色背景 + 高对比

const logs = ref([]);
const activeDropdown = ref(null);

const fetchLogs = async () => {
  try {
    const response = await fetch("http://localhost:8000/logs");
    const data = await response.json();
    logs.value = data;

    await nextTick(); // 等 Vue 渲染完再执行高亮
    highlightCode();
  } catch (error) {
    console.error("日志获取失败", error);
  }
};

// 解析 JSON 并美化缩进
const formatJSON = (jsonString) => {
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2);
  } catch (e) {
    return jsonString; // 解析失败，返回原始数据
  }
};

// 代码高亮
const highlightCode = () => {
  document.querySelectorAll("pre code").forEach((el) => {
    hljs.highlightElement(el);
  });
};

// 切换下拉菜单
const toggleDropdown = (id) => {
  activeDropdown.value = activeDropdown.value === id ? null : id;
};

onMounted(fetchLogs);
</script>

<template>
  <div class="container">
    <h2>📜 日志数据</h2>
    <button class="fetch-btn" @click="fetchLogs">Fetch Logs</button>

    <ul class="log-list">
      <li v-for="log in logs" :key="log.id" class="log-item">
        <div class="log-header">
          <span><strong>📌 IP 地址：</strong> {{ log.ip_address }}</span>
          <span><strong>🕒 时间：</strong> {{ log.log_date }}</span>
          <button @click="toggleDropdown(log.id)" class="toggle-btn">
            {{ activeDropdown === log.id ? "🔼 收起" : "🔽 展开" }}
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
/* 页面基础样式 */
.container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background: #121212; /* 🔥 黑色背景 */
  color: #f8f8f2; /* 亮色字体 */
  border-radius: 10px;
}

/* 按钮 */
.fetch-btn {
  background: #ff9800; /* 橙色按钮 */
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

/* 日志列表 */
.log-list {
  list-style: none;
  padding: 0;
}
.log-item {
  border-bottom: 1px solid #333;
  padding: 10px;
  margin-bottom: 10px;
}

/* 日志头部 */
.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.toggle-btn {
  background: #00acc1; /* 蓝色按钮 */
  color: #fff;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 5px;
}
.toggle-btn:hover {
  background: #008ba3;
}

/* JSON 代码高亮 */
pre {
  background: #1e1e1e; /* 深色背景 */
  padding: 10px;
  border-radius: 5px;
  overflow: auto;
}
code {
  font-family: "Courier New", monospace;
}
</style>
