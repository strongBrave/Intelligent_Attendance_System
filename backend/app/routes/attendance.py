from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Attendance, Department, FaceData, FaceUpdateRequest, db
from datetime import datetime, timedelta
import os
import uuid
from ..face_service import face_service
from ..utils import is_within_range, format_location_display

bp = Blueprint('attendance', __name__)

# ==================== 考勤打卡相关接口 ====================

@bp.route('/api/attendance/check_in', methods=['POST'])
@jwt_required()
def check_in():
    """用户签到"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 兼容json和form-data格式
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # 处理multipart/form-data格式
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location = request.form.get('location', '')
        
        # 处理人脸图片（如果有）
        face_image = request.files.get('face_image')
        face_url = None
        if face_image:
            # 保存人脸图片
            import uuid
            filename = f"checkin_{current_user_id}_{uuid.uuid4().hex}.jpg"
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            face_image.save(filepath)
            face_url = filepath
    else:
        # 处理JSON格式
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location = data.get('location', '')
        face_url = None
    
    today = datetime.now().date()
    
    # 检查今天是否已经签到
    existing_attendance = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_in'
    ).first()
    
    if existing_attendance:
        return jsonify({'error': '今日已签到'}), 400
    
    # 判断签到状态
    now = datetime.now()
    department = user.department
    status = 'normal'
    
    if department and department.sign_in_time:
        sign_in_time = datetime.strptime(department.sign_in_time, '%H:%M').time()
        if now.time() > sign_in_time:
            status = 'late'
    
    # 创建考勤记录
    attendance = Attendance(
        user_id=current_user_id,
        date=today,
        check_type='sign_in',
        status=status,
        time=now,
        location=location,
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None,
        face_url=face_url
    )
    db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '签到成功',
        'data': {
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'location': format_location_display(location)
        }
    })

@bp.route('/api/attendance/check_out', methods=['POST'])
@jwt_required()
def check_out():
    """用户签退"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 兼容json和form-data格式
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # 处理multipart/form-data格式
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location = request.form.get('location', '')
        
        # 处理人脸图片（如果有）
        face_image = request.files.get('face_image')
        face_url = None
        if face_image:
            # 保存人脸图片
            import uuid
            filename = f"checkout_{current_user_id}_{uuid.uuid4().hex}.jpg"
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            face_image.save(filepath)
            face_url = filepath
    else:
        # 处理JSON格式
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location = data.get('location', '')
        face_url = None
    
    today = datetime.now().date()
    
    # 检查今天是否已经签退
    existing_sign_out = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_out'
    ).first()
    
    if existing_sign_out:
        return jsonify({'error': '今日已签退'}), 400
    
    # 检查是否已签到
    existing_sign_in = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_in'
    ).first()
    
    if not existing_sign_in:
        return jsonify({'error': '请先签到'}), 400
    
    # 判断签退状态
    now = datetime.now()
    department = user.department
    status = existing_sign_in.status
    
    if department and department.sign_out_time:
        sign_out_time = datetime.strptime(department.sign_out_time, '%H:%M').time()
        if now.time() < sign_out_time:
            # 早退
            status = 'early_leave'
        elif department.late_leave_threshold:
            # 检查是否晚退
            late_leave_time = datetime.strptime(department.late_leave_threshold, '%H:%M').time()
            if now.time() > late_leave_time:
                status = 'late_leave'
    
    # 创建签退记录
    attendance = Attendance(
        user_id=current_user_id,
        date=today,
        check_type='sign_out',
        status=status,
        time=now,
        location=location,
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None,
        face_url=face_url
    )
    db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '签退成功',
        'data': {
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'location': format_location_display(location)
        }
    })

# ==================== 考勤查询相关接口 ====================

@bp.route('/api/attendance/records', methods=['GET'])
@jwt_required()
def get_attendance_records():
    """获取用户的考勤记录"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 获取查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = Attendance.query.filter_by(user_id=current_user_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    pagination = query.order_by(Attendance.date.desc(), Attendance.time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    records = []
    for record in pagination.items:
        record_data = {
            'id': record.id,
            'date': record.date.strftime('%Y-%m-%d'),
            'check_type': record.check_type,
            'status': record.status,
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S') if record.time else None,
            'location': format_location_display(record.location)
        }
        records.append(record_data)
    
    return jsonify({
        'records': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@bp.route('/api/attendance/today', methods=['GET'])
@jwt_required()
def get_today_attendance():
    """获取今天的考勤状态"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    today = datetime.now().date()
    
    # 查询今天的考勤记录
    check_in = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_in'
    ).first()
    
    check_out = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_out'
    ).first()
    
    return jsonify({
        'check_in': {
            'time': check_in.time.strftime('%Y-%m-%d %H:%M:%S') if check_in and check_in.time else None,
            'status': check_in.status if check_in else None,
            'location': format_location_display(check_in.location) if check_in else None
        },
        'check_out': {
            'time': check_out.time.strftime('%Y-%m-%d %H:%M:%S') if check_out and check_out.time else None,
            'status': check_out.status if check_out else None,
            'location': format_location_display(check_out.location) if check_out else None
        }
    })

