import os
import tempfile
from flask import Flask, request, jsonify, send_file, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder=".", static_url_path="")


@app.route("/")
def index():
    for name in ["index.html", "HTMLPage1.html"]:
        if os.path.exists(name):
            return send_from_directory(".", name)
    return "HTML fayl topilmadi", 404


@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "Avval Instagram havolasini kiriting!"}), 400

    if "instagram.com" not in url:
        return jsonify({"error": "Faqat Instagram havolasini kiriting!"}), 400

    temp_dir = tempfile.mkdtemp(prefix="insta_dl_")
    outtmpl = os.path.join(temp_dir, "video.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4/best",
        "noplaylist": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            for f in os.listdir(temp_dir):
                filename = os.path.join(temp_dir, f)
                break

        if not os.path.exists(filename):
            return jsonify({"error": "Videoni yuklab bo‘lmadi."}), 500

        return send_file(
            filename,
            as_attachment=True,
            download_name="instagram_video.mp4",
        )
    except Exception as e:
        return jsonify({"error": f"Xatolik: {str(e)}"}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)