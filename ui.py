import sys
from PyQt5.QtCore import Qt, QTimer, QEvent, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMainWindow, QSplitter, QScrollArea, QPushButton, QLineEdit, QFrame
from PyQt5.QtGui import QPainter, QColor, QPen

def interpolate_color(start_color, end_color, factor):
    """Linearly interpolate between two colors.
       factor should be between 0 (start_color) and 1 (end_color).
    """
    r = start_color[0] + (end_color[0] - start_color[0]) * factor
    g = start_color[1] + (end_color[1] - start_color[1]) * factor
    b = start_color[2] + (end_color[2] - start_color[2]) * factor
    return (int(r), int(g), int(b))

# --- Custom ToggleSwitch ---
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Increased fixed size to allow more margin so the slider outline isn’t cut off
        self.setFixedSize(70, 35)
        self._checked = False
        self._circle_pos = 3  # starting position with a bit more margin
        self.animation = QPropertyAnimation(self, b"circle_pos", self)
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        if self._checked:
            self.animation.setStartValue(3)
            self.animation.setEndValue(self.width() - self.height() + 3)
        else:
            self.animation.setStartValue(self.width() - self.height() + 3)
            self.animation.setEndValue(3)
        self.animation.start()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Draw slider background with highlighted outline
        slider_rect = self.rect()
        slider_color = QColor(200, 200, 200) if not self._checked else QColor(150, 150, 150)
        slider_outline = QColor(120, 120, 120)
        p.setPen(QPen(slider_outline, 2))
        p.setBrush(slider_color)
        p.drawRoundedRect(slider_rect, slider_rect.height() / 2, slider_rect.height() / 2)
        
        # Draw the sliding circle with a more prominent outline
        circle_diameter = self.height() - 6
        circle_rect = QRectF(self._circle_pos, 3, circle_diameter, circle_diameter)
        circle_color = QColor(255, 255, 255) if not self._checked else QColor(80, 80, 80)
        circle_outline = QColor(50, 50, 50)
        p.setPen(QPen(circle_outline, 3))
        p.setBrush(circle_color)
        p.drawEllipse(circle_rect)
        
        # Draw icon (sun for light mode, moon for dark mode) inside the circle
        icon = "☀" if not self._checked else "☾"
        p.setPen(QPen(Qt.black))
        font = p.font()
        font.setPointSize(10)
        p.setFont(font)
        p.drawText(circle_rect, Qt.AlignCenter, icon)
        p.end()

    def get_circle_pos(self):
        return self._circle_pos

    def set_circle_pos(self, pos):
        self._circle_pos = pos
        self.update()

    circle_pos = pyqtProperty(int, fget=get_circle_pos, fset=set_circle_pos)

