# -*- coding: utf-8 -*-
"""
特征提取服务：使用项目根目录下的 CatReID 模型（single_recognition.py）从图片路径提取 256 维向量。
供 VectorService 调用，用于以图搜猫和绑定猫向量。
"""
import os
import sys
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# 项目根目录（main.py 所在目录），供导入 single_recognition 使用
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_cat_reid = None


def _get_cat_reid():
    """懒加载 CatReID 单例，避免启动时必加载模型。"""
    global _cat_reid
    if _cat_reid is None:
        from single_recognition import CatReID
        _cat_reid = CatReID()
    return _cat_reid


def extract_features_from_path(image_path: str):
    """
    从本地图片路径提取 256 维特征向量（与 CatReID / ReIDResNet50 的 embed_dim 一致）。
    :param image_path: 本地图片绝对路径
    :return: list，长度为 256
    :raises FileNotFoundError: 文件不存在
    """
    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"图片不存在: {image_path}")
    pil_image = Image.open(image_path).convert("RGB")
    model = _get_cat_reid()
    vec = model.extract_features(pil_image)
    return vec.tolist()
