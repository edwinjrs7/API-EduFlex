import mysql.connector

def conectarBDD(database):
    return mysql.connector.connect(
        host= 'localhost',
        user = 'root',
        password = '',
        database = database
    )