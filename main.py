import os
import json
import base64
import asyncio,websocket
from fastapi import FastAPI,WebSocket,Request
from fastapi.responses import HTMLResponse,JSONResponse
from twilio.twiml.voice_response import VoiceResponse,Connect,Say,Stream

openai_api_key=""

port=5050
SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about "
    "anything the user is interested in and is prepared to offer them facts. "
    "You have a penchant for dad jokes, owl jokes, and rickrolling – subtly. "
    "Always stay positive, but work in a joke when appropriate."
)
voice="alloy"
app=FastAPI()
@app.api_route()