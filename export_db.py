import sqlite3
import csv
import json
import sys
DB_PATH = 'symbols.db'
TABLE_NAME = 'known_symbols'
def export_csv(output='symbols_export.csv'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT symbol, market_type, status, create_time_utc FROM {TABLE_NAME}")
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['symbol','market_type','status','create_time_utc'])
        writer.writerows(c.fetchall())
    conn.close()
    print(f"Exported to {output}")
def export_json(output='symbols_export.json'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT symbol, market_type, status, create_time_utc FROM {TABLE_NAME}")
    items = [dict(zip(['symbol','market_type','status','create_time_utc'], row)) for row in c.fetchall()]
    with open(output, 'w') as f:
        json.dump(items, f, indent=2)
    conn.close()
    print(f"Exported to {output}")
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        export_json()
    else:
        export_csv()
