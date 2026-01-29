import os
import re
import json
import time
import math
import shutil
import random
import argparse
import subprocess
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, Sampler
from torchvision import transforms
from torchvision.datasets.folder import default_loader
from torchvision.models import resnet50, ResNet50_Weights


# =========================
# Config (best default choices)
# =========================
KAGGLE_DATASET = "timost1234/cat-individuals"  # Cat Individuals (518 cats / 13536 images)
# KAGGLE_DATASET = "cronenberg64/cat-re-identification-image-dataset"
# You can switch to: "cronenberg64/cat-re-identification-image-dataset"
# but its folder structure may differ.

DEFAULT_MAX_IDS = 20
DEFAULT_P = 10  # identities per batch
DEFAULT_K = 4   # images per identity
DEFAULT_EMB = 256
DEFAULT_LR = 3e-4
DEFAULT_EPOCHS = 40
DEFAULT_MARGIN = 0.2


# =========================
# Utilities
# =========================
def seed_everything(seed: int = 42):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def run(cmd: List[str], cwd: Optional[str] = None):
    print(">>", " ".join(cmd))
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        print(p.stdout)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return p.stdout


def has_kaggle_token() -> bool:
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if os.path.exists(kaggle_json):
        return True
    # also accept env token
    return bool(os.environ.get("KAGGLE_API_TOKEN"))


def ensure_kaggle_cli():
    try:
        run(["kaggle", "--version"])
    except Exception:
        print("\n[ERROR] Kaggle CLI not found.\n"
              "Install it via:\n"
              "  pip install kaggle\n")
        raise


def list_image_files(folder: str) -> List[str]:
    exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
    out = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(exts):
                out.append(os.path.join(root, f))
    return out


def safe_name(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]+", "_", s)


# =========================
# Dataset Prep
# =========================
def kaggle_download_dataset(dataset: str, out_dir: str):
    """
    Downloads and unzips Kaggle dataset into out_dir/raw/
    """
    os.makedirs(out_dir, exist_ok=True)
    raw_dir = os.path.join(out_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    ensure_kaggle_cli()

    if not has_kaggle_token():
        raise RuntimeError(
            "Kaggle API token not found.\n"
            "Please do:\n"
            "  1) Log in to Kaggle -> Account -> Create New API Token\n"
            "  2) Put kaggle.json at ~/.kaggle/kaggle.json\n"
            "  3) chmod 600 ~/.kaggle/kaggle.json\n"
        )

    # download zip
    run(["kaggle", "datasets", "download", "-d", dataset, "-p", raw_dir, "--force"])

    # unzip all zips inside raw_dir
    for f in os.listdir(raw_dir):
        if f.lower().endswith(".zip"):
            zip_path = os.path.join(raw_dir, f)
            run(["python", "-c", "import zipfile; import sys; z=zipfile.ZipFile(sys.argv[1]); z.extractall(sys.argv[2]);",
                 zip_path, raw_dir])
    print(f"[OK] Downloaded & extracted to: {raw_dir}")


def infer_identity_folders(raw_dir: str) -> List[str]:
    """
    Heuristic: find subfolders that contain images.
    Return candidate identity folders (each should correspond to an individual cat).
    """
    candidates = []
    for root, dirs, files in os.walk(raw_dir):
        # treat folders with lots of images as identity folders
        imgs = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))]
        if len(imgs) >= 3:
            # if parent has many such folders, we want the identity-level folders,
            # not too deep. We'll accept and dedupe later.
            candidates.append(root)

    # dedupe: keep shortest paths preferentially
    candidates = sorted(set(candidates), key=lambda p: (p.count(os.sep), p))
    # remove those that are parents of others (we want leaf-ish folders)
    leaf = []
    for c in candidates:
        if not any((other != c and other.startswith(c + os.sep)) for other in candidates):
            leaf.append(c)
    return leaf


