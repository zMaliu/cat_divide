# -*- coding: utf-8 -*-
"""
YOLO 权重初始化：在未使用预训练时对模型进行 Kaiming/Xavier 初始化。
供 nets.yolo.YoloBody 在 pretrained=False 时调用。
"""
import torch
import torch.nn as nn


def weights_init(module):
    """
    对 nn.Module 及其子模块进行权重初始化。
    Conv2d: Kaiming normal；BatchNorm2d: weight=1, bias=0；Linear: Kaiming normal。
    """
    for m in module.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, 0, 0.01)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
