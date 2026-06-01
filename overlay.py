from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
import config

class OverlayWindow(QWidget):
    """
    Full-screen immersive overlay that displays structured analysis.
    Uses HTML-based styling for distinct sections (ISSUE, EXPLANATION, SOLUTION).
    """
    def __init__(self):
        super().__init__()
        
        # High-level window flags
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowTransparentForInput
        )
        
        # Transparency and click-through attributes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            self.setGeometry(primary_screen.geometry())
        
        # Main layout centered for immersive feel
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Central transparent panel
        self.panel = QFrame(self)
        opacity_val = int(config.OVERLAY_OPACITY * 255)
        self.panel.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(0, 0, 0, {opacity_val});
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        self.panel_layout = QVBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(40, 40, 40, 40)
        self.panel_layout.setSpacing(20)
        
        # Rich content label
        self.label = QLabel("", self.panel)
        self.label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {config.OVERLAY_TEXT_SIZE}px;
                background: transparent;
            }}
        """)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Width: 80% of screen for full-screen presence
        if primary_screen:
            self.label.setMaximumWidth(int(primary_screen.geometry().width() * 0.8))
        
        self.panel_layout.addWidget(self.label)
        self.main_layout.addWidget(self.panel)
        
        # Fade animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.setWindowOpacity(0.0)
        self.panel.hide()

        # Status indicator — fixed top-right corner
        self.status_label = QLabel("", self)
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setStyleSheet(
            "color: #4ade80;"
            "background: rgba(0, 0, 0, 120);"
            "border-radius: 8px;"
            "padding: 4px 10px;"
        )
        self.status_label.adjustSize()
        if primary_screen:
            screen_geom = primary_screen.geometry()
            self.status_label.move(
                screen_geom.width() - self.status_label.width() - 20, 20
            )
        self.status_label.show()

    def _format_text(self, text: str) -> str:
        """
        Parses structured text and applies color-coded HTML formatting.
        """
        # Define colors for headers
        color_map = {
            "ISSUE:": "#FF6B6B",      # Coral Red
            "EXPLANATION:": "#4D96FF", # Sky Blue
            "SOLUTION:": "#6BCB77"    # Emerald Green
        }
        
        formatted = text
        for header, color in color_map.items():
            if header in formatted:
                # Add spacing and styling to headers
                styled_header = (
                    f'<br><span style="color: {color}; font-size: {config.OVERLAY_HEADER_SIZE}px; '
                    f'font-weight: bold; text-transform: uppercase;">{header}</span><br>'
                )
                formatted = formatted.replace(header, styled_header)
        
        # Clean up leading breaks from first header
        if formatted.startswith("<br>"):
            formatted = formatted[4:]
            
        return formatted

    def update_text(self, text: str) -> None:
        """
        Formats and displays the structured text with a fade-in animation.
        """
        if not text:
            self.clear_text()
            return
            
        # Update with rich-text formatted content
        self.label.setText(self._format_text(text))
        
        if self.panel.isHidden():
            self.panel.show()
            try: self.animation.finished.disconnect()
            except: pass
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.start()

    def clear_text(self) -> None:
        """
        Hides the overlay with a fade-out animation.
        """
        if not self.panel.isHidden():
            self.animation.setStartValue(self.windowOpacity())
            self.animation.setEndValue(0.0)
            self.animation.finished.connect(self.panel.hide)
            self.animation.start()

    def set_status(self, state: str) -> None:
        """
        Updates the top-right status indicator.
        state='active'  → '● Active'  in green  (#4ade80)
        state='standby' → '⏸ Standby' in grey   (#9ca3af)
        """
        if state == "active":
            text = "● Active"
            color = "#4ade80"
        else:
            text = "⏸ Standby"
            color = "#9ca3af"

        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color};"
            "background: rgba(0, 0, 0, 120);"
            "border-radius: 8px;"
            "padding: 4px 10px;"
        )
        self.status_label.adjustSize()
        # Re-anchor to top-right after size change
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            screen_geom = primary_screen.geometry()
            self.status_label.move(
                screen_geom.width() - self.status_label.width() - 20, 20
            )
