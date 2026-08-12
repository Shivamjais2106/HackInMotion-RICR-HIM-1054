"""
Train rice leaf disease model using MobileNetV2 transfer learning
Classes: Bacterial leaf blight, Brown spot, Leaf smut
"""
import os, json, pickle
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import models, transforms, datasets
from torch.optim import Adam
from torch.optim.lr_scheduler import StepLR

DATA_DIR  = r"D:\Kisahn\kisann\backend\Data-raw\rice_leaf_diseases"
MODEL_OUT = "models/rice_disease_model.pth"
INFO_OUT  = "models/rice_disease_info.json"
EPOCHS    = 30
BATCH     = 8
IMG_SIZE  = 224
LR        = 1e-4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ── Transforms ───────────────────────────────────────────────────────────────
train_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(20),
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
print(f"Classes ({num_classes}): {class_names}")
print(f"Total images: {len(full_ds)}")

# 80/20 split
val_size   = max(1, int(0.2 * len(full_ds)))
train_size = len(full_ds) - val_size
train_ds, val_ds = random_split(full_ds, [train_size, val_size],
                                generator=torch.Generator().manual_seed(42))
# Use val transform for validation set
val_ds.dataset = datasets.ImageFolder(DATA_DIR, transform=val_tf)

train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_ds,   batch_size=BATCH, shuffle=False, num_workers=0)
print(f"Train: {train_size}  Val: {val_size}")

# ── Model: MobileNetV2 with frozen backbone ───────────────────────────────────
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
for p in model.features.parameters():
    p.requires_grad = False          # freeze backbone

model.classifier[1] = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.classifier[1].in_features, num_classes)
)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = Adam(model.classifier.parameters(), lr=LR)
scheduler = StepLR(optimizer, step_size=10, gamma=0.5)

# ── Training loop ─────────────────────────────────────────────────────────────
best_val_acc = 0.0
print("\nTraining...")
for epoch in range(1, EPOCHS + 1):
    # Train
    model.train()
    train_loss, train_correct = 0.0, 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        out  = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()
        train_loss    += loss.item() * imgs.size(0)
        train_correct += (out.argmax(1) == labels).sum().item()

    # Validate
    model.eval()
    val_correct = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            out = model(imgs)
            val_correct += (out.argmax(1) == labels).sum().item()

    t_acc = train_correct / train_size * 100
    v_acc = val_correct   / val_size   * 100
    scheduler.step()

    print(f"Epoch {epoch:02d}/{EPOCHS}  train_acc={t_acc:.1f}%  val_acc={v_acc:.1f}%")

    if v_acc >= best_val_acc:
        best_val_acc = v_acc
        torch.save(model.state_dict(), MODEL_OUT)

# ── Unfreeze all layers and fine-tune ─────────────────────────────────────────
print("\nFine-tuning all layers...")
for p in model.parameters():
    p.requires_grad = True
optimizer2 = Adam(model.parameters(), lr=LR / 10)

for epoch in range(1, 11):
    model.train()
    train_correct = 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer2.zero_grad()
        out  = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer2.step()
        train_correct += (out.argmax(1) == labels).sum().item()

    model.eval()
    val_correct = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            val_correct += (out.argmax(1) == labels).sum().item()

    t_acc = train_correct / train_size * 100
    v_acc = val_correct   / val_size   * 100
    print(f"FineTune {epoch:02d}/10  train_acc={t_acc:.1f}%  val_acc={v_acc:.1f}%")

    if v_acc >= best_val_acc:
        best_val_acc = v_acc
        torch.save(model.state_dict(), MODEL_OUT)

# ── Save class info ───────────────────────────────────────────────────────────
info = {"classes": class_names, "num_classes": num_classes, "best_val_acc": best_val_acc}
with open(INFO_OUT, "w") as f:
    json.dump(info, f, indent=2)

print(f"\n✅ Model saved → {MODEL_OUT}")
print(f"✅ Info  saved → {INFO_OUT}")
print(f"   Best val accuracy: {best_val_acc:.1f}%")
print(f"   Classes: {class_names}")
