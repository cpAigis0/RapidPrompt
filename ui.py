import sys
from PyQt5.QtCore import Qt, QTimer, QEvent, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMainWindow,
                             QSplitter, QScrollArea, QPushButton, QFrame, QSplitterHandle, QSpinBox, QTextEdit)
from PyQt5.QtGui import QPainter, QColor, QPen

def interpolate_color(start_color, end_color, factor):
    """Interpolate between two colors and clamp the values."""
    r = start_color[0] + (end_color[0] - start_color[0]) * factor
    g = start_color[1] + (end_color[1] - start_color[1]) * factor
    b = start_color[2] + (end_color[2] - start_color[2]) * factor
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return (r, g, b)

# --- FocusFrame: A QFrame with rounded subtle outline that highlights on focus ---
class FocusFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.normal_border = "2px solid #ccc"   # Subtle border color
        self.focus_border = "2px solid #888"    # More highlighted border when focused
        self.update_border(False)

    def update_border(self, focused):
        border_style = self.focus_border if focused else self.normal_border
        self.setStyleSheet(f"QFrame {{ border: {border_style}; border-radius: 8px; }}")

    def focusInEvent(self, event):
        self.update_border(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.update_border(False)
        super().focusOutEvent(event)

# --- ToggleSwitch (unchanged) ---
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 35)
        self._checked = True  # Start in dark mode (checked means dark mode active)
        self._circle_pos = self.width() - self.height() + 3  
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
        
        slider_rect = self.rect()
        slider_color = QColor(200, 200, 200) if not self._checked else QColor(150, 150, 150)
        slider_outline = QColor(120, 120, 120)
        p.setPen(QPen(slider_outline, 2))
        p.setBrush(slider_color)
        p.drawRoundedRect(slider_rect, slider_rect.height() / 2, slider_rect.height() / 2)
        
        circle_diameter = self.height() - 6
        circle_rect = QRectF(self._circle_pos, 3, circle_diameter, circle_diameter)
        circle_color = QColor(255, 255, 255) if not self._checked else QColor(80, 80, 80)
        circle_outline = QColor(50, 50, 50)
        p.setPen(QPen(circle_outline, 3))
        p.setBrush(circle_color)
        p.drawEllipse(circle_rect)
        
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

# --- Custom Splitter Handle with two parallel lines in the middle ---
class CustomSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), Qt.transparent)
        line_thickness = 2
        gap = 3
        line_length = 20
        if self.orientation() == Qt.Horizontal:
            total_width = 2 * line_thickness + gap
            x_start = int((self.width() - total_width) / 2)
            y_start = int((self.height() - line_length) / 2)
            p.fillRect(x_start, y_start, line_thickness, line_length, Qt.gray)
            p.fillRect(x_start + line_thickness + gap, y_start, line_thickness, line_length, Qt.gray)
        else:
            total_height = 2 * line_thickness + gap
            y_start = int((self.height() - total_height) / 2)
            x_start = int((self.width() - line_length) / 2)
            p.fillRect(x_start, y_start, line_length, line_thickness, Qt.gray)
            p.fillRect(x_start, y_start + line_thickness + gap, line_length, line_thickness, Qt.gray)
        p.end()
    
    def sizeHint(self):
        default_hint = super().sizeHint()
        if self.orientation() == Qt.Horizontal:
            return QSize(self.parent().handleWidth(), default_hint.height())
        else:
            return QSize(default_hint.width(), self.parent().handleWidth())

class CustomSplitter(QSplitter):
    def createHandle(self):
        return CustomSplitterHandle(self.orientation(), self)

