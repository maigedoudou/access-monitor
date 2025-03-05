import json
import logging
import requests
import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 只允许前端访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法 (GET, POST, DELETE等)
    allow_headers=["*"],  # 允许所有请求头
)

logging.basicConfig(level=logging.DEBUG)

db_config = {
    "host": "db",  # 容器内 MySQL 服务名称
    "user": "monitor",
    "password": "monitorpassword",
    "database": "access_monitor"
}

@app.get("/")
def read_root():
    return {"message": "Backend!!!"}

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from backend!"}

@app.get("/fetch_logs")
def fetch_logs():
    url = "http://192.168.10.250:10010/security/recent"
    logging.debug(f"访问 API: {url}")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        logging.debug(f"✅ API 返回数据: {data}")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API 请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"API 请求失败: {e}")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for entry in data.get("suspects", []):
            # 确保 details 是有效的 JSON 对象，而不是字符串
            details_json = json.dumps(entry, ensure_ascii=False)  # 将 entry 直接转为 JSON 格式
            
            # 插入数据
            cursor.execute(
                "INSERT INTO access_logs (log_date, ip_address, details) VALUES (%s, %s, %s)",
                (data["date"], entry["ip"], details_json)
            )

        conn.commit()
        cursor.close()
        conn.close()
        logging.debug("✅ 数据成功插入 MySQL")
    except mysql.connector.Error as e:
        logging.error(f"❌ MySQL 插入失败: {e}")
        raise HTTPException(status_code=500, detail="数据库插入失败")

    return {"message": "Logs fetched successfully"}

@app.get("/logs")
def get_logs():
    """ 查询数据库中的访问日志 """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM access_logs ORDER BY created_at DESC LIMIT 10")
        logs = cursor.fetchall()

        cursor.close()
        conn.close()
        logging.debug(f"✅ 获取日志成功，共 {len(logs)} 条记录")
        return logs
    except mysql.connector.Error as e:
        logging.error(f"❌ MySQL 查询失败: {e}")
        raise HTTPException(status_code=500, detail="数据库查询失败")
