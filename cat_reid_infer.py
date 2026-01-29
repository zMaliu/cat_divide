"""cat_reid_infer.py

Standalone recognition/inference stage for cat ReID.

This file is meant to be used *alongside* your existing training script (cat_reid_train.py).
It does NOT change your old code.

Workflow
--------
1) Build a vector DB from a gallery folder (folder-per-identity):

   python cat_reid_infer.py build-db \
       --ckpt checkpoints/best_cat20_resnet50.pt \
       --gallery /path/to/gallery_root \
       --db vectordb_cat20.pt

   Expected gallery structure:
     gallery_root/
       ID_A/*.jpg
       ID_B/*.jpg

2) Recognize a query image by thresholded nearest-neighbor Euclidean distance:

   python cat_reid_infer.py recognize \
       --ckpt checkpoints/best_cat20_resnet50.pt \
       --db vectordb_cat20.pt \
       --query /path/to/query.jpg \
       --threshold 0.75 \
       --topk 5 \
       --update_db 1

   Behavior:
     - If min_dist < threshold: returns matched ID and nearest gallery image.
     - Else: returns NEW_xxxxxx, and (optionally) appends the query embedding into DB.

Notes on distance
-----------------
Your model outputs L2-normalized embeddings. Euclidean distance and cosine similarity
are equivalent for ranking on the unit sphere; threshold values differ by scale.
"""

from __future__ import annotations

import os
import re
import time
import argparse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.datasets.folder import default_loader

# Import the model definition from your existing file (no changes needed there)
from cat_reid_train import ReIDResNet50


# -------------------------
# Transforms (match val_tf)
# -------------------------

def build_infer_transform():
    """Keep consistent with val_tf used in your training script."""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(256),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])


# -------------------------
# Model loading
# -------------------------

def auto_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(ckpt_path: str, device: Optional[str] = None) -> Tuple[nn.Module, str]:
    """Load your checkpoint and return (model, device_string)."""
    if device is None:
        device = auto_device()

    ckpt = torch.load(ckpt_path, map_location="cpu")
    num_ids = int(ckpt.get("num_ids", 1))
    embed_dim = int(ckpt.get("embed_dim", 256))

    model = ReIDResNet50(num_ids=num_ids, embed_dim=embed_dim, pretrained=False)
    model.load_state_dict(ckpt["model"], strict=True)
    model.to(device)
    model.eval()
    return model, device


# -------------------------
# Vector DB format
# -------------------------
# torch.save({
#   "embs": FloatTensor [N,D] (CPU),
#   "ids":  List[str],
#   "paths":List[str],
#   "meta": Dict[str, Any]
# }, db_path)


def save_vector_db(db_path: str,
                   embs: torch.Tensor,
                   ids: List[str],
                   paths: List[str],
                   meta: Optional[Dict[str, Any]] = None) -> None:
    if embs.device.type != "cpu":
        embs = embs.cpu()
    payload = {
        "embs": embs.contiguous().float(),
        "ids": list(ids),
        "paths": list(paths),
        "meta": meta or {},
    }
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    torch.save(payload, db_path)


def load_vector_db(db_path: str) -> Dict[str, Any]:
    if not os.path.isfile(db_path):
        raise FileNotFoundError(f"Vector DB not found: {db_path}")
    db = torch.load(db_path, map_location="cpu")
    if "embs" not in db or "ids" not in db or "paths" not in db:
        raise RuntimeError(f"Bad vector DB format: {db_path}")
    db["meta"] = db.get("meta", {})
    return db


# -------------------------
# Gallery scanning
# -------------------------

def scan_gallery(gallery_root: str,
                 exts: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".webp")) -> Tuple[List[str], List[str]]:
    """Expect folder-per-identity gallery_root/ID/*.jpg"""
    if not os.path.isdir(gallery_root):
        raise FileNotFoundError(f"gallery_root not found: {gallery_root}")

    paths: List[str] = []
    ids: List[str] = []

    id_folders = [os.path.join(gallery_root, d) for d in os.listdir(gallery_root)
                  if os.path.isdir(os.path.join(gallery_root, d))]
    id_folders.sort()

    for folder in id_folders:
        id_name = os.path.basename(folder)
        for fn in sorted(os.listdir(folder)):
            if os.path.splitext(fn)[1].lower() in exts:
                paths.append(os.path.join(folder, fn))
                ids.append(id_name)

    if len(paths) == 0:
        raise RuntimeError(f"No images found under: {gallery_root}")

    return paths, ids


# -------------------------
# Embedding
# -------------------------

class ImagePathDataset(Dataset):
    def __init__(self, paths: List[str], transform):
        self.paths = paths
        self.transform = transform
        self.loader = default_loader

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int):
        p = self.paths[idx]
        img = self.loader(p)
        if self.transform is not None:
            img = self.transform(img)
        return img, p


@torch.no_grad()
def embed_paths(model: nn.Module,
                paths: List[str],
                device: str,
                batch_size: int = 64,
                num_workers: int = 0) -> Tuple[torch.Tensor, List[str]]:
    tf = build_infer_transform()
    ds = ImagePathDataset(paths, transform=tf)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    Z: List[torch.Tensor] = []
    P: List[str] = []

    for x, p in loader:
        x = x.to(device, non_blocking=True)
        z, _ = model(x)  # z already L2-normalized inside model forward
        Z.append(z.detach().cpu())
        P.extend(list(p))

    if len(Z) == 0:
        return torch.empty((0, 0)), []

    return torch.cat(Z, dim=0), P


# -------------------------
# Recognition by threshold
# -------------------------

@dataclass
class Neighbor:
    rank: int
    dist: float
    id: str
    path: str


