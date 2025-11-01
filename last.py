import os
import re
import logging
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import pymongo as mongo
from helper.source_types import SOURCE_TYPES
from helper.project_priority import PROJECT_PRIORITY_LIST, get_project_priority

os.system("cls" if os.name == "nt" else "clear")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")

client = mongo.MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]

now = date.today()
skip_date = 1
now_datetime = datetime.combine(now, datetime.min.time())
skip_datetime =now_datetime - timedelta(days=skip_date-1)  
first_of_month = date(now.year, now.month, 1)
first_of_month_datetime = datetime.combine(first_of_month, datetime.min.time())
if now.day == 1:
    prev_month_last_day = first_of_month - timedelta(days=1)
    first_of_month = date(prev_month_last_day.year, prev_month_last_day.month, 1)
    print(f"[DEBUG] Hari ini tanggal 1 → ambil data dari bulan sebelumnya: {first_of_month.strftime('%Y-%m-%d')}")

first_of_month_datetime = datetime.combine(first_of_month, datetime.min.time())

log_filename = "mismatch_log.txt"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="a"
)

def get_latest_data_grouped_by_source(id_project):
    pipeline = [
        {
            "$match": {
                "id_project": id_project,
                "date": {"$gte": first_of_month_datetime},
            }
        },
        {"$group": {"_id": "$source", "last_date": {"$first": "$date"}, "id_origin": {"$first": "$id_origin"}}},
        {"$sort": {"last_date": 1}},  # Sorting by 'last_date' ascending
    ]
    return list(db.streams.aggregate(pipeline))


projects = list(db.projects.find({"status": {"$nin": [0, 4]}}).sort("tier", 1))
source_summary = {}
source_counts = {}
priority_counts = {}

print("-" * 100)
for project in projects:
    project_id = project["_id"]
    display_type = project.get("display_tipe")
    latest_data = get_latest_data_grouped_by_source(project_id)

    if latest_data:
        for data in latest_data:
            if isinstance(data["last_date"], datetime):
                if data["last_date"] < skip_datetime:
                    source = data["_id"]

                    expected_display_type = SOURCE_TYPES.get(source)

                    mismatch = False
                    if expected_display_type is not None:
                        if display_type == 3:
                            mismatch = False
                        elif expected_display_type != display_type:
                            mismatch = True
            
                    if mismatch:
                        log_msg = (
                            f"⚠️ MISMATCH: Project '{project['name']}' "
                            f"({project_id}) display_type={display_type}, "
                            f"tapi source='{source}' bertipe {expected_display_type} | "
                            f"Last date: {data['last_date']}"
                        )
                        logging.warning(log_msg)
                        continue
                    
                    if source not in source_summary:
                        source_summary[source] = []

                    source_summary[source].append({
                        "tier": project["tier"],
                        "name": project["name"],
                        "id": project["_id"],
                        "last_date": data["last_date"],
                        "id_origin": data.get("id_origin"),
                        "priority": get_project_priority(project["name"])
                    })

                    source_counts[source] = source_counts.get(source, 0) + 1
            else:
                print(f"Invalid format data {data['_id']}")

def tier_sort_key(tier_value):
    if isinstance(tier_value, str):
        return ord(tier_value.upper()[0])
    return 999

exclude_sources = ["forum", "blog", "review"]
    
for source, projects_data in source_summary.items():
    if source in exclude_sources:
        continue
    print(source)
    for proj in sorted(
        projects_data,
        key=lambda x: (x["last_date"])
    ):
        print(f"- [{proj['tier']}] {proj['name']} ({proj['id']}) - {proj['last_date']} - {proj.get('id_origin', '-')}")
    print()

def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())

print("=== PRIORITAS PROJECT ===")
project_delay_map = {}
for source, projects_data in source_summary.items():
    if source in exclude_sources:
        continue
    for proj in projects_data:
        norm_name = normalize_name(proj["name"])
        if norm_name not in project_delay_map:
            project_delay_map[norm_name] = []
        project_delay_map[norm_name].append({
            "source": source,
            "last_date": proj["last_date"]
        })

for pname in PROJECT_PRIORITY_LIST:
    nkey = normalize_name(pname)
    if nkey in project_delay_map:
        print(f"\n {pname}")
        for s in sorted(project_delay_map[nkey], key=lambda x: x["last_date"]):
            print(f" - {s['source']} - {s['last_date'].strftime('%Y-%m-%d %H:%M:%S')}")
print()

for source, projects_data in source_summary.items():
    if source in exclude_sources:
        continue
    for proj in projects_data:
        if proj["name"] in PROJECT_PRIORITY_LIST:
            priority_counts[source] = priority_counts.get(source, 0) + 1


print("=== TOTAL PER SOURCE ===")   
for source, total in source_counts.items():
    if source in exclude_sources:
        continue
    priority_total = priority_counts.get(source, 0)
    print(f"{source} ({total} total, {priority_total} prioritas)")
print("-" * 100)
