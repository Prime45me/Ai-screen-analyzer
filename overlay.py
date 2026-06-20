from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QApplication, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor
import config


class OverlayWindow(QWidget):
    """
    Fullscreen transparent overlay — click-through, always-on-top.
    Displays structured AI responses with visual hierarchy and smooth animations.
    """

    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
            self._screen_width = screen.geometry().width()
            self._screen_height = screen.geometry().height()
        else:
            self._screen_width = 1920
            self._screen_height = 1080

        # --- Root layout ---
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 40)
        root.setSpacing(0)
        root.addStretch()
        root.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        # --- Panel ---
        panel_width = min(760, int(self._screen_width * 0.55))

        self.panel = QFrame()
        self.panel.setFixedWidth(panel_width)
        self.panel.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(10, 10, 14, 220);
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.07);
            }}
        """)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(22, 18, 22, 20)
        panel_layout.setSpacing(10)

        # --- Header bar: accent line + label ---
        header = QHBoxLayout()
        header.setSpacing(10)

        accent = QFrame()
        accent.setFixedSize(3, 16)
        accent.setStyleSheet("background-color: #60a5fa; border-radius: 2px;")

        self.section_tag = QLabel("AI ASSISTANT")
        self.section_tag.setFont(QFont("Consolas", 8))
        self.section_tag.setStyleSheet("color: rgba(96, 165, 250, 0.7); background: transparent; letter-spacing: 2px;")

        header.addWidget(accent)
        header.addWidget(self.section_tag)
        header.addStretch()
        panel_layout.addLayout(header)

        # --- Divider ---
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(255,255,255,0.06); border: none;")
        panel_layout.addWidget(divider)

        # --- ISSUE row ---
        issue_row = QHBoxLayout()
        issue_row.setSpacing(10)

        issue_tag = QLabel("ISSUE")
        issue_tag.setFont(QFont("Consolas", 8))
        issue_tag.setFixedWidth(72)
        issue_tag.setAlignment(Qt.AlignmentFlag.AlignTop)
        issue_tag.setStyleSheet("""
            color: #f87171;
            background: rgba(248, 113, 113, 0.1);
            border-radius: 4px;
            padding: 2px 6px;
        """)

        self.issue_label = QLabel("")
        self.issue_label.setFont(QFont("Segoe UI", config.OVERLAY_TEXT_SIZE - 1))
        self.issue_label.setStyleSheet("color: #f1f5f9; background: transparent;")
        self.issue_label.setWordWrap(True)
        self.issue_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        issue_row.addWidget(issue_tag, 0, Qt.AlignmentFlag.AlignTop)
        issue_row.addWidget(self.issue_label, 1)
        panel_layout.addLayout(issue_row)

        # --- EXPLANATION row ---
        expl_row = QHBoxLayout()
        expl_row.setSpacing(10)

        expl_tag = QLabel("WHY")
        expl_tag.setFont(QFont("Consolas", 8))
        expl_tag.setFixedWidth(72)
        expl_tag.setAlignment(Qt.AlignmentFlag.AlignTop)
        expl_tag.setStyleSheet("""
            color: #60a5fa;
            background: rgba(96, 165, 250, 0.1);
            border-radius: 4px;
            padding: 2px 6px;
        """)

        self.expl_label = QLabel("")
        self.expl_label.setFont(QFont("Segoe UI", config.OVERLAY_TEXT_SIZE - 2))
        self.expl_label.setStyleSheet("color: #94a3b8; background: transparent;")
        self.expl_label.setWordWrap(True)
        self.expl_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        expl_row.addWidget(expl_tag, 0, Qt.AlignmentFlag.AlignTop)
        expl_row.addWidget(self.expl_label, 1)
        panel_layout.addLayout(expl_row)

        # --- SOLUTION row ---
        soln_row = QHBoxLayout()
        soln_row.setSpacing(10)

        soln_tag = QLabel("FIX")
        soln_tag.setFont(QFont("Consolas", 8))
        soln_tag.setFixedWidth(72)
        soln_tag.setAlignment(Qt.AlignmentFlag.AlignTop)
        soln_tag.setStyleSheet("""
            color: #4ade80;
            background: rgba(74, 222, 128, 0.1);
            border-radius: 4px;
            padding: 2px 6px;
        """)

        self.soln_label = QLabel("")
        self.soln_label.setFont(QFont("Segoe UI Semibold", config.OVERLAY_TEXT_SIZE - 1))
        self.soln_label.setStyleSheet("color: #e2e8f0; background: transparent;")
        self.soln_label.setWordWrap(True)
        self.soln_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        soln_row.addWidget(soln_tag, 0, Qt.AlignmentFlag.AlignTop)
        soln_row.addWidget(self.soln_label, 1)
        panel_layout.addLayout(soln_row)

        root.addWidget(self.panel, 0, Qt.AlignmentFlag.AlignHCenter)

        # --- Opacity effect for fade animation ---
        self._opacity_effect = QGraphicsOpacityEffect(self.panel)
        self._opacity_effect.setOpacity(0.0)
        self.panel.setGraphicsEffect(self._opacity_effect)

        self._anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.panel.hide()

        # --- Status indicator ---
        self.status_label = QLabel("● Active", self)
        self.status_label.setFont(QFont("Consolas", 9))
        self.status_label.setStyleSheet("""
            color: #4ade80;
            background: rgba(10, 10, 14, 180);
            border-radius: 8px;
            padding: 4px 10px;
        """)
        self.status_label.adjustSize()
        self._reposition_status()

    # ------------------------------------------------------------------

    def _reposition_status(self):
        self.status_label.adjustSize()
        x = self._screen_width - self.status_label.width() - 20
        self.status_label.move(x, 20)

    def _fade_in(self):
        self.panel.show()
        self._anim.stop()
        self._anim.setStartValue(self._opacity_effect.opacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _fade_out(self):
        self._anim.stop()
        self._anim.setStartValue(self._opacity_effect.opacity())
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.panel.hide)
        self._anim.start()

    # ------------------------------------------------------------------

    def update_text(self, issue: str, explanation: str, solution: str) -> None:
        """Update all three response sections and fade the panel in."""
        self.issue_label.setText(issue)
        self.expl_label.setText(explanation)
        self.soln_label.setText(solution)
        self._fade_in()

    def show_loading(self) -> None:
        """Show a brief loading state while the API call is in flight."""
        self.issue_label.setText("Analyzing…")
        self.expl_label.setText("")
        self.soln_label.setText("")
        self._fade_in()

    def clear_text(self) -> None:
        """Fade out and hide the panel."""
        try:
            self._anim.finished.disconnect()
        except RuntimeError:
            pass
        self._fade_out()

    def set_status(self, state: str) -> None:
        """Update the top-right status indicator."""
        if state == "active":
            self.status_label.setText("● Active")
            self.status_label.setStyleSheet("""
                color: #4ade80;
                background: rgba(10, 10, 14, 180);
                border-radius: 8px;
                padding: 4px 10px;
            """)
        else:
            self.status_label.setText("⏸ Standby")
            self.status_label.setStyleSheet("""
                color: #9ca3af;
                background: rgba(10, 10, 14, 180);
                border-radius: 8px;
                padding: 4px 10px;
            """)
        self._reposition_status()