
from ultralytics import YOLO
from app.schemas.response import BaseResponse
import uuid
import cv2
from PIL import Image
import numpy as np
import os

class YOLOService:
    def __init__(self):
        try:
            # 加载训练好的权重文件
            #weights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "best_epoch_weights.pt")
            weights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "best_epoch_weights.pt")
            print(f"尝试加载权重文件: {weights_path}")
            
            if not os.path.exists(weights_path):
                raise FileNotFoundError(f"权重文件不存在: {weights_path}")

            print("开始加载YOLO模型...")
            self.model = YOLO(weights_path)
            print("YOLO模型加载成功")
            
            self.confidence_threshold = 0.5
            
        except Exception as e:
            print(f"YOLO模型初始化失败: {str(e)}")
            self.model = None

    def detect_cat_in_image(self, image_path):
        """
        在图片中检测猫咪并返回结果
        """
        try:
            print(f"开始检测图片: {image_path}")
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return BaseResponse.error(400, f"图片文件不存在: {image_path}")

            
            # 运行检测
            print("运行YOLO检测...")
            results = self.model(image_path, conf=self.confidence_threshold)
            print(f"检测完成，结果数量: {len(results)}")

            # 处理结果
            detections = []
            for i, result in enumerate(results):
                print(f"处理结果 {i+1}")
                boxes = result.boxes
                if boxes is not None:
                    for j, box in enumerate(boxes):
                        try:
                            detection = {
                                'class': result.names[int(box.cls[0])] if hasattr(result, 'names') and result.names else 'cat',
                                'confidence': float(box.conf[0]),
                                'bbox': {
                                    'x1': int(box.xyxy[0][0]),
                                    'y1': int(box.xyxy[0][1]),
                                    'x2': int(box.xyxy[0][2]),
                                    'y2': int(box.xyxy[0][3])
                                }
                            }
                            detections.append(detection)
                            print(f"添加检测结果 {j+1}: {detection}")
                        except Exception as box_error:
                            print(f"处理检测框时出错: {str(box_error)}")
                            continue

            print(f"最终检测结果数量: {len(detections)}")
            return BaseResponse.success({"detections": detections})
        except Exception as e:
            print(f"检测过程中发生错误: {str(e)}")
            return BaseResponse.error(500, f"检测失败: {str(e)}")

# 创建全局实例
yolo_service = YOLOService() if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "best_epoch_weights.pt")) else None