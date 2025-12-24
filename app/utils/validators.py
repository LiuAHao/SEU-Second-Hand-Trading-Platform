"""
数据校验工具
用于注册、登录等表单验证
"""


class Validators:
    """数据校验工具类"""
    
    @staticmethod
    def is_valid_seu_email(email):
        """检查是否为SEU邮箱 (@seu.edu.cn)"""
        # TODO: 使用正则表达式验证邮箱格式
        pass
    
    @staticmethod
    def is_valid_username(username):
        """
        检查用户名有效性
        要求: 3-16字符，仅字母数字下划线
        """
        # TODO: 使用正则表达式验证
        pass
    
    @staticmethod
    def is_valid_password(password):
        """
        检查密码有效性
        要求: 8+ 字符，包含大小写字母和数字
        """
        # TODO: 验证密码强度
        pass
    
    @staticmethod
    def is_valid_price(price):
        """检查价格有效性"""
        # TODO: 验证价格范围和格式
        pass
    
    @staticmethod
    def is_valid_title(title):
        """检查商品标题有效性"""
        # TODO: 验证标题长度
        pass
    
    @staticmethod
    def is_valid_description(description):
        """检查商品描述有效性"""
        # TODO: 验证描述长度
        pass
