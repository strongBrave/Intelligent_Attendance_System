#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Department, FaceData, Attendance

def insert_initial_data():
    """插入初始数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查是否已有数据
            existing_depts = Department.query.all()
            if existing_depts:
                print(f"数据库中已有 {len(existing_depts)} 个部门")
                for dept in existing_depts:
                    print(f"  - {dept.name}")
                return
            
            print("开始插入初始数据...")
            
            # 创建默认部门
            default_dept = Department(
                name='技术部',
                sign_in_time='09:00',
                sign_out_time='18:00',
                late_threshold='09:30',
                absent_threshold='10:00',
                early_leave_threshold='17:30'
            )
            
            hr_dept = Department(
                name='人事部',
                sign_in_time='08:30',
                sign_out_time='17:30',
                late_threshold='08:45',
                absent_threshold='09:15',
                early_leave_threshold='17:15'
            )
            
            finance_dept = Department(
                name='财务部',
                sign_in_time='09:00',
                sign_out_time='18:00',
                late_threshold='09:30',
                absent_threshold='10:00',
                early_leave_threshold='17:30'
            )
            
            db.session.add(default_dept)
            db.session.add(hr_dept)
            db.session.add(finance_dept)
            db.session.commit()
            print("✓ 默认部门创建成功")
            
            # 检查是否已有管理员
            existing_admin = User.query.filter_by(role='admin').first()
            if existing_admin:
                print(f"管理员已存在: {existing_admin.name} ({existing_admin.phone})")
            else:
                # 创建默认管理员账户
                from werkzeug.security import generate_password_hash
                
                admin = User(
                    name='管理员',
                    phone='13800138000',
                    password=generate_password_hash('admin123'),
                    role='admin',
                    department_id=default_dept.id
                )
                
                db.session.add(admin)
                db.session.commit()
                print("✓ 默认管理员账户创建成功")
                print("管理员手机号: 13800138000")
                print("管理员密码: admin123")
            
            print("\n✓ 初始数据插入完成！")
            
        except Exception as e:
            print(f"✗ 插入初始数据失败: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    insert_initial_data() 