from flask import Flask, render_template, request
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files["image"]

    if not file:
        return "No file selected"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    img = Image.open(filepath)
    exif_data = img.getexif()

    metadata = {}

    if exif_data:
        for tag_id, value in exif_data.items():

            tag = TAGS.get(tag_id, tag_id)

            if isinstance(tag, int):
                continue

            if isinstance(value, bytes):
                continue

            metadata[tag] = value

    with open(filepath, "rb") as f:
        file_data = f.read()

    md5_hash = hashlib.md5(file_data).hexdigest()
    sha256_hash = hashlib.sha256(file_data).hexdigest()

    summary = []

    if "Software" in metadata:
        summary.append(f"⚠️ Image may have been edited using: {metadata['Software']}")
    else:
        summary.append("✅ No editing software information found")

    if "GPSInfo" in metadata:
        summary.append("📍 GPS metadata is present")
    else:
        summary.append("⚠️ GPS metadata not available")

    if "DateTimeOriginal" in metadata:
        summary.append(f"📅 Captured on: {metadata['DateTimeOriginal']}")
    else:
        summary.append("⚠️ Original capture date not found")

    return f"""
    <h1>Image Forensic Analysis Report</h1>

    <h3>File Information</h3>

    <p><strong>File Name:</strong> {file.filename}</p>

    <p><strong>MD5:</strong> {md5_hash}</p>

    <p><strong>SHA-256:</strong> {sha256_hash}</p>

    <h3>Metadata</h3>

    <pre>{metadata}</pre>

    <h3>Forensic Summary</h3>

    <ul>
        {''.join([f'<li>{item}</li>' for item in summary])}
    </ul>

    <br>

    <a href="/">Analyze Another Image</a>
    """


if __name__ == "__main__":
    app.run(debug=True)