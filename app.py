from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import logging
from twilio.twiml.voice_response import VoiceResponse, Gather
from ai_processing import extract_intent
from database import fetch_dynamic_details
from utils import twilio_response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/incoming_call")
async def incoming_call():
    """Handles incoming calls and prompts the user to speak."""
    try:
        twiml = VoiceResponse()
        gather = Gather(
            action="/process_speech",
            input="speech dtmf",
            language="en-IN",
            enhanced="true",
            action_on_empty_result="false",
            timeout=3
        )
        gather.say("Welcome! Please ask about any loan type available.", language="en")
        twiml.append(gather)
        return Response(content=str(twiml), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error in incoming_call: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.post("/process_speech")
async def process_speech(request: Request):
    """Processes user speech and fetches loan details dynamically."""
    try:
        form = await request.form()
        user_text = form.get("SpeechResult", "").strip()
        logger.info(f"Received Speech: {user_text}")

        if not user_text:
            return twilio_response("I couldn't hear you. Please try again.", "/incoming_call")

        # AI Intent Recognition
        intent = await extract_intent(user_text)
        if not intent:
            return twilio_response("Sorry, I couldn't understand your request.")

        # Fetch Loan Details
        details = await fetch_dynamic_details(intent)

        response_text = (
            " ".join([f"{key}: {value}" for key, value in details.items()])
            if details
            else "I couldn't find details for your query."
        )

        return twilio_response(response_text)

    except Exception as e:
        logger.error(f"Error in process_speech: {e}")
        return twilio_response("An error occurred while processing your request. Please try again.")
