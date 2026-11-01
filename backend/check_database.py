
import sqlite3

connection = sqlite3.connect("ecovision.db")

cursor = connection.cursor()

cursor.execute("PRAGMA table_info(environmental_readings)")

columns = cursor.fetchall()

print("Environmental Readings Table Columns:\n")

for column in columns:
    print(column[1])

connection.close()
