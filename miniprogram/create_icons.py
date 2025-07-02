#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建微信小程序图标文件
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(text, filename, color=(102, 126, 234), size=(81, 81)):
    """创建简单的图标"""
    # 创建图像
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    circle_bbox = (5, 5, size[0]-5, size[1]-5)
    draw.ellipse(circle_bbox, fill=color)
    
    # 添加文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # 使用默认字体
        font = ImageFont.load_default()
    
    # 计算文字位置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # 绘制文字
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # 保存图片
    img.save(filename, 'PNG')
    print(f"创建图标: {filename}")

def main():
    """主函数"""
    # 确保images目录存在
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # 图标配置
    icons = [
        ("打卡", "attendance.png", (102, 126, 234)),  # 蓝色
        ("打卡", "attendance-active.png", (102, 126, 234)),  # 蓝色
        ("日历", "calendar.png", (153, 153, 153)),  # 灰色
        ("日历", "calendar-active.png", (102, 126, 234)),  # 蓝色
        ("统计", "stats.png", (153, 153, 153)),  # 灰色
        ("统计", "stats-active.png", (102, 126, 234)),  # 蓝色
        ("我的", "profile.png", (153, 153, 153)),  # 灰色
        ("我的", "profile-active.png", (102, 126, 234)),  # 蓝色
    ]
    
    # 创建图标
    for text, filename, color in icons:
        filepath = os.path.join(images_dir, filename)
        create_icon(text, filepath, color)
    
    print("所有图标创建完成！")
    print("现在可以在app.json中恢复tabBar配置了。")

if __name__ == "__main__":
    main() 