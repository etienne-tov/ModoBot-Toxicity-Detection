from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import tensorflow as tf

app = FastAPI()

# Charger le modèle
MODEL = tf.keras.models.load_model("./comment_toxic_saved_model")

# Noms des labels
label_names = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hat']

class TextInput(BaseModel):
    text: str

@app.get("/")
def hello():
    return "Hello, I am alive"

@app.post("/predict_toxicity")
async def predict_toxicity(text_input: TextInput):
    try:
        # Valider la présence du champ "text" dans la requête
        text = text_input.text
    except KeyError:
        raise HTTPException(status_code=400, detail="Champ 'text' manquant dans la requête")

    try:
        # Effectuer la prédiction avec le modèle
        text_ = np.array([text])
        predictions = MODEL.predict(text_)

        # Créer un dictionnaire de résultats
        results = {"text": text, "predictions": {}}

        # Associer chaque prédiction à son label correspondant
        for label_name, prediction in zip(label_names, predictions.flatten()):
            results["predictions"][label_name] = bool(prediction > 0.5)

        return results
    except Exception as e:
        # Gérer les erreurs liées à la prédiction
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {str(e)}")



