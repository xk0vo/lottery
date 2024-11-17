import os
import json
import random
import time
import dateutil
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
            # 已结束
            past.append(lottery)
        elif lottery["begin"] > now:
            # 未开始
            comi.append(lottery)
        else:
            # 进行中
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
        # 获取表单数据
        form = request.form.to_dict()
        if int(form["participator"]) <= 0:
            now = datetime.datetime.now()
            new = datetime.datetime.fromtimestamp(time.time() + 86400)
            return render_template(
                "create_lottery.html",
                dat=f'{now.strftime("%Y-%m-%d")}',
                datt=f'{new.strftime("%Y-%m-%d")}',
                tim=f'{now.strftime("%H:%M")}',
                message=["参与人数应大于0"],
            )
        awards = []
        for k in form:
            # 奖品id
            if k.startswith("rewardcnt"):
                awards.append(k[9:])
        if not awards:  # 奖品不能为空
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
        try:
            entry["begin"] = parse(
                f"{form['begin_date']} {form['begin_time']}"
            ).timestamp()
            entry["end"] = parse(f"{form['end_date']} {form['end_time']}").timestamp()
        except dateutil.parser._parser.ParserError as e:
            # 日期格式错误
            now = datetime.datetime.now()
            new = datetime.datetime.fromtimestamp(time.time() + 86400)
            return render_template(
                "create_lottery.html",
                dat=f'{now.strftime("%Y-%m-%d")}',
                datt=f'{new.strftime("%Y-%m-%d")}',
                tim=f'{now.strftime("%H:%M")}',
                message=[e.args[0] % e.args[1]],
            )
        entry["participator"] = int(form["participator"])
        for i in awards:
            award = [
                form[f"reward{i}"],  # 奖品名称
                int(form[f"rewardcnt{i}"]),  # 奖品数量
                int(form[f"rewardcnt{i}"]),  # 奖品剩余数量
            ]
            entry["rewards"][i] = award
        lotes["lotteries"].append(entry)  # 添加抽奖活动
        lotes["id"] += 1  # 更新id
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
    enable = True  # 是否可以参与
    info = os.path.join(".", "lotteries", f"{lid}.json")
    with open("lotteries.json", "r") as f:
        lotes = json.load(f)
    lot = None
    for lottery in lotes["lotteries"]:
        if lottery["id"] == lid:
            lot = lottery
    if not lot:
        return abort(404)  # 未找到抽奖活动
    if f"{lid}.json" not in os.listdir("lotteries"):
        with open(info, "w") as f:
            d = {"participator": [], "results": {}}  # 参与者，结果
            for i in lot["rewards"]:
                d["results"][i] = []
            json.dump(d, f)  # 写入结果
        results = None
        award = None
    else:
        award = None
        with open(info, "r") as f:
            results = json.load(f)
        for i in results["results"]:
            for p in results["results"][i]:
                if p[0] == session.get("user_id", None):
                    # 已中奖
                    award = lot["rewards"][i][0]
                    break
    b = datetime.datetime.fromtimestamp(lot["begin"]).strftime("%Y-%m-%d %H:%M:%S")
    # 开始时间
    e = datetime.datetime.fromtimestamp(lot["end"]).strftime("%Y-%m-%d %H:%M:%S")
    # 结束时间
    if lot["begin"] < time.time() < lot["end"]:
        if results:
            if session.get("user_id", None) in results["participator"]:
                # 已参与
                enable = False
            else:
                if len(results["participator"]) < lot["participator"]:  # 参与人数未满
                    rewards = []
                    reward_keys = []
                    for i in lot["rewards"]:
                        reward_keys.append(i)
                        # 奖品id
                    for k in reward_keys:
                        for i in range(lot["rewards"][k][1]):
                            rewards.append(k)
                            # 奖品id
                    if rewards:  # 奖品不为空
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
        p=len(results["participator"]) if results else 0,
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
            d = {"participator": [], "results": {}}
            for i in lot["rewards"]:
                d["results"][i] = []
            json.dump(d, f)
        results = None
    else:
        with open(info, "r") as f:
            results = json.load(f)
    reward_keys = []
    for i in lot["rewards"]:
        reward_keys.append(i)  # 奖品id
    if lot["begin"] < time.time() < lot["end"]:
        if results:
            if session.get("user_id", None) not in results["participator"]:  # 未参与
                if len(results["participator"]) < lot["participator"]:  # 参与人数未满
                    rewards = []
                    for k in reward_keys:
                        for i in range(lot["rewards"][k][1]):
                            rewards.append(k)  # 奖品id
                    choice = random.choice(rewards)  # 随机选择奖品
                    lot["rewards"][choice][1] -= 1  # 奖品数量减1
                    results["participator"].append(session.get("user_id"))  # 添加参与者
                    results["results"][choice].append(
                        [
                            session.get("user_id"),  # 用户名
                            datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),  # 时间
                        ]
                    )
                    with open(info, "w") as f:
                        json.dump(results, f)  # 写入结果
                    with open("lotteries.json", "w") as f:
                        lotes["lotteries"][lotid] = lot  # 更新奖品数量
                        json.dump(lotes, f)
    return redirect(f"/lottery/{lid}")  # 重定向到抽奖页面