@bp.route('/api/user/today', methods=['GET'])
@jwt_required()
def get_user_today_attendance():
    """获取用户今天的考勤状态（兼容接口）"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    today = datetime.now().date()
    
    # 查询今天的考勤记录
    check_in = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_in'
    ).first()
    
    check_out = Attendance.query.filter_by(
        user_id=current_user_id,
        date=today,
        check_type='sign_out'
    ).first()
    
    return jsonify({
        'success': True,
        'data': {
            'check_in': {
                'time': check_in.time.strftime('%Y-%m-%d %H:%M:%S') if check_in and check_in.time else None,
                'status': check_in.status if check_in else None,
                'location': format_location_display(check_in.location) if check_in else None
            },
            'check_out': {
                'time': check_out.time.strftime('%Y-%m-%d %H:%M:%S') if check_out and check_out.time else None,
                'status': check_out.status if check_out else None,
                'location': format_location_display(check_out.location) if check_out else None
            }
        }
    })

@bp.route('/api/user/month', methods=['GET'])
@jwt_required()
def get_month_attendance():
    """获取用户月度考勤数据"""
    try:
        user_id = get_jwt_identity()
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
        
        # 获取当月的所有考勤记录
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        attendances = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.date >= start_date,
            Attendance.date < end_date
        ).order_by(Attendance.date, Attendance.time).all()
        
        # 按日期组织数据
        daily_attendance = {}
        for attendance in attendances:
            date_str = attendance.date.strftime('%Y-%m-%d')
            
            if date_str not in daily_attendance:
                daily_attendance[date_str] = {
                    'date': date_str,
                    'sign_in': None,
                    'sign_out': None,
                    'status': 'absent',
                    'location': None
                }
            
            # 根据check_type分类处理
            if attendance.check_type == 'sign_in':
                daily_attendance[date_str]['sign_in'] = {
                    'time': attendance.time.strftime('%H:%M:%S'),
                    'status': attendance.status,
                    'location': format_location_display(attendance.location)
                }
                daily_attendance[date_str]['status'] = attendance.status
                daily_attendance[date_str]['location'] = format_location_display(attendance.location)
            elif attendance.check_type == 'sign_out':
                daily_attendance[date_str]['sign_out'] = {
                    'time': attendance.time.strftime('%H:%M:%S'),
                    'status': attendance.status,
                    'location': format_location_display(attendance.location)
                }
                # 如果有签退记录，状态以签退为准（包含早退、晚退等）
                if attendance.status in ['early_leave', 'late_leave']:
                    daily_attendance[date_str]['status'] = attendance.status
                if not daily_attendance[date_str]['location']:
                    daily_attendance[date_str]['location'] = format_location_display(attendance.location)
        
        # 转换为列表格式
        result = list(daily_attendance.values())
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 人脸识别相关接口 ====================

@bp.route('/api/user/face_status', methods=['GET'])
@jwt_required()
def get_face_status():
    """获取用户人脸注册状态"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        has_face = user.face_data is not None
        face_url = user.face_data.face_url if user.face_data else None
        
        return jsonify({
            'success': True,
            'has_face': has_face,
            'face_url': face_url
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/attendance/check_distance', methods=['POST'])
@jwt_required()
def check_distance():
    """检查用户是否在打卡范围内"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'error': '位置信息不完整'}), 400
    
    if not user.department or not user.department.location:
        return jsonify({
            'in_range': True,
            'message': '部门未设置打卡位置'
        })
    
    in_range = is_within_range(latitude, longitude, user.department.location, user.department.distance_threshold)
    
    return jsonify({
        'in_range': in_range,
        'message': '在打卡范围内' if in_range else '不在打卡范围内',
        'department_location': user.department.location,
        'distance_threshold': user.department.distance_threshold
    })

@bp.route('/api/attendance/verify_face', methods=['POST'])
@jwt_required()
def verify_face():
    """人脸识别验证（不创建考勤记录，仅验证）"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 兼容json和form-data
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files.get('face_image')
    else:
        data = request.get_json()
        file = None

    if not file or not file.filename:
        return jsonify({'error': '请提供人脸图片'}), 400

    try:
        # 保存临时图片
        now = datetime.now()
        filename = f"verify_{current_user_id}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 人脸识别
        current_features, _ = face_service.extract_face_features(filepath)
        if current_features is not None:
            user_faces = face_service.get_user_faces(current_user_id)
            if user_faces:
                max_similarity = 0
                for user_face in user_faces:
                    user_face_features = user_face.get_features()
                    similarity = face_service.calculate_similarity(current_features, user_face_features)
                    max_similarity = max(max_similarity, similarity)
                
                # 删除临时文件
                os.remove(filepath)
                
                if max_similarity >= 0.9:
                    return jsonify({
                        'success': True,
                        'similarity': max_similarity,
                        'message': '人脸验证成功'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'similarity': max_similarity,
                        'message': f'人脸验证失败，相似度: {max_similarity:.4f}'
                    })
            else:
                os.remove(filepath)
                return jsonify({
                    'success': False,
                    'message': '用户未注册人脸信息'
                })
        else:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'message': '未检测到人脸，请确保人脸在画面中'
            })
        
    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({
            'success': False,
            'message': f'人脸验证处理失败: {str(e)}'
        }), 500

