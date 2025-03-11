from twilio.twiml.voice_response import VoiceResponse

def twilio_response(message, redirect_url=None):
    """Helper function to generate a Twilio-compatible XML response."""
    response = VoiceResponse()
    response.say(message, voice="alice")

    if redirect_url:
        response.redirect(redirect_url)

    return str(response)
