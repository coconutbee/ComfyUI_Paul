import os
import glob
import pickle
import torch
import numpy as np
from PIL import Image
import torch.nn.functional as F

# --------------------------------------------------
# 1) 設定參數
# --------------------------------------------------
# 指向你的 StyleGAN2 pkl 權重檔路徑
STYLEGAN2_PKL = '/media/avlab/1EC4447D760E2354/Paul/ComfyUI/test_csim/stylegan2/config/ffhq-512-avg-tpurun1.pkl'

# 要批量篩選的圖片資料夾
INPUT_IMAGE_DIR = '/media/avlab/1EC4447D760E2354/Paul/ComfyUI/output_images'

# (可選) 若要把判定為「假臉」的圖片移到指定資料夾，可在這裡指定
FAKE_OUTPUT_DIR = 'test_csim/stylegan2/stylegan2_fake_images_tpurun'
TRUE_OUTPUT_DIR = 'test_csim/stylegan2/stylegan2_true_images_tpurun'

# 設定輸入圖片的解析度 (依照你下載的模型而定，FFHQ 通常是 1024)
RESOLUTION = 512

# GPU 或 CPU 裝置
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 閾值 (threshold)，判斷是「真臉」的機率門檻
# 若 score > 0.5 則視為「真臉」，否則「假臉」
THRESHOLD = 0.5

# --------------------------------------------------
# 2) 讀取 StyleGAN2 Discriminator
# --------------------------------------------------
def load_stylegan2_discriminator(pkl_path):
    """
    從指定的 .pkl 檔中載入 Discriminator。
    回傳一個已凍結 (eval, no_grad) 的模型物件。
    """
    with open(pkl_path, 'rb') as f:
        resume_data = pickle.load(f)  # 內含 {'G':..., 'D':..., 'G_ema':...}
    D = resume_data['D']
    D.eval().requires_grad_(False).to(DEVICE)
    return D

# --------------------------------------------------
# 3) 前處理函式
# --------------------------------------------------
def preprocess_image(image_path, resolution=512):
    """
    讀取、縮放、正規化到 [-1,1]，回傳 PyTorch tensor, shape=[1, 3, H, W]
    """
    pil_img = Image.open(image_path).convert('RGB')
    # resize 到指定解析度
    pil_img = pil_img.resize((resolution, resolution), Image.LANCZOS)
    arr = np.array(pil_img, dtype=np.float32)

    # 正規化到 [-1, 1]
    arr = arr / 127.5 - 1.0

    # (H, W, C) -> (C, H, W)
    arr = np.transpose(arr, (2, 0, 1))

    # 建立 batch 維度
    img_tensor = torch.from_numpy(arr).unsqueeze(0).to(DEVICE)
    return img_tensor

# --------------------------------------------------
# 4) 主程式：批量篩選
# --------------------------------------------------
def main():
    # 4.1) 讀取 Discriminator
    print("Loading Discriminator from:", STYLEGAN2_PKL)
    D = load_stylegan2_discriminator(STYLEGAN2_PKL)

    # 4.2) 找出所有圖片
    os.makedirs(FAKE_OUTPUT_DIR, exist_ok=True)
    image_paths = sorted(glob.glob(os.path.join(INPUT_IMAGE_DIR, '*.*')))

    if not image_paths:
        print(f"No images found in {INPUT_IMAGE_DIR}")
        return

    # 4.3) 逐張處理
    print(f"Found {len(image_paths)} images. Start filtering...")
    real_count = 0
    fake_count = 0

    for img_path in image_paths:
        # 前處理
        img_tensor = preprocess_image(img_path, RESOLUTION)

        # StyleGAN2 的 D.forward(x, img) 寫法可能略有不同
        # 有些實作只需 D(img_tensor)；請依照實際 networks_stylegan2.py 定義做調整
        with torch.no_grad():
            score = D(img_tensor, img_tensor)  # logits, shape: [1, 1]

        # 轉成 0~1 機率
        prob_real = torch.sigmoid(score).item()

        # 判斷結果
        if prob_real > THRESHOLD:
            # 視為真臉
            real_count += 1
            # 這裡不做移動，只是印出 log
            print(f"[REAL] {img_path} => prob_real={prob_real:.4f}")
            base_name = os.path.basename(img_path)
            dstt_path = os.path.join(TRUE_OUTPUT_DIR, base_name)
            os.rename(img_path, dstt_path)
        else:
            # 視為假臉
            fake_count += 1
            print(f"[FAKE] {img_path} => prob_real={prob_real:.4f}")
            # (可選) 把它移到 FAKE_OUTPUT_DIR
            base_name = os.path.basename(img_path)
            dstf_path = os.path.join(FAKE_OUTPUT_DIR, base_name)
            os.rename(img_path, dstf_path)

    print("Filtering done!")
    print(f"Total images: {len(image_paths)}")
    print(f"Real: {real_count}, Fake: {fake_count}")

# --------------------------------------------------
# 5) 執行
# --------------------------------------------------
if __name__ == "__main__":
    main()

