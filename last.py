import os
from datetime import date, datetime
import pymongo as mongo

os.system("cls" if os.name == "nt" else "clear")

client = mongo.MongoClient(
    "mongodb://medmon_kabayan:kabayan123***@localhost:7018/medmon?authSource=medmon"
)
db = client["medmon"]

now = date.today()
now_datetime = datetime.combine(now, datetime.min.time())
first_of_month = date(now.year, now.month, 1)
first_of_month_datetime = datetime.combine(first_of_month, datetime.min.time())


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
    latest_data = get_latest_data_grouped_by_source(project["_id"])

    if latest_data:
        for data in latest_data:
            if isinstance(data["last_date"], datetime):
                if data["last_date"] < now_datetime:
                    source = data["_id"]

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

for source, projects_data in source_summary.items():
    print(source)
    for proj in sorted(
        projects_data,
        key=lambda x: (tier_sort_key(x["tier"]), x["last_date"])
    ):
        print(f"- [{proj['tier']}] {proj['name']} ({proj['id']}) - {proj['last_date']}")
    print()

print("-" * 100)
