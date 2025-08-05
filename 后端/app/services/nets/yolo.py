"""
nets.yolo 模块的兼容性实现
"""
import torch
import torch.nn as nn

class ConvBNSiLU(nn.Module):
    """Conv + BN + SiLU activation"""
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, groups=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, groups=groups, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)
        self.act = nn.SiLU(inplace=True)

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))

class Bottleneck(nn.Module):
    """Standard bottleneck"""
    def __init__(self, in_channels, out_channels, shortcut=True, expansion=0.5):
        super().__init__()
        hidden_channels = int(out_channels * expansion)
        self.cv1 = ConvBNSiLU(in_channels, hidden_channels, 1, 1)
        self.cv2 = ConvBNSiLU(hidden_channels, out_channels, 3, 1, 1)
        self.use_add = shortcut and in_channels == out_channels

    def forward(self, x):
        return x + self.cv2(self.cv1(x)) if self.use_add else self.cv2(self.cv1(x))

class C2f(nn.Module):
    """CSP Bottleneck with 2 convolutions"""
    def __init__(self, in_channels, out_channels, n=1, shortcut=False, expansion=0.5):
        super().__init__()
        hidden_channels = int(out_channels * expansion)
        self.c = int(out_channels // 2)
        self.cv1 = ConvBNSiLU(in_channels, hidden_channels, 1, 1)
        self.cv2 = ConvBNSiLU(in_channels, hidden_channels, 1, 1)
        self.cv3 = ConvBNSiLU(hidden_channels, out_channels, 1)
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
        self.cv1 = ConvBNSiLU(in_channels, c_, 1, 1)
        self.cv2 = ConvBNSiLU(c_ * 4, out_channels, 1, 1)
        self.m = nn.MaxPool2d(kernel_size=k, stride=1, padding=k // 2)

    def forward(self, x):
        x = self.cv1(x)
        y1 = self.m(x)
        y2 = self.m(y1)
        return self.cv2(torch.cat((x, y1, y2, self.m(y2)), 1))

class DFL(nn.Module):
    """Distribution Focal Loss (DFL) layer"""
    def __init__(self, c1=16):
        super().__init__()
        self.c1 = c1
        self.conv = nn.Conv2d(c1, 1, 1, bias=False).requires_grad_(False)
        x = torch.arange(c1, dtype=torch.float)
        self.conv.weight.data[:] = nn.Parameter(x.view(1, c1, 1, 1))
        self.c1 = c1

    def forward(self, x):
        b, c, a = x.shape  # batch, channels, anchors
        return self.conv(x.view(b, 4, self.c1, a).transpose(2, 1).softmax(1)).view(b, 4, a)

class YoloBody(nn.Module):
    """YOLO model body for compatibility"""
    def __init__(self, nc=80, ch=()):
        super().__init__()
        self.nc = nc
        self.ch = ch
        self.model = nn.ModuleList()  # 添加一个ModuleList来支持下标访问
        
    def forward(self, x):
        return x
        
    def get(self, key, default=None):
        """Get method for compatibility"""
        return getattr(self, key, default)
        
    def __getitem__(self, index):
        """Support subscript access"""
        return self.model[index] if index < len(self.model) else None

class YOLO(nn.Module):
    """YOLO model for compatibility"""
    def __init__(self, nc=80, ch=()):
        super().__init__()
        self.nc = nc
        self.ch = ch
        
    def forward(self, x):
        return x
