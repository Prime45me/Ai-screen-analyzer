import logging
import numpy as np
import easyocr
import PIL.Image
import google.generativeai as genai
import config

logger = logging.getLogger("App")

# Initialize the EasyOCR reader once at module level (lazy initialization)
_ocr_reader = None

def _get_ocr_reader():
    """Lazily initializes and returns the EasyOCR reader."""
    global _ocr_reader
    if _ocr_reader is None:
        logger.info("Initializing EasyOCR reader (first run may take a moment)...")
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
        logger.info("EasyOCR reader ready.")
    return _ocr_reader


def extract_text_from_image(image_np: np.ndarray) -> str:
    """
    Uses EasyOCR to extract all text from a NumPy image array.
    Returns the concatenated text as a single string.
    """
    try:
        reader = _get_ocr_reader()
        results = reader.readtext(image_np, detail=0, paragraph=True)
        extracted = "\n".join(results).strip()
        logger.info(f"OCR extracted {len(extracted)} chars.")
        return extracted
    except Exception as e:
        logger.error(f"OCR Error: {e}")
        return ""


def analyze_screenshot(image_pil: PIL.Image.Image, highlighted_text: str | None = None) -> str:
    """
    Extracts text from the screen via local OCR, then analyzes it
    using the Gemini Text API (no Vision/image upload needed).
    Returns a structured ISSUE / EXPLANATION / SOLUTION response.
    If highlighted_text is provided, it is prepended to the prompt as focus context.
    """
    try:
        # Convert PIL Image to NumPy array for OCR
        image_np = np.array(image_pil)
        
        # Step 1: Extract text locally with OCR
        screen_text = extract_text_from_image(image_np)

        if not screen_text:
            return "Could not read any text from the screen."

        # Step 2: Configure Gemini Text API
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')

        # Step 3: Build a text-only prompt using the OCR output
        # If highlighted_text is provided, prepend focus context block
        highlighted_block = ""
        if highlighted_text is not None:
            highlighted_block = (
                f"The user has highlighted this text on screen:\n\"{highlighted_text}\"\n"
                "Focus your analysis on this selection specifically.\n\n"
            )

        prompt = (
            highlighted_block +
            "You are a real-time screen assistant. The following text was extracted "
            "from the user's screen via OCR. Analyze it and respond in exactly three sections:\n\n"
            "ISSUE: [Briefly identify the main problem, error, or focal point]\n"
            "EXPLANATION: [Explain the context or root cause in 1-2 sentences]\n"
            "SOLUTION: [Provide the specific code, command, or fix]\n\n"
            "Keep the entire response under 100 words. Be direct and technical.\n\n"
            "--- SCREEN TEXT ---\n"
            f"{screen_text[:3000]}"  # Cap at 3000 chars to stay within token limits
        )

        response = model.generate_content(prompt)

        if response and response.text:
            return response.text.strip()
        else:
            return "Could not analyze screen."

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return "Could not analyze screen."
