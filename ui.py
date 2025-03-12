import sys
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QMainWindow, QSplitter, QScrollArea

def interpolate_color(start_color, end_color, factor):
    """Linearly interpolate between two colors.
       factor should be between 0 (start_color) and 1 (end_color).
    """
    r = start_color[0] + (end_color[0] - start_color[0]) * factor
    g = start_color[1] + (end_color[1] - start_color[1]) * factor
    b = start_color[2] + (end_color[2] - start_color[2]) * factor
    return (int(r), int(g), int(b))

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)  # Emits True for dark mode, False for light mode

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.sun_label = QLabel("☀")
        self.sun_label.setAlignment(Qt.AlignCenter)
        self.switch = QCheckBox()  # We use a checkbox as our toggle
        self.moon_label = QLabel("☾")
        self.moon_label.setAlignment(Qt.AlignCenter)

        self.switch.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border: 1px solid #ffffff;
                border-radius: 10px;
                background: #888888;
            }
            QCheckBox::indicator:unchecked {
                background: #cccccc;
            }
            QCheckBox::indicator:checked {
                background: #555555;
            }
        """)
        layout.addWidget(self.sun_label)
        layout.addWidget(self.switch)
        layout.addWidget(self.moon_label)
        self.switch.stateChanged.connect(lambda state: self.toggled.emit(state == Qt.Checked))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark/Light Mode UI")
        self.resize(400, 300)
        self.init_ui()
        # Define color tuples: (R, G, B)
        self.light_bg = (255, 255, 255)
        self.dark_bg = (45, 45, 45)
        self.light_text = (0, 0, 0)
        self.dark_text = (220, 220, 220)
        # Initially in light mode
        self.current_bg = self.light_bg
        self.current_text = self.light_text
        self.update_stylesheet(self.current_bg, self.current_text)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        # Create and place toggle switch in the top-left corner
        self.toggle = ToggleSwitch()
        self.toggle.toggled.connect(self.handle_mode_change)
        main_layout.addWidget(self.toggle, alignment=Qt.AlignLeft)
        # Replace placeholder label with a QSplitter containing three scrollable parts
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: gray; }")
        for i in range(1, 4):
            scroll = QScrollArea()
            part = QWidget()
            scroll.setWidget(part)
            scroll.setWidgetResizable(True)
            part_layout = QVBoxLayout(part)
            placeholder = QLabel(f"Placeholder {i}")
            placeholder.setAlignment(Qt.AlignCenter)
            part_layout.addWidget(placeholder)
            self.splitter.addWidget(scroll)
        main_layout.addWidget(self.splitter, stretch=1)

    def handle_mode_change(self, dark_mode):
        # Determine target colors based on mode
        target_bg = self.dark_bg if dark_mode else self.light_bg
        target_text = self.dark_text if dark_mode else self.light_text
        # Animate transition over 500ms (20 steps, 25ms interval)
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
                # Save final colors
                self.current_bg = end_bg
                self.current_text = end_text

        self.timer = QTimer(self)
        self.timer.timeout.connect(update_step)
        self.timer.start(interval)
    
    def update_stylesheet(self, bg_color, text_color):
        # Set background and text colors for the main window and its children
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
