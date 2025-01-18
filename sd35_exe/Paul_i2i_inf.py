import websocket  # websocket-client
import uuid
import json
import urllib.request
import urllib.parse
import os
from tqdm import tqdm
import random
import copy

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

def get_images(ws, prompt, name, output_folder):
    """
    ws: 連線的 websocket
    prompt: 要執行的 ComfyUI workflow (dict)
    name: 生成圖檔的檔名前綴
    output_folder: 輸出圖檔的資料夾路徑
    """
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    
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
    
    # 只下載 node_id == "31" (假設你想要儲存的是 SaveImage 節點輸出)
    node_id = "31"
    if node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for idx, image in enumerate(node_output['images']):
                # 為了保證每張圖都有獨特名稱，可以加上 seed 或 idx
                image_name = f"{name}.png"
                filepath = os.path.join(output_folder, image_name)

                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                with open(filepath, "wb") as f:
                    f.write(image_data)

                images_output.append(filepath)

        output_images[node_id] = images_output
    
    # 回傳只包含 node "31" 的輸出
    return output_images

def main():
    # 讀取預設的 prompt (ComfyUI workflow)
    with open("sd35_i2i_canny.json", "r", encoding="utf-8") as f:
        base_prompt = json.load(f)

    # 指定要讀取的文字檔資料夾
    prompt_folder = "/media/avlab/reggie/Paul_sd35/ComfyUI_Paul/sd35_exe/ICIP2025/cfpfp_false"
    # 這個 output_folder 會是「所有圖」最終存放的總資料夾，實際會在 get_images 裡細分
    base_output_folder = "data_add/sd35/cfpfp"
    os.makedirs(base_output_folder, exist_ok=True)

    # 你可以定義要重複產圖的次數，或直接列出多個 seed
    # 在此示範：用多個 seed，跑好幾次 (也可改為 range() 迴圈隨機 seed)
    seeds_to_try = [3359554859, 5255954760, 7953954761, 84657912, 123456852, 94562458, 65423897, 95468723, 69858461, 456871130, 1256257894, 89752612311]

    # 走訪 prompt_folder 裡的所有檔案
    for current_root, dirs, files in os.walk(prompt_folder):
        for file_name in files:
            txt_path = os.path.join(current_root, file_name)
            img_path = txt_path.replace("cfpfp_false", "cfpfp_17deg").replace(".txt", ".png")

            # 讀取 prompt 的文字內容
            with open(txt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()
                print(f"Recent prompt is {prompt_content}")

            # 取得圖檔基底名稱 (ex: xxx.png -> xxx)
            image_name_base = os.path.basename(img_path).split(".")[0]

            # 對同一個 txt 檔，跑多次 (或多 seed)
            for seed in seeds_to_try:
                # 每跑一次，就複製一份 base_prompt，確保不互相干擾
                prompt = copy.deepcopy(base_prompt)

                # 依需求修改 prompt 的參數 (以下編號請對照你的 workflow JSON)
                prompt["6"]["inputs"]["text"] = prompt_content     # e.g. TextInput 節點
                prompt["3"]["inputs"]["seed"] = seed               # e.g. Seed 節點
                prompt["24"]["inputs"]["image"] = img_path         # e.g. ImageLoad 節點

                # 準備輸出的資料夾：可以在 base_output_folder 下，額外根據 seed、檔名等做分層
                output_folder = os.path.join(base_output_folder, f"_{seed}")
                os.makedirs(output_folder, exist_ok=True)

                # 連線 websockets 並執行
                ws = websocket.WebSocket()
                ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

                # image_name_base 為基底，再加上 seed，做出區分
                final_image_name = f"{image_name_base}_{seed}"

                images = get_images(ws, prompt, final_image_name, output_folder)

                ws.close()
                
                # 這裡的 images 即是 node "31" 的所有輸出檔路徑，若要後續處理可繼續使用
                # print(f"Images generated for seed {seed}:", images)

if __name__ == "__main__":
    main()
