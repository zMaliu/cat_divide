# cat_reid.py
import os
import torch
from nets.single_recognition import ReIDResNet50

class CatReID:
    _defaults = {
        "model_path": "model_data\single_recognition.pt",
        "device": 'auto',
        "threshold": 0.75,
        "new_id_prefix": "NEW"
    }

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)
        
        if self.device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # 初始化模型
        self._init_model()

        # 初始化向量数据库 


    def _init_model(self):
        """初始化并加载模型权重。checkpoint 若含 embed/bn 等旧键名会映射为当前结构的 embed_layer 并忽略多余键。"""
        print(f"Loading Cat ReID model from {self.model_path}...")
        checkpoint = torch.load(self.model_path, map_location='cpu')
        raw_state = checkpoint.get('model', checkpoint)

        self.model = ReIDResNet50(
            num_ids=checkpoint.get('num_ids', 1),
            embed_dim=checkpoint.get('embed_dim', 256),
            pretrained=False
        )
        # 兼容旧 checkpoint：embed -> embed_layer，忽略 bn 等多余键
        state_dict = {}
        for k, v in raw_state.items():
            if k.startswith("bn."):
                continue
            if k.startswith("embed."):
                state_dict["embed_layer." + k[6:]] = v
            else:
                state_dict[k] = v
        self.model.load_state_dict(state_dict, strict=False)
        self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully.")

    def extract_features(self, image):
        """
        从 PIL Image 或 tensor 中提取特征向量
        Returns: normalized embedding (numpy array or tensor)
        """
        from torchvision import transforms
        if not isinstance(image, torch.Tensor):
            transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            image = transform(image).unsqueeze(0)
        
        image = image.to(self.device)
        with torch.no_grad():
            embedding, _ = self.model(image)
        return embedding.cpu().numpy()[0] # 返回单个向量

    def recognize_image(self, image, update_db=True):
        """
        识别单张图片
        Args:
            image: PIL Image or path to image
            update_db: whether to add new cat to DB
        Returns:
            dict: recognition result
        """
        if self.db is None:
            raise ValueError("Vector database not initialized. Provide 'db_path' in constructor.")
        
        # 处理图像路径
        if isinstance(image, str):
            from PIL import Image
            image_pil = Image.open(image)
            query_path = image
        else:
            image_pil = image
            query_path = "in-memory"

        # 提取特征
        query_emb = self.extract_features(image_pil)
        
        # 在数据库中查询

        return result