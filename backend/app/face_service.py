import os
import json
import numpy as np
import cv2
from PIL import Image
from scipy.datasets import face
import torch
import requests
import base64
from io import BytesIO
from facenet_pytorch import MTCNN
from .models import db, User, FaceData, Attendance

class FaceService:
    def __init__(self):
        """初始化人脸识别服务"""
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        # 初始化MTCNN人脸检测器（只用于人脸检测，不用于特征提取）
        self.mtcnn = MTCNN(keep_all=False, device=self.device)
        
        # 云端特征提取API配置
        # 访问云端需要先映射端口，否则无法访问，ssh -p 11265 -L 5001:127.0.0.1:4999 root@connect.cqa1.seetacloud.com
        self.cloud_api_url = "http://127.0.0.1:5001/extract_features"
        self.cloud_api_timeout = int(os.getenv('CLOUD_API_TIMEOUT', '30'))  # 30秒超时
        
        # 设置相似度阈值
        self.similarity_threshold = 0.6
        
        # 创建上传目录
        self.upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'faces')
        os.makedirs(self.upload_folder, exist_ok=True)

    def _image_to_base64(self, image):
        """将PIL Image转换为base64字符串"""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def _call_cloud_feature_api(self, image_base64):
        """调用云端特征提取API"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            # 移除None值的headers
            headers = {k: v for k, v in headers.items() if v is not None}
            
            payload = {
                'image_data': image_base64,
                'format': 'base64'
            }
            
            response = requests.post(
                self.cloud_api_url,
                json=payload,
                headers=headers,
                timeout=self.cloud_api_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    features = np.array(result.get('features', []))
                    return features if len(features) > 0 else None
                else:
                    print(f"云端API返回错误: {result.get('error', 'Unknown error')}")
                    return None
            else:
                print(f"云端API请求失败: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("云端API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"云端API请求异常: {str(e)}")
            return None
        except Exception as e:
            print(f"云端特征提取失败: {str(e)}")
            return None

    def extract_face_features(self, image_data):
        """从图片数据中提取人脸特征向量（使用云端模型）"""
        try:
            # 将图片数据转换为PIL Image
            if isinstance(image_data, str):
                # 如果是文件路径
                image = Image.open(image_data).convert('RGB')
            else:
                # 如果是二进制数据
                image = Image.open(image_data).convert('RGB')
            
            # 使用MTCNN检测人脸
            face = self.mtcnn(image)
            if face is None:
                return None, None
            
            # 获取人脸框坐标
            boxes, _ = self.mtcnn.detect(image)
            face_box = None
            if boxes is not None and len(boxes) > 0:
                # 取第一个检测到的人脸框
                face_box = boxes[0].tolist()  # [x1, y1, x2, y2]
            
            # 将检测到的人脸转换为PIL Image
            face_tensor = face.permute(1, 2, 0)  # 转换维度 (C, H, W) -> (H, W, C)
            face_tensor = (face_tensor + 1) / 2 * 255  # 归一化到0-255
            face_array = face_tensor.cpu().numpy().astype(np.uint8)
            face_image = Image.fromarray(face_array)
            
            # 将人脸图片转换为base64
            face_base64 = self._image_to_base64(face_image)
            
            # 调用云端API提取特征
            features = self._call_cloud_feature_api(face_base64)
            
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
            "model": "Cloud-based Feature Extraction",
            "api_url": self.cloud_api_url,
            "feature_dim": "Variable (depends on cloud model)",
            "similarity_threshold": self.similarity_threshold,
            "device": str(self.device),
            "local_detection": "MTCNN"
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

    # 测试云端API连接
    def test_cloud_api_connection(self):
        """测试云端API连接"""
        try:
            # 创建一个简单的测试图片
            test_image = Image.new('RGB', (160, 160), color='white')
            test_base64 = self._image_to_base64(test_image)
            
            # 调用API
            features = self._call_cloud_feature_api(test_base64)
            
            if features is not None:
                return True, f"云端API连接成功，特征维度: {len(features)}"
            else:
                return False, "云端API连接失败"
                
        except Exception as e:
            return False, f"云端API测试失败: {str(e)}"

# 创建全局实例
face_service = FaceService() 
# face_service.test_cloud_api_connection() // test cloud api connection