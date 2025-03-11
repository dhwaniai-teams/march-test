import os
import requests
from fastapi import FastAPI, Form, Query
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from groq import Groq  # Import Groq SDK

app = FastAPI()

# Set your Groq API Key (Store securely in environment variables)
GROQ_API_KEY = "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"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

LANGUAGE_OPTIONS = {
    "1": {"lang": "en", "twilio_code": "en-IN", "voice": "Google.en-IN-Wavenet-D", "message": "You have selected English."},
    "2": {"lang": "hi", "twilio_code": "hi-IN", "voice": "Google.hi-IN-Wavenet-C", "message": "आपने हिंदी चुनी है।"},
    "3": {"lang": "kn", "twilio_code": "kn-IN", "voice": "Google.kn-IN-Wavenet-A", "message": "ನೀವು ಕನ್ನಡ ಆಯ್ಕೆ ಮಾಡಿಕೊಂಡಿದ್ದೀರಿ."}
}

@app.post("/incoming_call", response_class=PlainTextResponse)
async def incoming_call():
    """Handles incoming calls and asks the user to select a language."""
    response = VoiceResponse()
    gather = Gather(action="/select_language", num_digits=1)

    gather.say("Press 1 for English.", language="en", voice="Google.en-IN-Wavenet-D")
    gather.say("हिंदी के लिए 2 दबाएं।", language="hi", voice="Google.hi-IN-Wavenet-C")
    gather.say("ಕನ್ನಡಕ್ಕಾಗಿ 3 ಒತ್ತಿರಿ.", language="kn", voice="Google.kn-IN-Wavenet-A")

    response.append(gather)
    return str(response)

@app.post("/select_language", response_class=PlainTextResponse)
async def select_language(Digits: str = Form(...)):
    """Processes language selection and prompts user for input."""
    if Digits not in LANGUAGE_OPTIONS:
        return str(VoiceResponse().say("Invalid selection. Please try again.", language="en"))

    selected_language = LANGUAGE_OPTIONS[Digits]
    lang_code = selected_language["lang"]
    twilio_lang = selected_language["twilio_code"]
    voice = selected_language["voice"]
    message = selected_language["message"]

    response = VoiceResponse()
    response.say(message, language=twilio_lang, voice=voice)

    gather = Gather(
        action=f"/process_speech?lang={lang_code}",
        input="speech",
        language=twilio_lang,
        action_on_empty_result=True
    )
    gather.say(
        "अब बोलें।" if lang_code == "hi" else
        "ಇದೀಗ ಮಾತನಾಡಿ." if lang_code == "kn" else
        "You may speak now.", language=twilio_lang, voice=voice
    )

    response.append(gather)
    return str(response)

def get_ai_response(user_text, lang):
    """Fetches AI-generated response from Groq API."""
    system_prompt = {
        "en": "You are an AI that only responds in English, keeping responses short and precise.",
        "hi": "आप केवल हिंदी में उत्तर देने वाले एआई हैं, संक्षिप्त और सटीक उत्तर दें।",
        "kn": "ನೀವು ಕೇವಲ ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸುವ ಎಐ, ಉತ್ತರಗಳನ್ನು ಸಂಕ್ಷಿಪ್ತವಾಗಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಇಡಿ."
    }

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt.get(lang, "You are a helpful assistant.")},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.3-70b-versatile",  # Ensure this is the correct Groq model
            stream=False,
        )

        ai_response = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error fetching response from Groq: {e}")
        ai_response = {
            "hi": "मुझे खेद है, मैं आपकी सहायता नहीं कर सकता।",
            "kn": "ಕ್ಷಮಿಸಿ, ನಾನು ಸಹಾಯ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ.",
            "en": "Sorry, I am unable to process your request."
        }.get(lang, "Sorry, an error occurred.")

    print(f"\nUser ({lang}): {user_text}")
    print(f"AI Response: {ai_response}\n")

    return ai_response

@app.post("/process_speech", response_class=PlainTextResponse)
async def process_speech(SpeechResult: str = Form(None), lang: str = Query("en")):
    """Processes user speech input and gets AI response."""
    if lang not in ["en", "hi", "kn"]:
        lang = "en"  # Default to English if the language is unknown

    voice = next((value["voice"] for value in LANGUAGE_OPTIONS.values() if value["lang"] == lang), "Google.en-IN-Wavenet-D")

    if not SpeechResult:
        response = VoiceResponse()
        response.say(
            "I didn't catch that. Please try again." if lang == "en" else
            "मैंने सुना नहीं, कृपया पुनः प्रयास करें।" if lang == "hi" else
            "ನಾನು ಕೇಳಲಿಲ್ಲ, ದಯವಿಟ್ಟು ಪುನಃ ಪ್ರಯತ್ನಿಸಿ.",
            language=lang,
            voice=voice
        )
        return str(response)

    ai_response = get_ai_response(SpeechResult, lang)

    response = VoiceResponse()
    response.say(ai_response, language=lang, voice=voice)

    # Repeat speech recognition to continue conversation
    gather = Gather(
        action=f"/process_speech?lang={lang}",
        input="speech",
        language=LANGUAGE_OPTIONS.get(lang, {}).get("twilio_code", "en-IN"),
        action_on_empty_result=True
    )
    gather.say(
        "You may continue speaking." if lang == "en" else
        "आप जारी रख सकते हैं।" if lang == "hi" else
        "ನೀವು ಮುಂದುವರಿಸಬಹುದು.",
        language=lang,
        voice=voice
    )
    response.append(gather)

    return str(response)
