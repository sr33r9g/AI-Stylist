import numpy as np
import cv2
import ultralytics
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import chromadb
import ollama
import os
import socket
import struct
import pickle

# --- 1. AI SETUP ---
print("Initializing AI Models...")
yolo_model = ultralytics.YOLO('best1.pt')
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

attributes = {
    "color": ["black", "white", "gray", "red", "blue","green", "yellow", "brown", "pink", "purple"],
    "fit": ["oversized baggy fit", "slim tight fit", "regular standard fit", "cropped short fit"],
    "style": ["formal professional", "casual streetwear", "vintage retro", "sporty athletic"]
}

client = chromadb.PersistentClient(path='./my_local_data')
collection = client.get_or_create_collection(name='my_knowledge_base')

# --- 2. PROCESSING FUNCTIONS ---

def detect_dress(img_rgb):
    results = yolo_model(img_rgb, verbose=False)
    boxes, names = [], []
    for r in results:
        for box in r.boxes:
            b = box.xyxy[0].cpu().numpy().astype(int)
            boxes.append(b)
            names.append(yolo_model.names[int(box.cls)])
    return boxes, names

def get_best_attribute(crop_pil, options):
    prompts = [f"a photo of a {opt} garment" for opt in options]
    inputs = clip_processor(text=prompts, images=crop_pil, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        outputs = clip_model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)
    best_idx = probs.argmax().item()
    return options[best_idx]

def smart_detect(img_array):
    boxes, names = detect_dress(img_array) 
    analysis_results = []
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        crop = img_array[y1:y2, x1:x2]
        if crop.size == 0: continue
        crop_pil = Image.fromarray(crop)
        
        feat = {"category": names[i]}
        for attr_type, options in attributes.items():
            feat[attr_type] = get_best_attribute(crop_pil, options)
            
        desc = f"{feat['fit']} {feat['color']} {feat['category']} in a {feat['style']} style"
        analysis_results.append(desc)
    return analysis_results

# --- 3. SERVER LOGIC ---

def start_server(host='0.0.0.0', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket option to allow immediate reuse of the port after restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"✅ Streaming Brain Server ready on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        try:
            # 1. Receive Header (Payload Size)
            header_size = struct.calcsize("Q")
            header_data = b""
            while len(header_data) < header_size:
                chunk = conn.recv(header_size - len(header_data))
                if not chunk: break
                header_data += chunk
            
            if not header_data: continue
            msg_size = struct.unpack("Q", header_data)[0]

            # 2. Receive Payload (Occasion + Image)
            payload_data = b""
            while len(payload_data) < msg_size:
                chunk = conn.recv(min(4096, msg_size - len(payload_data)))
                if not chunk: break
                payload_data += chunk
            
            payload = pickle.loads(payload_data)
            occasion = payload.get('occasion', 'Casual')
            image_bytes = payload.get('image_bytes')

            # 3. Decode and Process
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                descriptions = smart_detect(img_rgb)
                
                if descriptions:
                    outfit_features = " & ".join(descriptions)
                    query = f"Advice for {occasion} with {outfit_features}"
                    docs = collection.query(query_texts=[query], n_results=3)
                    
                    context = "\n".join(docs['documents'][0]) if docs['documents'] else ""
                    prompt=f"""
### Role
You are a Senior Fashion Stylist. Your goal is to adapt the user's current outfit to a specific occasion using expert style logic, with a high-level focus on color theory and garment construction.

### Contextual Style Guidelines
{context}

### User Input
- **Current Outfit:** {descriptions}
- **Target Occasion:** {occasion}

### Instructions
1. **The Adaptation:** Analyze how the "Current Outfit" can be elevated to fit the "Target Occasion." Apply the "Color Strategy" and "Guidelines" from the context to bridge the gap between the user's current pieces and the desired aesthetic.
2. **Color Combination Logic:** - Evaluate the interaction between the existing colors from Current Outfit .
    - Suggest a specific color palette for added layers or accessories that follows the "Color Strategy" (e.g., Monochromatic, Complementary, or Analogous) to harmonize the look.
3. **Styling Fixes:** Provide specific technical advice on how to wear the current pieces (e.g., precise tucking methods, sleeve rolls, or structural layering) to meet the standards of the occasion.
4. **Accessory Integration:** Recommend specific accessories (footwear, belts, timepieces) that use color and texture to transition the casual materials (denim/linen) into a sophisticated "Casual/Lifestyle" ensemble.

### Constraints
- Focus strictly on the "Target Occasion" provided.
- Maintain a sophisticated, authoritative, and expert tone.
- Do not include conversational filler or AI self-references.
- Output the recommendation in clear, concise bullet points using professional fashion terminology.
"""
                    
                    # --- STREAMING START ---
                    stream = ollama.generate(model="gemma3:1b", prompt=prompt, stream=True)
                    for chunk in stream:
                        text_chunk = chunk['response']
                        conn.sendall(text_chunk.encode('utf-8'))
                else:
                    conn.sendall(b"No clothing detected in the image.")
            else:
                conn.sendall(b"Error: Failed to decode image.")

        except Exception as e:
            print(f"Processing Error: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    start_server()