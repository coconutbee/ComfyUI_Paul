#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
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
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt, name):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    output_folder = "output_images" # 這裡可以改你的output圖片資料夾
    os.makedirs(output_folder, exist_ok=True)
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
            # bytesIO = BytesIO(out[8:])
            # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_name = f"{name}.png" # 這裡可以改你的圖片名稱
                filepath = os.path.join(output_folder, image_name)
                
                # Check if the file already exists
                if os.path.exists(filepath):
                    print(f"File already exists, skipping: {filepath}")
                    images_output.append(filepath)
                    continue

                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                with open(filepath, "wb") as f:
                    f.write(image_data)
                images_output.append(file_path)
        output_images[node_id] = images_output

    return output_images


with open("sd35_workflow.json", "r", encoding="utf-8") as f:
    prompt_text = f.read()

prompt = json.loads(prompt_text)
#set the text prompt for our positive CLIPTextEncode
# prompt["6"]["inputs"]["text"] = "masterpiece, a young american teenager girl with a beautiful smile"
prompt["7"]["inputs"]["text"] = "unrealistic, animate, cropped, low quality, monochrome"
#set the seed for our KSampler node
# prompt["3"]["inputs"]["seed"] = 0
prompt["3"]["inputs"]["clip_name3"] = "t5xxl_fp16.safetensors"
prompt["4"]["inputs"]["ckpt_name"] = "sd3.5_medium.safetensors"


# tqdm
file_paths = []
prompt_folder = "prompt"  # 這裡可以放你的prompt資料夾
for root, dirs, files in os.walk(prompt_folder):
    for file_name in files:
        file_paths.append(os.path.join(root, file_name))

for file_path in tqdm(file_paths, desc="Processing files", unit="file"):
    with open(os.path.join(file_path), "r", encoding="utf-8") as f:
        prompt_content = f.read()
        prompt["6"]["inputs"]["text"] = prompt_content
        seed = random.randint(0, 4294967295)
        prompt["3"]["inputs"]["seed"] = seed
        image_name = os.path.basename(file_path).split(".")[0]
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        images = get_images(ws, prompt, image_name)
        ws.close() # for in case this example is used in an environment where it will be repeatedly called, like in a Gradio app. otherwise, you'll randomly receive connection timeouts

#Commented out code to display the output images:

# for node_id in images:
#     for image_data in images[node_id]:
#         from PIL import Image
#         import io
#         image = Image.open(io.BytesIO(image_data))
#         image.show()

