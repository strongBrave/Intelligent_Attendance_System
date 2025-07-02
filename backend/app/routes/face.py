from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from .. import db
from ..models import User, FaceData, Attendance
from ..face_service import face_service
from datetime import datetime
import uuid

bp = Blueprint('face', __name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads/faces'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@bp.route('/model_info', methods=['GET'])
def get_model_info():
    """获取人脸识别模型信息"""
    try:
        model_info = face_service.get_model_info()
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': model_info
        })
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'获取失败: {str(e)}'})

@bp.route('/register_face', methods=['POST'])
def register_face():
    """注册人脸特征（单张图片）"""
    try:
        # 获取用户ID
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'code': 1, 'msg': '用户ID不能为空'})
        
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 1, 'msg': '用户不存在'})
        
        # 检查是否已经注册过人脸
        if user.face_data:
            return jsonify({'code': 1, 'msg': '用户已注册人脸信息'})
        
        # 获取上传的图片
        if 'face_image' not in request.files:
            return jsonify({'code': 1, 'msg': '请上传人脸图片'})
        
        file = request.files['face_image']
        if file.filename == '':
            return jsonify({'code': 1, 'msg': '请选择图片文件'})
        
        # 保存图片
        filename = f"{user_id}_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 提取人脸特征
        
        features, _ = face_service.extract_face_features(filepath)
        if features is None:
            # 删除保存的图片
            os.remove(filepath)
            return jsonify({'code': 1, 'msg': '无法从图片中提取人脸特征，请确保图片中有清晰的人脸'})
        
        # 创建人脸数据记录
        face_data = FaceData(
            face_url=filepath,
            user=user
        )
        face_data.set_features(features)
        
        # 保存到数据库
        db.session.add(face_data)
        db.session.commit()
        
        return jsonify({
            'code': 0, 
            'msg': '人脸注册成功',
            'data': {
                'face_data_id': face_data.id,
                'feature_dim': len(features),
                'model_info': face_service.get_model_info()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'人脸注册失败: {str(e)}'})

@bp.route('/register_multiple_faces', methods=['POST'])
def register_multiple_faces():
    """注册多张人脸图片并计算平均特征向量"""
    try:
        # 获取用户ID
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'code': 1, 'msg': '用户ID不能为空'})
        
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 1, 'msg': '用户不存在'})
        
        # 检查是否已经注册过人脸
        if user.face_data:
            return jsonify({'code': 1, 'msg': '用户已注册人脸信息'})
        
        # 获取上传的图片
        files = request.files.getlist('face_images')
        if not files or len(files) == 0:
            return jsonify({'code': 1, 'msg': '请上传人脸图片'})
        
        if len(files) > 5:
            return jsonify({'code': 1, 'msg': '最多只能上传5张图片'})
        
        # 保存图片并提取特征
        saved_files = []
        image_data_list = []
        
        for i, file in enumerate(files):
            if file.filename == '':
                continue
                
            # 保存图片
            filename = f"{user_id}_{uuid.uuid4().hex}_{i}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            saved_files.append(filepath)
            
            # 读取图片数据
            with open(filepath, 'rb') as f:
                image_data = f.read()
            image_data_list.append(image_data)
        
        if len(image_data_list) == 0:
            return jsonify({'code': 1, 'msg': '没有有效的图片文件'})
        
        # 提取多张图片的特征向量
        features_list = []
        for image_data in image_data_list:
            features, _ = face_service.extract_face_features(image_data)
            if features is not None:
                features_list.append(features)
        
        # 计算平均特征向量
        average_features = face_service.calculate_average_features(features_list)
        if average_features is None:
            # 清理保存的文件
            for filepath in saved_files:
                if os.path.exists(filepath):
                    os.remove(filepath)
            return jsonify({'code': 1, 'msg': '无法计算平均特征向量'})
        
        # 使用第一张图片作为主要图片
        main_image_path = saved_files[0]
        
        # 创建人脸数据记录
        face_data = FaceData(
            face_url=main_image_path,
            user=user
        )
        face_data.set_features(average_features)
        
        # 保存到数据库
        db.session.add(face_data)
        db.session.commit()
        
        # 清理其他图片文件（只保留主图片）
        for filepath in saved_files[1:]:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({
            'code': 0, 
            'msg': f'人脸注册成功，处理了 {len(features_list)} 张图片',
            'data': {
                'face_data_id': face_data.id,
                'feature_dim': len(average_features),
                'processed_images': len(features_list),
                'valid_images': len([f for f in features_list if f is not None]),
                'model_info': face_service.get_model_info()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        # 清理保存的文件
        for filepath in saved_files:
            if os.path.exists(filepath):
                os.remove(filepath)
        return jsonify({'code': 1, 'msg': f'人脸注册失败: {str(e)}'})

@bp.route('/average_features', methods=['POST'])
def average_features():
    """计算多个特征向量的平均值并更新用户的人脸特征"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        features_list = data.get('features_list', [])
        
        if not user_id:
            return jsonify({'code': 1, 'msg': '用户ID不能为空'})
        
        if len(features_list) < 2:
            return jsonify({'code': 1, 'msg': '至少需要2个特征向量才能计算平均值'})
        
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 1, 'msg': '用户不存在'})
        
        # 计算平均特征向量
        average_features = face_service.calculate_average_features(features_list)
        if average_features is None:
            return jsonify({'code': 1, 'msg': '无法计算平均特征向量'})
        
        # 更新用户的人脸特征
        if user.face_data:
            user.face_data.set_features(average_features)
        else:
            # 创建新的人脸数据记录
            face_data = FaceData(
                face_url="",  # 这里可以设置为空，因为特征向量已经计算好了
                user=user
            )
            face_data.set_features(average_features)
            db.session.add(face_data)
        
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'msg': '平均特征向量计算成功',
            'data': {
                'feature_dim': len(average_features),
                'processed_features': len(features_list),
                'valid_features': len([f for f in features_list if f is not None])
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'计算平均特征向量失败: {str(e)}'})

@bp.route('/user_face_info/<int:user_id>', methods=['GET'])
def get_user_face_info(user_id):
    """获取用户人脸信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 1, 'msg': '用户不存在'})
        
        if not user.face_data:
            return jsonify({'code': 1, 'msg': '用户未注册人脸信息'})
        
        face_data = user.face_data
        features = face_data.get_features()
        
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': {
                'user_id': user_id,
                'username': user.username,
                'face_data_id': face_data.id,
                'face_url': face_data.face_url,
                'feature_dim': len(features) if features is not None else 0,
                'has_features': features is not None,
                'model_info': face_service.get_model_info()
            }
        })
        
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'获取失败: {str(e)}'})

