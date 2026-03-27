import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from cv_processor import process_cv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super_secret_key_123")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "cv_file" not in request.files:
            flash("Dosya seçilmedi.", "danger")
            return redirect(request.url)
        
        file = request.files["cv_file"]
        if file.filename == "":
            flash("Dosya seçilmedi.", "danger")
            return redirect(request.url)
            
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            
            try:
                # Process the CV
                result = process_cv(filepath)
                return render_template("index.html", result=result)
            except Exception as e:
                flash(f"Hata oluştu: {str(e)}", "danger")
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
            return redirect(url_for("index"))
        else:
            flash("Lütfen sadece PDF dosyası yükleyin.", "danger")
            
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
