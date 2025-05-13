from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import sys
print(sys.path)
import logging
from PIL import Image
import numpy as np
import cv2

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from yolo import YOLO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EN2CN_CAT_BREED = {
    "Abyssinian": "阿比西尼亚猫",
    "Persian": "波斯猫",
    "Siamese": "暹罗猫",
    "British_Shorthair": "英国短毛猫",
    # ... 继续补充你的所有猫品种
}

# 猫品种信息数据库
CAT_BREED_INFO = {
    "阿比西尼亚猫": {
        "description": "阿比西尼亚猫是家猫品种之一,属于食肉目猫科猫属。性格活泼热情，较为温顺，叫声小，爱干净，喜欢与人类玩耍，适合家庭饲养。"
    },
    "波斯猫": {
        "description": "波斯猫是一种长毛猫，性格温顺，喜欢安静。它们有着圆脸、短鼻子和浓密的毛发。波斯猫需要定期梳理毛发，适合室内饲养。"
    },
    "暹罗猫": {
        "description": "暹罗猫是一种短毛猫，性格活泼好动，非常聪明。它们有着蓝色的眼睛和独特的重点色。暹罗猫喜欢与人互动，需要主人的关注。"
    },
    "英国短毛猫": {
        "description": "英国短毛猫是一种中等体型的猫，性格温和，容易相处。它们有着圆脸、短鼻子和浓密的短毛。英国短毛猫适合家庭饲养。"
    },
    # 可以添加更多猫品种信息
}

# 初始化YOLO模型
yolo = YOLO()

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image = Image.open(filepath)

        # 关键：要加 return_predictions=True
        result = yolo.detect_image(image, return_predictions=True)
        predictions = result.get("predictions", [])
        if len(predictions) > 0:
            best = max(predictions, key=lambda x: x["confidence"])
            #breed = best["class_name"]
            breed_en = best["class_name"]  # 识别出来的英文名
            breed_cn = EN2CN_CAT_BREED.get(breed_en, breed_en)  # 没有映射就显示英文名
            confidence = best["confidence"]
            breed_info = CAT_BREED_INFO.get(breed_cn, {"description": "暂无该品种的详细信息"})
            return jsonify({
                "breed": breed_cn,
                "confidence": confidence,
                "description": breed_info["description"]
            })
        else:
            return jsonify({'error': 'No cat detected in the image'}), 400

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': 'Error processing image'}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 

#  python cat_breed_detector/server/app.py