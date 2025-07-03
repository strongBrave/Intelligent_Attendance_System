from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # 基础配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = 'your-secret-key-here'  # 生产环境中应该使用环境变量
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'msg': 'Token已过期', 'error': 'token_expired'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'msg': '无效的Token', 'error': 'invalid_token'}, 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'msg': '缺少Token', 'error': 'authorization_required'}, 401

    # 注册蓝图
    from .routes.auth import bp as auth_bp
    from .routes.user import bp as user_bp
    from .routes.attendance import bp as attendance_bp
    from .routes.admin import bp as admin_bp
    from .routes.face import bp as face_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(face_bp, url_prefix='/api/face')

    # 添加静态文件路由，用于提供人脸照片访问
    @app.route('/uploads/faces/<path:filename>')
    def serve_face_image(filename):
        """提供人脸照片访问"""
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
        response = send_from_directory(uploads_dir, filename)
        # 添加CORS头
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app 