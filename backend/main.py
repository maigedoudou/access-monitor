import json
import logging
import requests
import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

logging.basicConfig(level=logging.DEBUG)

db_config = {
    "host": "db", 
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
        logging.debug(f"✅ APIからのデータを返す: {data}")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ APIリクエストが失敗する: {e}")
        raise HTTPException(status_code=500, detail=f"APIリクエストが失敗する: {e}")


    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for entry in data.get("suspects", []):
  
            details_json = json.dumps(entry, ensure_ascii=False) 
            
            cursor.execute(
                "INSERT INTO access_logs (log_date, ip_address, details) VALUES (%s, %s, %s)",
                (data["date"], entry["ip"], details_json)
            )

        conn.commit()
        cursor.close()
        conn.close()
        logging.debug("✅ データがMySQLに正常に挿入されました")
    except mysql.connector.Error as e:
        logging.error(f"❌ MySQLへの挿入に失敗しました: {e}")
        raise HTTPException(status_code=500, detail="データベースへの挿入に失敗しました")

    return {"message": "Logs fetched successfully"}

@app.get("/logs")
def get_logs():
    """ データベースのアクセスログを検索する """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM access_logs ORDER BY created_at DESC LIMIT 10")
        logs = cursor.fetchall()

        cursor.close()
        conn.close()
        logging.debug(f"✅ ログの取得に成功しました，合計で {len(logs)} 件の記録があります")
        return logs
    except mysql.connector.Error as e:
        logging.error(f"❌ MySQLの検索が失敗しました: {e}")
        raise HTTPException(status_code=500, detail="データベースの検索が失敗しました")
