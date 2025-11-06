import os
from datetime import datetime, date
from dotenv import load_dotenv
import pymongo as mongo

# Bersihkan terminal
os.system("cls" if os.name == "nt" else "clear")

# Load variabel dari .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")

if not MONGO_URI or not MONGO_DBNAME:
    raise ValueError("❌ Pastikan MONGO_URI dan MONGO_DBNAME sudah diatur di .env")

# Koneksi ke MongoDB
client = mongo.MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]

# Setup tanggal
now = date.today()
first_of_month = date(now.year, now.month, 1)
first_of_month_datetime = datetime.combine(first_of_month, datetime.min.time())

print("-" * 100)
print(f"[DEBUG] Menampilkan semua last_date per project sejak {first_of_month_datetime.strftime('%Y-%m-%d')}")
print("-" * 100)

# Ambil semua sumber unik di streams
all_sources = db.streams.distinct("source")
print(f"[INFO] Total sumber terdeteksi: {len(all_sources)} -> {', '.join(sorted(all_sources))}")
print("-" * 100)

def get_latest_data_grouped_by_source(id_project):
    pipeline = [
        {
            "$match": {
                "id_project": id_project,
                "date": {"$gte": first_of_month_datetime},
            }
        },
        {
            "$group": {
                "_id": "$source",
                "last_date": {"$first": "$date"},
                "id_origin": {"$first": "$id_origin"}
            }
        },
        {"$sort": {"last_date": 1}},
    ]
    return list(db.streams.aggregate(pipeline))

projects = list(db.projects.find({"status": 1}).sort("tier", 1))

for idx, project in enumerate(projects, start=1):
    project_id = project["_id"]
    project_name = project["name"]
    tier = project.get("tier", "-")

    latest_data = get_latest_data_grouped_by_source(project_id)
    data_by_source = {item["_id"]: item for item in latest_data}

    print(f"\n[{idx:03}]  {project_name} (tier {tier})")

    if not latest_data:
        print("  ⚠️ Tidak ada data bulan ini")

    # Loop semua source agar semua muncul
    for source in sorted(all_sources):
        if source in data_by_source:
            data = data_by_source[source]
            last_date = data["last_date"]
            id_origin = data.get("id_origin", "-")
            if isinstance(last_date, datetime):
                print(f" - {source:<15} {last_date.strftime('%Y-%m-%d %H:%M:%S')} | id_origin: {id_origin}")
            else:
                print(f" - {source:<15} (invalid date format)")
        else:
            print(f" - {source:<15} tidak ada data")

print("\n" + "-" * 100)
print("[SELESAI] Semua project dan source sudah ditampilkan.")
print("-" * 100)
