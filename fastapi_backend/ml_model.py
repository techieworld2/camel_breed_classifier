import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import io
import numpy as np
import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image
import cv2

MODEL_PATH = "best_model.pt"
IMAGE_SIZE = 224
BREEDS_CANONICAL = ["Majaheem Camel", "Bactrian Camel", "Libyan Camel"]
DROMEDARY_LABEL = "Arabian Camel (Dromedary)"


class ImageTabularNet(nn.Module):
    """The exact architecture from your Streamlit app"""
    def __init__(self, num_breeds=3, tab_in=4, pretrained=False):
        super().__init__()
        base = models.resnet18(weights=None)
        in_feats = base.fc.in_features
        base.fc = nn.Identity()
        self.cnn = base

        self.tab = nn.Sequential(
            nn.Linear(tab_in, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Linear(32, 32),
            nn.ReLU(),
        )

        fused_dim = in_feats + 32
        self.breed_head = nn.Sequential(
            nn.Linear(fused_dim, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, num_breeds)
        )
        self.rating_head = nn.Sequential(
            nn.Linear(fused_dim, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 1)
        )

    def forward(self, img, tab):
        f_img = self.cnn(img)
        f_tab = self.tab(tab)
        x = torch.cat([f_img, f_tab], dim=1)
        breed_logits = self.breed_head(x)
        rating = self.rating_head(x).squeeze(1)
        return breed_logits, rating


class _ActGradHook:
    def __init__(self, module):
        self.activations = None
        self.gradients = None
        self.h1 = module.register_forward_hook(self._fwd)
        self.h2 = module.register_full_backward_hook(self._bwd)
    def _fwd(self, m, i, o):  
        self.activations = o.detach()
    def _bwd(self, m, gi, go): 
        self.gradients = go[0].detach()
    def close(self): 
        self.h1.remove()
        self.h2.remove()


class CamelClassifier:
    def __init__(self, model_path: str = MODEL_PATH):
        self.device = torch.device("cpu")
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    def _load_model(self, path: str):
        model = ImageTabularNet(num_breeds=len(BREEDS_CANONICAL), tab_in=4)
        state = torch.load(path, map_location="cpu")
        model.load_state_dict(state)
        model.to(self.device).eval()
        return model

    def preprocess_image(self, image_bytes: bytes):
        """Convert image bytes to tensor"""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = self.transform(img).unsqueeze(0)
        return img, img_tensor

    def _get_target_layer_resnet18(self):
        blk = self.model.cnn.layer4[-1]
        return getattr(blk, "conv2", blk)

    def gradcam_heatmap(self, img_t, tab_t, class_idx=None):
        """Generate Grad-CAM heatmap"""
        self.model.eval()
        target = self._get_target_layer_resnet18()
        hook = _ActGradHook(target)

        img_t = img_t.clone().requires_grad_(True)
        logits, _ = self.model(img_t, tab_t)
        if class_idx is None:
            class_idx = int(torch.argmax(logits, dim=1).item())
        score = logits[0, class_idx]
        self.model.zero_grad(set_to_none=True)
        score.backward(retain_graph=True)

        A = hook.activations[0]
        dA = hook.gradients[0]
        weights = dA.mean(dim=(1, 2))
        cam = torch.relu((weights[:, None, None] * A).sum(dim=0))
        cam -= cam.min()
        if cam.max() > 0:
            cam /= cam.max()
        hook.close()
        return cam.cpu().numpy(), class_idx

    def overlay_cam_on_pil(self, pil_img, cam, alpha=0.4):
        """Overlay Grad-CAM on PIL image"""
        H, W = pil_img.size[1], pil_img.size[0]
        cam_resized = cv2.resize(cam, (W, H))
        heat = np.uint8(255 * cam_resized)
        heat = cv2.applyColorMap(heat, cv2.COLORMAP_JET)[:, :, ::-1]
        base = np.array(pil_img).astype(np.float32)
        over = (alpha * heat + (1 - alpha) * base).clip(0, 255).astype(np.uint8)
        return Image.fromarray(over)

    def predict(self, image_bytes: bytes, head_size: float, leg_condition: float, 
                coat_quality: float, overall_fitness: float, conf_thresh: float = 0.60):
        """
        Main prediction function
        Returns: dict with breed, confidence, rating, probabilities, and gradcam image
        """
        # Preprocess image
        pil_img, img_t = self.preprocess_image(image_bytes)
        
        # Prepare tabular features
        tab_vals = [head_size, leg_condition, coat_quality, overall_fitness]
        tab = torch.tensor(tab_vals, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            logits, rating = self.model(img_t.to(self.device), tab)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            rating = float(rating.item())
        
        # Get top prediction
        top_idx = int(np.argmax(probs))
        top_conf = float(probs[top_idx])
        label = BREEDS_CANONICAL[top_idx] if top_conf >= conf_thresh else DROMEDARY_LABEL
        
        # Generate Grad-CAM
        cam, _ = self.gradcam_heatmap(img_t.to(self.device), tab, class_idx=top_idx)
        cam_overlay = self.overlay_cam_on_pil(pil_img, cam)
        
        # Convert Grad-CAM to base64
        import base64
        buf = io.BytesIO()
        cam_overlay.save(buf, format="PNG")
        gradcam_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Prepare probabilities for all classes
        probabilities = {
            breed: float(prob) 
            for breed, prob in zip(BREEDS_CANONICAL, probs)
        }
        
        return {
            "breed": label,
            "confidence": top_conf,
            "rating": rating,
            "probabilities": probabilities,
            "gradcam_image": gradcam_b64,
            "is_dromedary_fallback": label == DROMEDARY_LABEL
        }


# Global classifier instance
_classifier_instance = None

def get_classifier():
    """Singleton pattern for model loading"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = CamelClassifier()
    return _classifier_instance
