import subprocess

def convert720p(source):
    target = source + '_720p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, target)
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stderr)
