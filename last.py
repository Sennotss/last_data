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
project_summary_obj = {}

print("-" * 100)

for project in projects:
    project_obj = {"exist": False, "sources": []}

    latest_data = get_latest_data_grouped_by_source(project["_id"])

    if latest_data:
        for data in latest_data:
            if isinstance(data["last_date"], datetime):
                if data["last_date"] < now_datetime:
                    project_obj["exist"] = True

                    project_obj["sources"].append(
                        f"{data['last_date']} -- {data['_id']}"
                    )

                    if data["_id"] not in project_summary_obj:
                        project_summary_obj[data["_id"]] = 0
                        continue

                    project_summary_obj[data["_id"]] += 1
            else:
                print(f"Invalid date format for {data['_id']}")

    if project_obj["exist"]:
        print(f"Project: [{project['tier']}] {project['name']} ({project['_id']})")

        for source in project_obj["sources"]:
            print(source)

        print("-" * 100)

if project_summary_obj:
    project_summary_array = [{"source": source_id, "count": count} for source_id, count in project_summary_obj.items()]
    sorted_project_summary_array = sorted(project_summary_array, key=lambda x: x['count'], reverse=True)

    for spsa in sorted_project_summary_array:
        print(f"Source {spsa['source']}: {spsa['count']} projects")


    print("-" * 100)
