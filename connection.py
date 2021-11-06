import pymysql
def Connect():
    conn = pymysql.connect(host="13.232.35.56", user="inderjit", password="inderjit@123", database="inderjit")
    return conn