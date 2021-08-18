from flask import Flask, render_template, abort
import os
import subprocess
import binascii


# cinepak also works and looks a little better, slightly bigger file size
# also slooooow to compress
VIDEO_CODEC = "svq1"
# pcm_s16be, pcm_u8, pcm_mulaw, adpcm_ms also work
AUDIO_CODEC = "adpcm_ms"

app = Flask(__name__)

# youtube-dl --get-filename -o "%(id)s.%(ext)s" -f worst https://www.youtube.com/watch\?v\=7fn2eJdyVqg

@app.route("/video/<id>")
def get_video(id):
    filename_result = subprocess.run(
        [
            "youtube-dl",
            "--get-filename",
            "-o",
            "%(id)s.%(ext)s",
            "-f",
            "worst",
            id
        ],
        capture_output=True,
        text=True
    )
    if not filename_result.stdout:
        abort(404)
    filename = filename_result.stdout.strip()
    
    print(f"Result: {filename}")

    # actually download it
    subprocess.run(
        [
            "youtube-dl",
            "-o",
            "%(id)s.%(ext)s",
            "-f",
            "worst",
            id
        ]
    )

    # supposedly it exists now, reencode
    # ffmpeg -i dolce.mp4 -c:v svq1 -c:a adpcm_ms -ar 11025 -vf "scale=-1:144, framerate=15" -movflags faststart dolce-svq1.mov
    converted_filename = id + ".mov"
    subprocess.run(
        [
            "ffmpeg",
            "-n", # exit if output already exists
            "-i",
            filename,
            "-c:v",
            VIDEO_CODEC,
            "-c:a",
            AUDIO_CODEC,
            "-ar",
            "11025",
            "-vf",
            "scale=-1:144, framerate=15",
            "-movflags",
            "faststart",
            "static/" + converted_filename # TODO don't hardcode static/
        ]
    )

    nocache_id = binascii.b2a_hex(os.urandom(4)).decode('utf-8')
    return render_template('video.html', video_id=converted_filename, nocache_id=nocache_id)
