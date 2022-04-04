import os
import json
import subprocess
import shlex
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
    return json_datas

def write_json(json_datas, json_path):
    with open(json_path, "w") as write_file :
        json.dump(json_datas, write_file, indent=4, sort_keys=False)

def get_ffprobe_output(video_path):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(video_path)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)
    return ffprobeOutput

def get_metadata_from_ffprobe(ffprobe_output, metadata_id):
    return ffprobe_output['streams'][0][metadata_id]

def iterate_files():
    settings = read_json(settings_path)
    if settings is None:
        print("No settings file, abort")
        return
    old_db = read_json(db_path)

    json_datas = initialize_json()

    for root, dirs, files in os.walk(settings["path_to_monitor"]):
        for f in files:
            filepath=os.path.join(root, f)
            if os.path.splitext(f)[1] in settings["video_extensions"]:
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
                        "status": "treated",
                        "ffprobe": get_ffprobe_output(filepath),
                    })
                else:
                    json_datas["files"].append({
                        "filepath": filepath,
                        "status": "to_treat",
                        "ffprobe": get_ffprobe_output(filepath),
                    })
            else:
                print("Skipping %s" % filepath)

    return json_datas

def update_db():
    json_datas=iterate_files()
    write_json(json_datas, db_path)

update_db()