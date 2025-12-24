"""
密码加密与验证工具
使用bcrypt进行安全加密
"""


class PasswordHelper:
    """密码加密与验证"""
    
    @staticmethod
    def hash_password(password):
        """
        加密密码
        TODO: 使用bcrypt进行密码加密
        - 成本因子：12
        - 返回哈希值字符串
        """
        pass
    
    @staticmethod
    def verify_password(password, hashed):
        """
        验证密码
        TODO: 使用bcrypt验证密码是否匹配
        - 返回True或False
        """
        pass
