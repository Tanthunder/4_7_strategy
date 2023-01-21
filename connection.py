''' connecting to postgres db '''

import psycopg2
import os

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="invest_trade_manage_dev",
    user=os.environ.get('POSTGRES_DB_USER'),
    password=os.environ.get('POSTGRES_DB_PAS'),
)
conn.autocommit = True
cursor = conn.cursor()

#cursor.execute("insert into reference values (100, 115);")
#cursor.execute("delete from reference")

