import uvicorn
from fastapi import FastAPI
from app import app as twilio_app  # Importing the Twilio FastAPI app

app = FastAPI()

# Mount the Twilio app
app.mount("/", twilio_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
