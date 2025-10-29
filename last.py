import os
import logging
from datetime import date, datetime, timedelta
import pymongo as mongo
from helper.source_types import SOURCE_TYPES

os.system("cls" if os.name == "nt" else "clear")

client = mongo.MongoClient(
    "mongodb://medmon_kabayan:kabayan123***@localhost:7018/medmon?authSource=medmon"
)
db = client["medmon"]

now = date.today()
skip_date = 1,
now_datetime = datetime.combine(now, datetime.min.time())
skip_datetime = now_datetime - timedelta(days=skip_date-1)  
first_of_month = date(now.year, now.month, 1)
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
        {"$group": {"_id": "$source", "last_date": {"$max": "$date"}}},
        {"$sort": {"last_date": 1}},  # Sorting by 'last_date' ascending
    ]
    return list(db.streams.aggregate(pipeline))


projects = list(db.projects.find({"status": {"$nin": [0, 4]}}).sort("tier", 1))
source_summary = {}

print("-" * 100)
for project in projects:
    project_id = project["_id"]
    display_type = project.get("display_tipe")
    latest_data = get_latest_data_grouped_by_source(project_id)

    if latest_data:
        for data in latest_data:
            if isinstance(data["last_date"], datetime):
                if data["last_date"] < now_datetime:
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
                        "last_date": data["last_date"]
                    })
            else:
                print(f"Invalid format data {data['_id']}")


def tier_sort_key(tier_value):
    if isinstance(tier_value, str):
        return ord(tier_value.upper()[0])
    return 999

exclude_sources = ["forum", "blog"]

for source, projects_data in source_summary.items():
    print(source)
    if source in exclude_sources:
        continue
    for proj in sorted(
        projects_data,
        key=lambda x: (x["last_date"])
    ):
        print(f"- [{proj['tier']}] {proj['name']} ({proj['id']}) - {proj['last_date']}")
    print()

print("-" * 100)
