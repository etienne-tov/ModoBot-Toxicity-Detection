from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import tensorflow as tf

app = FastAPI()

MODEL = tf.keras.models.load_model("./comment_toxic_saved_model")

label_names = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hat']

class TextInput(BaseModel):
    text: str

@app.get("/")
def hello():
    return "Hello, I am alive"

@app.post("/predict_toxicity")
async def predict_toxicity(text_input: TextInput):
    try:
        text = text_input.text
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing 'text' field in query")

    try:
        text_ = np.array([text])
        predictions = MODEL.predict(text_)

        results = {"text": text, "predictions": {}}

        for label_name, prediction in zip(label_names, predictions.flatten()):
            results["predictions"][label_name] = bool(prediction > 0.5)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
