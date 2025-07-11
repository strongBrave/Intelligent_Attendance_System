import os
import json
import numpy as np
import cv2
from PIL import Image
import torch
from io import BytesIO
from facenet_pytorch import MTCNN, InceptionResnetV1
from .models import db, User, FaceData, Attendance

class FaceService:
    def __init__(self):
        """初始化人脸识别服务"""
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        # 初始化MTCNN人脸检测器
        self.mtcnn = MTCNN(
            image_size=160, 
            margin=0, 
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], 
            factor=0.709, 
            post_process=True,
            device=self.device
        )
        
        # 初始化FaceNet特征提取模型
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # 设置相似度阈值
        self.similarity_threshold = 0.6  # 调整阈值，facenet通常使用较低阈值
        
        # 创建上传目录
        self.upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
        os.makedirs(self.upload_folder, exist_ok=True)

    def extract_face_features(self, image_data):
        """从图片数据中提取人脸特征向量（使用本地FaceNet模型）"""
        try:
            # 将图片数据转换为PIL Image
            if isinstance(image_data, str):
                # 如果是文件路径
                image = Image.open(image_data).convert('RGB')
            else:
                # 如果是二进制数据
                image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # 使用MTCNN检测和裁剪人脸
            face_tensor = self.mtcnn(image)
            if face_tensor is None:
                return None, None
            
            # 获取人脸框坐标（用于调试或显示）
            boxes, _ = self.mtcnn.detect(image)
            face_box = None
            if boxes is not None and len(boxes) > 0:
                # 取第一个检测到的人脸框
                face_box = boxes[0].tolist()  # [x1, y1, x2, y2]
            
            # 添加batch维度并移到设备
            face_tensor = face_tensor.unsqueeze(0).to(self.device)
            
            # 使用FaceNet提取特征
            with torch.no_grad():
                embeddings = self.resnet(face_tensor)
                # 转换为numpy数组
                features = embeddings.cpu().numpy().flatten()
            
            return features, face_box
            
        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            return None, None

    def calculate_similarity(self, features1, features2):
        """计算两个特征向量的余弦相似度"""
        try:
            # 归一化特征向量
            features1_norm = features1 / np.linalg.norm(features1)
            features2_norm = features2 / np.linalg.norm(features2)
            
            # 计算余弦相似度
            similarity = np.dot(features1_norm, features2_norm)
            return float(similarity)
            
        except Exception as e:
            return 0.0

    def process_multiple_faces(self, image_data_list, user_id):
        """处理多张人脸图片，计算平均特征向量"""
        try:
            features_list = []
            
            for i, image_data in enumerate(image_data_list):
                features, _ = self.extract_face_features(image_data)
                if features is not None:
                    features_list.append(features)
            
            if not features_list:
                return None
            
            if len(features_list) == 1:
                return features_list[0]
            
            # 计算平均特征向量
            average_features = np.mean(features_list, axis=0)
            return average_features
            
        except Exception as e:
            return None

    def calculate_average_features(self, features_list):
        """计算多个特征向量的平均值"""
        try:
            if not features_list:
                return None
            
            if len(features_list) == 1:
                return features_list[0]
            
            # 计算平均特征向量
            average_features = np.mean(features_list, axis=0)
            return average_features
            
        except Exception as e:
            return None

    def verify_face(self, current_features, user_id):
        """验证人脸是否匹配"""
        try:
            # 获取用户的人脸特征
            user_faces = self.get_user_faces(user_id)
            if not user_faces:
                return False, 0.0
            
            # 计算最大相似度
            max_similarity = 0.0
            for user_face in user_faces:
                user_features = user_face.get_features()
                if user_features is not None:
                    similarity = self.calculate_similarity(current_features, user_features)
                    max_similarity = max(max_similarity, similarity)
            
            # 判断是否匹配
            is_match = max_similarity >= self.similarity_threshold
            return is_match, max_similarity
            
        except Exception as e:
            return False, 0.0

    def process_attendance_face(self, image_data, user_id, session, User, FaceData, Attendance):
        """处理考勤时的人脸验证"""
        try:
            # 提取当前图片的特征向量
            current_features, face_box = self.extract_face_features(image_data)
            if current_features is None:
                return False, "未检测到人脸或特征提取失败，请重试", 0.0, None
            
            # 验证人脸
            is_match, similarity = self.verify_face(current_features, user_id)
            
            if not is_match:
                return False, f"人脸验证失败，相似度: {similarity:.4f}", similarity, face_box
            
            return True, "人脸验证成功", similarity, face_box
            
        except Exception as e:
            return False, f"人脸验证处理失败: {str(e)}", 0.0, None

    def get_user_faces(self, user_id):
        """获取用户的人脸数据"""
        try:
            user = User.query.get(user_id)
            if not user:
                return []
            
            if not user.face_data:
                return []
            
            return [user.face_data]
            
        except Exception as e:
            return []

    def get_model_info(self):
        """获取模型信息"""
        return {
            "model": "FaceNet (facenet-pytorch)",
            "detection_model": "MTCNN",
            "feature_extraction_model": "InceptionResnetV1 (VGGFace2)",
            "feature_dim": 512,
            "similarity_threshold": self.similarity_threshold,
            "device": str(self.device),
            "local_processing": True
        }

    def detect_faces_with_boxes(self, image_data):
        """检测图片中的人脸并返回坐标框"""
        try:
            # 将图片数据转换为PIL Image
            if isinstance(image_data, str):
                image = Image.open(image_data).convert('RGB')
            else:
                image = Image.open(image_data).convert('RGB')
            
            # 获取图片尺寸
            image_width, image_height = image.size
            
            # 检测人脸框
            boxes, probs = self.mtcnn.detect(image)
            
            if boxes is None:
                return [], image_width, image_height
            
            # 转换坐标格式
            face_boxes = []
            for i, box in enumerate(boxes):
                face_boxes.append({
                    'box': box.tolist(),  # [x1, y1, x2, y2]
                    'confidence': float(probs[i]) if probs is not None else 1.0
                })
            
            return face_boxes, image_width, image_height
            
        except Exception as e:
            return [], 0, 0

    def test_model_functionality(self):
        """测试本地模型功能"""
        try:
            # 创建一个简单的测试图片，模拟人脸
            test_image = Image.new('RGB', (224, 224), color=(128, 128, 128))
            
            # 尝试检测人脸（期望失败，因为是空白图片）
            face_tensor = self.mtcnn(test_image)
            
            # 测试模型是否正确加载
            model_device = next(self.resnet.parameters()).device
            model_loaded = True
            
            return True, f"本地模型测试成功 - 设备: {model_device}, FaceNet已加载: {model_loaded}"
                
        except Exception as e:
            return False, f"本地模型测试失败: {str(e)}"

# 创建全局实例
face_service = FaceService()