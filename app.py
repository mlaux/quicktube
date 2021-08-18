from flask import Flask, render_template
import os
import binascii


# cinepak also works and looks a little better, slightly bigger file size
# also slooooow to compress
VIDEO_CODEC = "svq1"
# pcm_s16be, pcm_u8, pcm_mulaw, adpcm_ms also work
AUDIO_CODEC = "adpcm_ms"

app = Flask(__name__)

@app.route("/video/<id>")
def get_video(id):
    nocache_id = binascii.b2a_hex(os.urandom(4)).decode('utf-8')
    return render_template('video.html', video_id=id, nocache_id=nocache_id)
