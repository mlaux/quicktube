import binascii
import os
import subprocess

from flask import Flask, render_template, abort, request, redirect, url_for
from youtube_search import YoutubeSearch

# cinepak also works and looks a little better, slightly bigger file size
# also slooooow to compress
VIDEO_CODEC = "svq1"

# pcm_s16be, pcm_u8, pcm_mulaw, adpcm_ms also work
AUDIO_CODEC = "adpcm_ms"

app = Flask(__name__)

# youtube-dl --get-filename -o "%(id)s.%(ext)s" -f worst https://www.youtube.com/watch\?v\=7fn2eJdyVqg

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/search")
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('home'))

    results = YoutubeSearch(query, max_results=10).to_dict()
    print(results[0])

    return render_template('search.html', results=results, query=query)

@app.route("/video/<id>")
def video(id):
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

    if request.args.get('nodl', ''):
        return render_template('video.html', video_id='', nocache_id='')

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
    # TODO stream this through ffmpeg to stdout so we don't have to wait for the whole thing to convert
    # i'm pretty sure that's incompatible with "faststart" because the "moov atom" needs to be at the beginning
    # ffmpeg -i input.mp4 -c:v svq1 -c:a adpcm_ms -ar 11025 -vf "scale=-1:144, framerate=15" -movflags faststart output.mov
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
