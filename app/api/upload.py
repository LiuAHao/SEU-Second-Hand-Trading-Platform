"""文件上传接口（本地存储）"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from app.utils.response import APIResponse
from app.middleware.auth_middleware import auth_required

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_MIMETYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def _allowed_file(mimetype: str, filename: str) -> bool:
    ext = os.path.splitext(filename.lower())[1]
    return mimetype in ALLOWED_MIMETYPES and ext in ALLOWED_EXTENSIONS


@upload_bp.route('/image', methods=['POST'])
@auth_required
def upload_image():
    """上传图片到本地 static/uploads，支持区分商品/头像存储路径"""
    file = request.files.get('file')
    if not file:
        return APIResponse.validation_error({'file': '缺少文件'})

    if not _allowed_file(file.mimetype, file.filename):
        return APIResponse.validation_error({'file': '仅支持 jpg/jpeg/png/webp 图片'})

    # 目标类别：item（商品）/ avatar（头像）
    file_type = (request.form.get('type') or 'item').lower()
    if file_type not in {'item', 'avatar'}:
        return APIResponse.validation_error({'type': 'type 只能是 item 或 avatar'})

    # 生成保存路径：static/uploads/{items|avatars}/{user_id}/{yyyyMMdd}/uuid.ext
    from flask import g
    user_id = getattr(g, 'user_id', None) or 'anonymous'

    date_str = datetime.utcnow().strftime('%Y%m%d')
    category_folder = 'items' if file_type == 'item' else 'avatars'
    upload_root = os.path.join(current_app.root_path, 'static', 'uploads', category_folder, str(user_id), date_str)
    os.makedirs(upload_root, exist_ok=True)

    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(upload_root, filename)

    try:
        file.save(save_path)
    except Exception as exc:  # noqa
        return APIResponse.server_error(message='文件保存失败', errors={'detail': str(exc)})

    # 返回前端可访问的相对路径
    url = f"/static/uploads/{category_folder}/{user_id}/{date_str}/{filename}"
    return APIResponse.success(data={'url': url}, message='上传成功')
