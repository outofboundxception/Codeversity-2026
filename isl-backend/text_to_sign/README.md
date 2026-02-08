## 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows

## 2. Install dependencies
pip install -r requirements.txt

## 3. Download NLTK data (run once)
python -m nltk.downloader punkt wordnet stopwords averaged_perceptron_tagger

## 4. Run the backend server
uvicorn app:app --reload


Server will start at:

http://localhost:8000


API documentation:

http://localhost:8000/docs

API Usage
Endpoint
POST /predict

Request body
{
  "text": "Hello how are you"
}

Response
{
  "text": "Hello how are you",
  "images": [
    "/signs/words/hello.jpg",
    "/signs/alphabets/h.jpg",
    "/signs/alphabets/o.jpg",
    "/signs/alphabets/w.jpg"
  ]
}


Each image URL can be directly used in the frontend.

Frontend Animation (JavaScript)

Below is a simple way to animate signs sequentially using plain JavaScript.

HTML
<img id="signPlayer" width="300" />

JavaScript
async function playISLAnimation(text) {
  const res = await fetch("http://localhost:8000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text })
  });

  const data = await res.json();
  const images = data.images;

  const imgElement = document.getElementById("signPlayer");

  for (const img of images) {
    imgElement.src = `http://localhost:8000${img}`;
    await new Promise(resolve => setTimeout(resolve, 600));
  }
}

Example call
playISLAnimation("Hello how are you");


Each sign is shown for 600 ms. Adjust timing as needed.
