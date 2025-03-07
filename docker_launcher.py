import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu
import subprocess
import webbrowser
import threading
import os
import time

# 颜色 & UI 设计
BG_COLOR = "#1E1E1E"
TEXT_COLOR = "#D4D4D4"
BUTTON_COLOR = "#007AFF"  # Mac 风格蓝色
LOG_COLOR = {
    "INFO": "#9CDCFE",
    "WARNING": "#DCDCAA",
    "ERROR": "#F44747",
}
STATUS_COLOR = {
    "Stopped": "gray",
    "Starting": "yellow",
    "Running": "green",
    "Error": "red"
}

# 旋转动画
SPINNER = ["◐", "◓", "◑", "◒"]
spinner_idx = 0

# 记录出现过的容器
tracked_containers = {}

context_menu = None

def update_spinner():
    global spinner_idx
    spinner_idx = (spinner_idx + 1) % len(SPINNER)
    return SPINNER[spinner_idx]

# 检测 Docker 是否运行
def check_docker_status():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

# 启动 Docker Compose
def start_docker():
    if not check_docker_status():
        log_message("Docker is not running!", "ERROR")
        return
    log_message("Starting Docker Compose...", "INFO")
    update_docker_status("Starting")
    threading.Thread(target=run_docker_compose, daemon=True).start()

