from . import db
from datetime import datetime
import numpy as np
import json

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    # 打卡时间配置
    sign_in_time = db.Column(db.String(5), default='09:00')  # 签到时间，格式 HH:MM
    sign_out_time = db.Column(db.String(5), default='18:00')  # 签退时间，格式 HH:MM
    late_threshold = db.Column(db.String(5), default='09:30')  # 迟到阈值，格式 HH:MM
    absent_threshold = db.Column(db.String(5), default='10:00')  # 缺勤阈值，格式 HH:MM
    early_leave_threshold = db.Column(db.String(5), default='17:30')  # 早退阈值，格式 HH:MM
    late_leave_threshold = db.Column(db.String(5), default='19:00')  # 晚退阈值，格式 HH:MM
    location = db.Column(db.String(128))  # 打卡位置
    distance_threshold = db.Column(db.Float, default=100.0)  # 打卡距离阈值（米）
    employees = db.relationship('User', backref='department', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 姓名
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)  # 手机号作为登录凭证
    role = db.Column(db.String(16), default='user')  # user/admin
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    face_data_id = db.Column(db.Integer, db.ForeignKey('face_data.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FaceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    face_url = db.Column(db.String(256))
    # 存储512维人脸特征向量，使用JSON格式存储
    face_features = db.Column(db.Text)  # JSON格式存储512维特征向量
    user = db.relationship('User', backref='face_data', uselist=False)
    
    def set_features(self, features):
        """设置人脸特征向量"""
        if isinstance(features, np.ndarray):
            features = features.tolist()
        self.face_features = json.dumps(features)
    
    def get_features(self):
        """获取人脸特征向量"""
        if self.face_features:
            try:
                return np.array(json.loads(self.face_features))
            except:
                return None
        return None

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, default=datetime.utcnow().date)  # 考勤日期
    check_type = db.Column(db.String(16))  # sign_in, sign_out
    status = db.Column(db.String(16))      # normal, late, absent, overtime
    time = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(128))
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度
    face_url = db.Column(db.String(256))
    # 存储考勤时的人脸特征向量，用于后续验证
    check_face_features = db.Column(db.Text)  # JSON格式存储512维特征向量
    similarity_score = db.Column(db.Float)    # 相似度分数
    remark = db.Column(db.String(256))        # 备注信息，用于标记补录、状态更新等操作
    user = db.relationship('User', backref='attendances')
    
    def set_check_features(self, features):
        """设置考勤时的人脸特征向量"""
        if isinstance(features, np.ndarray):
            features = features.tolist()
        self.check_face_features = json.dumps(features)
    
    def get_check_features(self):
        """获取考勤时的人脸特征向量"""
        if self.check_face_features:
            try:
                return np.array(json.loads(self.check_face_features))
            except:
                return None
        return None

class FaceUpdateRequest(db.Model):
    """人脸照片修改审核申请表"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    old_face_url = db.Column(db.String(256))  # 原照片路径
    new_face_url = db.Column(db.String(256))  # 新照片路径
    old_face_features = db.Column(db.Text)    # 原特征向量（JSON格式）
    new_face_features = db.Column(db.Text)    # 新特征向量（JSON格式）
    status = db.Column(db.String(16), default='pending')  # pending/approved/rejected
    reason = db.Column(db.String(512))        # 申请原因
    admin_comment = db.Column(db.String(512)) # 管理员备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 处理的管理员ID
    
    # 关联关系
    user = db.relationship('User', foreign_keys=[user_id], backref='face_update_requests')
    admin = db.relationship('User', foreign_keys=[admin_id])
    
    def set_old_features(self, features):
        """设置原特征向量"""
        if isinstance(features, np.ndarray):
            features = features.tolist()
        self.old_face_features = json.dumps(features)
    
    def get_old_features(self):
        """获取原特征向量"""
        if self.old_face_features:
            try:
                return np.array(json.loads(self.old_face_features))
            except:
                return None
        return None
    
    def set_new_features(self, features):
        """设置新特征向量"""
        if isinstance(features, np.ndarray):
            features = features.tolist()
        self.new_face_features = json.dumps(features)
    
    def get_new_features(self):
        """获取新特征向量"""
        if self.new_face_features:
            try:
                return np.array(json.loads(self.new_face_features))
            except:
                return None
        return None 