"""
密码加密与验证工具
使用bcrypt进行安全加密
"""


class PasswordHelper:
    """密码加密与验证"""
    
    @staticmethod
    def hash_password(password):
        """
        加密密码，返回bcrypt哈希
        """
        import bcrypt
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed):
        """
        验证密码是否匹配bcrypt哈希
        """
        import bcrypt
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
        return bcrypt.checkpw(password, hashed)
