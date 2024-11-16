import json
import time
from flask import Blueprint, g, redirect, render_template, request, session
from .auth import login_required
import datetime
from dateutil.parser import parse

bp = Blueprint("lottery", __name__, url_prefix="/")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/lottery/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        with open("lotteries.json", "r") as f:
            lotes = json.load(f)
        form = request.form.to_dict()
        awards = []
        for k in form:
            if k.startswith("rewardcnt"):
                awards.append(k[9:])
        entry = {"uid": session.get("user_id"), "id": lotes["id"], "rewards": []}
        entry["begin"] = parse(f"{form['begin_date']} {form['begin_time']}").timestamp()
        entry["end"] = parse(f"{form['end_date']} {form['end_time']}").timestamp()
        entry["participator"] = int(form["participator"])
        for i in awards:
            award = [form[f"reward{i}"], form[f"rewardcnt{i}"]]
            entry["rewards"].append(award)
        lotes["lotteries"].append(entry)
        lotes["id"] += 1
        with open("lotteries.json", "w") as f:
            json.dump(lotes, f)
        return redirect("/")
    else:
        now = datetime.datetime.now()
        new = datetime.datetime.fromtimestamp(time.time() + 86400)
        return render_template(
            "create_lottery.html",
            dat=f'{now.strftime("%Y-%m-%d")}',
            datt=f'{new.strftime("%Y-%m-%d")}',
            tim=f'{now.strftime("%H:%M")}',
        )
