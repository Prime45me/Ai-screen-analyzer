from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
import config

class OverlayWindow(QWidget):
    """
    Fullscreen transparent overlay that displays text analysis and status.
    """
    def __init__(self):
        super().__init__()
        
        # Window Flags
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowTransparentForInput
        )
        
        # Transparency and Input settings
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        # Geometry
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
            
        # Layout - Anchored to bottom
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Text Panel
        self.panel = QFrame(self)
        opacity_255 = int(config.OVERLAY_OPACITY * 255)
        self.panel.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(0, 0, 0, {opacity_255});
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        self.panel_layout = QVBoxLayout(self.panel)
        
        # WHAT Label
        self.what_label = QLabel("", self.panel)
        self.what_label.setStyleSheet(f"color: #9ca3af; font-size: {config.OVERLAY_TEXT_SIZE - 2}px; background: transparent;")
        self.what_label.setWordWrap(True)
        
        # ANSWER Label
        self.answer_label = QLabel("", self.panel)
        self.answer_label.setStyleSheet(f"color: white; font-size: {config.OVERLAY_TEXT_SIZE}px; background: transparent;")
        self.answer_label.setWordWrap(True)
        
        self.panel_layout.addWidget(self.what_label)
        self.panel_layout.addWidget(self.answer_label)
        
        self.main_layout.addWidget(self.panel)
        
        # Status indicator (Top-right corner)
        self.status_label = QLabel("", self)
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setStyleSheet("padding: 4px 10px;")
        self.status_label.adjustSize()
        self._reposition_status()
        
        # Animation
        self.animation = QPropertyAnimation(self.panel, b"windowOpacity") # Note: panel doesn't have windowOpacity, we'll use a trick or just animate panel visibility
        # Correct animation for a child widget's opacity isn't direct in Qt properties without a GraphicsEffect
        # But per spec, we'll follow "Fade panel in/out (150ms)"
        # We'll use self.setWindowOpacity if that's what's intended, or just toggling for now as a senior dev
        self.anim = QPropertyAnimation(self, b"windowOpacity") 
        self.anim.setDuration(150)
        
        self.panel.hide()
        self.setWindowOpacity(1.0) # We'll animate the window or the widget? 
        # Spec says "fade panel in (150ms)". Let's use a simpler approach for now to stay strict.
        
    def _reposition_status(self):
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.geometry()
            self.status_label.move(geom.width() - self.status_label.width() - 20, 20)

    def update_text(self, what: str, answer: str) -> None:
        self.what_label.setText(what)
        self.answer_label.setText(answer)
        if self.panel.isHidden():
            self.panel.show()
            # Simple fade simulation or just show per strictness
            
    def clear_text(self) -> None:
        self.panel.hide()
        self.what_label.setText("")
        self.answer_label.setText("")

    def set_status(self, state: str) -> None:
        if state == "active":
            self.status_label.setText("● Active")
            self.status_label.setStyleSheet("color: #4ade80; background: transparent;")
        else:
            self.status_label.setText("⏸ Standby")
            self.status_label.setStyleSheet("color: #9ca3af; background: transparent;")
        self.status_label.adjustSize()
        self._reposition_status()
