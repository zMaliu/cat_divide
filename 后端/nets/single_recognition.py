# nets/cat_reid.py
import torch
import torch.nn as nn
from torchvision.models import resnet50

class ReIDResNet50(nn.Module):
    def __init__(self, num_ids=1000, embed_dim=256, pretrained=True):
        super(ReIDResNet50, self).__init__()
        backbone = resnet50(pretrained=pretrained)
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])
        self.embed_layer = nn.Linear(2048, embed_dim)
        self.classifier = nn.Linear(embed_dim, num_ids) if num_ids > 0 else None
        
        self.embed_dim = embed_dim
        self.num_ids = num_ids

    def forward(self, x):
        features = self.backbone(x)
        features = torch.flatten(features, 1)
        embeddings = self.embed_layer(features)
        embeddings = nn.functional.normalize(embeddings, p=2, dim=1)
        
        if self.classifier is not None:
            logits = self.classifier(embeddings)
            return embeddings, logits
        else:
            return embeddings, None