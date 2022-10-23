import sqlite3

connection = sqlite3.connect('identifier.sqlite')
cursor = connection.cursor()

with open('nmap-mac-prefixes.txt', 'r') as f:
    for line in f:
        data = line.split(maxsplit=1)
        ven_name = data[1].replace('\n', '').replace("'", '')
        mac = data[0]
        print(mac, ven_name)
        cursor.executescript(f"INSERT INTO vendors (name,mac_prefix) VALUES ('{ven_name}','{mac}')")