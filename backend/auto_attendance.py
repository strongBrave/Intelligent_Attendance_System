#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动考勤记录生成脚本
根据部门时间规则，自动为缺勤和晚退的员工创建考勤记录
"""

import os
import sys
import schedule
import time
from datetime import datetime, date, timedelta
from flask import Flask

# 确保能找到app模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Department, Attendance

def create_absent_records():
    """检查并创建缺勤记录"""
    print(f"[{datetime.now()}] 开始检查缺勤记录...")
    
    today = date.today()
    current_time = datetime.now().time()
    
    # 检查是否为工作日（周一到周五）
    if today.weekday() >= 5:  # 5=周六, 6=周日
        print(f"今天是周末（{today.strftime('%A')}），跳过缺勤检查")
        return
    
    # 获取所有部门
    departments = Department.query.all()
    
    for dept in departments:
        if not dept.absent_threshold:
            continue
            
        # 解析缺勤阈值时间
        try:
            absent_time = datetime.strptime(dept.absent_threshold, '%H:%M').time()
        except:
            print(f"部门 {dept.name} 的缺勤阈值时间格式错误: {dept.absent_threshold}")
            continue
        
        # 只有当前时间超过缺勤阈值时才处理
        if current_time < absent_time:
            continue
            
        print(f"处理部门: {dept.name}, 缺勤阈值: {dept.absent_threshold}")
        
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
                print(f"  创建缺勤记录: {employee.name} ({employee.phone})")
    
    db.session.commit()
    print(f"[{datetime.now()}] 缺勤记录检查完成\n")

def create_late_leave_records():
    """检查并创建晚退记录"""
    print(f"[{datetime.now()}] 开始检查晚退记录...")
    
    today = date.today()
    current_time = datetime.now().time()
    
    # 检查是否为工作日（周一到周五）
    if today.weekday() >= 5:  # 5=周六, 6=周日
        print(f"今天是周末（{today.strftime('%A')}），跳过晚退检查")
        return
    
    # 获取所有部门
    departments = Department.query.all()
    
    for dept in departments:
        if not dept.late_leave_threshold:
            continue
            
        # 解析晚退阈值时间
        try:
            late_leave_time = datetime.strptime(dept.late_leave_threshold, '%H:%M').time()
        except:
            print(f"部门 {dept.name} 的晚退阈值时间格式错误: {dept.late_leave_threshold}")
            continue
        
        # 只有当前时间超过晚退阈值时才处理
        if current_time < late_leave_time:
            continue
            
        print(f"处理部门: {dept.name}, 晚退阈值: {dept.late_leave_threshold}")
        
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
            if not existing_sign_in:
                continue
                
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
                print(f"  创建晚退记录: {employee.name} ({employee.phone})")
    
    db.session.commit()
    print(f"[{datetime.now()}] 晚退记录检查完成\n")

def run_auto_attendance():
    """运行自动考勤检查"""
    try:
        # 创建缺勤记录
        create_absent_records()
        
        # 创建晚退记录
        create_late_leave_records()
        
    except Exception as e:
        print(f"[{datetime.now()}] 自动考勤检查出错: {e}")

def setup_schedule():
    """设置定时任务"""
    # 每天多个时间点检查，确保不遗漏
    schedule.every().day.at("10:30").do(run_auto_attendance)  # 上午检查缺勤
    schedule.every().day.at("12:00").do(run_auto_attendance)  # 中午检查
    schedule.every().day.at("15:00").do(run_auto_attendance)  # 下午检查
    schedule.every().day.at("18:30").do(run_auto_attendance)  # 下班后检查晚退
    schedule.every().day.at("20:00").do(run_auto_attendance)  # 晚上检查
    schedule.every().day.at("22:00").do(run_auto_attendance)  # 夜间检查
    
    print("定时任务已设置:")
    print("- 10:30 检查缺勤记录")
    print("- 12:00 中午检查")
    print("- 15:00 下午检查") 
    print("- 18:30 检查晚退记录")
    print("- 20:00 晚上检查")
    print("- 22:00 夜间检查")

def run_once():
    """手动运行一次检查（用于测试）"""
    print("=" * 50)
    print("手动执行自动考勤检查")
    print("=" * 50)
    run_auto_attendance()

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 手动运行一次
        run_once()
        return
    
    # 启动定时任务
    print("=" * 50)
    print("自动考勤系统启动")
    print("=" * 50)
    
    setup_schedule()
    
    print(f"\n[{datetime.now()}] 系统启动完成，等待定时任务...")
    print("按 Ctrl+C 停止程序\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] 程序已停止")

if __name__ == "__main__":
    # 确保在Flask应用上下文中运行
    app = create_app()
    with app.app_context():
        main() 