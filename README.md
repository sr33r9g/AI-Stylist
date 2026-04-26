VisionFabric: Privacy-First AI Fashion Stylist 🛡️👔
VisionFabric is a multi-modal AI agent that transforms raw computer vision data into personalized fashion advice. By combining real-time object detection with a local Retrieval-Augmented Generation (RAG) system, it provides context-aware styling recommendations without ever sending your data to the cloud.

🌟 Key Features
Privacy-First Architecture: Powered by Ollama, all Large Language Model (LLM) reasoning happens locally on your machine. No images or style data ever leave your device.

Semantic Feature Extraction: Uses OpenAI’s CLIP to understand not just color, but the "vibe," fit, and style of a garment.

Context-Aware RAG: A ChromaDB vector database containing specialized fashion rules for Indian Weddings, Corporate Interviews, and Formal Events.

Real-Time Detection: Implements YOLOv10 for high-speed, accurate clothing identification.

Local Client-Server Model: A decoupled architecture ensuring zero-latency performance and high data sovereignty.

🏗️ System Architecture
VisionFabric operates on a decentralized local framework to ensure maximum security:

Client (Streamlit): A streamlined interface that handles image capture and "Occasion" selection.

Server (Python Backend): - Vision Engine: YOLOv10 (Object Detection) + CLIP (Semantic Attribute Extraction).

Knowledge Base: ChromaDB (Vector retrieval for fashion etiquette).

Reasoning Engine: Ollama (Synthesizing vision data and rules into a human-like recommendation).

🛠️ Tech Stack
Language: Python 3.10+

Computer Vision: Ultralytics YOLOv10, OpenAI CLIP

Vector Database: ChromaDB

LLM Engine: Ollama (Llama 3 / Mistral)

Frontend: Streamlit

Data Processing: OpenCV, NumPy, Scikit-learn

🚀 Getting Started
1. Prerequisites
Install Ollama

Pull your preferred model (e.g., Llama 3):

Bash
ollama pull llama3
2. Installation
Clone the repository:

Bash
git clone https://github.com/YOUR_USERNAME/VisionFabric.git
cd VisionFabric
Install dependencies:

Bash
pip install -r requirements.txt
3. Run the Application
VisionFabric requires both the backend server and the frontend client to be running simultaneously.

Terminal 1: Start the AI Inference Server

Bash
python server.py
Terminal 2: Start the Streamlit Frontend

Bash
streamlit run app.py
📖 Sample Knowledge Base
The system includes specialized rules generated for real-world scenarios:

Indian Weddings: Etiquette for Haldi, Sangeet, and Reception ceremonies.

Professional: Style guides for Tech Startups vs. Traditional Corporate interviews.

Lifestyle: Recommendations for casual dates, travel, and formal galas.

🛡️ Privacy Statement
VisionFabric was built with Data Sovereignty at its core. Unlike commercial fashion apps, this system does not upload images to external servers. All image processing, vector search, and language generation occur strictly on the local host.

🤝 Contributing
Contributions are welcome! If you have ideas for more fashion rules or want to optimize the CLIP-based feature extraction, please open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
