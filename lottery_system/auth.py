from flask import Blueprint, g, request

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        return ''
    else:
        return 'Register'

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        return ''
    else:
        return 'login'

@bp.route('/logout')
def logout():
    return 'logout'
