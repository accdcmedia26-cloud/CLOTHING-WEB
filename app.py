from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# SETTINGS
# =========================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect("clothing.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT NOT NULL,

            size TEXT NOT NULL,

            color TEXT NOT NULL,

            price REAL NOT NULL,

            description TEXT,

            image TEXT

        )
    """)

    conn.commit()
    conn.close()


# =========================
# CHECK IMAGE
# =========================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products
    )


# =========================
# ADD PRODUCT
# =========================

@app.route("/add_product", methods=["POST"])
def add_product():

    name = request.form.get("name")
    category = request.form.get("category")
    size = request.form.get("size")
    color = request.form.get("color")
    price = request.form.get("price")
    description = request.form.get("description")

    image_filename = ""

    image = request.files.get("image")

    if image and image.filename:

        if allowed_file(image.filename):

            image_filename = secure_filename(
                image.filename
            )

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                image_filename
            )

            image.save(image_path)

    conn = get_db()

    conn.execute("""
        INSERT INTO products
        (
            name,
            category,
            size,
            color,
            price,
            description,
            image
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        category,
        size,
        color,
        price,
        description,
        image_filename
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# =========================
# RUN WEBSITE
# =========================

if __name__ == "__main__":

    create_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )