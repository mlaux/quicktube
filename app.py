from flask import Flask, render_template

app = Flask(__name__)

@app.route("/video/<id>")
def get_video(id):
    return render_template('video.html', video_id=id)
