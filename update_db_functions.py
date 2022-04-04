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

def iterate_files_through_db():
    settings = read_json(settings_path)

    if os.path.isfile(db_path):
        old_db=read_json(db_path)
    else:
        old_db=None

    json_datas = initialize_json()

    for root, dirs, files in os.walk(settings["path_to_monitor"]):
        for f in files:
            filepath=os.path.join(root, f)
            if os.path.splitext(f)[1] in settings["video_extensions"]:
                # check if already exists
                existing=None
                if old_db is not None:
                    for of in old_db["files"]:
                        if of["filepath"]==filepath:
                            if of["status"]!="to_treat":
                                of["status"]="treated"
                                existing=of
                                break
                            else:
                                existing=of
                                break
                print("Adding %s" % filepath)
                if existing is not None:
                    json_datas["files"].append(existing)
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
    json_datas=iterate_files_through_db()
    write_json(json_datas, db_path)

def sort_files():
    settings = read_json(settings_path)
    db_datas=iterate_files_through_db()

    to_transcode=[]
    to_copy=[]

    for f in db_datas["files"]:
        if f["status"]=="to_treat":
            print("Treating %s" % f["filepath"])

            #transcode file
            if settings["transcode_files"]:
                if not settings["transcode_only_codec"]:
                    to_transcode.append(f["filepath"])
                elif get_metadata_from_ffprobe(f["ffprobe"],"codec_name") in settings["codecs_to_transcode"]:
                    to_transcode.append(f["filepath"])
                else:
                    to_copy.append(f["filepath"])
            
            #copy files
            else:
                to_copy.append(f["filepath"])
    
    return to_transcode, to_copy

def check_error():
    # no settings
    if not os.path.isfile(settings_path):
        print("No settings file, abort")
        return True
    settings=read_json(settings_path)

    # no path to monitor/copy
    for id in ["path_to_monitor","path_to_copy"]:
        if not settings[id]:
            print("Missing %s, check settings.json, abort" % id)
            return True
        elif not os.path.isdir(settings[id]):
            print("Folder does not exist : %s, abort" % settings[id])
            return True

    # transcode and no ffmpeg_command
    if settings["transcode_files"] and not settings["ffmpeg_command"]:
        print("No ffmpeg command to transcode, check settings.json, abort")
        return True

    return False


#update_db()
lists=sort_files()
print()
print("TO TRANSCODE")
for i in lists[0]:
    print(i)
print()
print("TO COPY")
for i in lists[1]:
    print(i)