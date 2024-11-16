import os
import json
import random
import time
from flask import Blueprint, redirect, render_template, request, session, abort
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
            award = [
                form[f"reward{i}"],
                int(form[f"rewardcnt{i}"]),
                int(form[f"rewardcnt{i}"]),
            ]
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
    enable = True
    info = os.path.join(".", "lotteries", f"{lid}.json")
    with open("lotteries.json", "r") as f:
        lotes = json.load(f)
    lot = None
    for lottery in lotes["lotteries"]:
        if lottery["id"] == lid:
            lot = lottery
    if not lot:
        return abort(404)
    if f"{lid}.json" not in os.listdir("lotteries"):
        with open(info, "w") as f:
            d = {"particaiptor": [], "results": {}}
            for i in lot["rewards"]:
                d["results"][i] = []
            json.dump(d, f)
        results = None
        award = None
    else:
        award = None
        with open(info, "r") as f:
            results = json.load(f)
        for i in results["results"]:
            for p in results["results"][i]:
                if p[0] == session.get("user_id", None):
                    award = lot["rewards"][i][0]
                    break
    b = datetime.datetime.fromtimestamp(lot["begin"]).strftime("%Y-%m-%d %H:%M:%S")
    e = datetime.datetime.fromtimestamp(lot["end"]).strftime("%Y-%m-%d %H:%M:%S")
    if lot["begin"] < time.time() < lot["end"]:
        if results:
            if session.get("user_id", None) in results["particaiptor"]:
                enable = False
            else:
                if len(results["particaiptor"]) < lot["participator"]:
                    rewards = []
                    reward_keys = []
                    for i in lot["rewards"]:
                        reward_keys.append(i)
                    for k in reward_keys:
                        for i in range(lot["rewards"][k][1]):
                            rewards.append(k)
                    if rewards:
                        enable = True
                    else:
                        enable = False
                else:
                    enable = False
    else:
        enable = False
    return render_template(
        "lottery.html",
        lottery=lot,
        begin=b,
        end=e,
        enable=enable,
        award=award,
        results=results,
        p=len(results["particaiptor"]) if results else 0
    )


@bp.route("/lottery/<int:lid>/draw")
@login_required
def draw(lid):
    info = os.path.join(".", "lotteries", f"{lid}.json")
    with open("lotteries.json", "r") as f:
        lotes = json.load(f)
    lot = None
    lotid = 0
    for lottery in lotes["lotteries"]:
        if lottery["id"] == lid:
            lot = lottery
            break
        lotid += 1
    if not lot:
        return abort(404)
    if f"{lid}.json" not in os.listdir("lotteries"):
        with open(info, "w") as f:
            d = {"particaiptor": [], "results": {}}
            for i in lot['rewards']:
                d['results'][i] = []
            json.dump(d, f)
        results = None
    else:
        with open(info, "r") as f:
            results = json.load(f)
    reward_keys = []
    for i in lot["rewards"]:
        reward_keys.append(i)

    if lot["begin"] < time.time() < lot["end"]:
        if results:
            if session.get("user_id", None) not in results["particaiptor"]:
                if len(results["particaiptor"]) < lot["participator"]:
                    rewards = []
                    for k in reward_keys:
                        for i in range(lot["rewards"][k][1]):
                            rewards.append(k)
                    choice = random.choice(rewards)
                    lot["rewards"][choice][1] -= 1
                    results["particaiptor"].append(session.get("user_id"))
                    results["results"][choice].append(
                        [
                            session.get("user_id"),
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ]
                    )
                    with open(info, "w") as f:
                        json.dump(results, f)
                    with open("lotteries.json", "w") as f:
                        lotes["lotteries"][lotid] = lot
                        json.dump(lotes, f)
    return redirect(f"/lottery/{lid}")
