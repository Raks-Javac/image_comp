# 🖼️ Image Comparison API

A FastAPI-based microservice that compares two base64-encoded images using Google's Gemini (Generative AI) and returns a similarity score along with an explanation of differences and similarities.

## 🚀 Features

- Accepts two images in base64 format.
- Uses Google Gemini (`gemini-1.5-pro`) to analyze and compare the images.
- Returns:
  - Similarity Score (0 to 100)
  - Human-readable explanation of the differences and similarities.

## 🧠 Powered By

- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Generative AI](https://ai.google.dev/)
- [Pillow (PIL)](https://python-pillow.org/)

## 📦 Installation

1. **Clone the Repository**

```bash
git clone https://github.com/raks-javac/image-comparison-api.git
cd image-comparison-api
```

2. **Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up Environment Variables**

Create a `.env` file in the root directory and add your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

4. **Run the App**

```bash
uvicorn main:app --reload
```

The app will be available at: [http://localhost:8000](http://localhost:8000)

## 🛠️ API Endpoints

### `GET /`

Check if the API is running.

**Response:**
```json
{
  "message": "Image Comparison API is running"
}
```

### `POST /compare`

Compares two base64-encoded images.

**Request Body:**
```json
{
  "image1": "data:image/png;base64,iVBORw0K...",
  "image2": "data:image/png;base64,iVBORw0K..."
}
```

**Response:**
```json
{
  "similarity_score": 87.5,
  "explanation": "Both images share similar structure and content, but differ slightly in color and background elements."
}
```

## 📁 Project Structure

```
.
├── main.py                     # Main FastAPI app
├── models/
│   └── image_models.py         # Pydantic request/response models
├── .env                        # Environment variables
└── requirements.txt            # Python dependencies
```

## ✅ Requirements

- Python 3.8+
- Valid Google API key with access to Gemini 1.5 Pro
- Dependencies listed in `requirements.txt`:
  - fastapi
  - python-dotenv
  - google-generativeai
  - pillow
  - uvicorn

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request.

## 📄 License

This project is licensed under the MIT License.

## 🙋‍♂️ Author

**Your Name**  
GitHub: [@Raks-Javac](https://github.com/Raks-Javac)
