import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
import subprocess
import threading
import os
import time
import subprocess
import platform


# color & UI 
BG_COLOR = "#ECF0F1"   
BUTTON_COLOR = "#34495E"  
TEXT_COLOR = "#ffffff"  
STOP_COLOR = "#E74C3C"  
FETCH_COLOR = "#34495E"  
CLEAR_COLOR = "#34495E"  

LOG_COLOR = {
    "INFO": "#9CDCFE",
    "WARNING": "#DCDCAA",
    "ERROR": "#F44747",
}
STATUS_COLOR = {
    "Stopped": "white",
    "Starting": "white",
    "Running": "white",
    "Error": "red"
}

# 回転アニメーション
SPINNER = ["◐", "◓", "◑", "◒"]
spinner_idx = 0

tracked_containers = {}

context_menu = None

def update_spinner():
    global spinner_idx
    spinner_idx = (spinner_idx + 1) % len(SPINNER)
    return SPINNER[spinner_idx]


def check_docker_status():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

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
        
        update_docker_status("Stopped")
        update_container_status(retries=5, delay=1)  

    except Exception as e:
        log_message(f"Error: {e}", "ERROR")
        update_docker_status("Error")

def clear_cache():
    log_message("Clearing Docker Cache...", "WARNING")
    threading.Thread(target=run_clear_cache, daemon=True).start()

def run_clear_cache():
    try:
        process = subprocess.Popen(["docker", "system", "prune", "-f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        animate_log_output(process)
        log_message("Cache Cleared!", "INFO")

        global tracked_containers
        tracked_containers.clear()  
        update_container_status()   

    except Exception as e:
        log_message(f"Error: {e}", "ERROR")

def log_message(message, level="INFO"):
    log_box.insert("end", f"[{update_spinner()} {level}] {message}\n", level)
    log_box.see("end")


# 動的スクロール出力
def animate_log_output(process):
    for line in process.stdout:
        log_message(line.strip(), "INFO")
        time.sleep(0.1)

# Dockerコンテナのステータス
def update_container_status(retries=5, delay=1):
    
    for _ in range(retries):
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}} {{.Status}}"],
                capture_output=True, text=True
            )
            containers = result.stdout.strip().split("\n")

            for row in container_table.get_children():
                container_table.delete(row)

            for container in containers:
                if container:
                    parts = container.split(maxsplit=1)
                    if len(parts) == 2:
                        name, status = parts
                        tracked_containers[name] = status  

            for name, status in tracked_containers.items():
                status_color = STATUS_COLOR["Running"] if "Up" in status else STATUS_COLOR["Stopped"]
                container_table.insert("", "end", values=(name, status), tags=(status_color,))

            if all("Exited" in status or "Created" in status for status in tracked_containers.values()):
                break

        except Exception as e:
            log_message(f"Error fetching containers: {e}", "ERROR")

        time.sleep(delay)  


# Docker のステータスを表示する
def update_docker_status(status):
    status_label.config(text=f"Docker Status: {status}", fg=STATUS_COLOR.get(status, "gray"))

# 右クリックメニュー - 操作コンテナ
def on_right_click(event):
    selected_item = container_table.identify_row(event.y)
    if selected_item and container_table.exists(selected_item):
        container_table.selection_set(selected_item)
        show_menu(event, selected_item)

def show_menu(event, selected_item):
    global context_menu
  
    if context_menu:
        context_menu.destroy()
    
    context_menu = Menu(root, tearoff=0)
    context_menu.add_command(label="Start", command=lambda: manage_container("start", selected_item))
    context_menu.add_command(label="Stop", command=lambda: manage_container("stop", selected_item))
    context_menu.add_command(label="Restart", command=lambda: manage_container("restart", selected_item))
    
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


def fetch_frontend():
    url = "http://localhost:3000"
    try:
        if platform.system() == "Windows":  # Windows
            os.startfile(url)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", url])
        elif platform.system() == "Linux":  # Linux
            subprocess.Popen(["xdg-open", url])
        elif "microsoft" in platform.version().lower():  # WSL
            subprocess.Popen(["explorer.exe", url])
        else:
            log_message(f"Unsupported OS", "ERROR")
    except Exception as e:
        log_message(f"Cannot open frontend: {e}", "ERROR")


# UI 
root = tk.Tk()
root.title("Docker Launcher")
root.geometry("1000x400")
root.configure(bg=BG_COLOR)


# ログ
frame_log = tk.Frame(root, bg=BG_COLOR)
frame_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  


log_box = scrolledtext.ScrolledText(
    frame_log, 
    bg="#2C3E50",  
    fg="#ECF0F1",  
    font=("Helvetica", 11),  
    wrap=tk.WORD,
    height=8,  
    padx=10, pady=10,  
    bd=0,  
    relief="flat"  
)
log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)


# ログレベルの色を設定する (オプション)
for level, color in LOG_COLOR.items():
    log_box.tag_configure(level, foreground=color)


# ボタンフレーム
frame_buttons = tk.Frame(root, bg=BG_COLOR)
frame_buttons.pack(fill=tk.X, padx=5, pady=5)

btn_start = tk.Button(frame_buttons, text="Start", command=start_docker, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"))
btn_stop = tk.Button(frame_buttons, text="Stop", command=stop_docker, bg=STOP_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"))
btn_fetch = tk.Button(frame_buttons, text="Open Frontend", command=fetch_frontend, bg=FETCH_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"))
btn_clear = tk.Button(frame_buttons, text="Clear Cache", command=clear_cache, bg=CLEAR_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"))

btn_start.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
btn_stop.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
btn_fetch.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
btn_clear.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)


# Dockerステータス バー
status_frame = tk.Frame(root, bg=BG_COLOR)
status_frame.pack(fill=tk.X, padx=5, pady=5)

status_label = tk.Label(status_frame, text="Docker Status: Unknown", fg="white", bg="grey", font=("Helvetica", 12, "bold"), anchor="w", padx=10)
status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)  


# Dockerコンテナステータステーブル
frame_table = tk.Frame(root, bg=BG_COLOR)
frame_table.pack(fill=tk.X, padx=5, pady=5)

container_table = ttk.Treeview(frame_table, columns=("Container Name", "Status"), show="headings", height=5) 
container_table.heading("Container Name", text="Container Name", anchor="w")
container_table.heading("Status", text="Status", anchor="w")


container_table.column("Container Name", width=200, anchor="w")
container_table.column("Status", width=100, anchor="center")

container_table.pack(fill=tk.X, padx=5, pady=5)

container_table.bind("<Button-3>", on_right_click)




root.mainloop()









