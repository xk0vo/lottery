from flask import Blueprint, g, render_template

bp = Blueprint('lottery', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('index.html')
