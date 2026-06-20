# Application Performance Summary

## Current Configuration
- **Model**: `gemini-flash-latest` (Optimized for speed and stable quota)
- **Polling Interval**: `3.0 seconds`
- **Capture Interval**: `10.0 seconds`
- **Minimum Text Length**: `3 characters`

## Latency & Responsiveness
- **API Response Time**: Typically 1.5s - 3.0s depending on network.
- **UI Refresh Rate**: The overlay updates every ~3-5 seconds when text changes are detected.
- **CPU Usage**: Minimal; the application sleeps between polls.

## Quota Performance
- **Tier**: Google AI Studio (Free)
- **Sustainability**: The 3s polling rate is designed to be sustainable for continuous use during work sessions without triggering 429 exhaustion for several hours.
- **Error Recovery**: Automatically detects 429 errors and notifies the user via the overlay.
