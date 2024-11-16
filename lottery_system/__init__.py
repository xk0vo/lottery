from flask import Flask
import os

listdir = os.listdir()
# 创建users.json用于存储用户信息
if "users.json" not in listdir:
    with open("users.json", "w") as f:
        f.write('{"users": []}')
if "lotteries.json" not in listdir:
    with open("lotteries.json", "w") as f:
        f.write('{"lotteries": [], "id": 0}')
if "lotteries" not in listdir:
    os.mkdir("lotteries")


def create_app():
    app = Flask(__name__)
    app.secret_key = "2024040113_3e4ad72baa24deb4ff7d093cfcace6665a83cc406cc960c9"
    from . import auth, lottery, api

    # 注册蓝图
    app.register_blueprint(auth.bp)
    app.register_blueprint(lottery.bp)
    app.register_blueprint(api.bp)
    return app
