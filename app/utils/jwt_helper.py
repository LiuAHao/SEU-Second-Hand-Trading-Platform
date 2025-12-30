"""
JWT Token 管理
用于用户认证和会话管理
"""



import jwt
from datetime import datetime, timedelta
from flask import current_app

SECRET_KEY = 'jwt-secret-key'  # 可从配置读取
ALGORITHM = 'HS256'
EXPIRES_DAYS = 7

def generate_token(user_id):
    """
    生成JWT Token
    :param user_id: int
    :return: token字符串
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=EXPIRES_DAYS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_token(token):
    """
    验证Token
    :param token: str
    :return: payload字典 或 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def refresh_token(token):
    """
    刷新Token
    :param token: str
    :return: 新token
    """
    payload = verify_token(token)
    if not payload or 'user_id' not in payload:
        return None
    return generate_token(payload['user_id'])

