from google import genai
import config

def analyze_text(text: str) -> str:
    """
    Sends highlighted text to Gemini with a strict structural prompt.
    """
    try:
        # Initialize with API key
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        system_prompt = (
            "You are a real-time assistant. The user has highlighted this text.\n"
            "If it is code: identify the language, explain what it does in 1–2 sentences, "
            "flag any obvious issues and suggest a fix.\n"
            "If it is an error message: explain the cause and give a concrete fix in 2–3 sentences.\n"
            "If it is plain text: summarize it in 1–2 sentences.\n"
            "Keep all responses under 80 words. Be direct and concise.\n"
            "Format your response as:\n"
            "WHAT: one line describing what this is\n"
            "ANSWER: your explanation or fix"
        )
        
        # Send request
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nTEXT TO ANALYZE:\n{text}"
        )
        
        if response and response.text:
            return response.text.strip()
        
        return "Could not analyze text."
        
    except Exception as e:
        print(f"Vision API Error: {e}")
        return "Could not analyze text."
