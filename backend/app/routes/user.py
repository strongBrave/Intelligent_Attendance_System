from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, db

bp = Blueprint('user', __name__)

@bp.route('/api/user/profile', methods=['GET'])
@jwt_required()
def profile():
    """获取用户信息"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 构建部门信息
    department_info = None
    if user.department:
        department_info = {
            'id': user.department.id,
            'name': user.department.name
        }
    
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,  # 修改为name字段
            'phone': user.phone,
            'role': user.role,
            'department': department_info  # 返回完整的部门对象
        }
    })

@bp.route('/api/user/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    if 'phone' in data:
        # 检查手机号是否已被其他用户使用
        existing_user = User.query.filter_by(phone=data['phone']).first()
        if existing_user and existing_user.id != current_user_id:
            return jsonify({'error': '手机号已被使用'}), 400
        user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({'message': '信息更新成功'}) 