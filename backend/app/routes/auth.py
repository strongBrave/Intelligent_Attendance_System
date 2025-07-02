from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
import random
import string
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import re

bp = Blueprint('auth', __name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 验证码存储（在生产环境中应该使用Redis）
captcha_store = {}

def generate_captcha_text(length=4):
    """生成随机验证码文本"""
    # 使用数字和大写字母，避免容易混淆的字符
    chars = string.ascii_uppercase + string.digits
    # 排除容易混淆的字符
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    return ''.join(random.choice(chars) for _ in range(length))

def validate_password_strength(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    
    return True, "密码强度符合要求"

def create_captcha_image(text, width=120, height=40):
    """创建验证码图片"""
    # 创建图片
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 添加干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='lightgray')
    
    # 添加干扰点
    for i in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='lightgray')
    
    # 绘制验证码文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype('arial.ttf', 24)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 计算文字位置
    text_width = draw.textlength(text, font=font)
    text_height = 24
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文字，每个字符稍微旋转
    for i, char in enumerate(text):
        char_x = x + i * (text_width // len(text))
        char_y = y + random.randint(-3, 3)
        # 随机颜色
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((char_x, char_y), char, font=font, fill=color)
    
    # 转换为base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

@bp.route('/api/verify-old-password', methods=['POST'])
def verify_old_password():
    """验证原密码"""
    try:
        data = request.json
        phone = data.get('phone')
        old_password = data.get('old_password')
        
        if not phone or not old_password:
            return jsonify({'msg': '手机号和密码不能为空'}), 400
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify({'msg': '手机号格式不正确'}), 400
        
        # 查找用户
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'msg': '该手机号未注册'}), 404
        
        # 验证原密码
        if not check_password_hash(user.password, old_password):
            logger.warning(f"找回密码验证失败: 手机号 {phone} - 原密码错误")
            return jsonify({'msg': '原密码错误'}), 401
        
        logger.info(f"找回密码验证成功: {user.name} ({phone})")
        
        return jsonify({
            'msg': '验证成功',
            'phone': phone,
            'user_name': user.name
        })
        
    except Exception as e:
        logger.error(f"验证原密码失败: {str(e)}")
        return jsonify({'msg': '验证失败'}), 500

@bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.json
        phone = data.get('phone')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not phone or not new_password or not confirm_password:
            return jsonify({'msg': '请填写完整信息'}), 400
        
        # 验证两次密码是否一致
        if new_password != confirm_password:
            return jsonify({'msg': '两次输入的密码不一致'}), 400
        
        # 验证密码强度
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'msg': message}), 400
        
        # 查找用户
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'msg': '用户不存在'}), 404
        
        # 更新密码
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        logger.info(f"密码重置成功: {user.name} ({phone})")
        
        return jsonify({'msg': '密码重置成功'})
        
    except Exception as e:
        logger.error(f"重置密码失败: {str(e)}")
        return jsonify({'msg': '重置密码失败'}), 500

@bp.route('/api/captcha', methods=['GET'])
def get_captcha():
    """获取验证码"""
    try:
        # 生成验证码文本
        captcha_text = generate_captcha_text(4)
        
        # 创建验证码图片
        captcha_image = create_captcha_image(captcha_text)
        
        # 生成唯一ID
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # 存储验证码（5分钟有效期）
        captcha_store[captcha_id] = {
            'text': captcha_text,
            'created_at': datetime.now(),
            'expires_at': datetime.now().timestamp() + 300  # 5分钟
        }
        
        # 清理过期的验证码
        current_time = datetime.now().timestamp()
        expired_keys = [k for k, v in captcha_store.items() if v['expires_at'] < current_time]
        for key in expired_keys:
            del captcha_store[key]
        
        logger.info(f"生成验证码: {captcha_id} -> {captcha_text}")
        
        return jsonify({
            'captcha_id': captcha_id,
            'captcha_image': f'data:image/png;base64,{captcha_image}'
        })
        
    except Exception as e:
        logger.error(f"生成验证码失败: {str(e)}")
        return jsonify({'error': '生成验证码失败'}), 500

@bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')  # 姓名
    password = data.get('password')
    phone = data.get('phone')
    if not name or not password or not phone:
        return jsonify({'msg': '信息不完整'}), 400
    
    # 密码强度验证
    if len(password) < 6:
        return jsonify({'msg': '密码长度至少6位'}), 400
    
    if User.query.filter_by(phone=phone).first():
        return jsonify({'msg': '手机号已存在'}), 400
    
    user = User(name=name, password=generate_password_hash(password), phone=phone)
    db.session.add(user)
    db.session.commit()
    
    # 记录注册日志
    logger.info(f"新用户注册: {name} ({phone})")
    
    return jsonify({'msg': '注册成功'})

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')  # 使用手机号登录
    password = data.get('password')
    captcha_id = data.get('captcha_id')
    captcha_text = data.get('captcha_text')
    
    if not phone or not password:
        return jsonify({'msg': '手机号和密码不能为空'}), 400
    
    # 验证验证码
    if not captcha_id or not captcha_text:
        return jsonify({'msg': '请输入验证码'}), 400
    
    # 检查验证码是否存在且未过期
    if captcha_id not in captcha_store:
        return jsonify({'msg': '验证码已过期，请重新获取'}), 400
    
    captcha_data = captcha_store[captcha_id]
    current_time = datetime.now().timestamp()
    
    if captcha_data['expires_at'] < current_time:
        # 删除过期验证码
        del captcha_store[captcha_id]
        return jsonify({'msg': '验证码已过期，请重新获取'}), 400
    
    # 验证验证码文本（不区分大小写）
    if captcha_text.upper() != captcha_data['text'].upper():
        # 删除已使用的验证码
        del captcha_store[captcha_id]
        logger.warning(f"验证码错误: 手机号 {phone}, 输入: {captcha_text}, 正确: {captcha_data['text']}")
        return jsonify({'msg': '验证码错误'}), 400
    
    # 删除已使用的验证码
    del captcha_store[captcha_id]
    
    user = User.query.filter_by(phone=phone).first()
    if not user or not check_password_hash(user.password, password):
        # 记录登录失败日志
        logger.warning(f"登录失败: 手机号 {phone} - 密码错误或用户不存在")
        return jsonify({'msg': '手机号或密码错误'}), 401
    
    # 记录成功登录日志
    logger.info(f"用户登录成功: {user.name} ({phone})")
    
    # 使用flask_jwt_extended创建token，将user.id转换为字符串
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'token': access_token, 
        'user': {
            'id': user.id, 
            'name': user.name,  # 返回姓名
            'phone': user.phone,
            'role': user.role,
            'department': {
                'id': user.department.id if user.department else None,
                'name': user.department.name if user.department else None
            } if user.department else None
        }
    })

@bp.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    
    return jsonify({
        'id': user.id,
        'name': user.name,  # 返回姓名
        'phone': user.phone,
        'role': user.role,
        'department': {
            'id': user.department.id if user.department else None,
            'name': user.department.name if user.department else None
        } if user.department else None
    }) 