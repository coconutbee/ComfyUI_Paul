import websocket  # websocket-client
import uuid
import json
import urllib.request
import urllib.parse
import os
from tqdm import tqdm
import random

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_images(ws, prompt, name):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    output_folder = "data_add/ICIP_cplfw_sd35"  # 這裡可依需求改你的輸出資料夾
    os.makedirs(output_folder, exist_ok=True)
    
    # 等待後端執行完畢
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            # 如果需要 preview，可以在這裡 decode
            continue
    
    # 取得這次 prompt 的 history
    history = get_history(prompt_id)[prompt_id]
    
    # ## 新增：只下載 node_id == "31" (SaveImage) 的輸出
    node_id = "31"
    if node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                # 為了保證每張圖都有獨特名稱，你可以加上 seed 或其他資訊
                image_name = f"cplfw_{name}.png"
                filepath = os.path.join(output_folder, image_name)

                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                with open(filepath, "wb") as f:
                    f.write(image_data)

                images_output.append(filepath)

        output_images[node_id] = images_output
    
    # 回傳只包含 node "31" 的輸出
    return output_images


# ---------- 下面的主程式與你原本的 workflow 讀取、檔名設定等流程相同 ----------

# 讀取預設的 prompt
with open("sd35_i2i_canny.json", "r", encoding="utf-8") as f:
    prompt_text = f.read()

prompt = json.loads(prompt_text)

prompt_folder = "/media/avlab/reggie/Paul_sd35/ComfyUI_Paul/sd35_exe/ICIP2025/cplfw_false"
for current_root, dirs, files in os.walk(prompt_folder):
    for file_name in files:
        txt_path = os.path.join(current_root, file_name)
        img_path = txt_path.replace("cplfw_false", "cplfw_17deg").replace(".txt", ".png")
        
        with open(txt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
            print(f"Recent prompt is {prompt_content}")
        
        # 設定 prompt 內容
        prompt["6"]["inputs"]["text"] = prompt_content
        seed = 50
        prompt["3"]["inputs"]["seed"] = seed
        prompt["24"]["inputs"]["image"] = img_path
        
        # 提取圖檔基底名稱
        image_name = os.path.basename(img_path).split(".")[0]
        
        # 連線 websockets 並執行
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        images = get_images(ws, prompt, image_name)
        ws.close()
        
        # 後續如果要做甚麼，可以加在這裡 (images 就是 node 31 的輸出檔路徑)
