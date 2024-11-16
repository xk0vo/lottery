from flask import Flask
import os
# 创建users.json用于存储用户信息
if 'users.json' not in os.listdir():
    with open('users.json', 'w') as f:
        f.write('{"users": []}')
if 'lotteries.json' not in os.listdir():
    with open('lotteries.json', 'w') as f:
        f.write('{"lotteries": [], "id": 0}')

def create_app():
    app = Flask(__name__)
    app.secret_key = '2024040113_3e4ad72baa24deb4ff7d093cfcace6665a83cc406cc960c9'
    from . import auth, lottery
    # 注册蓝图
    app.register_blueprint(auth.bp)
    app.register_blueprint(lottery.bp)
    return app
