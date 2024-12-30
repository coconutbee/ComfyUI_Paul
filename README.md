# ComfyUI 架設

```text
git clone https://github.com/comfyanonymous/ComfyUI.git
conda create -n comfy python=3.10
```
```text
conda activate comfy
cd ComfyUI/sd35_exe
pip install -r requirements.txt
```
安裝pytorch可能會遇到cuda版本不相符的問題，出現問題可以到[pytorch](https://pytorch.org/get-started/locally/)找適合的pytorch版本

到stable diffusion 3.5的hugging face 安裝stable diffusion model。  
1. if you don't have a ssh key on hugging face:  
   1.  ssh-keygen -t rsa -b 4096 -C "your_email@example.com" # generate a key  
   2.  cat ~/.ssh/id_rsa.pub # copy the content starting with "ssh-rsa" till the end  
   3.  paste your key on "SSH & GPG Keys" -> 路徑:"頭像" ->  "SSH and GPG Keys" 
2. git lfs install  
3. git clone git@hf.co:stabilityai/stable-diffusion-3.5-large  

安裝完成sd model後:  
1. 把sd3.5_large.safetensors放到 /ComfyUI/models/checkpoints
2. 安裝[openai-CLIP L](https://huggingface.co/stabilityai/stable-diffusion-3.5-large/blob/main/text_encoders/clip_l.safetensors)
3. 安裝[openai-CLIP G](https://huggingface.co/stabilityai/stable-diffusion-3.5-large/blob/main/text_encoders/clip_g.safetensors)
4. 安裝[t5xxl_fp16.safetensors](https://huggingface.co/stabilityai/stable-diffusion-3.5-large/blob/main/text_encoders/t5xxl_fp16.safetensors)
5. 安裝[t5xxl_fp8_e4m3fn.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/t5xxl_fp8_e4m3fn.safetensors)  
6. 把CLIP與T5模型都放到 /ComfyUI/models/clip

## 執行ComfyUI workflow
```text
1. python main.py # 把ComfyUI打開，不要關掉
2. cd sd35_exe
3. Paul_apicall.py
```
