from flask import Flask, render_template
import os
import binascii

app = Flask(__name__)

@app.route("/video/<id>")
def get_video(id):
    nocache_id = binascii.b2a_hex(os.urandom(4)).decode('utf-8')
    return render_template('video.html', video_id=id, nocache_id=nocache_id)
