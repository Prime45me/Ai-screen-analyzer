import logging
import io
import base64
import PIL.Image
import google.generativeai as genai
import config

logger = logging.getLogger("App")


def analyze_screenshot(image_pil: PIL.Image.Image) -> str:
    """
    Accepts a Pillow Image, encodes it as JPEG, sends it to the Gemini
    Vision API, and returns a structured ISSUE / EXPLANATION / SOLUTION response.
    """
    try:
        # Encode Pillow image to JPEG bytes in memory
        buffer = io.BytesIO()
        image_pil.save(buffer, format="JPEG", quality=config.IMAGE_JPEG_QUALITY)
        image_bytes = buffer.getvalue()

        # Configure the Gemini SDK
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')

        # System prompt with strict three-part structure
        system_prompt = (
            "You are a real-time screen assistant. Analyze the screenshot and provide a response in exactly three sections:\n"
            "ISSUE: [Briefly identify the main problem, error, or focal point]\n"
            "EXPLANATION: [Explain the context or root cause in 1-2 sentences]\n"
            "SOLUTION: [Provide the specific code, command, or step-by-step fix]\n\n"
            "Keep the entire response under 100 words. Be direct and technical."
        )

        # Build the image part inline
        image_part = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(image_bytes).decode("utf-8")
        }

        response = model.generate_content([system_prompt, image_part])

        if response and response.text:
            return response.text.strip()
        else:
            return "Could not analyze screen."

    except Exception as e:
        logger.error(f"Vision API Error: {str(e)}")
        return "Could not analyze screen."