# --- Settings Menu Widget ---
class SettingsMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px solid #888;
                border-radius: 8px;
            }
            QPushButton#closeButton {
                border: none;
                font-weight: bold;
            }
            QPushButton#resetButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton#resetButton:hover {
                background-color: #45a049;
            }
        """)
        layout = QVBoxLayout(self)
        # Title bar with close button
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        close_button = QPushButton("X")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.hide)
        title_layout.addWidget(close_button)
        layout.addLayout(title_layout)
        
        # Add dark/light toggle switch and reset button
        controls_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.toggle = ToggleSwitch()  # our custom toggle switch
        controls_layout.addWidget(self.reset_button)
        controls_layout.addWidget(self.toggle)
        layout.addLayout(controls_layout)

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark/Light Mode UI")
        # Set initial size to roughly half of 1920x1080 (e.g., 960x540)
        self.resize(960, 540)
        self.init_ui()
        # Color definitions
        self.light_bg = (255, 255, 255)
        self.dark_bg = (45, 45, 45)
        self.light_text = (0, 0, 0)
        self.dark_text = (220, 220, 220)
        self.current_bg = self.light_bg
        self.current_text = self.light_text
        self.update_stylesheet(self.current_bg, self.current_text)

    def init_ui(self):
        # Main container widget and layout
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.central_layout = QVBoxLayout(self.central)
        self.central_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- Splitter with three parts ---
        self.splitter = QSplitter(Qt.Horizontal)
        # Thinner splitter handles (4px wide) and no extra outline
        self.splitter.setStyleSheet("QSplitter::handle { width: 4px; background-color: gray; }")
        
        # Part 1: Contains a QLineEdit for text input (styled)
        scroll1 = QScrollArea()
        part1 = QWidget()
        scroll1.setWidget(part1)
        scroll1.setWidgetResizable(True)
        part1_layout = QVBoxLayout(part1)
        part1_layout.addStretch()
        self.text_input = QLineEdit("Text")
        self.text_input.setMaximumWidth(200)
        self.text_input.setStyleSheet("QLineEdit { background-color: #fff; border: 1px solid #888; padding: 3px; }")
        part1_layout.addWidget(self.text_input, alignment=Qt.AlignCenter)
        part1_layout.addStretch()
        self.splitter.addWidget(scroll1)
        
        # Part 2: Displays the text from Part 1 in a QLabel
        scroll2 = QScrollArea()
        part2 = QWidget()
        scroll2.setWidget(part2)
        scroll2.setWidgetResizable(True)
        part2_layout = QVBoxLayout(part2)
        part2_layout.addStretch()
        self.text_display = QLabel(self.text_input.text())
        self.text_display.setStyleSheet("QLabel { background-color: #ddd; border: 1px solid #666; padding: 3px; }")
        self.text_display.setAlignment(Qt.AlignCenter)
        part2_layout.addWidget(self.text_display, alignment=Qt.AlignCenter)
        part2_layout.addStretch()
        self.splitter.addWidget(scroll2)
        
        # Part 3: A simple placeholder
        scroll3 = QScrollArea()
        part3 = QWidget()
        scroll3.setWidget(part3)
        scroll3.setWidgetResizable(True)
        part3_layout = QVBoxLayout(part3)
        placeholder = QLabel("Placeholder 3")
        placeholder.setAlignment(Qt.AlignCenter)
        part3_layout.addWidget(placeholder)
        self.splitter.addWidget(scroll3)
        
        self.central_layout.addWidget(self.splitter, stretch=1)
        
        # Connect text input changes to update the display in Part 2
        self.text_input.textChanged.connect(self.text_display.setText)
        
        # --- Bottom bar: Cogwheel button ---
        bottom_bar = QHBoxLayout()
        self.cog_button = QPushButton("⚙")
        self.cog_button.setFixedSize(30, 30)
        self.cog_button.clicked.connect(self.show_settings_menu)
        bottom_bar.addWidget(self.cog_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        self.central_layout.addLayout(bottom_bar)
        
        # --- Settings Menu (overlay) ---
        self.settings_menu = SettingsMenu(self.central)
        self.settings_menu.hide()
        # Connect controls inside settings to functionality
        self.settings_menu.reset_button.clicked.connect(self.reset_splitter)
        self.settings_menu.toggle.toggled.connect(self.handle_mode_change)
        
        # Install event filter on the central widget to close settings if clicking outside
        self.central.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.central and event.type() == QEvent.MouseButtonPress:
            if self.settings_menu.isVisible():
                if not self.settings_menu.geometry().contains(event.pos()):
                    self.settings_menu.hide()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reposition the settings menu to bottom left if it is visible
        if self.settings_menu.isVisible():
            menu_width = int(self.width() * 0.3)
            menu_height = int(self.height() * 0.3)
            self.settings_menu.setFixedSize(menu_width, menu_height)
            self.settings_menu.move(10, self.central.height() - menu_height - 10)

    def show_settings_menu(self):
        menu_width = int(self.width() * 0.3)
        menu_height = int(self.height() * 0.3)
        self.settings_menu.setFixedSize(menu_width, menu_height)
        self.settings_menu.move(10, self.central.height() - menu_height - 10)
        self.settings_menu.show()

    def reset_splitter(self):
        count = self.splitter.count()
        total = sum(self.splitter.sizes())
        sizes = [total // count] * count
        self.splitter.setSizes(sizes)

    def handle_mode_change(self, dark_mode):
        target_bg = self.dark_bg if dark_mode else self.light_bg
        target_text = self.dark_text if dark_mode else self.light_text
        self.animate_color_change(self.current_bg, target_bg, self.current_text, target_text, duration=500)

    def animate_color_change(self, start_bg, end_bg, start_text, end_text, duration=500):
        steps = 20
        interval = duration // steps
        self.step = 0
        self.steps = steps

        def update_step():
            factor = self.step / self.steps
            new_bg = interpolate_color(start_bg, end_bg, factor)
            new_text = interpolate_color(start_text, end_text, factor)
            self.update_stylesheet(new_bg, new_text)
            self.step += 1
            if self.step > self.steps:
                self.timer.stop()
                self.current_bg = end_bg
                self.current_text = end_text

        self.timer = QTimer(self)
        self.timer.timeout.connect(update_step)
        self.timer.start(interval)

    def update_stylesheet(self, bg_color, text_color):
        style = f"""
            QWidget {{
                background-color: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]});
                color: rgb({text_color[0]}, {text_color[1]}, {text_color[2]});
                font-size: 14px;
            }}
        """
        self.setStyleSheet(style)

# For testing the UI module independently
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
