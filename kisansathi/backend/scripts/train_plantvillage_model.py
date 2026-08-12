"""
Train PlantVillage disease model using MobileNetV2 transfer learning
15 classes, ~20K images
"""
import os, json, torch, torch.nn as nn
from torch.utils.data import DataLoader, random_split, WeightedRandomSampler
from torchvision import models, transforms, datasets
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
import numpy as np

DATA_DIR  = r"D:\Kisahn\kisann\backend\Data-raw\PlantVillage\PlantVillage"
MODEL_OUT = "models/plantvillage_model.pth"
INFO_OUT  = "models/plantvillage_info.json"

EPOCHS    = 15
BATCH     = 32
IMG_SIZE  = 224
LR        = 1e-3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ── Transforms ───────────────────────────────────────────────────────────────
train_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE + 20, IMG_SIZE + 20)),
    transforms.RandomCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])
val_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

# ── Dataset ───────────────────────────────────────────────────────────────────
full_ds = datasets.ImageFolder(DATA_DIR, transform=train_tf)
class_names = full_ds.classes
num_classes = len(class_names)
total = len(full_ds)
print(f"Classes ({num_classes}): {class_names}")
print(f"Total images: {total}")

# 85/15 split
val_size   = int(0.15 * total)
train_size = total - val_size
train_ds, val_ds = random_split(full_ds, [train_size, val_size],
                                generator=torch.Generator().manual_seed(42))

# Weighted sampler to handle class imbalance
targets = [full_ds.targets[i] for i in train_ds.indices]
class_counts = np.bincount(targets)
weights = 1.0 / class_counts[targets]
sampler = WeightedRandomSampler(weights, len(weights))

train_loader = DataLoader(train_ds, batch_size=BATCH, sampler=sampler, num_workers=0)
# val uses val_tf via a separate dataset
val_ds_clean = datasets.ImageFolder(DATA_DIR, transform=val_tf)
val_subset   = torch.utils.data.Subset(val_ds_clean, val_ds.indices)
val_loader   = DataLoader(val_subset, batch_size=BATCH, shuffle=False, num_workers=0)

print(f"Train: {train_size}  Val: {val_size}")

# ── Model ─────────────────────────────────────────────────────────────────────
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
# Freeze all except last 3 feature blocks + classifier
for i, layer in enumerate(model.features):
    if i < 15:
        for p in layer.parameters():
            p.requires_grad = False

model.classifier[1] = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.classifier[1].in_features, num_classes)
)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LR)
scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)

# ── Training ──────────────────────────────────────────────────────────────────
best_val_acc = 0.0
print("\nTraining...")
for epoch in range(1, EPOCHS + 1):
    model.train()
    correct, total_seen = 0, 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(imgs), labels)
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            preds = model(imgs).argmax(1)
            correct    += (preds == labels).sum().item()
            total_seen += labels.size(0)
    scheduler.step()

    # Validation
    model.eval()
    val_correct = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            val_correct += (model(imgs).argmax(1) == labels).sum().item()

    t_acc = correct    / total_seen * 100
    v_acc = val_correct / val_size  * 100
    print(f"Epoch {epoch:02d}/{EPOCHS}  train={t_acc:.1f}%  val={v_acc:.1f}%")

    if v_acc >= best_val_acc:
        best_val_acc = v_acc
        torch.save(model.state_dict(), MODEL_OUT)
        print(f"  ✅ Saved (best val={best_val_acc:.1f}%)")

# ── Save info ─────────────────────────────────────────────────────────────────
info = {"classes": class_names, "num_classes": num_classes,
        "best_val_acc": best_val_acc, "img_size": IMG_SIZE}
with open(INFO_OUT, "w") as f:
    json.dump(info, f, indent=2)

print(f"\n✅ Model → {MODEL_OUT}")
print(f"✅ Info  → {INFO_OUT}")
print(f"   Best val accuracy: {best_val_acc:.1f}%")
print(f"   Classes: {class_names}")