def make_new_id(existing_ids: List[str], prefix: str = "NEW") -> str:
    """Generate NEW_000001 style IDs based on what's already in DB."""
    pat = re.compile(rf"^{re.escape(prefix)}_(\d+)$")
    nxt = 1
    for x in existing_ids:
        m = pat.match(str(x))
        if m:
            nxt = max(nxt, int(m.group(1)) + 1)
    return f"{prefix}_{nxt:06d}"


@torch.no_grad()
def recognize_one(model: nn.Module,
                  query_path: str,
                  db_path: str,
                  threshold: float,
                  device: str,
                  update_db: bool = True,
                  new_id_prefix: str = "NEW",
                  topk: int = 5) -> Dict[str, Any]:
    """Recognize a single image with thresholded nearest-neighbor Euclidean distance."""
    if not os.path.isfile(query_path):
        raise FileNotFoundError(f"query image not found: {query_path}")

    db = load_vector_db(db_path)
    gZ: torch.Tensor = db["embs"]
    g_ids: List[str] = db["ids"]
    g_paths: List[str] = db["paths"]

    if gZ.numel() == 0:
        raise RuntimeError("Vector DB is empty. Build it from gallery first.")

    qZ, _ = embed_paths(model, [query_path], device=device, batch_size=1, num_workers=0)
    if qZ.numel() == 0:
        raise RuntimeError("Failed to compute query embedding.")
    q = qZ[0].unsqueeze(0).float()  # [1,D]

    # Euclidean distances: [N]
    dists = torch.cdist(q, gZ.float(), p=2).squeeze(0)

    min_dist, min_idx = torch.min(dists, dim=0)

    # Top-k nearest (smallest distance)
    k = min(int(topk), int(dists.numel()))
    vals, idxs = torch.topk(dists, k=k, largest=False, sorted=True)
    neighbors: List[Dict[str, Any]] = []
    for r, (d, j) in enumerate(zip(vals.tolist(), idxs.tolist()), start=1):
        neighbors.append({
            "rank": r,
            "dist": float(d),
            "id": g_ids[j],
            "path": g_paths[j],
        })

    is_new = float(min_dist.item()) >= float(threshold)

    if not is_new:
        j = int(min_idx)
        return {
            "is_new": False,
            "threshold": float(threshold),
            "min_dist": float(min_dist.item()),
            "pred_id": g_ids[j],
            "pred_path": g_paths[j],
            "topk": neighbors,
            "query_path": query_path,
        }

    # New identity
    new_id = make_new_id(g_ids, prefix=new_id_prefix)

    if update_db:
        new_embs = torch.cat([gZ, q.squeeze(0).unsqueeze(0).cpu()], dim=0)
        new_ids = list(g_ids) + [new_id]
        new_paths = list(g_paths) + [query_path]
        meta = dict(db.get("meta", {}))
        meta["last_update_time"] = time.time()
        save_vector_db(db_path, new_embs, new_ids, new_paths, meta=meta)

    return {
        "is_new": True,
        "threshold": float(threshold),
        "min_dist": float(min_dist.item()),
        "pred_id": new_id,
        "pred_path": "",
        "topk": neighbors,
        "query_path": query_path,
        "db_updated": bool(update_db),
    }


# -------------------------
# Build DB
# -------------------------

@torch.no_grad()
def build_db(model: nn.Module,
             gallery_root: str,
             db_path: str,
             device: str,
             batch_size: int = 64,
             num_workers: int = 0,
             meta: Optional[Dict[str, Any]] = None) -> None:
    g_paths, g_ids = scan_gallery(gallery_root)
    gZ, g_paths = embed_paths(model, g_paths, device=device, batch_size=batch_size, num_workers=num_workers)
    save_vector_db(db_path, gZ, g_ids, g_paths, meta=meta)


# -------------------------
# CLI
# -------------------------

def _cmd_build_db(args):
    model, device = load_model(args.ckpt, device=args.device)
    build_db(model,
             gallery_root=args.gallery,
             db_path=args.db,
             device=device,
             batch_size=args.batch_size,
             num_workers=args.num_workers,
             meta={"built_from": args.gallery})
    print(f"[OK] Saved vector DB: {args.db}")


def _cmd_recognize(args):
    model, device = load_model(args.ckpt, device=args.device)
    res = recognize_one(model,
                        query_path=args.query,
                        db_path=args.db,
                        threshold=args.threshold,
                        device=device,
                        update_db=bool(args.update_db),
                        new_id_prefix=args.new_id_prefix,
                        topk=args.topk)
    # Print JSON for easy downstream integration
    print(torch.tensor(0))  # keep stdout deterministic if you parse? (optional)
    print("=== RESULT(JSON) ===")
    import json
    print(json.dumps(res, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_db = sub.add_parser("build-db")
    p_db.add_argument("--ckpt", type=str, required=True)
    p_db.add_argument("--gallery", type=str, required=True)
    p_db.add_argument("--db", type=str, default="vectordb_cat20.pt")
    p_db.add_argument("--device", type=str, default=None)
    p_db.add_argument("--batch_size", type=int, default=64)
    p_db.add_argument("--num_workers", type=int, default=0)
    p_db.set_defaults(func=_cmd_build_db)

    p_rec = sub.add_parser("recognize")
    p_rec.add_argument("--ckpt", type=str, required=True)
    p_rec.add_argument("--db", type=str, required=True)
    p_rec.add_argument("--query", type=str, required=True)
    p_rec.add_argument("--threshold", type=float, required=True)
    p_rec.add_argument("--topk", type=int, default=5)
    p_rec.add_argument("--update_db", type=int, default=1, help="1 to append new identity embeddings, 0 to not")
    p_rec.add_argument("--new_id_prefix", type=str, default="NEW")
    p_rec.add_argument("--device", type=str, default=None)
    p_rec.set_defaults(func=_cmd_recognize)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