@bp.route('/api/attendance/detect_faces', methods=['POST'])
@jwt_required()
def detect_faces():
    """检测图片中的人脸并返回坐标框"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 兼容json和form-data
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        file = request.files.get('face_image')
    else:
        data = request.get_json()
        file = None

    if not file or not file.filename:
        return jsonify({'error': '请提供人脸图片'}), 400

    try:
        # 保存临时图片
        now = datetime.now()
        filename = f"detect_{current_user_id}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 检测人脸框
        face_boxes, image_width, image_height = face_service.detect_faces_with_boxes(filepath)
        
        # 删除临时文件
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'face_boxes': face_boxes,
            'face_count': len(face_boxes),
            'image_width': image_width,
            'image_height': image_height,
            'message': f'检测到 {len(face_boxes)} 个人脸'
        })
        
    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({
            'success': False,
            'message': f'人脸检测处理失败: {str(e)}'
        }), 500

# ==================== 人脸更新申请相关接口 ====================

@bp.route('/api/user/face-update-request', methods=['POST'])
@jwt_required()
def submit_face_update_request():
    """用户提交人脸更新申请"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 检查是否有待处理的申请
    existing_request = FaceUpdateRequest.query.filter_by(
        user_id=current_user_id,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': '您已有待处理的人脸更新申请，请等待审核结果'}), 400
    
    # 获取申请参数
    face_image = request.files.get('face_image')
    reason = request.form.get('reason', '').strip()
    
    if not face_image or not face_image.filename:
        return jsonify({'error': '请上传新的人脸照片'}), 400
    
    if not reason:
        return jsonify({'error': '请填写申请原因'}), 400
    
    try:
        # 保存新照片
        filename = f"face_update_{current_user_id}_{uuid.uuid4().hex}.jpg"
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'faces')
        os.makedirs(upload_dir, exist_ok=True)
        new_face_path = os.path.join(upload_dir, filename)
        face_image.save(new_face_path)
        
        # 提取新照片的人脸特征
        print(f"[人脸检测] 开始为用户 {current_user_id} 提取人脸特征，图片路径: {new_face_path}")
        new_features, _ = face_service.extract_face_features(new_face_path)
        
        if new_features is None:
            print(f"[人脸检测] 用户 {current_user_id} 人脸特征提取失败，删除无效照片")
            os.remove(new_face_path)  # 删除无效照片
            return jsonify({'error': '未检测到人脸，请确保照片中有清晰的人脸'}), 400
        
        print(f"[人脸检测] 用户 {current_user_id} 人脸特征提取成功，特征维度: {len(new_features)}")
        
        # 获取原照片信息
        old_face_url = None
        old_features = None
        if user.face_data:
            old_face_url = user.face_data.face_url
            old_features = user.face_data.get_features()
            print(f"[人脸检测] 用户 {current_user_id} 已有原人脸数据，路径: {old_face_url}")
        else:
            print(f"[人脸检测] 用户 {current_user_id} 首次注册人脸")
        
        # 创建审核申请
        face_request = FaceUpdateRequest(
            user_id=current_user_id,
            old_face_url=old_face_url,
            new_face_url=new_face_path,
            reason=reason,
            status='pending'
        )
        
        # 设置特征向量
        if old_features is not None:
            face_request.set_old_features(old_features)
        face_request.set_new_features(new_features)
        
        db.session.add(face_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '人脸更新申请已提交，请等待管理员审核',
            'request_id': face_request.id
        })
        
    except Exception as e:
        # 清理上传的文件
        if 'new_face_path' in locals() and os.path.exists(new_face_path):
            os.remove(new_face_path)
        
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'提交申请失败: {str(e)}'
        }), 500

@bp.route('/api/user/face-update-request/status', methods=['GET'])
@jwt_required()
def get_face_update_request_status():
    """获取用户的人脸更新申请状态"""
    current_user_id = int(get_jwt_identity())
    
    # 查找最新的申请
    latest_request = FaceUpdateRequest.query.filter_by(
        user_id=current_user_id
    ).order_by(FaceUpdateRequest.created_at.desc()).first()
    
    if not latest_request:
        return jsonify({
            'success': True,
            'has_request': False,
            'message': '暂无人脸更新申请记录'
        })
    
    status_map = {
        'pending': '待审核',
        'approved': '已通过',
        'rejected': '已拒绝'
    }
    
    return jsonify({
        'success': True,
        'has_request': True,
        'request': {
            'id': latest_request.id,
            'status': latest_request.status,
            'status_text': status_map.get(latest_request.status, latest_request.status),
            'reason': latest_request.reason,
            'admin_comment': latest_request.admin_comment,
            'created_at': latest_request.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': latest_request.updated_at.strftime('%Y-%m-%d %H:%M:%S') if latest_request.updated_at else None
        }
    }) 