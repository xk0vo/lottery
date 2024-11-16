from flask import Blueprint, g, render_template, request
from .auth import login_required
import datetime

bp = Blueprint("lottery", __name__, url_prefix="/")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/lottery/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        return ""
    else:
        now = datetime.datetime.now()
        return render_template(
            "create_lottery.html",
            dat=f'{now.strftime("%Y-%m-%d")}',
            tim=f'{now.strftime("%H:%M")}',
        )
