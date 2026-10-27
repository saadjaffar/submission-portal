import json
import os
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for


def is_valid_url(url: str) -> bool:
    if not url or " " in url:
        return False
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def validate_submission(form: dict) -> dict:
    errors = {}
    if not form["name"]:
        errors["name"] = "Name is required."
    if not form["reg_no"]:
        errors["reg_no"] = "Registration number is required."
    if not form["title"]:
        errors["title"] = "Assignment title is required."
    if not form["url"]:
        errors["url"] = "Submission URL is required."
    elif not is_valid_url(form["url"]):
        errors["url"] = "Enter a valid URL starting with http:// or https://"
    return errors


def create_app(data_file=None):
    app = Flask(__name__)
    app.config["DATA_FILE"] = data_file or os.environ.get("DATA_FILE", "submissions.json")

    def load():
        try:
            with open(app.config["DATA_FILE"], encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(items):
        with open(app.config["DATA_FILE"], "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    @app.route("/", methods=["GET", "POST"])
    def index():
        errors, form, status = {}, {}, 200
        if request.method == "POST":
            form = {k: request.form.get(k, "").strip()
                    for k in ("name", "reg_no", "title", "url")}
            errors = validate_submission(form)
            if not errors:
                items = load()
                items.append(form)
                save(items)
                return redirect(url_for("index"))
            status = 400
        return render_template("index.html", errors=errors, form=form,
                               submissions=load()), status

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)