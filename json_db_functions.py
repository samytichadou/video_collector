import os
import json
from datetime import datetime

db_path = os.path.join(os.getcwd(), "db.json")
settings_path = os.path.join(os.getcwd(), "settings.json")

def get_datetime():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_json(filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r") as read_file:
        datas = json.load(read_file)
    return datas    

def initialize_json():
    json_datas = {}
    json_datas["time"] = get_datetime()
    json_datas["files"] = []
    return

def iterate_files():
    settings = read_json(settings_path)
    if settings is None:
        print("No settings file, abort")
        return
    old_db = read_json(db_path)

    json_datas = initialize_json()

    for root, dirs, files in os.walk(settings["path_to_monitor"]):
        for f in files:
            if settings["video_extensions"] in f:
                filepath=os.path.join(root, f)
                # check if already exists
                chk_exist=False
                if old_db is not None:
                    for of in old_db["files"]:
                        if of["filepath"]==filepath:
                            chk_exist=True
                            break
                print("Adding %s" % filepath)
                if chk_exist:
                    json_datas["files"].append({
                        "filepath" : filepath,
                        "status" : "treated",
                    })
                else:
                    json_datas["files"].append({
                        "filepath" : filepath,
                        "status" : "to_treat",
                    })

    return json_datas