def run_docker_compose():
    try:
        process = subprocess.Popen(["docker-compose", "up", "-d"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        animate_log_output(process)
        log_message("Docker Compose started!", "INFO")
        update_docker_status("Running")
        update_container_status()
    except Exception as e:
        log_message(f"Error: {e}", "ERROR")
        update_docker_status("Error")

# 停止 Docker Compose
def stop_docker():
    log_message("Stopping Docker Compose...", "WARNING")
    update_docker_status("Stopped")
    threading.Thread(target=run_docker_down, daemon=True).start()

def run_docker_down():
    try:
        process = subprocess.Popen(
            ["docker-compose", "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        animate_log_output(process)
        log_message("Docker Compose stopped!", "INFO")
        
        # 确保 Docker 状态正确更新
        update_docker_status("Stopped")
        update_container_status(retries=5, delay=1)  # 多次尝试获取最新状态

    except Exception as e:
        log_message(f"Error: {e}", "ERROR")
        update_docker_status("Error")

# 清除 Docker Cache
def clear_cache():
    log_message("Clearing Docker Cache...", "WARNING")
    threading.Thread(target=run_clear_cache, daemon=True).start()

def run_clear_cache():
    try:
        process = subprocess.Popen(["docker", "system", "prune", "-f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        animate_log_output(process)
        log_message("Cache Cleared!", "INFO")

        global tracked_containers
        tracked_containers.clear()  # 清空所有容器记录
        update_container_status()   # 重新刷新表格，彻底移除停止的容器

    except Exception as e:
        log_message(f"Error: {e}", "ERROR")

# 记录日志
def log_message(message, level="INFO"):
    log_box.insert("end", f"[{update_spinner()} {level}] {message}\n", level)
    log_box.see("end")

# 动态滚动输出
def animate_log_output(process):
    for line in process.stdout:
        log_message(line.strip(), "INFO")
        time.sleep(0.1)

# Docker 容器状态
def update_container_status(retries=5, delay=1):
    """确保 Docker 容器状态更新，Stop 后仍然显示 Exited X seconds"""
    for _ in range(retries):
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}} {{.Status}}"],
                capture_output=True, text=True
            )
            containers = result.stdout.strip().split("\n")

            # 先清空表格，防止 UI 乱
            for row in container_table.get_children():
                container_table.delete(row)

            # 重新填充表格
            for container in containers:
                if container:
                    parts = container.split(maxsplit=1)
                    if len(parts) == 2:
                        name, status = parts
                        tracked_containers[name] = status  # 记录容器状态

            # 重新渲染 UI
            for name, status in tracked_containers.items():
                status_color = STATUS_COLOR["Running"] if "Up" in status else STATUS_COLOR["Stopped"]
                container_table.insert("", "end", values=(name, status), tags=(status_color,))

            # 如果所有容器都已退出，就不再重复检查
            if all("Exited" in status or "Created" in status for status in tracked_containers.values()):
                break

        except Exception as e:
            log_message(f"Error fetching containers: {e}", "ERROR")

        time.sleep(delay)  # 等待一会儿再尝试




# 显示 Docker 状态
def update_docker_status(status):
    status_label.config(text=f"Docker Status: {status}", fg=STATUS_COLOR.get(status, "gray"))

# 右键菜单 - 操作容器
def on_right_click(event):
    selected_item = container_table.identify_row(event.y)
    if selected_item and container_table.exists(selected_item):  # 确保 ID 存在
        container_table.selection_set(selected_item)
        show_menu(event, selected_item)

def show_menu(event, selected_item):
    global context_menu
    # 先销毁已有的菜单（防止重复）
    if context_menu:
        context_menu.destroy()
    
    context_menu = Menu(root, tearoff=0)
    context_menu.add_command(label="Start", command=lambda: manage_container("start", selected_item))
    context_menu.add_command(label="Stop", command=lambda: manage_container("stop", selected_item))
    context_menu.add_command(label="Restart", command=lambda: manage_container("restart", selected_item))
    
    # 在点击其他地方时，销毁菜单
    root.bind("<Button-1>", lambda e: context_menu.destroy())
    
    context_menu.post(event.x_root, event.y_root)
    
def manage_container(action, selected_item):
    if not selected_item or not container_table.exists(selected_item):
        log_message("Invalid container selection.", "ERROR")
        return

    container_data = container_table.item(selected_item, "values")
    if not container_data:
        log_message("Failed to retrieve container info.", "ERROR")
        return
    
    container_name = container_data[0]
    log_message(f"{action.capitalize()} {container_name}...", "INFO")
    threading.Thread(target=run_container_command, args=(container_name, action), daemon=True).start()

def run_container_command(container_name, action):
    try:
        subprocess.run(["docker", action, container_name], capture_output=True, text=True)
        log_message(f"{container_name} {action}ed successfully!", "INFO")
        update_container_status()
    except Exception as e:
        log_message(f"Error managing container: {e}", "ERROR")

# 打开前端
def fetch_frontend():
    url = "http://localhost:3000"
    try:
        if os.name == "nt":  # Windows
            os.startfile(url)
        elif "microsoft" in os.uname().release.lower():  # WSL
            subprocess.run(["explorer.exe", url])
        else:  # Linux / macOS
            subprocess.run(["xdg-open", url])
    except Exception as e:
        log_message(f"Cannot open frontend: {e}", "ERROR")

# UI 设计
root = tk.Tk()
root.title("Docker Launcher")
root.geometry("1000x650")
root.configure(bg=BG_COLOR)

# 日志框
frame_log = tk.Frame(root, bg=BG_COLOR)
frame_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

log_box = scrolledtext.ScrolledText(frame_log, bg="black", fg=TEXT_COLOR, font=("Consolas", 10), wrap=tk.WORD)
log_box.pack(fill=tk.BOTH, expand=True)
for level, color in LOG_COLOR.items():
    log_box.tag_configure(level, foreground=color)

# 按钮框架
frame_buttons = tk.Frame(root, bg=BG_COLOR)
frame_buttons.pack(fill=tk.X, padx=5, pady=5)

btn_start = tk.Button(frame_buttons, text="Start", command=start_docker, bg=BUTTON_COLOR, fg="white", font=("Helvetica", 12, "bold"))
btn_stop = tk.Button(frame_buttons, text="Stop", command=stop_docker, bg="red", fg="white", font=("Helvetica", 12, "bold"))
btn_fetch = tk.Button(frame_buttons, text="Open Frontend", command=fetch_frontend, bg="blue", fg="white", font=("Helvetica", 12, "bold"))
btn_clear = tk.Button(frame_buttons, text="Clear Cache", command=clear_cache, bg="gray", fg="white", font=("Helvetica", 12, "bold"))

btn_start.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
btn_stop.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
btn_fetch.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
btn_clear.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)

# Docker 状态
status_label = tk.Label(root, text="Docker Status: Unknown", fg="gray", bg=BG_COLOR, font=("Helvetica", 12, "bold"))
status_label.pack(pady=10)

# Docker 容器状态
container_table = ttk.Treeview(root, columns=("Container Name", "Status"), show="headings")
container_table.heading("Container Name", text="Container Name")
container_table.heading("Status", text="Status")
container_table.pack(fill=tk.BOTH, expand=True)

container_table.bind("<Button-3>", on_right_click)

root.mainloop()
