import mysql.connector

mydb = mysql.connector.connect(
    
    host="gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
    user="QseGRPMo1XqGtHz.root",
    password="v9Ut1oWS3QywXWeR",
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS gestao_farmacia")
print("Base de dados 'gestao_farmacia' criada com sucesso!")