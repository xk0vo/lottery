import functools
from flask import (
    Blueprint,
    flash,
    g,
    get_flashed_messages,
    request,
    render_template,
    session,
    redirect,
    url_for,
)
import json
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    with open("users.json", "r") as f:
        users = json.load(f)
    if request.method == "POST":
        # 校验用户名
        username, password = request.form["username"], request.form["password"]
        if username in [i["username"] for i in users["users"]]:
            return render_template(
                "login_register.html", text="register", error_username="用户名已存在"
            )
        # hash密码
        # generate_password_hash() is used to securely hash the password, and that hash is stored.
        # https://flask.palletsprojects.com/en/stable/tutorial/views/
        passwdhash = generate_password_hash(password)
        users["users"].append({"username": username, "password": passwdhash})
        session.clear()
        # 登录
        session["user_id"] = username
        # 写入用户信息
        with open("users.json", "w") as f:
            json.dump(users, f)
        return redirect("/")
    else:
        # 渲染注册页面
        return render_template("login_register.html", text="register")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        with open("users.json", "r") as f:
            users = json.load(f)
        username, password = request.form["username"], request.form["password"]
        if username not in [i["username"] for i in users["users"]]:
            return render_template(
                "login_register.html", text="login", error_username="用户名或密码错误"
            )
        for user in users["users"]:
            if user["username"] == username:
                if check_password_hash(user["password"], password):
                    session.clear()
                    # 登录
                    session["user_id"] = username
                    return redirect("/")
        return render_template(
            "login_register.html", text="login", error_username="用户名或密码错误"
        )
    else:
        message = get_flashed_messages()
        return render_template("login_register.html", text="login", message=message)


# https://flask.palletsprojects.com/en/stable/tutorial/views/#require-authentication-in-other-views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("请先登录")
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


@bp.route("/logout")
@login_required
def logout():
    # 注销
    session.clear()
    return redirect("/")
