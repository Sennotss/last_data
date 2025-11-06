PROJECT_PRIORITY_LIST = [
    "Bali United",
    "BJB",
    "Immoderma",
    "Media Kernel",
    "BP Tapera",
    "MMS Group",
    "API Mandiri",
    "Pemprov Sumut",
    "Gubernur-Indonesia",
    "Teladan Prima Agro",
    "DISPAMSANAU",
    "Kejaksaan Agung RI",
    "kemenparekraf",
    "DPRD DKI Jakarta"
]

PROJECT_PRIORITY_MAP = {name: index + 1 for index, name in enumerate(PROJECT_PRIORITY_LIST)}

def get_project_priority(project_name: str) -> int:
    if not project_name:
        return 999
    return PROJECT_PRIORITY_MAP.get(project_name.lower().strip(), 999)