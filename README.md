# AI Screen Assistant

An immersive, full-screen Python desktop application that actively monitors your screen and provides real-time, AI-driven analysis using Google's Gemini Vision API. It's built for developers, designers, and anyone who wants an intelligent assistant looking over their shoulder.

## Features

- 🧠 **Context-Aware Analysis**: Automatically identifies errors, explains complex code, or summarizes workflows based on what's visible on your screen.
- 🎨 **Immersive Full-Screen UI**: A beautifully frosted, transparent 60%-opacity overlay built with PyQt6.
- 🧱 **Structured Responses**: Analysis is always delivered in an easy-to-read, color-coded structure:
  - **ISSUE**: Identifies the primary problem or focal point.
  - **EXPLANATION**: Deep dive into the context or root cause.
  - **SOLUTION**: Actionable steps, commands, or code snippets.
- 🖱️ **Completely Click-Through**: You can continue to use your mouse and keyboard seamlessly without the overlay interrupting your workflow.
- ⚡ **Intelligent Image Diffing (Quota Saver)**: Compares your current screen array with the previous one. If your screen hasn't moved or changed significantly, the API call is skipped to save your Gemini API quota limits.

## Requirements

- Python 3.9+
- Windows (Currently optimized for Windows primary display capturing)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Prime45me/Ai-screen-analyzer.git
   cd Ai-screen-analyzer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Usage

Start the background monitoring loop:
```bash
python main.py
```

- The UI will fade in with analysis when a significant change on screen is detected.
- The default capture interval is every 15 seconds (can be changed in `config.py`).
- Press `Ctrl+C` in the terminal to exit the application.

## Libraries Used
- **PyQt6**: UI & Overlay mechanics.
- **mss**: Ultra-fast screen capturing.
- **OpenCV / NumPy**: Fast image manipulation and diffing algorithms.
- **Pillow**: Python imaging library.
- **Google Generative AI**: Access to Gemini Flash Models.
