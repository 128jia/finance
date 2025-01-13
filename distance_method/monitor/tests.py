from django.test import TestCase

import psycopg2
import psycopg2

try:
    # 連接到 PostgreSQL
    db_conn = psycopg2.connect(
        database="distance_method",  # 資料庫名稱
        user="Tommy",                # 使用者名稱
        password="900128",           # 密碼
        host="localhost",            # 主機名，Docker 中可能為 'localhost' 或容器 IP
        port=5432                    # 埠號
    )

    # 創建游標
    db_cursor = db_conn.cursor()

    # 測試查詢
    db_cursor.execute("SELECT version();")
    version = db_cursor.fetchone()
    print("PostgreSQL version:", version)

    # 關閉連接
    db_cursor.close()
    db_conn.close()

except Exception as e:
    print("Error connecting to PostgreSQL:", e)
