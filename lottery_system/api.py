from flask import Blueprint, request, send_file
import qrcode
import io
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/qrcode/<int:lid>')
def qr(lid):
    # https://github.com/lincolnloop/python-qrcode?tab=readme-ov-file#usage
    img = qrcode.make(f'http://{request.host}/lottery/{lid}')
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
