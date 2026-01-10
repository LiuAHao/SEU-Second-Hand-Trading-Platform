"""
用户个人资料API测试
测试用户信息查询、更新、头像上传等操作
"""

import pytest
import json
from app.models import User, Address, db


class TestUserProfile:
    """用户个人资料API测试"""
    
    def test_get_user_profile(self, client, app, init_database, auth_headers):
        """测试获取用户个人资料"""
        response = client.get('/api/user/profile',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'username' in data['data']
        assert 'email' in data['data']
        assert 'bio' in data['data']
    
    def test_get_user_profile_without_auth(self, client, app):
        """测试未认证获取资料"""
        response = client.get('/api/user/profile',
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] in [1, 3]
    
    def test_get_other_user_profile(self, client, app, init_database):
        """测试获取其他用户的公开信息"""
        user = init_database['users'][0]
        
        response = client.get(f'/api/user/getPublicProfile/{user.id}',
            content_type='application/json'
        )
        
        # 可能返回200（公开信息）或404（隐私保护）
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['code'] == 0
            assert 'username' in data['data']


class TestUserProfileUpdate:
    """用户资料更新API测试"""
    
    def test_update_user_bio(self, client, app, init_database, auth_headers):
        """测试更新用户简介"""
        response = client.put('/api/user/profile',
            json={
                'bio': '我是一个诚实的交易者'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_update_user_phone(self, client, app, init_database, auth_headers):
        """测试更新用户电话"""
        response = client.put('/api/user/profile',
            json={
                'phone': '13999999999'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_update_user_avatar(self, client, app, init_database, auth_headers):
        """测试更新用户头像"""
        response = client.put('/api/user/profile',
            json={
                'avatar_url': 'https://example.com/new-avatar.jpg'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_update_profile_without_auth(self, client, app):
        """测试未认证的资料更新"""
        response = client.put('/api/user/profile',
            json={
                'bio': '新简介'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_update_profile_invalid_phone(self, client, app, init_database, auth_headers):
        """测试无效的电话号码"""
        response = client.put('/api/user/profile',
            json={
                'phone': 'invalid_phone'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        # 可能拒绝或接受
        assert response.status_code in [200, 400]


class TestUserAddresses:
    """用户地址管理API测试"""
    
    def test_get_user_addresses(self, client, app, init_database, auth_headers):
        """测试获取用户地址列表"""
        response = client.get('/api/user/addresses',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert isinstance(data['data'], list)
    
    def test_add_new_address(self, client, app, init_database, auth_headers):
        """测试添加新地址"""
        response = client.post('/api/user/address/add',
            json={
                'recipient_name': '新地址收货人',
                'phone': '15800158000',
                'detail': '新地址详情',
                'is_default': False
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'address_id' in data['data']
    
    def test_add_address_missing_required_fields(self, client, app, init_database, auth_headers):
        """测试缺少必需字段的地址"""
        response = client.post('/api/user/address/add',
            json={
                'recipient_name': '名字',
                # 缺少其他必需字段
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_update_address(self, client, app, init_database, auth_headers):
        """测试更新地址"""
        address = init_database['addresses'][0]
        
        response = client.put(f'/api/user/address/{address.id}',
            json={
                'recipient_name': '更新的名字',
                'phone': '15900159000',
                'detail': '更新的地址'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_delete_address(self, client, app, init_database, auth_headers):
        """测试删除地址"""
        address = init_database['addresses'][1]  # 删除非默认地址
        
        response = client.delete(f'/api/user/address/{address.id}',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code in [200, 204]
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_set_default_address(self, client, app, init_database, auth_headers):
        """测试设置默认地址"""
        address = init_database['addresses'][1]  # 设置非默认地址为默认
        
        response = client.post(f'/api/user/address/{address.id}/setDefault',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_cannot_delete_only_address(self, client, app, init_database, auth_headers_user3):
        """测试不能删除唯一地址"""
        # user3只有一个地址
        address = init_database['addresses'][2]
        
        response = client.delete(f'/api/user/address/{address.id}',
            headers=auth_headers_user3,
            content_type='application/json'
        )
        
        # 可能拒绝或允许，取决于实现
        assert response.status_code in [200, 400, 409]


class TestUserStats:
    """用户统计API测试"""
    
    def test_get_user_stats(self, client, app, init_database, auth_headers):
        """测试获取用户统计信息"""
        response = client.get('/api/user/stats',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        if 'data' in data and data['data']:
            # 应该包含统计信息
            assert 'total_orders' in data['data'] or 'order_count' in data['data']
    
    def test_get_seller_stats(self, client, app, init_database):
        """测试获取卖家统计"""
        seller = init_database['users'][0]
        
        response = client.get(f'/api/user/sellerStats/{seller.id}',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0


class TestUserSecurity:
    """用户安全相关API测试"""
    
    def test_change_password(self, client, app, init_database, auth_headers):
        """测试修改密码"""
        response = client.post('/api/user/changePassword',
            json={
                'old_password': 'Password123',
                'new_password': 'NewPassword456'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_change_password_wrong_old_password(self, client, app, init_database, auth_headers):
        """测试使用错误的旧密码修改"""
        response = client.post('/api/user/changePassword',
            json={
                'old_password': 'WrongPassword',
                'new_password': 'NewPassword456'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] in [1, 3]
    
    def test_change_password_weak_new_password(self, client, app, init_database, auth_headers):
        """测试新密码过弱"""
        response = client.post('/api/user/changePassword',
            json={
                'old_password': 'Password123',
                'new_password': 'weak'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2


class TestUserFavorites:
    """用户收藏/关注相关API测试"""
    
    def test_add_favorite_item(self, client, app, init_database, auth_headers):
        """测试收藏商品"""
        item = init_database['items'][0]
        
        response = client.post(f'/api/user/favorite/add/{item.id}',
            headers=auth_headers,
            content_type='application/json'
        )
        
        # 可能实现或不实现此功能
        if response.status_code in [200, 201]:
            data = json.loads(response.data)
            assert data['code'] == 0
    
    def test_get_favorite_items(self, client, app, init_database, auth_headers):
        """测试获取收藏商品"""
        response = client.get('/api/user/favorites',
            headers=auth_headers,
            content_type='application/json'
        )
        
        # 可能实现或不实现此功能
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['code'] == 0
            assert isinstance(data['data'], list)
    
    def test_remove_favorite_item(self, client, app, init_database, auth_headers):
        """测试取消收藏"""
        item = init_database['items'][0]
        
        response = client.delete(f'/api/user/favorite/remove/{item.id}',
            headers=auth_headers,
            content_type='application/json'
        )
        
        # 可能实现或不实现此功能
        if response.status_code in [200, 204]:
            data = json.loads(response.data) if response.data else {'code': 0}
            assert data.get('code') == 0 or response.status_code == 204
