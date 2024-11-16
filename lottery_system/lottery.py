import json
import time
from flask import Blueprint, g, redirect, render_template, request, session, abort
from .auth import login_required
import datetime
from dateutil.parser import parse

bp = Blueprint("lottery", __name__, url_prefix="/")


@bp.route("/")
def index():
    with open("lotteries.json", "r") as f:
        lotes = json.load(f)
    past = []
    curr = []
    comi = []
    for lottery in lotes["lotteries"]:
        now = time.time()
        if lottery["end"] < now:
            past.append(lottery)
        elif lottery["begin"] > now:
            comi.append(lottery)
        else:
            curr.append(lottery)
    return render_template(
        "index.html", now_lottery=curr, coming_lottery=comi, past_lottery=past
    )


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
        if not awards:
            now = datetime.datetime.now()
            new = datetime.datetime.fromtimestamp(time.time() + 86400)
            return render_template(
                "create_lottery.html",
                dat=f'{now.strftime("%Y-%m-%d")}',
                datt=f'{new.strftime("%Y-%m-%d")}',
                tim=f'{now.strftime("%H:%M")}',
                message=["奖品不能为空"],
            )
        entry = {"uid": session.get("user_id"), "id": lotes["id"], "rewards": {}}
        entry["title"] = form["title"]
        entry["begin"] = parse(f"{form['begin_date']} {form['begin_time']}").timestamp()
        entry["end"] = parse(f"{form['end_date']} {form['end_time']}").timestamp()
        entry["participator"] = int(form["participator"])
        for i in awards:
            award = [form[f"reward{i}"], int(form[f"rewardcnt{i}"])]
            entry["rewards"][i] = award
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


@bp.route("/lottery/<int:lid>")
def view(lid):
    with open("lotteries.json", "r") as f:
        lotes = json.load(f)
    lot = None
    for lottery in lotes["lotteries"]:
        if lottery['id'] == lid:
            lot = lottery
    if not lot:
        return abort(404)
    b = datetime.datetime.fromtimestamp(lot['begin']).strftime("%Y-%m-%d %H:%M:%S")
    e = datetime.datetime.fromtimestamp(lot['end']).strftime("%Y-%m-%d %H:%M:%S")
    if lot['begin'] < time.time() < lot['end']:
        enable = True
    else:
        enable = False
    return render_template('lottery.html', lottery=lot, begin=b, end=e, enable=enable)
