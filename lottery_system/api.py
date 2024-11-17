import json
import os
from flask import Blueprint, abort, request, send_file
import qrcode
import io

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/qrcode/<int:lid>")
def qr(lid):
    # https://github.com/lincolnloop/python-qrcode?tab=readme-ov-file#usage
    img = qrcode.make(f"http://{request.host}/lottery/{lid}")
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@bp.route("/export/<int:lid>")
def export(lid):
    info = os.path.join(".", "lotteries", f"{lid}.json")
    with open("lotteries.json", "r") as f:
        lotes = json.load(f)
    lot = None
    lotid = 0
    # 查找抽奖活动
    for lottery in lotes["lotteries"]:
        if lottery["id"] == lid:
            lot = lottery
            break
        lotid += 1
    if not lot:
        # 未找到抽奖活动
        return abort(404)
    with open(info, "r") as f:
        results = json.load(f)
    data = [["用户名", "时间", "奖品"]]
    for k in results["results"]:
        # k: 奖品id
        v = lot["rewards"][k][0]
        # v: 奖品名称
        for user in results["results"][k]:
            data.append([user[0], user[1], v])
    f = "\n".join([",".join(i) for i in data])
    buf = io.BytesIO()
    buf.write(f.encode(encoding="gbk"))  # 防止中文乱码
    buf.seek(0)
    return send_file(buf, mimetype="text/csv")
