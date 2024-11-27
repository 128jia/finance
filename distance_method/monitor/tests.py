from django.test import TestCase

import psycopg2

# 使用新創建的用戶和資料庫進行連接
conn = psycopg2.connect(
    host="localhost",
    database="distance_method",
    user="thomas",
    password="AUTh6496",
    port=5432  # 根據您的配置，如果是其他端口，如 5433，請更改
)

print("Database connected successfully!")

