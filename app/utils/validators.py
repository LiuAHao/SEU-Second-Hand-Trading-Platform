"""
数据校验工具
用于注册、登录等表单验证
"""
import re
from typing import Optional, Tuple


class Validators:
    """数据校验工具类"""
    # 正则表达式模式
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@seu\.edu\.cn$'
    USERNAME_PATTERN = r'^[a-zA-Z0-9_]{3,16}$'
    PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$'
    PRICE_PATTERN = r'^\d+(\.\d{1,2})?$'
    @staticmethod
    def is_valid_seu_email(email: str) -> Tuple[bool, str]:
        """
        检查是否为有效的SEU邮箱 (@seu.edu.cn)
        
        Args:
            email: 邮箱地址
            
        Returns:
            (是否有效, 错误信息)
        """
        if not email or not isinstance(email, str):
            return False, "邮箱不能为空"
        
        # 基本邮箱格式验证
        if '@' not in email or '.' not in email:
            return False, "邮箱格式不正确"
        
        # SEU邮箱域名验证
        if not re.match(Validators.EMAIL_PATTERN, email):
            return False, "请输入有效的SEU邮箱 (@seu.edu.cn)"
        
        # 长度验证
        if len(email) > 100:
            return False, "邮箱地址过长"
        
        # 额外的格式检查
        local_part = email.split('@')[0]
        if not local_part:
            return False, "邮箱用户名不能为空"
        
        # 检查是否有连续的点或特殊字符
        if '..' in local_part or local_part.startswith('.') or local_part.endswith('.'):
            return False, "邮箱用户名格式不正确"
        
        return True, "邮箱验证通过"
    
    @staticmethod
    def is_valid_username(username: str) -> Tuple[bool, str]:
        """
        检查用户名有效性
        要求: 3-16字符，仅字母数字下划线，不能以下划线开头或结尾
        
        Args:
            username: 用户名
            
        Returns:
            (是否有效, 错误信息)
        """
        if not username or not isinstance(username, str):
            return False, "用户名不能为空"
        
        # 去除首尾空格
        username = username.strip()
        
        # 长度检查
        if len(username) < 3:
            return False, "用户名至少需要3个字符"
        if len(username) > 16:
            return False, "用户名不能超过16个字符"
        
        # 格式检查
        if not re.match(Validators.USERNAME_PATTERN, username):
            return False, "用户名只能包含字母、数字和下划线"
        
        # 检查是否以下划线开头或结尾
        if username.startswith('_') or username.endswith('_'):
            return False, "用户名不能以下划线开头或结尾"
        
        # 检查连续下划线
        if '__' in username:
            return False, "用户名不能包含连续的下划线"
        
        # 检查是否为保留用户名
        reserved_names = ['admin', 'administrator', 'root', 'system', 'test', 
                         'user', 'null', 'undefined', 'seu', 'seuedu']
        if username.lower() in reserved_names:
            return False, "该用户名不可用"
        
        # 检查是否只包含数字
        if username.isdigit():
            return False, "用户名不能只包含数字"
        
        return True, "用户名验证通过"
    
    @staticmethod
    def is_valid_password(password: str) -> Tuple[bool, str]:
        """
        检查密码有效性
        要求: 8+ 字符，包含大小写字母和数字，可选特殊字符
        
        Args:
            password: 密码
            
        Returns:
            (是否有效, 错误信息)
        """
        if not password or not isinstance(password, str):
            return False, "密码不能为空"
        
        # 长度检查
        if len(password) < 8:
            return False, "密码至少需要8个字符"
        if len(password) > 50:
            return False, "密码不能超过50个字符"
        
        # 强度检查
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not has_lowercase:
            return False, "密码必须包含至少一个小写字母"
        if not has_uppercase:
            return False, "密码必须包含至少一个大写字母"
        if not has_digit:
            return False, "密码必须包含至少一个数字"
        
        # 检查常用弱密码
        weak_passwords = [
            'password', '123456', 'qwerty', 'admin', 'welcome',
            'seu123456', 'seueducn', 'password123'
        ]
        if password.lower() in weak_passwords:
            return False, "密码过于简单，请使用更复杂的密码"
        
        # 检查连续字符或重复字符
        if Validators._has_sequential_chars(password):
            return False, "密码不能包含连续的字符"
        
        # 检查键盘连续序列
        keyboard_sequences = [
            'qwerty', 'asdfgh', 'zxcvbn',
            '123456', 'abcdef'
        ]
        for seq in keyboard_sequences:
            if seq in password.lower():
                return False, "密码包含常见的键盘序列"
        
        return True, "密码验证通过"
    
    @staticmethod
    def is_valid_price(price, min_price=0.01, max_price=100000) -> Tuple[bool, str]:
        """
        检查价格有效性
        
        Args:
            price: 价格（可以是字符串、整数或浮点数）
            min_price: 最小价格，默认0.01
            max_price: 最大价格，默认100000
            
        Returns:
            (是否有效, 错误信息)
        """
        if price is None:
            return False, "价格不能为空"
        
        # 转换为字符串处理
        price_str = str(price)
        
        # 检查是否为空
        if not price_str.strip():
            return False, "价格不能为空"
        
        # 格式检查
        if not re.match(Validators.PRICE_PATTERN, price_str):
            return False, "价格格式不正确，最多保留两位小数"
        
        try:
            price_float = float(price_str)
        except ValueError:
            return False, "价格必须是有效的数字"
        
        # 范围检查
        if price_float < min_price:
            return False, f"价格不能低于{min_price}"
        if price_float > max_price:
            return False, f"价格不能超过{max_price}"
        
        # 检查异常值
        if price_float == 0:
            return False, "价格不能为0"
        
        return True, "价格验证通过"
    
    @staticmethod
    def is_valid_title(title: str, min_length=2, max_length=100) -> Tuple[bool, str]:
        """
        检查商品标题有效性
        
        Args:
            title: 商品标题
            min_length: 最小长度，默认2
            max_length: 最大长度，默认100
            
        Returns:
            (是否有效, 错误信息)
        """
        if not title or not isinstance(title, str):
            return False, "标题不能为空"
        
        # 去除首尾空格
        title = title.strip()
        
        # 长度检查
        if len(title) < min_length:
            return False, f"标题至少需要{min_length}个字符"
        if len(title) > max_length:
            return False, f"标题不能超过{max_length}个字符"
        
        # 检查是否包含非法字符
        illegal_chars = ['<', '>', '&', '"', "'", '\\', '/', ';', 
                        '\u0000', '\u0001', '\u0002', '\u0003']  # 控制字符
        for char in illegal_chars:
            if char in title:
                return False, "标题包含非法字符"
        
        # 检查重复空格
        if '  ' in title:
            return False, "标题不能包含连续的空格"
        
        # 检查是否为纯空格或特殊字符
        if title.isspace():
            return False, "标题不能只包含空格"
        
        # 检查标题内容合理性（可选）
        if len(set(title)) == 1:  # 所有字符都相同
            return False, "标题不能只包含重复的字符"
        
        return True, "标题验证通过"
    
    @staticmethod
    def is_valid_description(description: str, min_length=10, max_length=2000) -> Tuple[bool, str]:
        """
        检查商品描述有效性
        
        Args:
            description: 商品描述
            min_length: 最小长度，默认10
            max_length: 最大长度，默认2000
            
        Returns:
            (是否有效, 错误信息)
        """
        if description is None:
            return False, "描述不能为空"
        
        if not isinstance(description, str):
            return False, "描述必须是字符串"
        
        # 去除首尾空格
        description = description.strip()
        
        # 长度检查
        if len(description) < min_length:
            return False, f"描述至少需要{min_length}个字符"
        if len(description) > max_length:
            return False, f"描述不能超过{max_length}个字符"
        
        # 检查是否包含非法字符（HTML标签等）
        html_pattern = r'<[^>]+>'
        if re.search(html_pattern, description):
            return False, "描述不能包含HTML标签"
        
        # 检查是否包含脚本标签
        script_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'onclick=',
            r'onload=',
            r'onerror='
        ]
        for pattern in script_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return False, "描述包含不安全的内容"
        
        # 检查是否为纯空格
        if description.isspace():
            return False, "描述不能只包含空格"
        
        # 检查内容重复性（防止垃圾信息）
        words = description.split()
        if len(words) > 10:
            # 检查是否有过多重复的词语
            word_counts = {}
            for word in words:
                if len(word) > 2:  # 只统计长度大于2的词
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # 如果有词语出现次数过多，可能是垃圾信息
            for word, count in word_counts.items():
                if count > 10:
                    return False, "描述包含过多重复内容"
        
        return True, "描述验证通过"
    
    @staticmethod
    def is_valid_phone(phone: str) -> Tuple[bool, str]:
        """
        检查手机号有效性（中国手机号）
        
        Args:
            phone: 手机号
            
        Returns:
            (是否有效, 错误信息)
        """
        if not phone or not isinstance(phone, str):
            return False, "手机号不能为空"
        
        phone = phone.strip()
        
        # 中国手机号正则：1开头，第二位3-9，总共11位
        pattern = r'^1[3-9]\d{9}$'
        
        if not re.match(pattern, phone):
            return False, "请输入有效的中国手机号（11位数字）"
        
        return True, "手机号验证通过"
    
    @staticmethod
    def is_valid_user_type(user_type: str) -> Tuple[bool, str]:
        """
        检查用户类型有效性
        
        Args:
            user_type: 用户类型
            
        Returns:
            (是否有效, 错误信息)
        """
        valid_types = ['student', 'teacher', 'staff', 'alumni']
        
        if not user_type or not isinstance(user_type, str):
            return False, "用户类型不能为空"
        
        if user_type.lower() not in valid_types:
            return False, f"用户类型必须是以下之一: {', '.join(valid_types)}"
        
        return True, "用户类型验证通过"
    
    @staticmethod
    def is_valid_item_category(category: str) -> Tuple[bool, str]:
        """
        检查商品分类有效性
        
        Args:
            category: 商品分类
            
        Returns:
            (是否有效, 错误信息)
        """
        # 常见的二手商品分类
        valid_categories = [
            'books', 'electronics', 'clothing', 'furniture',
            'sports', 'daily', 'others', 'academic'
        ]
        
        if not category or not isinstance(category, str):
            return False, "商品分类不能为空"
        
        if category.lower() not in valid_categories:
            return False, f"商品分类必须是以下之一: {', '.join(valid_categories)}"
        
        return True, "商品分类验证通过"
    
    @staticmethod
    def is_valid_item_status(status: str) -> Tuple[bool, str]:
        """
        检查商品状态有效性
        
        Args:
            status: 商品状态
            
        Returns:
            (是否有效, 错误信息)
        """
        valid_statuses = ['available', 'sold', 'reserved', 'pending']
        
        if not status or not isinstance(status, str):
            return False, "商品状态不能为空"
        
        if status.lower() not in valid_statuses:
            return False, f"商品状态必须是以下之一: {', '.join(valid_statuses)}"
        
        return True, "商品状态验证通过"
    
    # 辅助方法
    @staticmethod
    def _has_sequential_chars(password: str) -> bool:
        """检查密码是否包含连续字符"""
        for i in range(len(password) - 2):
            # 检查数字连续
            if password[i:i+3].isdigit():
                nums = [int(c) for c in password[i:i+3]]
                if nums == sorted(nums) and all(nums[j+1] - nums[j] == 1 for j in range(2)):
                    return True
        
        return False
    
    @staticmethod
    def validate_register_data(data: dict) -> dict:
        """
        验证注册数据
        
        Args:
            data: 包含注册信息的字典
            
        Returns:
            包含验证结果的字典
        """
        errors = {}
        
        # 用户名验证
        if 'username' in data:
            is_valid, msg = Validators.is_valid_username(data['username'])
            if not is_valid:
                errors['username'] = msg
        
        # 邮箱验证
        if 'email' in data:
            is_valid, msg = Validators.is_valid_seu_email(data['email'])
            if not is_valid:
                errors['email'] = msg
        
        # 密码验证
        if 'password' in data:
            is_valid, msg = Validators.is_valid_password(data['password'])
            if not is_valid:
                errors['password'] = msg
        
        # 用户类型验证（可选）
        if 'user_type' in data:
            is_valid, msg = Validators.is_valid_user_type(data['user_type'])
            if not is_valid:
                errors['user_type'] = msg
        
        # 手机号验证（可选）
        if 'phone' in data:
            is_valid, msg = Validators.is_valid_phone(data['phone'])
            if not is_valid:
                errors['phone'] = msg
        
        return errors
    
    @staticmethod
    def validate_item_data(data: dict) -> dict:
        """
        验证商品数据
        
        Args:
            data: 包含商品信息的字典
            
        Returns:
            包含验证结果的字典
        """
        errors = {}
        
        # 标题验证
        if 'title' in data:
            is_valid, msg = Validators.is_valid_title(data['title'])
            if not is_valid:
                errors['title'] = msg
        
        # 描述验证
        if 'description' in data:
            is_valid, msg = Validators.is_valid_description(data['description'])
            if not is_valid:
                errors['description'] = msg
        
        # 价格验证
        if 'price' in data:
            is_valid, msg = Validators.is_valid_price(data['price'])
            if not is_valid:
                errors['price'] = msg
        
        # 分类验证
        if 'category' in data:
            is_valid, msg = Validators.is_valid_item_category(data['category'])
            if not is_valid:
                errors['category'] = msg
        
        # 状态验证（可选）
        if 'status' in data:
            is_valid, msg = Validators.is_valid_item_status(data['status'])
            if not is_valid:
                errors['status'] = msg
        
        return errors
    
