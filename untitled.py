import sqlite3
email='him.mj26@gmail.com'
con=sqlite3.connect("user_database.db")
conn=con.cursor()
conn.execute("SELECT * FROM COUPLES WHERE email1=? OR EMAIL2=?",(email,email))
k=conn.fetchall()
for row in k:
	c=row
print c