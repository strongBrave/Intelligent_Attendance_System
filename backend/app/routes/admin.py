from flask import Blueprint, request, jsonify
from ..models import User, Department, Attendance, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, time, date
from sqlalchemy import or_, desc, asc
import re
from ..utils import format_location_display

bp = Blueprint('admin', __name__)

# 公共工具函数
def time_to_minutes(time_str):
    """将时间字符串转换为分钟数"""
    if isinstance(time_str, str):
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    elif isinstance(time_str, time):
        return time_str.hour * 60 + time_str.minute
    return 0

def determine_sign_in_status(dept, attendance_record, current_time_minutes):
    """根据时间规则判断签到状态"""
    late_threshold_minutes = time_to_minutes(dept.late_threshold)
    absent_threshold_minutes = time_to_minutes(dept.absent_threshold)
    
    if attendance_record is None:
        # 没有签到记录，根据当前时间判断
        if current_time_minutes > absent_threshold_minutes:
            return ['absent', 'not_signed_in']
        elif current_time_minutes > late_threshold_minutes and current_time_minutes <= absent_threshold_minutes:
            return ['late', 'not_signed_in']
        else:
            return ['not_signed_in', 'not_signed_in']
    else:
        # 有签到记录，根据status判断
        if attendance_record.status == 'absent':
            return ['absent', 'sign_in']
        elif attendance_record.status == 'late':
            return ['late', 'sign_in']
        else:
            return ['normal', 'sign_in']

def determine_sign_out_status(dept, attendance_record, current_time_minutes):
    """根据时间规则判断签退状态"""
    early_leave_threshold_minutes = time_to_minutes(dept.early_leave_threshold)
    late_leave_threshold_minutes = time_to_minutes(dept.late_leave_threshold)
        
    if attendance_record is None:
        if current_time_minutes > late_leave_threshold_minutes:
            return ['late_leave', 'not_signed_out']
        else:
            return ['not_signed_out', 'not_signed_out']
    else:
        if attendance_record.status == 'early_leave':
            return ['early_leave', 'sign_out']
        elif attendance_record.status == 'late_leave':
            return ['late_leave', 'sign_out']
        else:
            return ['normal', 'sign_out']

@bp.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取所有用户，支持搜索和排序"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    # 获取查询参数
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'name')  # 默认按姓名排序
    sort_order = request.args.get('sort_order', 'asc')  # asc 或 desc
    
    # 构建查询
    query = User.query
    
    # 添加搜索条件（姓名或手机号模糊搜索）
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                User.name.like(search_pattern),
                User.phone.like(search_pattern)
            )
        )
    
    # 添加排序
    if sort_by == 'department':
        # 按部门排序，需要join部门表
        query = query.outerjoin(Department)
        if sort_order == 'desc':
            query = query.order_by(desc(Department.name), asc(User.name))
        else:
            query = query.order_by(asc(Department.name), asc(User.name))
    elif sort_by == 'name':
        # 按姓名排序
        if sort_order == 'desc':
            query = query.order_by(desc(User.name))
        else:
            query = query.order_by(asc(User.name))
    elif sort_by == 'phone':
        # 按手机号排序
        if sort_order == 'desc':
            query = query.order_by(desc(User.phone))
        else:
            query = query.order_by(asc(User.phone))
    elif sort_by == 'role':
        # 按角色排序
        if sort_order == 'desc':
            query = query.order_by(desc(User.role))
        else:
            query = query.order_by(asc(User.role))
    else:
        # 默认按姓名排序
        query = query.order_by(asc(User.name))
    
    users = query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,  # 姓名
            'phone': user.phone,
            'role': user.role,
            'department': user.department.name if user.department else '未分配',
            'department_id': user.department_id,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        user_list.append(user_data)
    
    return jsonify({
        'users': user_list,
        'total': len(user_list),
        'search': search,
        'sort_by': sort_by,
        'sort_order': sort_order
    })

