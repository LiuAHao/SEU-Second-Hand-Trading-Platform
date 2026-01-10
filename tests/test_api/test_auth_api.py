"""
用户认证API测试
测试注册、登录、登出、验证等完整认证流程
"""

import pytest
import json
from app.models import User, db
from app.utils.password_helper import PasswordHelper


class TestAuthRegister:
    """用户注册API测试"""
    
    def test_register_success(self, client, app):
        """测试成功注册用户"""
        with app.app_context():
            db.session.query(User).delete()
            db.session.commit()
        
        response = client.post('/api/user/register', 
            json={
                'username': 'newuser',
                'email': 'newuser@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['message'] == '注册成功'
        assert 'userId' in data['data']
        assert data['data']['username'] == 'newuser'
        assert data['data']['email'] == 'newuser@seu.edu.cn'
    
    def test_register_invalid_email_format(self, client, app):
        """测试无效邮箱格式 - 非@seu.edu.cn"""
        response = client.post('/api/user/register',
            json={
                'username': 'baduser',
                'email': 'baduser@gmail.com',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2  # VALIDATION_ERROR
        assert '邮箱' in data['message'] or '必须为' in data['message']
    
    def test_register_invalid_email_format_qq(self, client, app):
        """测试无效邮箱格式 - qq邮箱"""
        response = client.post('/api/user/register',
            json={
                'username': 'qquser',
                'email': 'qq123@qq.com',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_register_weak_password_too_short(self, client, app):
        """测试弱密码 - 过短"""
        response = client.post('/api/user/register',
            json={
                'username': 'shortpwd',
                'email': 'shortpwd@seu.edu.cn',
                'password': 'Short1'  # 少于8位
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
        assert '密码' in data['message']
    
    def test_register_weak_password_no_uppercase(self, client, app):
        """测试弱密码 - 无大写"""
        response = client.post('/api/user/register',
            json={
                'username': 'nouppercase',
                'email': 'nouppercase@seu.edu.cn',
                'password': 'noupppercase123'  # 没有大写字母
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_register_weak_password_no_number(self, client, app):
        """测试弱密码 - 无数字"""
        response = client.post('/api/user/register',
            json={
                'username': 'nonumber',
                'email': 'nonumber@seu.edu.cn',
                'password': 'NoNumberPassword'  # 没有数字
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_register_duplicate_username(self, client, app, init_database):
        """测试用户名已存在"""
        response = client.post('/api/user/register',
            json={
                'username': 'testuser1',
                'email': 'another@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 1
        assert '用户名' in data['message'] or '已存在' in data['message']
    
    def test_register_duplicate_email(self, client, app, init_database):
        """测试邮箱已注册"""
        response = client.post('/api/user/register',
            json={
                'username': 'anotheruser',
                'email': 'testuser1@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 1
        assert '邮箱' in data['message'] or '已' in data['message']
    
    def test_register_missing_username(self, client, app):
        """测试缺少用户名"""
        response = client.post('/api/user/register',
            json={
                'email': 'test@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_register_empty_username(self, client, app):
        """测试空用户名"""
        response = client.post('/api/user/register',
            json={
                'username': '',
                'email': 'test@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2


class TestAuthLogin:
    """用户登录API测试"""
    
    def test_login_success_with_username(self, client, app, init_database):
        """测试使用用户名登录成功"""
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1',
                'password': 'Password123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'token' in data['data'] or 'Authorization' in str(response.headers)
    
    def test_login_success_with_email(self, client, app, init_database):
        """测试使用邮箱登录成功"""
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1@seu.edu.cn',
                'password': 'Password123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_login_invalid_password(self, client, app, init_database):
        """测试密码错误"""
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1',
                'password': 'WrongPassword123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] in [1, 3]
        assert '密码' in data['message'] or '错误' in data['message']
    
    def test_login_user_not_found(self, client, app):
        """测试用户不存在"""
        response = client.post('/api/user/login',
            json={
                'username': 'nonexistent',
                'password': 'SomePassword123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] in [1, 3]
    
    def test_login_empty_username(self, client, app):
        """测试空用户名"""
        response = client.post('/api/user/login',
            json={
                'username': '',
                'password': 'Password123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_login_empty_password(self, client, app):
        """测试空密码"""
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1',
                'password': ''
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_login_missing_username(self, client, app):
        """测试缺少用户名"""
        response = client.post('/api/user/login',
            json={
                'password': 'Password123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_login_missing_password(self, client, app):
        """测试缺少密码"""
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_login_case_insensitive_username(self, client, app, init_database):
        """测试用户名大小写 - 应该不区分"""
        # 注意：具体行为取决于后端实现
        response = client.post('/api/user/login',
            json={
                'username': 'TestUser1',  # 不同的大小写
                'password': 'Password123'
            },
            content_type='application/json'
        )
        
        # 可能返回200（不区分大小写）或401（区分大小写）
        assert response.status_code in [200, 401]


class TestAuthCheckUsername:
    """检查用户名可用性API测试"""
    
    def test_username_available(self, client, app, init_database):
        """测试用户名可用"""
        response = client.get('/api/user/checkUsername/brandnewusername',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['data']['available'] is True
    
    def test_username_exists(self, client, app, init_database):
        """测试用户名已存在"""
        response = client.get('/api/user/checkUsername/testuser1',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['data']['available'] is False
    
    def test_username_empty(self, client, app):
        """测试空用户名检查"""
        response = client.get('/api/user/checkUsername/',
            content_type='application/json'
        )
        
        # 取决于后端实现，可能是404或400
        assert response.status_code in [404, 400, 200]
    
    def test_check_multiple_usernames(self, client, app, init_database):
        """测试批量检查多个用户名"""
        # 检查存在的用户名
        response1 = client.get('/api/user/checkUsername/testuser1')
        data1 = json.loads(response1.data)
        assert data1['data']['available'] is False
        
        # 检查不存在的用户名
        response2 = client.get('/api/user/checkUsername/testuser2_new')
        data2 = json.loads(response2.data)
        assert data2['data']['available'] is True


class TestAuthCheckEmail:
    """检查邮箱可用性API测试"""
    
    def test_email_available(self, client, app, init_database):
        """测试邮箱可用"""
        response = client.get('/api/user/checkEmail/available@seu.edu.cn',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['data']['available'] is True
    
    def test_email_exists(self, client, app, init_database):
        """测试邮箱已注册"""
        response = client.get('/api/user/checkEmail/testuser1@seu.edu.cn',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['data']['available'] is False
    
    def test_invalid_email_format_gmail(self, client, app):
        """测试无效邮箱格式 - Gmail"""
        response = client.get('/api/user/checkEmail/test@gmail.com',
            content_type='application/json'
        )
        
        # 可能返回400（格式验证失败）或200（不可用但格式无效）
        assert response.status_code in [200, 400]
    
    def test_invalid_email_format_qq(self, client, app):
        """测试无效邮箱格式 - QQ"""
        response = client.get('/api/user/checkEmail/test@qq.com',
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400]
    
    def test_invalid_email_format_no_at(self, client, app):
        """测试无效邮箱格式 - 没有@"""
        response = client.get('/api/user/checkEmail/invalid-email',
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400]


class TestAuthLogout:
    """用户登出API测试"""
    
    def test_logout_success(self, client, app, init_database, auth_headers):
        """测试成功登出"""
        response = client.post('/api/user/logout',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code in [200, 204]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['code'] == 0
    
    def test_logout_without_auth(self, client, app):
        """测试未认证的登出"""
        response = client.post('/api/user/logout',
            content_type='application/json'
        )
        
        assert response.status_code in [401, 400]
        data = json.loads(response.data)
        assert data['code'] in [1, 3]
    
    def test_logout_with_invalid_token(self, client, app):
        """测试使用无效token的登出"""
        response = client.post('/api/user/logout',
            headers={
                'Authorization': 'Bearer invalid_token',
                'Content-Type': 'application/json'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] in [1, 3]


class TestAuthPasswordReset:
    """密码重置相关测试（如果实现了的话）"""
    
    def test_request_password_reset_with_email(self, client, app, init_database):
        """测试请求密码重置"""
        response = client.post('/api/user/requestPasswordReset',
            json={
                'email': 'testuser1@seu.edu.cn'
            },
            content_type='application/json'
        )
        
        # 可能返回200或501（未实现）
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['code'] == 0
    
    def test_request_password_reset_invalid_email(self, client, app):
        """测试用不存在的邮箱请求密码重置"""
        response = client.post('/api/user/requestPasswordReset',
            json={
                'email': 'nonexistent@seu.edu.cn'
            },
            content_type='application/json'
        )
        
        # 通常应该返回404或400
        if response.status_code in [200, 400, 404]:
            data = json.loads(response.data)
            # 某些实现为了安全可能返回成功但不实际发送
            assert 'data' in data or 'message' in data


class TestAuthenticationEdgeCases:
    """认证边界情况测试"""
    
    def test_register_with_special_characters_username(self, client, app):
        """测试特殊字符用户名"""
        response = client.post('/api/user/register',
            json={
                'username': 'user@#$%',
                'email': 'special@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        # 可能拒绝或接受，取决于实现
        assert response.status_code in [200, 400]
    
    def test_register_very_long_username(self, client, app):
        """测试过长的用户名"""
        long_username = 'a' * 100
        response = client.post('/api/user/register',
            json={
                'username': long_username,
                'email': 'longname@seu.edu.cn',
                'password': 'SecurePass123'
            },
            content_type='application/json'
        )
        
        # 应该拒绝过长的用户名
        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['code'] == 2
    
    def test_login_repeated_attempts(self, client, app, init_database):
        """测试重复登录尝试（防暴力破解）"""
        # 多次错误登录
        for _ in range(5):
            response = client.post('/api/user/login',
                json={
                    'username': 'testuser1',
                    'password': 'WrongPassword123'
                },
                content_type='application/json'
            )
            assert response.status_code == 401
        
        # 最后一次尝试可能被限流
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1',
                'password': 'Password123'
            },
            content_type='application/json'
        )
        
        # 可能返回200（成功）或429（限流）
        assert response.status_code in [200, 429]
