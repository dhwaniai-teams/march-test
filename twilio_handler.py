from fastapi import Request
from twilio.twiml.voice_response import VoiceResponse
from ai_processing import extract_intent
from database import fetch_dynamic_details
from utils import twilio_response

async def handle_incoming_call():
    """Handles incoming Twilio calls."""
    twiml = VoiceResponse()
    gather = twiml.gather(input="speech dtmf", action="/process_speech", timeout=3)
    gather.say("Please ask about any available loans.")
    return twilio_response(str(twiml))

async def process_speech(request: Request):
    """Handles speech processing from Twilio."""
    form = await request.form()
    user_text = form.get("SpeechResult", "").strip()

    if not user_text:
        return twilio_response("I couldn't hear you. Please try again.")

    intent = await extract_intent(user_text)

    if not intent:
        return twilio_response("I couldn't understand your request.")

    details = await fetch_dynamic_details(intent)

    response_text = (
        " ".join([f"{key}: {value}" for key, value in details.items()])
        if details
        else "I couldn't find details for your query."
    )

    return twilio_response(response_text)