@bp.route('/api/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建新用户"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    name = data.get('name')  # 姓名
    password = data.get('password')
    phone = data.get('phone')
    role = data.get('role', 'user')
    department_id = data.get('department_id')
    
    if not name or not password or not phone:
        return jsonify({'error': '姓名、密码和手机号不能为空'}), 400
    
    # 密码强度验证
    if len(password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return jsonify({'error': '手机号已存在'}), 400
    
    user = User(
        name=name,  # 姓名
        password=generate_password_hash(password),
        phone=phone,
        role=role,
        department_id=department_id
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '用户创建成功',
        'user': {
            'id': user.id,
            'name': user.name,  # 姓名
            'phone': user.phone,
            'role': user.role
        }
    }), 201

@bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    if 'name' in data:  # 更新姓名
        user.name = data['name']
    
    if 'phone' in data:
        # 检查手机号是否已被其他用户使用
        existing_user = User.query.filter_by(phone=data['phone']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': '手机号已存在'}), 400
        user.phone = data['phone']
    
    if 'role' in data:
        user.role = data['role']
    
    if 'department_id' in data:
        user.department_id = data['department_id']
    
    if 'password' in data and data['password']:
        # 密码强度验证
        if len(data['password']) < 6:
            return jsonify({'error': '密码长度至少6位'}), 400
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    
    return jsonify({'message': '用户信息更新成功'})

@bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    if current_user.id == user_id:
        return jsonify({'error': '不能删除自己的账号'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'})

@bp.route('/api/admin/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """获取所有部门"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    departments = Department.query.all()
    dept_list = []
    for dept in departments:
        dept_data = {
            'id': dept.id,
            'name': dept.name,
            'sign_in_time': dept.sign_in_time,
            'sign_out_time': dept.sign_out_time,
            'late_threshold': dept.late_threshold,
            'absent_threshold': dept.absent_threshold,
            'early_leave_threshold': dept.early_leave_threshold,
            'late_leave_threshold': dept.late_leave_threshold,
            'location': dept.location,
            'distance_threshold': dept.distance_threshold,
            'user_count': len(dept.employees) if dept.employees else 0
        }
        dept_list.append(dept_data)
    return jsonify({'departments': dept_list})

@bp.route('/api/admin/departments', methods=['POST'])
@jwt_required()
def create_department():
    """创建新部门"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    data = request.get_json()
    name = data.get('name')
    sign_in_time = data.get('sign_in_time', '09:00')
    sign_out_time = data.get('sign_out_time', '18:00')
    late_threshold = data.get('late_threshold', '09:30')
    absent_threshold = data.get('absent_threshold', '10:00')
    early_leave_threshold = data.get('early_leave_threshold', '17:30')
    late_leave_threshold = data.get('late_leave_threshold', '19:00')
    location = data.get('location', '')
    distance_threshold = data.get('distance_threshold', 100.0)
    if not name:
        return jsonify({'error': '部门名称不能为空'}), 400
    existing_dept = Department.query.filter_by(name=name).first()
    if existing_dept:
        return jsonify({'error': '部门名称已存在'}), 400
    new_dept = Department(
        name=name,
        sign_in_time=sign_in_time,
        sign_out_time=sign_out_time,
        late_threshold=late_threshold,
        absent_threshold=absent_threshold,
        early_leave_threshold=early_leave_threshold,
        late_leave_threshold=late_leave_threshold,
        location=location,
        distance_threshold=distance_threshold
    )
    db.session.add(new_dept)
    db.session.commit()
    return jsonify({
        'message': '部门创建成功',
        'department': {
            'id': new_dept.id,
            'name': new_dept.name,
            'sign_in_time': new_dept.sign_in_time,
            'sign_out_time': new_dept.sign_out_time,
            'late_threshold': new_dept.late_threshold,
            'absent_threshold': new_dept.absent_threshold,
            'early_leave_threshold': new_dept.early_leave_threshold,
            'location': new_dept.location,
            'distance_threshold': new_dept.distance_threshold
        }
    }), 201

@bp.route('/api/admin/departments/<int:department_id>', methods=['PUT'])
@jwt_required()
def update_department(department_id):
    """更新部门信息"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'error': '部门不存在'}), 404
    data = request.get_json()
    name = data.get('name')
    sign_in_time = data.get('sign_in_time')
    sign_out_time = data.get('sign_out_time')
    late_threshold = data.get('late_threshold')
    absent_threshold = data.get('absent_threshold')
    early_leave_threshold = data.get('early_leave_threshold')
    late_leave_threshold = data.get('late_leave_threshold')
    location = data.get('location')
    distance_threshold = data.get('distance_threshold')
    if name:
        department.name = name
    if sign_in_time:
        department.sign_in_time = sign_in_time
    if sign_out_time:
        department.sign_out_time = sign_out_time
    if late_threshold:
        department.late_threshold = late_threshold
    if absent_threshold:
        department.absent_threshold = absent_threshold
    if early_leave_threshold:
        department.early_leave_threshold = early_leave_threshold
    if late_leave_threshold:
        department.late_leave_threshold = late_leave_threshold
    if location is not None:
        department.location = location
    if distance_threshold is not None:
        department.distance_threshold = distance_threshold
    db.session.commit()
    return jsonify({'message': '部门信息更新成功'})

@bp.route('/api/admin/departments/<int:department_id>', methods=['DELETE'])
@jwt_required()
def delete_department(department_id):
    """删除部门"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'error': '部门不存在'}), 404
    db.session.delete(department)
    db.session.commit()
    return jsonify({'message': '部门删除成功'})

@bp.route('/api/admin/departments/<int:department_id>/users', methods=['GET'])
@jwt_required()
def get_department_users(department_id):
    """获取部门下的员工列表"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'error': '部门不存在'}), 404
    
    users = []
    for user in department.employees:
        user_data = {
            'id': user.id,
            'name': user.name,  # 姓名
            'phone': user.phone,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        users.append(user_data)
    
    return jsonify({
        'department': {
            'id': department.id,
            'name': department.name
        },
        'users': users,
        'total': len(users)
    })

@bp.route('/api/admin/attendance/stats', methods=['GET'])
@jwt_required()
def get_attendance_stats():
    """获取考勤统计信息"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    # 获取查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department_id = request.args.get('department_id')
    
    # 构建查询条件
    query = Attendance.query
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    if department_id:
        query = query.join(User).filter(User.department_id == department_id)
    
    records = query.all()
    
    # 统计信息
    total_records = len(records)
    on_time_count = len([r for r in records if r.status == '正常'])
    late_count = len([r for r in records if r.status == '迟到'])
    absent_count = len([r for r in records if r.status == '缺勤'])
    
    # 按日期统计
    daily_stats = {}
    for record in records:
        date_str = record.date.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {'正常': 0, '迟到': 0, '缺勤': 0}
        daily_stats[date_str][record.status] += 1
    
    return jsonify({
        'total_records': total_records,
        'on_time_count': on_time_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'daily_stats': daily_stats
    })

@bp.route('/api/admin/attendance/records', methods=['GET'])
@jwt_required()
def get_attendance_records():
    """获取考勤记录列表"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id')
    name = request.args.get('name')  # 员工姓名
    department_id = request.args.get('department_id')  # 部门ID
    date = request.args.get('date')  # 单个日期查询（保持兼容性）
    start_date = request.args.get('start_date')  # 起始日期
    end_date = request.args.get('end_date')  # 终止日期
    status = request.args.get('status')
    
    # 构建查询条件
    query = db.session.query(Attendance).join(User)
    
    if user_id:
        query = query.filter(Attendance.user_id == user_id)
    if name:
        query = query.filter(User.name.like(f'%{name}%'))
    if department_id:
        query = query.filter(User.department_id == department_id)
    
    # 日期查询逻辑：优先使用日期区间，如果没有则使用单个日期
    if start_date and end_date:
        # 使用日期区间查询
        query = query.filter(Attendance.date >= start_date, Attendance.date <= end_date)
    elif date:
        # 使用单个日期查询（保持兼容性）
        query = query.filter(Attendance.date == date)
    
    if status:
        query = query.filter(Attendance.status == status)
    
    # 分页查询
    pagination = query.order_by(Attendance.date.desc(), Attendance.time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    records = []
    for record in pagination.items:
        # 格式化位置信息
        formatted_location = format_location_display(record.location)
        
        record_data = {
            'id': record.id,
            'user_id': record.user_id,
            'name': record.user.name,  # 姓名
            'department': record.user.department.name if record.user.department else '',
            'date': record.date.strftime('%Y-%m-%d'),
            'check_type': record.check_type,
            'status': record.status,
            'time': record.time.strftime('%Y-%m-%d %H:%M:%S') if record.time else None,
            'location': formatted_location,
            'remark': record.remark or ''  # 返回数据库中的备注字段
        }
        
        records.append(record_data)
    
    return jsonify({
        'records': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@bp.route('/api/admin/departments/<int:department_id>', methods=['GET'])
@jwt_required()
def get_department_detail(department_id):
    """获取部门详细信息"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'error': '部门不存在'}), 404
    
    # 获取部门员工列表
    employees = []
    for user in department.employees:
        if user.role == 'user':  # 只返回普通员工，不包括管理员
            employee_data = {
                'id': user.id,
                'name': user.name,
                'phone': user.phone,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            employees.append(employee_data)
    
    return jsonify({
        'department': {
            'id': department.id,
            'name': department.name,
            'sign_in_time': department.sign_in_time,
            'sign_out_time': department.sign_out_time,
            'late_threshold': department.late_threshold,
            'absent_threshold': department.absent_threshold,
            'early_leave_threshold': department.early_leave_threshold,
            'late_leave_threshold': department.late_leave_threshold
        },
        'employees': employees,
        'total_employees': len(employees)
    })

@bp.route('/api/admin/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    today = date.today()
    current_time = datetime.now().time()
    
    # 获取所有部门
    departments = Department.query.all()
    department_stats = []
    current_time_minutes = time_to_minutes(current_time)
    
    for dept in departments:
        # 获取部门所有员工
        employees = User.query.filter_by(department_id=dept.id, role='user').all()
        total_employees = len(employees)
        
        # 获取今天的考勤记录
        today_attendances = db.session.query(Attendance).filter(
            Attendance.user_id.in_([emp.id for emp in employees]),
            Attendance.date == today
        ).all()
        
        # 按员工ID和类型组织考勤记录
        sign_in_records = {}
        sign_out_records = {}
        for attendance in today_attendances:
            if attendance.check_type == 'sign_in':
                sign_in_records[attendance.user_id] = attendance
            elif attendance.check_type == 'sign_out':
                sign_out_records[attendance.user_id] = attendance
        
        # 统计各种状态的人数
        sign_in_count = 0
        sign_out_count = 0
        late_count = 0
        absent_count = 0
        early_leave_count = 0
        late_leave_count = 0
        not_signed_in_count = 0
        not_signed_out_count = 0
        
        for employee in employees:
            # 判断签到状态
            sign_in_record = sign_in_records.get(employee.id)
            sign_in_status, check_type = determine_sign_in_status(dept, sign_in_record, current_time_minutes)
            
            if sign_in_status == 'normal':
                sign_in_count += 1
            elif sign_in_status == 'late':
                late_count += 1
            elif sign_in_status == 'absent':
                absent_count += 1
            elif check_type == 'not_signed_in':
                # 必须用check_type来判断
                not_signed_in_count += 1
            
            # 判断签退状态（只有已签到的员工才统计签退）
            if sign_in_record is not None:
                sign_out_record = sign_out_records.get(employee.id)
                sign_out_status, check_type = determine_sign_out_status(dept, sign_out_record, current_time_minutes)
                
                if sign_out_status == 'normal':
                    sign_out_count += 1
                elif sign_out_status == 'early_leave':
                    early_leave_count += 1
                elif sign_out_status == 'late_leave':
                    late_leave_count += 1
                elif check_type == 'not_signed_out':
                    # 已签到但未签退,必须用check_type来判断
                    not_signed_out_count += 1
        
        # 计算出勤率（正常签到的比例）
        attendance_rate = round((sign_in_count / total_employees * 100) if total_employees > 0 else 0, 1)
        
        department_stats.append({
            'department': {
                'id': dept.id,
                'name': dept.name
            },
            'total_employees': total_employees,
            'sign_in_count': sign_in_count,
            'sign_out_count': sign_out_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'early_leave_count': early_leave_count,
            'late_leave_count': late_leave_count,
            'not_signed_in_count': not_signed_in_count,
            'not_signed_out_count': not_signed_out_count,
            'attendance_rate': attendance_rate
        })
    
    # 计算总体统计
    total_employees = sum(stat['total_employees'] for stat in department_stats)
    total_sign_in = sum(stat['sign_in_count'] for stat in department_stats)
    total_sign_out = sum(stat['sign_out_count'] for stat in department_stats)
    total_late = sum(stat['late_count'] for stat in department_stats)
    total_absent = sum(stat['absent_count'] for stat in department_stats)
    total_early_leave = sum(stat['early_leave_count'] for stat in department_stats)
    total_late_leave = sum(stat['late_leave_count'] for stat in department_stats)
    total_not_signed_in = sum(stat['not_signed_in_count'] for stat in department_stats)
    total_not_signed_out = sum(stat['not_signed_out_count'] for stat in department_stats)
    print(total_absent)
    return jsonify({
        'departments': department_stats,
        'summary': {
            'total_employees': total_employees,
            'total_sign_in': total_sign_in,
            'total_sign_out': total_sign_out,
            'total_late': total_late,
            'total_absent': total_absent,
            'total_early_leave': total_early_leave,
            'total_late_leave': total_late_leave,
            'total_not_signed_in': total_not_signed_in,
            'total_not_signed_out': total_not_signed_out,
            'overall_attendance_rate': round((total_sign_in / total_employees * 100) if total_employees > 0 else 0, 1)
        }
    })

@bp.route('/api/admin/departments/<int:department_id>/attendance-detail', methods=['GET'])
@jwt_required()
def get_department_attendance_detail(department_id):
    """获取部门详细考勤分类数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'error': '部门不存在'}), 404
    
    from datetime import date, datetime
    
    today = date.today()
    current_time = datetime.now().time()
    
    # 获取部门所有员工
    employees = User.query.filter_by(department_id=department_id, role='user').all()
    employee_ids = [emp.id for emp in employees]
    current_time_minutes = time_to_minutes(current_time)
    
    # 获取今天的考勤记录
    today_attendances = db.session.query(Attendance).filter(
        Attendance.user_id.in_(employee_ids),
        Attendance.date == today
    ).all()
    
    # 按员工ID和类型组织考勤记录
    sign_in_records_dict = {}
    sign_out_records_dict = {}
    for attendance in today_attendances:
        if attendance.check_type == 'sign_in':
            sign_in_records_dict[attendance.user_id] = attendance
        elif attendance.check_type == 'sign_out':
            sign_out_records_dict[attendance.user_id] = attendance
    
    # 分类数据
    sign_in_records = []      # 正常签到
    sign_out_records = []     # 正常签退
    late_records = []         # 迟到
    early_leave_records = []  # 早退
    late_leave_records = []   # 晚退
    absent_records = []       # 缺勤
    not_signed_in_records = [] # 未签到
    not_signed_out_records = [] # 未签退
    
    # 处理每个员工的考勤状态
    for employee in employees:
        sign_in_record = sign_in_records_dict.get(employee.id)
        sign_out_record = sign_out_records_dict.get(employee.id)
        
        # 判断签到状态
        sign_in_status, check_type = determine_sign_in_status(department, sign_in_record, current_time_minutes)

        # 根据签到状态分类
        if sign_in_status == 'normal':
            # 正常签到
            record_data = {
                'id': sign_in_record.id,
                'user_id': employee.id,
                'name': employee.name,
                'phone': employee.phone,
                'time': sign_in_record.time.strftime('%Y-%m-%d %H:%M:%S'),
                'location': format_location_display(sign_in_record.location),
                'status': 'normal',
                'check_type': check_type,
                'remark': sign_in_record.remark or '正常签到'
            }
            sign_in_records.append(record_data)
        elif sign_in_status == 'late':
            # 迟到
            default_remark = '迟到' if check_type == 'sign_in' else '未签到，当前时间已经处于迟到时间，判定为迟到'
            record_data = {
                'id': sign_in_record.id if sign_in_record else None,
                'user_id': employee.id,
                'name': employee.name,
                'phone': employee.phone,
                'time': sign_in_record.time.strftime('%Y-%m-%d %H:%M:%S') if sign_in_record else None,
                'location': format_location_display(sign_in_record.location) if sign_in_record else None,
                'status': 'late',
                'check_type': check_type,
                'remark': (sign_in_record.remark if sign_in_record and sign_in_record.remark else default_remark)
            }
            late_records.append(record_data)
        elif sign_in_status == 'absent':
            # 缺勤
            default_remark = '缺勤' if check_type == 'sign_in' else '未签到，当前时间已经处于缺勤时间，判定为缺勤'
            record_data = {
                'id': sign_in_record.id if sign_in_record else None,
                'user_id': employee.id,
                'name': employee.name,
                'phone': employee.phone,
                'time': sign_in_record.time.strftime('%Y-%m-%d %H:%M:%S') if sign_in_record else None,
                'location': format_location_display(sign_in_record.location) if sign_in_record else None,
                'status': 'absent',
                'check_type': check_type,
                'remark': (sign_in_record.remark if sign_in_record and sign_in_record.remark else default_remark)
            }
            absent_records.append(record_data)
        elif sign_in_status == 'not_signed_in':
            # 未签到
            record_data = {
                'id': None,
                'user_id': employee.id,
                'name': employee.name,
                'phone': employee.phone,
                'time': None,
                'location': None,
                'status': 'not_signed_in',
                'check_type': check_type,  # 统一命名
                'remark': '今天还未签到'
            }
            not_signed_in_records.append(record_data)
        
        # 判断签退状态（只有已签到的员工才统计签退）
        if sign_in_record is not None:
            sign_out_status, check_type = determine_sign_out_status(department, sign_out_record, current_time_minutes)
            
            if sign_out_status == 'normal':
                # 正常签退
                record_data = {
                    'id': sign_out_record.id,
                    'user_id': employee.id,
                    'name': employee.name,
                    'phone': employee.phone,
                    'time': sign_out_record.time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': format_location_display(sign_out_record.location),
                    'status': 'normal',
                    'check_type': check_type,
                    'remark': sign_out_record.remark or '正常签退'
                }
                sign_out_records.append(record_data)
            elif sign_out_status == 'early_leave':
                # 早退
                record_data = {
                    'id': sign_out_record.id,
                    'user_id': employee.id,
                    'name': employee.name,
                    'phone': employee.phone,
                    'time': sign_out_record.time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': format_location_display(sign_out_record.location),
                    'status': 'early_leave',
                    'check_type': check_type,
                    'remark': sign_out_record.remark or '早退'
                }
                early_leave_records.append(record_data)
            elif sign_out_status == 'late_leave':
                # 晚退
                default_remark = '晚退' if check_type == 'sign_out' else '未签退，当前时间已经处于晚退时间，判定为晚退'
                record_data = {
                    'id': sign_out_record.id,
                    'user_id': employee.id,
                    'name': employee.name,
                    'phone': employee.phone,
                    'time': sign_out_record.time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': format_location_display(sign_out_record.location),
                    'status': 'late_leave',
                    'check_type': check_type,
                    'remark': sign_out_record.remark or default_remark
                }
                late_leave_records.append(record_data)
            elif sign_out_status == 'not_signed_out':
                # 已签到但未签退，创建未签退记录
                record_data = {
                    'id': None,  # 虚拟记录，没有实际ID
                    'user_id': employee.id,
                    'name': employee.name,
                    'phone': employee.phone,
                    'time': None,
                    'location': None,
                    'status': 'not_signed_out',
                    'check_type': check_type,  # 统一命名
                    'remark': '已签到但还未签退'
                }
                not_signed_out_records.append(record_data)
    
    # 计算统计信息
    total_employees = len(employees)
    sign_in_count = len(sign_in_records)
    sign_out_count = len(sign_out_records)
    late_count = len(late_records)
    early_leave_count = len(early_leave_records)
    late_leave_count = len(late_leave_records)
    absent_count = len(absent_records)
    not_signed_in_count = len(not_signed_in_records)
    not_signed_out_count = len(not_signed_out_records)
    print(absent_records)
    
    return jsonify({
        'department': {
            'id': department.id,
            'name': department.name
        },
        'date': today.strftime('%Y-%m-%d'),
        'sign_in_records': sign_in_records,      # 正常签到
        'sign_out_records': sign_out_records,    # 正常签退
        'late_records': late_records,            # 迟到
        'early_leave_records': early_leave_records,  # 早退
        'late_leave_records': late_leave_records,    # 晚退
        'absent_records': absent_records,        # 缺勤
        'not_signed_in_records': not_signed_in_records,  # 未签到
        'not_signed_out_records': not_signed_out_records,  # 未签退
        'summary': {
            'total_employees': total_employees,
            'sign_in_count': sign_in_count,
            'sign_out_count': sign_out_count,
            'late_count': late_count,
            'early_leave_count': early_leave_count,
            'late_leave_count': late_leave_count,
            'absent_count': absent_count,
            'not_signed_in_count': not_signed_in_count,
            'not_signed_out_count': not_signed_out_count
        }
    })

@bp.route('/api/admin/attendance/<int:attendance_id>/status', methods=['PUT'])
@jwt_required()
def update_attendance_status(attendance_id):
    """更新已有考勤记录的状态
    
    功能说明：
    - 只处理数据库中已存在的考勤记录
    - 修改记录的状态，并更新时间戳
    - 如需为没有记录的员工创建记录，请使用 makeup_attendance 接口
    """
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({'error': '考勤记录不存在'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': '状态不能为空'}), 400
    
    # 根据考勤类型验证状态值
    if attendance.check_type == 'sign_in':
        # 签到记录只能修改为这些状态
        valid_sign_in_statuses = ['normal', 'late', 'absent']
        if new_status not in valid_sign_in_statuses:
            return jsonify({'error': '签到记录只能修改为：正常、迟到、缺勤状态'}), 400
    elif attendance.check_type == 'sign_out':
        # 签退记录只能修改为这些状态
        valid_sign_out_statuses = ['normal', 'early_leave', 'late_leave']
        if new_status not in valid_sign_out_statuses:
            return jsonify({'error': '签退记录只能修改为：正常、早退、晚退状态'}), 400
    else:
        return jsonify({'error': f'不支持的考勤类型: {attendance.check_type}'}), 400
    
    # 保存原状态用于记录
    old_status = attendance.status
    
    # 更新状态和时间
    attendance.status = new_status
    current_time = datetime.now()
    attendance.time = current_time
    attendance.remark = f"[状态更新]: 从{old_status}更新为{new_status}, 更新时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
    db.session.commit()
    
    return jsonify({
        'message': '状态更新成功',
        'attendance': {
            'id': attendance.id,
            'user_id': attendance.user_id,
            'status': attendance.status,
            'check_type': attendance.check_type,
        }
    })

@bp.route('/api/admin/attendance/makeup', methods=['POST'])
@jwt_required()
def makeup_attendance():
    """管理员为没有考勤记录的员工补录记录
    
    功能说明：
    - 只处理虚拟类型：not_signed_in 和 not_signed_out
    - 为没有考勤记录的员工创建实际的考勤记录
    - 如需修改已有记录的状态，请使用 update_attendance_status 接口
    """
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403

    data = request.get_json()
    user_id = data.get('user_id')
    date_str = data.get('date')
    check_type = data.get('check_type', 'sign_in')
    status = data.get('status')
    time_str = data.get('time')
    location = data.get('location')

    if not user_id or not date_str or not status:
        return jsonify({'error': 'user_id、date、status为必填项'}), 400

    from datetime import datetime, date as dt_date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': '日期格式错误，应为YYYY-MM-DD'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 补录功能只处理虚拟类型（为没有记录的员工创建记录）
    if check_type not in ['not_signed_in', 'not_signed_out']:
        return jsonify({'error': '补录功能只支持not_signed_in和not_signed_out类型，如需修改已有记录请使用状态更新功能'}), 400

    # 验证状态和类型的合理性
    if check_type == 'not_signed_in':
        # 虚拟签到记录，用于处理未签到员工的状态变更
        # 只能补录为实际状态，不能补录为未签到（因为这是给未签到员工用的）
        valid_not_signed_in_statuses = ['normal', 'late', 'absent']
        if status not in valid_not_signed_in_statuses:
            return jsonify({'error': '未签到员工只能补录为正常、迟到或缺勤状态'}), 400
        
        # 检查当天是否已有真实的签到记录
        real_sign_in = Attendance.query.filter_by(user_id=user_id, date=date_obj, check_type='sign_in').first()
        if real_sign_in:
            return jsonify({'error': '员工当天已有签到记录，不能使用虚拟补录'}), 400
    elif check_type == 'not_signed_out':
        # 虚拟签退记录，用于处理已签到但未签退员工的状态变更
        # 只能补录为实际状态
        valid_not_signed_out_statuses = ['normal', 'early_leave', 'late_leave']
        if status not in valid_not_signed_out_statuses:
            return jsonify({'error': '未签退员工只能补录为正常、早退或晚退状态'}), 400
        
        # 必须要有签到记录才能补录虚拟签退
        sign_in_record = Attendance.query.filter_by(user_id=user_id, date=date_obj, check_type='sign_in').first()
        if not sign_in_record:
            return jsonify({'error': '员工当天未签到，不能补录签退记录'}), 400
        
        # 检查当天是否已有真实的签退记录
        real_sign_out = Attendance.query.filter_by(user_id=user_id, date=date_obj, check_type='sign_out').first()
        if real_sign_out:
            return jsonify({'error': '员工当天已有签退记录，不能使用虚拟补录'}), 400

    # 生成考勤时间 - 统一使用当前修改时间
    dt = datetime.now()  # 使用当前时间作为补录时间
    
    # 处理虚拟记录类型，转换为真实的check_type
    real_check_type = check_type
    if check_type == 'not_signed_in':
        real_check_type = 'sign_in'
    elif check_type == 'not_signed_out':
        real_check_type = 'sign_out'
    
    # 创建remark描述
    remark_text = f"[补录]: 补录{real_check_type}记录，状态为{status}，补录时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
    
    attendance = Attendance(
        user_id=user_id,
        date=date_obj,
        check_type=real_check_type,
        status=status,
        time=dt,
        location=location or '',
        remark=remark_text,
    )
    db.session.add(attendance)
    db.session.commit()

    return jsonify({
        'message': '补录成功',
        'attendance': {
            'id': attendance.id,
            'user_id': attendance.user_id,
            'date': attendance.date.strftime('%Y-%m-%d'),
            'check_type': check_type,  # 返回原始的check_type（可能是虚拟类型）
            'real_check_type': attendance.check_type,  # 实际存储的check_type
            'status': attendance.status,
            'time': attendance.time.strftime('%Y-%m-%d %H:%M:%S'),
            'location': attendance.location,
        }
    })

@bp.route('/api/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_detail(user_id):
    """获取单个用户详细信息"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    user_data = {
        'id': user.id,
        'name': user.name,
        'phone': user.phone,
        'role': user.role,
        'department_id': user.department_id,
        'department': {
            'id': user.department.id,
            'name': user.department.name
        } if user.department else None,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'face_data': {
            'id': user.face_data.id,
            'face_url': user.face_data.face_url,
            'has_features': user.face_data.get_features() is not None
        } if user.face_data else None
    }
    
    return jsonify({'user': user_data})

@bp.route('/api/admin/attendance/auto-check', methods=['POST'])
@jwt_required()
def run_auto_attendance_check():
    """手动执行自动考勤检查"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        today = datetime.now().date()
        current_time = datetime.now().time()
        
        absent_records_created = 0
        late_leave_records_created = 0
        details = []
        
        # 获取所有部门
        departments = Department.query.all()
        
        for dept in departments:
            dept_absent_count = 0
            dept_late_leave_count = 0
            
            # 处理缺勤记录
            if dept.absent_threshold:
                try:
                    absent_time = datetime.strptime(dept.absent_threshold, '%H:%M').time()
                    # 检查当前时间是否超过缺勤阈值
                    if current_time >= absent_time:
                        # 获取该部门所有员工
                        employees = User.query.filter_by(department_id=dept.id, role='user').all()
                        
                        for employee in employees:
                            # 检查今天是否已有签到记录
                            existing_sign_in = Attendance.query.filter_by(
                                user_id=employee.id,
                                date=today,
                                check_type='sign_in'
                            ).first()
                            
                            if not existing_sign_in:
                                # 没有签到记录，创建缺勤记录
                                absent_record = Attendance(
                                    user_id=employee.id,
                                    date=today,
                                    check_type='sign_in',
                                    status='absent',
                                    time=datetime.combine(today, absent_time),
                                    location='',
                                    remark=f'[系统自动]: 超过缺勤时间({dept.absent_threshold})未签到，自动标记为缺勤'
                                )
                                
                                db.session.add(absent_record)
                                absent_records_created += 1
                                dept_absent_count += 1
                                
                except ValueError:
                    continue
            
            # 处理晚退记录
            if dept.late_leave_threshold:
                try:
                    late_leave_time = datetime.strptime(dept.late_leave_threshold, '%H:%M').time()
                    # 检查当前时间是否超过晚退阈值
                    if current_time >= late_leave_time:
                        # 获取该部门所有员工
                        employees = User.query.filter_by(department_id=dept.id, role='user').all()
                        
                        for employee in employees:
                            # 检查今天是否已有签到记录
                            existing_sign_in = Attendance.query.filter_by(
                                user_id=employee.id,
                                date=today,
                                check_type='sign_in'
                            ).first()
                            
                            # 只有已签到的员工才处理晚退
                            if existing_sign_in:
                                # 检查今天是否已有签退记录
                                existing_sign_out = Attendance.query.filter_by(
                                    user_id=employee.id,
                                    date=today,
                                    check_type='sign_out'
                                ).first()
                                
                                if not existing_sign_out:
                                    # 没有签退记录，创建晚退记录
                                    late_leave_record = Attendance(
                                        user_id=employee.id,
                                        date=today,
                                        check_type='sign_out',
                                        status='late_leave',
                                        time=datetime.combine(today, late_leave_time),
                                        location='',
                                        remark=f'[系统自动]: 超过晚退时间({dept.late_leave_threshold})未签退，自动标记为晚退'
                                    )
                                    
                                    db.session.add(late_leave_record)
                                    late_leave_records_created += 1
                                    dept_late_leave_count += 1
                                    
                except ValueError:
                    continue
            
            # 记录部门详情
            if dept_absent_count > 0 or dept_late_leave_count > 0:
                details.append({
                    'department': dept.name,
                    'absent_count': dept_absent_count,
                    'late_leave_count': dept_late_leave_count
                })
        
        # 提交所有更改
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '自动考勤检查完成',
            'absent_records_created': absent_records_created,
            'late_leave_records_created': late_leave_records_created,
            'total_records_created': absent_records_created + late_leave_records_created,
            'details': details,
            'check_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'自动考勤检查失败: {str(e)}'
        }), 500

@bp.route('/api/admin/stats/attendance-distribution', methods=['GET'])
@jwt_required()
def get_attendance_distribution():
    """获取考勤状态分布数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取查询参数
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            query_date = datetime.now().date()
        
        # 统计各种考勤状态
        stats = {}
        
        # 统计签到状态
        sign_in_stats = db.session.query(
            Attendance.status,
            db.func.count(Attendance.id)
        ).filter(
            Attendance.date == query_date,
            Attendance.check_type == 'sign_in'
        ).group_by(Attendance.status).all()
        
        # 统计签退状态
        sign_out_stats = db.session.query(
            Attendance.status,
            db.func.count(Attendance.id)
        ).filter(
            Attendance.date == query_date,
            Attendance.check_type == 'sign_out'
        ).group_by(Attendance.status).all()
        
        # 初始化统计数据
        distribution = {
            'normal': 0,
            'late': 0,
            'absent': 0,
            'early_leave': 0,
            'late_leave': 0
        }
        
        # 合并签到统计
        for status, count in sign_in_stats:
            if status in distribution:
                distribution[status] += count
        
        # 合并签退统计
        for status, count in sign_out_stats:
            if status in distribution:
                distribution[status] += count
        
        # 转换为图表数据格式
        chart_data = [
            {'name': '正常', 'value': distribution['normal']},
            {'name': '迟到', 'value': distribution['late']},
            {'name': '缺勤', 'value': distribution['absent']},
            {'name': '早退', 'value': distribution['early_leave']},
            {'name': '晚退', 'value': distribution['late_leave']}
        ]
        
        return jsonify({
            'success': True,
            'date': date_str,
            'data': chart_data,
            'total': sum(distribution.values())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取考勤分布数据失败: {str(e)}'
        }), 500

@bp.route('/api/admin/stats/department-attendance-rate', methods=['GET'])
@jwt_required()
def get_department_attendance_rate():
    """获取部门出勤率对比数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取查询参数
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            query_date = datetime.now().date()
        
        departments = Department.query.all()
        department_stats = []
        
        for dept in departments:
            # 获取部门总员工数
            total_employees = User.query.filter_by(department_id=dept.id, role='user').count()
            if total_employees == 0:
                continue
            
            # 获取当日签到人数（正常+迟到）
            attended_count = Attendance.query.filter(
                Attendance.date == query_date,
                Attendance.check_type == 'sign_in',
                Attendance.status.in_(['normal', 'late']),
                Attendance.user_id.in_(
                    db.session.query(User.id).filter_by(department_id=dept.id, role='user')
                )
            ).count()
            
            # 计算出勤率
            attendance_rate = round((attended_count / total_employees) * 100, 2)
            
            department_stats.append({
                'department': dept.name,
                'total_employees': total_employees,
                'attended_count': attended_count,
                'attendance_rate': attendance_rate
            })
        
        return jsonify({
            'success': True,
            'date': date_str,
            'data': department_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取部门出勤率数据失败: {str(e)}'
        }), 500

@bp.route('/api/admin/stats/attendance-trend', methods=['GET'])
@jwt_required()
def get_attendance_trend():
    """获取出勤率趋势数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取查询参数（默认查询最近7天）
        days = int(request.args.get('days', 7))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # 跳过周末
            if current_date.weekday() < 5:  # 周一到周五
                # 获取总员工数
                total_employees = User.query.filter_by(role='user').count()
                
                if total_employees > 0:
                    # 获取当日出勤人数
                    attended_count = Attendance.query.filter(
                        Attendance.date == current_date,
                        Attendance.check_type == 'sign_in',
                        Attendance.status.in_(['normal', 'late'])
                    ).count()
                    
                    # 计算出勤率
                    attendance_rate = round((attended_count / total_employees) * 100, 2)
                    
                    trend_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'weekday': current_date.strftime('%m-%d'),
                        'attendance_rate': attendance_rate,
                        'attended_count': attended_count,
                        'total_employees': total_employees
                    })
            
            current_date += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'data': trend_data,
            'period': f'{start_date.strftime("%Y-%m-%d")} 到 {end_date.strftime("%Y-%m-%d")}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取出勤率趋势数据失败: {str(e)}'
        }), 500

@bp.route('/api/admin/stats/realtime-dashboard', methods=['GET'])
@jwt_required()
def get_realtime_dashboard():
    """获取实时考勤仪表盘数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        today = datetime.now().date()
        current_time = datetime.now()
        
        # 总员工数
        total_employees = User.query.filter_by(role='user').count()
        
        # 今日已签到人数
        signed_in_count = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_type == 'sign_in'
        ).count()
        
        # 今日已签退人数
        signed_out_count = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_type == 'sign_out'
        ).count()
        
        # 未签到人数
        not_signed_in_count = total_employees - signed_in_count
        
        # 未签退人数（已签到但未签退）
        not_signed_out_count = signed_in_count - signed_out_count
        
        # 迟到人数
        late_count = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_type == 'sign_in',
            Attendance.status == 'late'
        ).count()
        
        # 缺勤人数
        absent_count = Attendance.query.filter(
            Attendance.date == today,
            Attendance.check_type == 'sign_in',
            Attendance.status == 'absent'
        ).count()
        
        # 计算出勤率
        attendance_rate = round((signed_in_count / total_employees) * 100, 2) if total_employees > 0 else 0
        
        # 最近一小时签到数量
        one_hour_ago = current_time - timedelta(hours=1)
        recent_sign_ins = Attendance.query.filter(
            Attendance.check_type == 'sign_in',
            Attendance.time >= one_hour_ago
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_employees': total_employees,
                'signed_in_count': signed_in_count,
                'signed_out_count': signed_out_count,
                'not_signed_in_count': not_signed_in_count,
                'not_signed_out_count': not_signed_out_count,
                'late_count': late_count,
                'absent_count': absent_count,
                'attendance_rate': attendance_rate,
                'recent_sign_ins': recent_sign_ins,
                'update_time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取实时仪表盘数据失败: {str(e)}'
        }), 500

@bp.route('/api/admin/stats/location-distribution', methods=['GET'])
@jwt_required()
def get_location_distribution():
    """获取打卡地点分布数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取查询参数
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            query_date = datetime.now().date()
        
        # 查询当日所有打卡记录（有位置信息的）
        attendance_records = Attendance.query.filter(
            Attendance.date == query_date,
            Attendance.location != '',
            Attendance.location.isnot(None)
        ).all()
        
        location_stats = {}
        location_details = []
        
        for record in attendance_records:
            if record.location:
                # 解析位置信息
                location_display = format_location_display(record.location)
                
                if location_display not in location_stats:
                    location_stats[location_display] = 0
                location_stats[location_display] += 1
                
                # 添加详细记录
                location_details.append({
                    'user_name': record.user.name,
                    'location': location_display,
                    'check_type': record.check_type,
                    'status': record.status,
                    'time': record.time.strftime('%H:%M:%S')
                })
        
        # 转换为图表数据格式
        chart_data = [
            {'name': location, 'value': count}
            for location, count in location_stats.items()
        ]
        
        # 按数量排序
        chart_data.sort(key=lambda x: x['value'], reverse=True)
        
        return jsonify({
            'success': True,
            'date': date_str,
            'data': chart_data,
            'details': location_details,
            'total_records': len(attendance_records)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取打卡地点分布数据失败: {str(e)}'
        }), 500

@bp.route('/api/admin/stats/attendance-map', methods=['GET'])
@jwt_required()
def get_attendance_map_data():
    """获取打卡地图数据"""
    current_user = User.query.filter_by(id=int(get_jwt_identity())).first()
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取查询参数
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            query_date = datetime.now().date()
        
        # 查询当日所有打卡记录（有位置信息的）
        attendance_records = Attendance.query.filter(
            Attendance.date == query_date,
            Attendance.location != '',
            Attendance.location.isnot(None)
        ).all()
        
        # 分类处理签到和签退数据
        sign_in_data = []  # 签到类：签到、迟到、缺勤
        sign_out_data = []  # 签退类：签退、早退、晚退
        
        for record in attendance_records:
            if record.location:
                # 解析经纬度
                try:
                    coords_part = record.location.split(' (')[0] if '(' in record.location else record.location
                    if ',' in coords_part:
                        lat_str, lng_str = coords_part.split(',')
                        lat = float(lat_str.strip())
                        lng = float(lng_str.strip())
                        
                        # 获取地址显示
                        address = record.location.split(' (')[1].rstrip(')') if '(' in record.location else '未知地址'
                        
                        # 构建地图点数据
                        point_data = {
                            'id': record.id,
                            'user_name': record.user.name,
                            'user_id': record.user_id,
                            'lat': lat,
                            'lng': lng,
                            'address': address,
                            'time': record.time.strftime('%H:%M:%S'),
                            'status': record.status,
                            'check_type': record.check_type,
                            'remark': record.remark or ''
                        }
                        
                        # 分类：签到类包括签到、迟到、缺勤；签退类包括签退、早退、晚退
                        if record.check_type == 'sign_in':
                            sign_in_data.append(point_data)
                        elif record.check_type == 'sign_out':
                            sign_out_data.append(point_data)
                            
                except (ValueError, IndexError) as e:
                    # 跳过无效的位置数据
                    continue
        
        return jsonify({
            'success': True,
            'date': date_str,
            'sign_in_data': sign_in_data,
            'sign_out_data': sign_out_data,
            'total_records': len(sign_in_data) + len(sign_out_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取地图数据失败: {str(e)}'
        }), 500 