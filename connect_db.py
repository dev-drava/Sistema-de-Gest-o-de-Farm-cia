import mysql.connector

def start_connection():
    return mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
        user="QseGRPMo1XqGtHz.root",
        password="v9Ut1oWS3QywXWeR",
        database="gestao_farmacia",
        port="4000"
    )