@bp.route('/update_face/<int:user_id>', methods=['POST'])
def update_face(user_id):
    """更新用户人脸数据"""
    try:
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 1, 'msg': '用户不存在'})
        
        # 获取上传的图片
        files = request.files.getlist('face_images')
        if not files or len(files) == 0:
            return jsonify({'code': 1, 'msg': '请上传人脸图片'})
        
        if len(files) > 5:
            return jsonify({'code': 1, 'msg': '最多只能上传5张图片'})
        
        # 保存图片并提取特征
        saved_files = []
        image_data_list = []
        
        for i, file in enumerate(files):
            if file.filename == '':
                continue
                
            # 保存图片
            filename = f"{user_id}_{uuid.uuid4().hex}_{i}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            saved_files.append(filepath)
            
            # 读取图片数据
            image_data_list.append(filepath)
        
        if len(image_data_list) == 0:
            return jsonify({'code': 1, 'msg': '没有有效的图片文件'})
        
        # 提取多张图片的特征向量
        features_list = []
        for image_data in image_data_list:
            features, _ = face_service.extract_face_features(image_data)
            if features is not None:
                features_list.append(features)
        
        if len(features_list) == 0:
            # 清理保存的文件
            for filepath in saved_files:
                if os.path.exists(filepath):
                    os.remove(filepath)
            return jsonify({'code': 1, 'msg': '无法从图片中提取人脸特征，请确保图片中有清晰的人脸'})
        
        # 计算平均特征向量
        average_features = face_service.calculate_average_features(features_list)
        if average_features is None:
            # 清理保存的文件
            for filepath in saved_files:
                if os.path.exists(filepath):
                    os.remove(filepath)
            return jsonify({'code': 1, 'msg': '无法计算平均特征向量'})
        
        # 使用第一张图片作为主要图片
        main_image_path = saved_files[0]
        
        # 更新或创建人脸数据记录
        if user.face_data:
            # 删除旧的人脸图片文件
            if user.face_data.face_url and os.path.exists(user.face_data.face_url):
                os.remove(user.face_data.face_url)
            
            # 更新现有记录
            user.face_data.face_url = main_image_path
            user.face_data.set_features(average_features)
        else:
            # 创建新的人脸数据记录
            face_data = FaceData(
                face_url=main_image_path,
                user=user
            )
            face_data.set_features(average_features)
            db.session.add(face_data)
        
        # 保存到数据库
        db.session.commit()
        
        # 清理其他图片文件（只保留主图片）
        for filepath in saved_files[1:]:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({
            'code': 0, 
            'msg': f'人脸数据更新成功，处理了 {len(features_list)} 张图片',
            'data': {
                'face_data_id': user.face_data.id if user.face_data else None,
                'feature_dim': len(average_features),
                'processed_images': len(features_list),
                'valid_images': len([f for f in features_list if f is not None]),
                'model_info': face_service.get_model_info()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        # 清理保存的文件
        if 'saved_files' in locals():
            for filepath in saved_files:
                if os.path.exists(filepath):
                    os.remove(filepath)
        return jsonify({'code': 1, 'msg': f'人脸数据更新失败: {str(e)}'})

@bp.route('/delete_face/<int:user_id>', methods=['DELETE'])
def delete_face(user_id):
    """删除用户人脸信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 1, 'msg': '用户不存在'})
        
        if not user.face_data:
            return jsonify({'code': 1, 'msg': '用户未注册人脸信息'})
        
        face_data = user.face_data
        
        # 删除图片文件
        if face_data.face_url and os.path.exists(face_data.face_url):
            os.remove(face_data.face_url)
        
        # 删除数据库记录
        db.session.delete(face_data)
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'msg': '人脸信息删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'删除失败: {str(e)}'}) 