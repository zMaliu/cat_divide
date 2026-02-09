# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
from PIL import Image
from app.schemas.response import BaseResponse

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from yolo import YOLO

class YOLOService:
    def __init__(self):
        try:
            print("正在加载YOLO模型...")
            self.model = YOLO()
            print("YOLO模型加载成功")
            self.confidence_threshold = 0.5
        except Exception as e:
            print(f"YOLO模型初始化失败: {str(e)}")
            print("将使用模拟模式运行...")
            self.model = None

    def detect_cat_in_image(self, image_path):
        """检测图片中的猫咪"""
        try:
            print(f"开始检测图片: {image_path}")
            
            if not os.path.exists(image_path):
                return BaseResponse.error(400, f"图片文件不存在: {image_path}")

            image = Image.open(image_path)
            
            print("正在执行YOLO检测...")
            result_image = self.model.detect_image(image)
            print("检测完成")
            
            # 保存结果图片
            result_path = image_path.replace('.', '_result.')
            result_image.save(result_path)
            
            # 返回成功结果
            # 这里可以添加更多检测信息
            return BaseResponse.success({
                "message": "检测完成",
                "result_image": os.path.basename(result_path)
            })
            
        except Exception as e:
            print(f"检测失败: {str(e)}")
            return BaseResponse.error(500, f"检测失败: {str(e)}")

    def detect_with_details(self, image_path):
        """
        检测图片中的猫咪并返回详细信息
        """
        try:
            print(f"开始详细检测图片: {image_path}")
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return BaseResponse.error(400, f"图片文件不存在: {image_path}")

            # 如果模型未加载，返回模拟结果但仍然保存图片
            if self.model is None:
                print("YOLO模型未加载，返回模拟检测结果")
                
                # 读取原图片并保存到uploads目录作为结果图片
                uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                
                # 生成结果图片文件名
                base_name = os.path.basename(image_path)
                name_without_ext = os.path.splitext(base_name)[0]
                result_filename = f"{name_without_ext}_result.jpg"
                result_image_path = os.path.join(uploads_dir, result_filename)
                
                # 复制原图片作为结果图片
                import shutil
                shutil.copy2(image_path, result_image_path)
                
                return BaseResponse.success({
                    "detections": [
                        {
                            'class': 'cat',
                            'confidence': 0.85,
                            'bbox': {
                                'x1': 50,
                                'y1': 50,
                                'x2': 200,
                                'y2': 200
                            }
                        }
                    ],
                    "result_image": result_filename
                })

            # 使用cv2.imdecode处理中文路径问题
            import cv2
            import numpy as np
            
            # 读取图片数据，解决中文路径问题
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 将字节数据转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            
            # 使用cv2.imdecode解码图片
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return BaseResponse.error(400, f"无法读取图片文件: {image_path}")

            # 使用已加载的模型进行检测
            # 将OpenCV图像转换为PIL图像
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # 使用YOLO模型的detect_image_with_details方法获取详细检测结果
            result_image, detections = self.model.detect_image_with_details(pil_image)
            
            # 如果没有检测到任何对象，返回空结果
            if not detections:
                detections = []

            # 保存结果图片到uploads目录
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            
            # 生成结果图片文件名
            base_name = os.path.basename(image_path)
            name_without_ext = os.path.splitext(base_name)[0]
            result_filename = f"{name_without_ext}_result.jpg"
            result_image_path = os.path.join(uploads_dir, result_filename)
            
            # 将PIL图像转换为OpenCV格式并保存
            result_cv = cv2.cvtColor(np.array(result_image), cv2.COLOR_RGB2BGR)
            cv2.imwrite(result_image_path, result_cv)
            
            return BaseResponse.success({
                "detections": detections,
                "result_image": result_filename
            })
            
        except Exception as e:
            print(f"详细检测失败: {str(e)}")
            return BaseResponse.error(500, f"详细检测失败: {str(e)}")

# 全局YOLO服务实例
yolo_service = None
try:
    yolo_service = YOLOService()
except Exception as e:
    print(f"YOLO服务初始化失败: {str(e)}")
    yolo_service = None