# --- Custom widget for Part 3: a text field with a header ---
class TextFieldWithHeader(FocusFrame):
    def __init__(self, header_text="Header", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.header = QLabel(header_text)
        self.header.setStyleSheet("QLabel { color: #555; }")  # Subtle header text color
        layout.addWidget(self.header)
        self.text_edit = QTextEdit("")
        self.text_edit.setMaximumWidth(200)  # Fixed width; height is flexible
        layout.addWidget(self.text_edit)

# --- Settings Menu (Overlay) ---
class SettingsMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_mode(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        self.close_button = QPushButton("X")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.hide)
        title_layout.addWidget(self.close_button)
        layout.addLayout(title_layout)
        controls_layout = QVBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.toggle = ToggleSwitch()
        controls_layout.addWidget(self.reset_button, alignment=Qt.AlignCenter)
        controls_layout.addWidget(self.toggle, alignment=Qt.AlignCenter)
        layout.addLayout(controls_layout)
        spin_layout = QHBoxLayout()
        self.spin_label = QLabel("Part 3 Fields:")
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setValue(1)
        spin_layout.addWidget(self.spin_label)
        spin_layout.addWidget(self.spin_box)
        layout.addLayout(spin_layout)
    
    def update_mode(self, dark_mode):
        if dark_mode:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2D2D2D;
                    border: 2px solid #AAA;
                    border-radius: 8px;
                    color: white;
                }
                QPushButton#closeButton {
                    border: none;
                    font-weight: bold;
                    background: transparent;
                    color: white;
                }
                QPushButton#closeButton:pressed {
                    background-color: #555;
                }
                QPushButton#resetButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 15px;
                }
                QPushButton#resetButton:hover {
                    background-color: #45a049;
                }
                QSpinBox {
                    background-color: #444;
                    color: white;
                    border: 1px solid #888;
                    padding: 2px;
                }
                QLabel {
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border: 2px solid #888;
                    border-radius: 8px;
                    color: black;
                }
                QPushButton#closeButton {
                    border: none;
                    font-weight: bold;
                    background: transparent;
                    color: black;
                }
                QPushButton#closeButton:pressed {
                    background-color: #ccc;
                }
                QPushButton#resetButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 15px;
                }
                QPushButton#resetButton:hover {
                    background-color: #45a049;
                }
                QSpinBox {
                    background-color: #fff;
                    color: black;
                    border: 1px solid #888;
                    padding: 2px;
                }
                QLabel {
                    color: black;
                }
            """)

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RapidPrompt")
        self.resize(960, 540)
        self.light_bg = (255, 255, 255)
        self.dark_bg = (45, 45, 45)
        self.light_text = (0, 0, 0)
        self.dark_text = (220, 220, 220)
        self.current_bg = self.dark_bg
        self.current_text = self.dark_text
        self.animating = False
        self.init_ui()
        self.update_stylesheet(self.current_bg, self.current_text)

    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.central_layout = QVBoxLayout(self.central)
        self.central_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- Splitter with three areas ---
        self.splitter = CustomSplitter(Qt.Horizontal)
        
        # Part 1: Multi-line text field wrapped in a FocusFrame.
        scroll1 = QScrollArea()
        scroll1.setStyleSheet("QScrollArea { border: none; }")
        part1 = FocusFrame()
        scroll1.setWidget(part1)
        scroll1.setWidgetResizable(True)
        part1_layout = QVBoxLayout(part1)
        part1_layout.addStretch()
        self.text_input = QTextEdit("Text")
        self.text_input.setMaximumWidth(200)
        part1_layout.addWidget(self.text_input, alignment=Qt.AlignCenter)
        part1_layout.addStretch()
        self.splitter.addWidget(scroll1)
        
        # Part 2: Displays the text from Part 1, wrapped in a FocusFrame.
        scroll2 = QScrollArea()
        scroll2.setStyleSheet("QScrollArea { border: none; }")
        part2 = FocusFrame()
        scroll2.setWidget(part2)
        scroll2.setWidgetResizable(True)
        part2_layout = QVBoxLayout(part2)
        part2_layout.addStretch()
        self.text_display = QLabel(self.text_input.toPlainText())
        self.text_display.setStyleSheet("QLabel { padding: 3px; }")
        self.text_display.setAlignment(Qt.AlignCenter)
        part2_layout.addWidget(self.text_display, alignment=Qt.AlignCenter)
        part2_layout.addStretch()
        self.splitter.addWidget(scroll2)
        
        # Part 3: Contains text fields with headers, wrapped in a FocusFrame.
        scroll3 = QScrollArea()
        scroll3.setStyleSheet("QScrollArea { border: none; }")
        part3 = FocusFrame()
        scroll3.setWidget(part3)
        scroll3.setWidgetResizable(True)
        self.part3_layout = QVBoxLayout(part3)
        self.part3_layout.setContentsMargins(0, 0, 0, 0)
        self.part3_layout.setSpacing(5)
        self.part3_fields = []
        field = TextFieldWithHeader("Header")
        self.part3_fields.append(field)
        self.part3_layout.addWidget(field)
        self.splitter.addWidget(scroll3)
        
        self.central_layout.addWidget(self.splitter, stretch=1)
        
        # Update Part 2 when text in Part 1 changes.
        self.text_input.textChanged.connect(lambda: self.text_display.setText(self.text_input.toPlainText()))
        
        # --- Bottom bar: Cogwheel button to open settings ---
        bottom_bar = QHBoxLayout()
        self.cog_button = QPushButton("⚙")
        self.cog_button.setFixedSize(30, 30)
        self.cog_button.clicked.connect(self.show_settings_menu)
        bottom_bar.addWidget(self.cog_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        self.central_layout.addLayout(bottom_bar)
        
        # --- Settings Menu (overlay), hidden by default ---
        self.settings_menu = SettingsMenu(self.central)
        self.settings_menu.hide()
        self.settings_menu.reset_button.clicked.connect(self.reset_splitter)
        self.settings_menu.toggle.toggled.connect(self.handle_mode_change)
        self.settings_menu.spin_box.valueChanged.connect(self.update_part3_fields)
        self.settings_menu.update_mode(self.current_bg == self.dark_bg)
        self.central.installEventFilter(self)

    def update_part3_fields(self, count):
        current_count = len(self.part3_fields)
        if count > current_count:
            for i in range(count - current_count):
                field = TextFieldWithHeader("Header")
                self.part3_fields.append(field)
                self.part3_layout.addWidget(field)
        elif count < current_count:
            for i in range(current_count - count):
                field = self.part3_fields.pop()
                self.part3_layout.removeWidget(field)
                field.deleteLater()

    def eventFilter(self, obj, event):
        if obj == self.central and event.type() == QEvent.MouseButtonPress:
            if self.settings_menu.isVisible():
                if not self.settings_menu.geometry().contains(event.pos()):
                    self.settings_menu.hide()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.settings_menu.isVisible():
            menu_width = int(self.width() * 0.4)
            menu_height = int(self.height() * 0.4)
            self.settings_menu.setFixedSize(menu_width, menu_height)
            x = (self.width() - menu_width) // 2
            y = (self.height() - menu_height) // 2
            self.settings_menu.move(x, y)

    def show_settings_menu(self):
        menu_width = int(self.width() * 0.4)
        menu_height = int(self.height() * 0.4)
        self.settings_menu.setFixedSize(menu_width, menu_height)
        x = (self.width() - menu_width) // 2
        y = (self.height() - menu_height) // 2
        self.settings_menu.move(x, y)
        self.settings_menu.update_mode(self.current_bg == self.dark_bg)
        self.settings_menu.show()

    def reset_splitter(self):
        count = self.splitter.count()
        total = sum(self.splitter.sizes())
        sizes = [total // count] * count
        self.splitter.setSizes(sizes)

    def handle_mode_change(self, dark_mode):
        if self.animating:
            return
        target_bg = self.dark_bg if dark_mode else self.light_bg
        target_text = self.dark_text if dark_mode else self.light_text
        self.animating = True
        self.animate_color_change(self.current_bg, target_bg, self.current_text, target_text, duration=500)
        self.settings_menu.update_mode(dark_mode)

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
                self.animating = False

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
