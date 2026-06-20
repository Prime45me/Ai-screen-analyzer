from google import genai
from google.genai import types
import config

def analyze_text(text: str) -> str:
    """
    Sends highlighted text to Gemini with a strict structural prompt.
    """
    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)

        system_prompt = (
            "You are a sharp, experienced technical assistant. "
            "The user has highlighted text from their screen and needs you to help them with it directly.\n\n"
            "CRITICAL RULE: Always engage with the content — never describe or critique what the text is. "
            "If it is a question, answer it. If it is code, fix or explain it. "
            "If it is an error, diagnose and solve it. If it is a concept, explain it. "
            "Treat every input as something the user needs your help with, not something to review.\n\n"
            "Always respond in exactly this structure:\n\n"
            "ISSUE: One sentence — the core problem, question, or topic being addressed.\n"
            "EXPLANATION: 1–2 sentences — the cause, the reasoning, or the key context.\n"
            "SOLUTION: 1–2 sentences — the direct answer, fix, or actionable takeaway. "
            "If code needs fixing, show the corrected line inline.\n\n"
            "Rules:\n"
            "- Never say 'this text is...' or 'the user is asking...' or describe the input\n"
            "- Never use filler phrases like 'Great question' or 'Certainly'\n"
            "- Never repeat the input back\n"
            "- Stay under 100 words total\n"
            "- Be precise. Be useful. Skip everything else."
        )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
            )
        )

        if response and response.text:
            return response.text.strip()

        return "Could not analyze text."

    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "resource_exhausted" in err_msg:
            print("Vision API: Quota exhausted (429).")
            return "Quota reached. Pausing..."
        print(f"Vision API Error: {e}")
        return "Could not analyze text."