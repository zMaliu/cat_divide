
import os
from ultralytics import YOLO
from app.schemas.response import BaseResponse
import uuid
import cv2
from PIL import Image
import numpy as np

class YOLOService:
    def __init__(self):
        # 加载训练好的权重文件
        weights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "best_epoch_weights.pt")
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"权重文件不存在: {weights_path}")

        self.model = YOLO(weights_path)
        self.confidence_threshold = 0.5

    def detect_cat_in_image(self, image_path):
        """
        在图片中检测猫咪并返回结果
        """
        try:
            # 运行检测
            results = self.model(image_path, conf=self.confidence_threshold)

            # 处理结果
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        'class': result.names[int(box.cls[0])] if hasattr(result, 'names') else 'cat',
                        'confidence': float(box.conf[0]),
                        'bbox': {
                            'x1': int(box.xyxy[0][0]),
                            'y1': int(box.xyxy[0][1]),
                            'x2': int(box.xyxy[0][2]),
                            'y2': int(box.xyxy[0][3])
                        }
                    }
                    detections.append(detection)

            return BaseResponse.success({"detections": detections})
        except Exception as e:
            return BaseResponse.error(500, f"检测失败: {str(e)}")

# 创建全局实例
yolo_service = YOLOService() if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "best_epoch_weights.pt")) else None
