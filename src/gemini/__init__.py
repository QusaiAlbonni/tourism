from django.conf import settings
import google.generativeai as genai

version = getattr(settings,'GEMINI_GENERATIVE_MODEL')

gemini = genai.GenerativeModel(version)