"""
全局错误处理
捕获并标准化所有HTTP错误响应
"""


def register_error_handlers(app):  
    from flask import jsonify
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'code': 404, 'message': '资源不存在'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'code': 400, 'message': '请求参数错误'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'code': 401, 'message': '未认证'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'code': 403, 'message': '无权限'}), 403
