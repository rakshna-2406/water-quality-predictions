"""
data_view.py
------------
Shows dataset summary and sample images for the Water Quality Prediction System.

Usage:
    python data_view.py --data_dir "/mnt/data/water-quality-predictions/data/water images"

This script:
 - Prints counts of images under train/ and test/ for each class
 - Displays a few sample images (requires a display or Jupyter; will save sample grid as samples_grid.png)
"""
import argparse
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import random
import os

def gather_counts(data_dir):
    data_dir = Path(data_dir)
    summary = {}
    for split in ["train", "test"]:
        split_dir = data_dir / split
        if not split_dir.exists():
            continue
        for cls in sorted([p.name for p in split_dir.iterdir() if p.is_dir()]):
            cls_dir = split_dir / cls
            count = len(list(cls_dir.glob("**/*.*")))
            summary.setdefault(split, {})[cls] = count
    return summary

def save_samples_grid(data_dir, out_path="samples_grid.png", samples_per_class=4):
    data_dir = Path(data_dir)
    train_dir = data_dir / "train"
    classes = [p.name for p in train_dir.iterdir() if p.is_dir()]
    imgs = []
    for cls in classes:
        cls_dir = train_dir / cls
        all_imgs = list(cls_dir.glob("*"))
        if not all_imgs:
            continue
        chosen = random.sample(all_imgs, min(samples_per_class, len(all_imgs)))
        for p in chosen:
            try:
                img = Image.open(p).convert("RGB").resize((224,224))
                imgs.append((cls, img))
            except Exception as e:
                print("Skipping", p, ":", e)
    if not imgs:
        print("No images found to create sample grid.")
        return None
    # create grid
    cols = samples_per_class
    rows = len(classes)
    fig, axes = plt.subplots(rows, cols, figsize=(cols*2, rows*2))
    for i, (cls) in enumerate(classes):
        row_imgs = [im for c, im in imgs if c==cls][:cols]
        for j in range(cols):
            ax = axes[i,j] if rows>1 else axes[j]
            if j < len(row_imgs):
                ax.imshow(row_imgs[j])
                ax.set_title(cls if j==0 else "")
            ax.axis("off")
    plt.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="/mnt/data/water-quality-predictions/data/water images")
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print("[ERROR] data_dir does not exist:", data_dir)
        return
    summary = gather_counts(data_dir)
    print("Dataset summary (counts):")
    for split, d in summary.items():
        print(f"  {split}:")
        for cls, cnt in d.items():
            print(f"    {cls}: {cnt}")
    out = save_samples_grid(data_dir, out_path="samples_grid.png")
    if out:
        print("Saved sample grid to", out)
    else:
        print("No sample grid created.")

if __name__ == "__main__":
    main()
