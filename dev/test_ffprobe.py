file = r""

import subprocess
import shlex
import json

# function to find the resolution of the input video file
def get_ffprobe_output(pathToInputVideo):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)
    return ffprobeOutput

def get_metadata_from_ffprobe(ffprobe_output, metadata_id):
    return ffprobe_output['streams'][0][metadata_id]

ffp = get_ffprobe_output(file)
print(get_metadata(ffp, "codec_name"))