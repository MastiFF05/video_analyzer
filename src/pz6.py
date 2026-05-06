import torch
import torchvision.transforms as T
from torchvision.models import resnet50
from PIL import Image

class ResNetClassifier:
    def __init__(self):
        self.model = resnet50(pretrained=True)
        self.model.eval()
        self.transform = T.Compose([
            T.Resize(256), T.CenterCrop(224), T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])
    
    def classify(self, img_path):
        img = Image.open(img_path)
        batch = self.transform(img).unsqueeze(0)
        with torch.no_grad():
            outputs = self.model(batch)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        top_prob, top_catid = torch.topk(probs, 1)
        return {'class': top_catid.item(), 'prob': top_prob.item()}
