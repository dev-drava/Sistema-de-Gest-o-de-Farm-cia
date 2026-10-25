from mysql.connector import connect
from mysql.connector import Error
import hashlib


conexao = connect(
    host = "sql313.infinityfree.com",
    user = "if0_43235274",
    password = "gestaofarmacia",
    database = "if0_43235274_farmacia_db"
)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
