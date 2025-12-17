"""
Create a small demo model for testing detector pipeline.
This tries to build MobileNetV2 (if available) and save the full model object,
otherwise saves a tiny CNN model so detector can load it with torch.load().
"""
import os
import torch

out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Try to build Mobilenet via model_inference if torchvision is available; otherwise build a tiny sequential model
try:
    from services.model_inference import build_mobilenetv2_binary
    model = build_mobilenetv2_binary(num_classes=1, pretrained=False)
    # Save full model object
    dest = os.path.join(out_dir, 'detector.pth')
    torch.save(model, dest)
    print('Saved demo MobileNet model to', dest)
except Exception:
    # Fallback small CNN
    import torch.nn as nn

    class TinyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv2d(3, 8, kernel_size=3, stride=2, padding=1),
                nn.ReLU(),
                nn.Conv2d(8, 16, kernel_size=3, stride=2, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten(),
                nn.Linear(16, 1),
            )

        def forward(self, x):
            return self.net(x)

    model = TinyNet()
    dest = os.path.join(out_dir, 'detector.pth')
    torch.save(model, dest)
    print('Saved demo TinyNet model to', dest)
