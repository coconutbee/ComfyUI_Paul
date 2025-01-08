# ComfyUI 架設

```text
git clone https://github.com/coconutbee/ComfyUI_Paul.git
conda create -n comfy python=3.10
```
```text
conda activate comfy
cd ComfyUI_Paul/sd35_exe
```
## 安裝pytorch
### 方法一
```python
pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
```
### 方法二(自行安裝)
1. 可以到[pytorch](https://pytorch.org/get-started/locally/)找適合的pytorch版本
2. 如果CUDA版本比較舊可以到[pytorch_previous](https://pytorch.org/get-started/previous-versions/)找適合的pytorch版本

## 安裝requirements
```text
pip install -r requirements.txt
```

## 下載stable diffusion model
到[stable diffusion 3.5的hugging face](https://huggingface.co/stabilityai/stable-diffusion-3.5-medium)安裝stable diffusion model。  
1. if you don't have a ssh key on hugging face:  
   1.  ssh-keygen -t rsa -b 4096 -C "your_email@example.com" # generate a key  
   2.  cat ~/.ssh/id_rsa.pub # copy the content starting with "ssh-rsa" till the end  
   3.  paste your key on "SSH & GPG Keys" -> 路徑:"頭像" ->  "SSH and GPG Keys" 
2. git lfs install  
3.
   ```python
   cd ../models/checkpoints
   git clone git@hf.co:stabilityai/stable-diffusion-3.5-medium
   cd ../clip
   ```

## 下載CLIP、T5 embedding model
### 在huggingface申請access token
[Access Tokens link here](https://huggingface.co/settings/tokens)
1. press "Create new token" botton
2. Enter "Token name"
3. turn on everything at "User permissions" section below.
4. Press the "Copy" botton.
5. in command line:
   ```bash
   nano ~/.bashrc
   ```
6. Paste the following code at the bottom of the file:
   ```nano
   export HF_API_TOKEN=<token_you_copied>
   ```
   then press **"Ctrl + X" -> "Y" -> "Enter"**
7. in command line:
   ```bash
   source ~/.bashrc
   ```
### install everything
1. 安裝[openai-CLIP L](https://huggingface.co/stabilityai/stable-diffusion-3.5-large/blob/main/text_encoders/clip_l.safetensors)
2. 安裝[openai-CLIP G](https://huggingface.co/stabilityai/stable-diffusion-3.5-large/blob/main/text_encoders/clip_g.safetensors)
3. 安裝[t5xxl_fp16.safetensors](https://huggingface.co/stabilityai/stable-diffusion-3.5-large/blob/main/text_encoders/t5xxl_fp16.safetensors)
4. 安裝[t5xxl_fp8_e4m3fn.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/t5xxl_fp8_e4m3fn.safetensors)
   ※注意: 你目前資料夾路徑為"ComfyUI_Paul/models/clip/"
   ```python
   wget --header="Authorization: Bearer $HF_API_TOKEN" https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/text_encoders/clip_l.safetensors
   wget --header="Authorization: Bearer $HF_API_TOKEN" https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/text_encoders/clip_g.safetensors
   wget --header="Authorization: Bearer $HF_API_TOKEN" https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/text_encoders/t5xxl_fp16.safetensors
   wget --header="Authorization: Bearer $HF_API_TOKEN" https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors
   ```
   
6. 安裝[canny edge](https://huggingface.co/stabilityai/stable-diffusion-3.5-large-controlnet-canny/resolve/main/diffusion_pytorch_model.safetensors)
   ```python
   cd ../controlnet
   wget --header="Authorization: Bearer $HF_API_TOKEN" https://huggingface.co/stabilityai/stable-diffusion-3.5-large-controlnet-canny/resolve/main/diffusion_pytorch_model.safetensors
   ```
## 執行ComfyUI workflow
```text
1. conda activate comfy
2. python main.py # 到"/ComfyUI_Paul"把ComfyUI打開，不要關掉
# 再開一個ternimal
3. cd sd35_exe # 到"/ComfyUI_Paul/sd35_exe"
4. python Paul_apicall.py
```

## FAQ
```text
Q: 
TypeError: WebSocket.__init__() missing 3 required positional arguments: 'environ', 'socket', and 'rfile' 
A:
pip uninstall websocket websocket-client
pip install websocket-client
``` 
