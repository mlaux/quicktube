from flask import Flask

app = Flask(__name__)

@app.route("/video/<id>")
def get_video(id):
    return render_template('template.html', video_id=id)
