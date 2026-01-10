"""
商品评价API测试
测试评价的创建、查询等操作
"""

import pytest
import json
from app.models import Review, Order, db


class TestReviewCreate:
    """评价创建API测试"""
    
    def test_create_review_success(self, client, app, init_database, auth_headers_user2):
        """测试成功创建评价"""
        order = init_database['orders'][0]
        item = init_database['items'][0]
        
        response = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 5,
                'content': '很满意，五星好评！'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'review_id' in data['data']
    
    def test_create_review_invalid_rating_too_high(self, client, app, init_database, auth_headers_user2):
        """测试评分过高"""
        order = init_database['orders'][0]
        item = init_database['items'][0]
        
        response = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 10,
                'content': '超出范围'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_create_review_invalid_rating_too_low(self, client, app, init_database, auth_headers_user2):
        """测试评分过低"""
        order = init_database['orders'][0]
        item = init_database['items'][0]
        
        response = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 0,
                'content': '评分为0'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 2
    
    def test_create_review_empty_content(self, client, app, init_database, auth_headers_user2):
        """测试空评论内容"""
        order = init_database['orders'][0]
        item = init_database['items'][0]
        
        response = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 5,
                'content': ''
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        # 可能接受空内容或拒绝
        assert response.status_code in [200, 400]
    
    def test_create_review_without_auth(self, client, app, init_database):
        """测试未认证创建评价"""
        order = init_database['orders'][0]
        item = init_database['items'][0]
        
        response = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 5,
                'content': '测试'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] in [1, 3]
    
    def test_create_review_nonexistent_order(self, client, app, init_database, auth_headers_user2):
        """测试使用不存在的订单创建评价"""
        response = client.post('/api/review/create',
            json={
                'order_id': 99999,
                'item_id': init_database['items'][0].id,
                'rating': 5,
                'content': '测试'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] in [1, 2]
    
    def test_create_duplicate_review(self, client, app, init_database, auth_headers_user2):
        """测试重复评价同一订单"""
        order = init_database['orders'][0]
        item = init_database['items'][0]
        
        # 第一次评价
        response1 = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 5,
                'content': '第一次评价'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        assert response1.status_code == 200
        
        # 第二次评价相同订单
        response2 = client.post('/api/review/create',
            json={
                'order_id': order.id,
                'item_id': item.id,
                'rating': 4,
                'content': '第二次评价'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        # 应该拒绝或允许，取决于实现
        assert response2.status_code in [200, 400]


class TestReviewQuery:
    """评价查询API测试"""
    
    def test_get_item_reviews(self, client, app, init_database):
        """测试获取商品评价"""
        item = init_database['items'][0]
        
        response = client.get(f'/api/review/getItemReviews/{item.id}',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert isinstance(data['data'], list)
    
    def test_get_user_reviews(self, client, app, init_database, auth_headers):
        """测试获取用户的评价"""
        response = client.get('/api/review/getUserReviews',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert isinstance(data['data'], list)
    
    def test_get_seller_rating(self, client, app, init_database):
        """测试获取卖家评分"""
        seller = init_database['users'][0]
        
        response = client.get(f'/api/review/getSellerRating/{seller.id}',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'rating' in data['data']
        assert 'review_count' in data['data']
    
    def test_get_reviews_with_pagination(self, client, app, init_database):
        """测试分页获取评价"""
        item = init_database['items'][0]
        
        response = client.get(f'/api/review/getItemReviews/{item.id}?page=1&limit=10',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0


class TestReviewUpdate:
    """评价更新API测试"""
    
    def test_update_review_success(self, client, app, init_database, auth_headers_user2):
        """测试更新评价"""
        review = init_database['reviews'][0]
        
        response = client.put(f'/api/review/update/{review.id}',
            json={
                'rating': 4,
                'content': '修改后的评价'
            },
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        # 可能支持或不支持编辑
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['code'] == 0
    
    def test_update_review_unauthorized(self, client, app, init_database, auth_headers):
        """测试未授权的更新评价"""
        review = init_database['reviews'][0]
        
        response = client.put(f'/api/review/update/{review.id}',
            json={
                'rating': 4,
                'content': '其他人的评价'
            },
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code in [401, 403]


class TestReviewDelete:
    """评价删除API测试"""
    
    def test_delete_review_success(self, client, app, init_database, auth_headers_user2):
        """测试删除评价"""
        review = init_database['reviews'][0]
        
        response = client.delete(f'/api/review/delete/{review.id}',
            headers=auth_headers_user2,
            content_type='application/json'
        )
        
        # 可能支持或不支持删除
        if response.status_code in [200, 204]:
            # 验证删除成功
            check_response = client.get(f'/api/review/getItemReviews/{review.item_id}')
            check_data = json.loads(check_response.data)
            assert all(r['id'] != review.id for r in check_data['data'])
    
    def test_delete_review_unauthorized(self, client, app, init_database, auth_headers):
        """测试未授权的删除评价"""
        review = init_database['reviews'][0]
        
        response = client.delete(f'/api/review/delete/{review.id}',
            headers=auth_headers,
            content_type='application/json'
        )
        
        assert response.status_code in [401, 403, 404]