def select_20_identities(raw_dir: str, out_dir: str, max_ids: int = 20, min_imgs: int = 8, seed: int = 42):
    """
    Creates out_dir/cat20/ with structure:
      cat20/
        id_000/
          *.jpg
        ...
    It selects identities with >= min_imgs images.
    """
    rng = random.Random(seed)

    id_folders = infer_identity_folders(raw_dir)
    # collect (folder, images)
    pool = []
    for f in id_folders:
        imgs = list_image_files(f)
        if len(imgs) >= min_imgs:
            pool.append((f, imgs))

    if len(pool) < max_ids:
        raise RuntimeError(f"Not enough identity folders with >= {min_imgs} images. "
                           f"Found {len(pool)}. Try lowering --min_imgs.")

    rng.shuffle(pool)
    chosen = pool[:max_ids]

    dest_root = os.path.join(out_dir, "cat20")
    if os.path.exists(dest_root):
        shutil.rmtree(dest_root)
    os.makedirs(dest_root, exist_ok=True)

    manifest = []
    for new_id, (folder, imgs) in enumerate(chosen):
        # take all imgs (or cap)
        dest_id = f"id_{new_id:03d}"
        dest_folder = os.path.join(dest_root, dest_id)
        os.makedirs(dest_folder, exist_ok=True)

        for p in imgs:
            # copy (keep filename unique)
            base = os.path.basename(p)
            base = safe_name(base)
            dst = os.path.join(dest_folder, base)
            if os.path.exists(dst):
                # ensure unique
                stem, ext = os.path.splitext(base)
                dst = os.path.join(dest_folder, f"{stem}_{rng.randint(0,999999)}{ext}")
            shutil.copy2(p, dst)

        manifest.append({"new_id": new_id, "source_folder": folder, "num_images": len(imgs)})

    with open(os.path.join(out_dir, "cat20_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[OK] Prepared 20 identities at: {dest_root}")
    print(f"[OK] Manifest saved: {os.path.join(out_dir, 'cat20_manifest.json')}")
    return dest_root


# =========================
# Training Dataset + PK Sampler
# =========================
class FolderPerIdentityDataset(Dataset):
    """
    root/
      id_000/*.jpg
      id_001/*.jpg
    """
    def __init__(self, root: str, split: str = "train", split_ratio: float = 0.8,
                 transform=None, seed: int = 42):
        super().__init__()
        self.root = root
        self.transform = transform
        self.loader = default_loader

        id_folders = [os.path.join(root, d) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
        id_folders.sort()

        self.id_to_imgs: Dict[int, List[str]] = {}
        for idx, folder in enumerate(id_folders):
            imgs = list_image_files(folder)
            if len(imgs) < 2:
                continue
            self.id_to_imgs[idx] = imgs

        rng = random.Random(seed)
        self.samples: List[Tuple[str, int]] = []
        for y, imgs in self.id_to_imgs.items():
            imgs = imgs[:]
            rng.shuffle(imgs)
            n_train = max(1, int(len(imgs) * split_ratio))
            if split == "train":
                chosen = imgs[:n_train]
            else:
                chosen = imgs[n_train:] if len(imgs[n_train:]) > 0 else imgs[:1]
            for p in chosen:
                self.samples.append((p, y))

        self.indices_by_id: Dict[int, List[int]] = {}
        for i, (_, y) in enumerate(self.samples):
            self.indices_by_id.setdefault(y, []).append(i)

        self.num_ids = len(self.indices_by_id)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        p, y = self.samples[idx]
        img = self.loader(p)
        if self.transform:
            img = self.transform(img)
        return img, y


class PKSampler(Sampler[List[int]]):
    def __init__(self, indices_by_id: Dict[int, List[int]], P: int, K: int, steps_per_epoch: int, seed: int = 42):
        self.indices_by_id = indices_by_id
        self.ids = sorted(indices_by_id.keys())
        self.P = P
        self.K = K
        self.steps = steps_per_epoch
        self.rng = random.Random(seed)
        if len(self.ids) < P:
            raise ValueError(f"Need at least P identities. Have {len(self.ids)}, P={P}")

    def __len__(self):
        return self.steps

    def __iter__(self):
        for _ in range(self.steps):
            chosen_ids = self.rng.sample(self.ids, self.P)
            batch = []
            for cid in chosen_ids:
                pool = self.indices_by_id[cid]
                if len(pool) >= self.K:
                    pick = self.rng.sample(pool, self.K)
                else:
                    pick = [self.rng.choice(pool) for _ in range(self.K)]
                batch.extend(pick)
            yield batch


# =========================
# Model (ResNet50 + BNNeck + Embedding)
# =========================
class ReIDResNet50(nn.Module):
    """
    Strong Baseline style:
    - ResNet50 backbone
    - embedding layer
    - BNNeck (BatchNorm neck) to improve discriminability
    """
    def __init__(self, num_ids: int, embed_dim: int = 256, pretrained: bool = True):
        super().__init__()
        weights = ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
        backbone = resnet50(weights=weights)

        self.backbone = nn.Sequential(*list(backbone.children())[:-1])  # avgpool output
        self.embed = nn.Linear(2048, embed_dim)
        self.bn = nn.BatchNorm1d(embed_dim)
        self.bn.bias.requires_grad_(False)

        # ID classifier head (for CE + label smoothing)
        self.classifier = nn.Linear(embed_dim, num_ids, bias=False)

        nn.init.normal_(self.embed.weight, std=0.01)
        nn.init.constant_(self.embed.bias, 0.0)
        nn.init.normal_(self.classifier.weight, std=0.01)

    def forward(self, x):
        feat = self.backbone(x).flatten(1)   # [B,2048]
        z = self.embed(feat)                 # [B,d]
        z_bn = self.bn(z)                    # BNNeck feature
        z_norm = F.normalize(z, p=2, dim=1)  # metric feature (normalized)
        logits = self.classifier(z_bn)       # classification logits
        return z_norm, logits


# =========================
# Losses
# =========================
def pairwise_d2(emb: torch.Tensor) -> torch.Tensor:
    # emb should be L2-normalized => d^2 = 2 - 2*cos
    sim = emb @ emb.t()
    return (2.0 - 2.0 * sim).clamp_min(0.0)


def batch_hard_triplet_loss(emb: torch.Tensor, labels: torch.Tensor, margin: float = 0.2) -> torch.Tensor:
    d2 = pairwise_d2(emb)
    B = emb.size(0)
    labels = labels.view(-1, 1)
    same = (labels == labels.t())
    diff = ~same
    eye = torch.eye(B, device=emb.device, dtype=torch.bool)
    same = same & (~eye)

    pos = d2.masked_fill(~same, -1.0)
    hardest_pos, _ = pos.max(dim=1)

    neg = d2.masked_fill(~diff, 1e9)
    hardest_neg, _ = neg.min(dim=1)

    loss = F.relu(hardest_pos - hardest_neg + margin)
    return loss.mean()


class CrossEntropyLabelSmoothing(nn.Module):
    def __init__(self, num_classes: int, eps: float = 0.1):
        super().__init__()
        self.num_classes = num_classes
        self.eps = eps

    def forward(self, logits, target):
        # target: [B]
        log_probs = F.log_softmax(logits, dim=1)
        n = logits.size(1)
        with torch.no_grad():
            true_dist = torch.zeros_like(log_probs)
            true_dist.fill_(self.eps / (n - 1))
            true_dist.scatter_(1, target.unsqueeze(1), 1.0 - self.eps)
        return (-true_dist * log_probs).sum(dim=1).mean()


# =========================
# Eval (retrieval)
# =========================
@torch.no_grad()
def extract_embeddings(model: nn.Module, loader: DataLoader, device: str):
    model.eval()
    Z, Y = [], []
    for x, y in loader:
        x = x.to(device, non_blocking=True)
        z, _ = model(x)
        Z.append(z.cpu())
        Y.append(y.cpu())
    return torch.cat(Z, dim=0), torch.cat(Y, dim=0)


@torch.no_grad()
def retrieval_top1_map(Z: torch.Tensor, Y: torch.Tensor):
    # self-retrieval sanity: query=gallery
    sim = Z @ Z.t()
    d2 = (2.0 - 2.0 * sim).clamp_min(0.0)
    Q = Z.size(0)

    top1 = 0
    ap_sum = 0.0

    for i in range(Q):
        yi = Y[i].item()
        dist = d2[i].clone()
        dist[i] = 1e9  # exclude self
        order = torch.argsort(dist)

        if Y[order[0]].item() == yi:
            top1 += 1

        matches = (Y[order] == yi).to(torch.int32)
        if matches.sum().item() == 0:
            continue
        cumsum = torch.cumsum(matches, dim=0)
        ranks = torch.arange(1, matches.numel() + 1)
        precision_at_k = (cumsum / ranks) * matches
        ap = precision_at_k.sum().item() / matches.sum().item()
        ap_sum += ap

    return top1 / Q, ap_sum / Q


# =========================
# Train
# =========================
def train(data_dir: str, epochs: int, P: int, K: int, embed_dim: int, lr: float, margin: float, seed: int):
    seed_everything(seed)
    # device = "cuda" if torch.cuda.is_available() else "cpu"      
    if torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        device = "mps"
        print(f"Device: {device}")
    else:
        device = "cpu"
        print("Device:", device)

    train_tf = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(256, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.RandomErasing(p=0.25, scale=(0.02, 0.2), ratio=(0.3, 3.3), value="random"),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(256),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    train_ds = FolderPerIdentityDataset(data_dir, split="train", split_ratio=0.8, transform=train_tf, seed=seed)
    val_ds = FolderPerIdentityDataset(data_dir, split="val", split_ratio=0.8, transform=val_tf, seed=seed)
    num_ids = train_ds.num_ids
    print(f"Train identities: {num_ids}, train images: {len(train_ds)}, val images: {len(val_ds)}")
    if num_ids < P:
        raise RuntimeError(f"Not enough identities for P={P}. Reduce P or provide more identities.")

    steps_per_epoch = 120     # 这里也从200改为50步长
    sampler = PKSampler(train_ds.indices_by_id, P=P, K=K, steps_per_epoch=steps_per_epoch, seed=seed)
    # train_loader = DataLoader(train_ds, batch_sampler=sampler, num_workers=4, pin_memory=True)
    # val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, num_workers=4, pin_memory=True)
    train_loader = DataLoader(train_ds, batch_sampler=sampler, num_workers=0)
    val_loader   = DataLoader(val_ds, batch_size=64, shuffle=False, num_workers=0)

    model = ReIDResNet50(num_ids=num_ids, embed_dim=embed_dim, pretrained=True).to(device)

    ce = CrossEntropyLabelSmoothing(num_classes=num_ids, eps=0.1).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda"))

    best_map = -1.0
    os.makedirs("checkpoints", exist_ok=True)

    # loss weights (strong baseline)
    w_tri = 1.0
    w_ce = 1.0

    for ep in range(1, epochs + 1):
        model.train()
        loss_sum = 0.0

        for (x, y) in train_loader:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            opt.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=(device == "cuda")):
                z, logits = model(x)
                loss_tri = batch_hard_triplet_loss(z, y, margin=margin)
                loss_ce = ce(logits, y)
                loss = w_tri * loss_tri + w_ce * loss_ce

            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()

            loss_sum += loss.item()

        sched.step()
        avg_loss = loss_sum / len(train_loader)

        Z, Y = extract_embeddings(model, val_loader, device)
        top1, mAP = retrieval_top1_map(Z, Y)
        print(f"Epoch {ep:03d} | loss {avg_loss:.4f} | val Top1 {top1:.4f} | val mAP {mAP:.4f} | lr {sched.get_last_lr()[0]:.2e}")

        if mAP > best_map:
            best_map = mAP
            torch.save({"model": model.state_dict(),
                        "num_ids": num_ids,
                        "embed_dim": embed_dim}, "checkpoints/best_cat20_resnet50.pt")
            print("[OK] Saved: checkpoints/best_cat20_resnet50.pt")

    print("Done. Best val mAP:", best_map)


# =========================
# CLI
# =========================
def cmd_download(args):
    out = args.out
    os.makedirs(out, exist_ok=True)
    kaggle_download_dataset(KAGGLE_DATASET, out_dir=out)
    raw_dir = os.path.join(out, "raw")
    select_20_identities(raw_dir=raw_dir, out_dir=out, max_ids=args.max_ids, min_imgs=args.min_imgs, seed=args.seed)


def cmd_train(args):
    data_dir = os.path.join(args.data, "cat20")
    if not os.path.exists(data_dir):
        raise RuntimeError(f"cat20 folder not found at {data_dir}. Run download first.")
    train(data_dir=data_dir, epochs=args.epochs, P=args.P, K=args.K,
          embed_dim=args.embed_dim, lr=args.lr, margin=args.margin, seed=args.seed)


def cmd_all(args):
    cmd_download(args)
    cmd_train(args)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_dl = sub.add_parser("download")
    p_dl.add_argument("--out", type=str, required=True, help="Output dir, will create raw/ and cat20/")
    p_dl.add_argument("--max_ids", type=int, default=DEFAULT_MAX_IDS)
    p_dl.add_argument("--min_imgs", type=int, default=8, help="Min images per identity to be eligible")
    p_dl.add_argument("--seed", type=int, default=42)
    p_dl.set_defaults(func=cmd_download)

    p_tr = sub.add_parser("train")
    p_tr.add_argument("--data", type=str, required=True, help="Dir containing cat20/ (produced by download)")
    p_tr.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    p_tr.add_argument("--P", type=int, default=DEFAULT_P)
    p_tr.add_argument("--K", type=int, default=DEFAULT_K)
    p_tr.add_argument("--embed_dim", type=int, default=DEFAULT_EMB)
    p_tr.add_argument("--lr", type=float, default=DEFAULT_LR)
    p_tr.add_argument("--margin", type=float, default=DEFAULT_MARGIN)
    p_tr.add_argument("--seed", type=int, default=42)
    p_tr.set_defaults(func=cmd_train)

    p_all = sub.add_parser("all")
    p_all.add_argument("--out", type=str, required=True)
    p_all.add_argument("--max_ids", type=int, default=DEFAULT_MAX_IDS)
    p_all.add_argument("--min_imgs", type=int, default=8)
    p_all.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    p_all.add_argument("--P", type=int, default=DEFAULT_P)
    p_all.add_argument("--K", type=int, default=DEFAULT_K)
    p_all.add_argument("--embed_dim", type=int, default=DEFAULT_EMB)
    p_all.add_argument("--lr", type=float, default=DEFAULT_LR)
    p_all.add_argument("--margin", type=float, default=DEFAULT_MARGIN)
    p_all.add_argument("--seed", type=int, default=42)
    p_all.set_defaults(func=cmd_all)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()