"""
nets.backbone 模块的兼容性实现
"""
import torch
import torch.nn as nn

class SiLU(nn.Module):
    """SiLU activation function"""
    def __init__(self, inplace=False):
        super().__init__()
        self.inplace = inplace

    def forward(self, x):
        return x * torch.sigmoid(x)

class Conv(nn.Module):
    """Standard convolution with args(ch_in, ch_out, kernel, stride, padding, groups, dilation, activation)"""
    default_act = SiLU()  # default activation

    def __init__(self, c1, c2, k=1, s=1, p=None, g=1, d=1, act=True):
        super().__init__()
        self.conv = nn.Conv2d(c1, c2, k, s, autopad(k, p, d), groups=g, dilation=d, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = self.default_act if act is True else act if isinstance(act, nn.Module) else nn.Identity()

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))

    def forward_fuse(self, x):
        return self.act(self.conv(x))

def autopad(k, p=None, d=1):  # kernel, padding, dilation
    """Pad to 'same' shape outputs"""
    if d > 1:
        k = d * (k - 1) + 1 if isinstance(k, int) else [d * (x - 1) + 1 for x in k]
    if p is None:
        p = k // 2 if isinstance(k, int) else [x // 2 for x in k]
    return p

class Bottleneck(nn.Module):
    """Standard bottleneck"""
    def __init__(self, in_channels, out_channels, shortcut=True, expansion=0.5):
        super().__init__()
        hidden_channels = int(out_channels * expansion)
        self.cv1 = Conv(in_channels, hidden_channels, 1, 1)
        self.cv2 = Conv(hidden_channels, out_channels, 3, 1, 1)
        self.use_add = shortcut and in_channels == out_channels

    def forward(self, x):
        return x + self.cv2(self.cv1(x)) if self.use_add else self.cv2(self.cv1(x))

class C2f(nn.Module):
    """CSP Bottleneck with 2 convolutions"""
    def __init__(self, in_channels, out_channels, n=1, shortcut=False, expansion=0.5):
        super().__init__()
        hidden_channels = int(out_channels * expansion)
        self.c = int(out_channels // 2)
        self.cv1 = Conv(in_channels, hidden_channels, 1, 1)
        self.cv2 = Conv(in_channels, hidden_channels, 1, 1)
        self.cv3 = Conv(hidden_channels, out_channels, 1)
        self.m = nn.Sequential(*(Bottleneck(hidden_channels, hidden_channels, shortcut, 1.0) for _ in range(n)))

    def forward(self, x):
        y = list(self.cv1(x).chunk(2, 1))
        y.extend(m(y[-1]) for m in self.m)
        return self.cv3(torch.cat([self.cv2(x)] + y, 1))

class SPPF(nn.Module):
    """Spatial Pyramid Pooling - Fast (SPPF) layer for YOLOv8"""
    def __init__(self, in_channels, out_channels, k=5):
        super().__init__()
        c_ = in_channels // 2
        self.cv1 = Conv(in_channels, c_, 1, 1)
        self.cv2 = Conv(c_ * 4, out_channels, 1, 1)
        self.m = nn.MaxPool2d(kernel_size=k, stride=1, padding=k // 2)

    def forward(self, x):
        x = self.cv1(x)
        y1 = self.m(x)
        y2 = self.m(y1)
        return self.cv2(torch.cat((x, y1, y2, self.m(y2)), 1))

class Backbone(nn.Module):
    """Base backbone class for compatibility"""
    def __init__(self):
        super().__init__()
        
    def forward(self, x):
        return x

class CSPDarknet(nn.Module):
    """CSPDarknet backbone for compatibility"""
    def __init__(self, base_channels, base_depth, phi, pretrained=False):
        super().__init__()
        self.base_channels = base_channels
        self.base_depth = base_depth
        self.phi = phi
        
    def forward(self, x):
        return x

class ResNet(nn.Module):
    """ResNet backbone for compatibility"""
    def __init__(self, depth, pretrained=False):
        super().__init__()
        self.depth = depth
        
    def forward(self, x):
        return x

class VGG(nn.Module):
    """VGG backbone for compatibility"""
    def __init__(self, depth, pretrained=False):
        super().__init__()
        self.depth = depth
        
    def forward(self, x):
        return x
