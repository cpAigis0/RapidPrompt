import sys
from PyQt5.QtCore import Qt, QTimer, QEvent, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMainWindow,
                             QSplitter, QScrollArea, QPushButton, QFrame, QSplitterHandle, QSpinBox,
                             QTextEdit, QLineEdit, QSizePolicy)
from PyQt5.QtGui import QPainter, QColor, QPen

def interpolate_color(start_color, end_color, factor):
    return (
        int(max(0, min(255, start_color[0] + (end_color[0] - start_color[0]) * factor))),
        int(max(0, min(255, start_color[1] + (end_color[1] - start_color[1]) * factor))),
        int(max(0, min(255, start_color[2] + (end_color[2] - start_color[2]) * factor)))
    )

# Keeping CustomOutlineFrame for the settings menu if needed,
# but not using it for the main parts anymore.
class CustomOutlineFrame(QFrame):
    def __init__(self, position="middle", parent=None):
        super().__init__(parent)
        self.position = position
        self.border_color = QColor("#e0e0e0")
        self.pen_width = 1
        self.radius = 8
        self.inset = 5  # Reduced inset for balanced spacing
        self.setContentsMargins(5, 5, 5, 5)
        self.setFrameStyle(QFrame.NoFrame)

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 35)
        self._checked = True
        self._circle_pos = self.width() - self.height() + 3
        self.animation = QPropertyAnimation(self, b"circle_pos")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._locked = False

    def lock(self, value):
        self._locked = value

    def mousePressEvent(self, event):
        if self._locked:
            return
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        self.animation.setStartValue(3 if self._checked else self.width() - self.height() + 3)
        self.animation.setEndValue(self.width() - self.height() + 3 if self._checked else 3)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        slider_color = QColor(200, 200, 200) if not self._checked else QColor(150, 150, 150)
        p.setPen(QPen(QColor(120, 120, 120), 2))
        p.setBrush(slider_color)
        p.drawRoundedRect(self.rect(), self.height()/2, self.height()/2)
        
        circle_diameter = self.height() - 6
        circle_rect = QRectF(self._circle_pos, 3, circle_diameter, circle_diameter)
        circle_color = QColor(255, 255, 255) if not self._checked else QColor(80, 80, 80)
        p.setPen(QPen(QColor(50, 50, 50), 3))
        p.setBrush(circle_color)
        p.drawEllipse(circle_rect)
        
        p.setPen(QPen(Qt.black))
        font = p.font()
        font.setPointSize(10)
        p.setFont(font)
        p.drawText(circle_rect, Qt.AlignCenter, "☀" if not self._checked else "☾")
        p.end()

    circle_pos = pyqtProperty(int, 
        lambda self: self._circle_pos,
        lambda self, pos: setattr(self, '_circle_pos', pos) or self.update())

class CustomSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        line_thickness = 1
        center_x = self.width() // 2
        line_length = 20
        y_start = (self.height() - line_length) // 2
        
        p.fillRect(center_x-2-line_thickness, y_start, line_thickness, line_length, Qt.gray)
        p.fillRect(center_x+2, y_start, line_thickness, line_length, Qt.gray)
        p.setPen(QPen(Qt.gray, 1))
        p.drawLine(center_x, 0, center_x, self.height())
        p.end()

    def sizeHint(self):
        default = super().sizeHint()
        if self.orientation() == Qt.Horizontal:
            return QSize(self.parent().handleWidth(), default.height())
        return QSize(default.width(), self.parent().handleWidth())

class CustomSplitter(QSplitter):
    def createHandle(self):
        return CustomSplitterHandle(self.orientation(), self)

class TextFieldWithHeader(QWidget):
    def __init__(self, header_text="Header", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.header = QLineEdit(header_text)
        self.header.setStyleSheet("QLineEdit { color: #555; font-size: 10px; border: none; }")
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumWidth(200)
        self.text_edit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        layout.addWidget(self.header)
        layout.addWidget(self.text_edit)

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()

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
        
        controls = QVBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        self.toggle = ToggleSwitch()
        controls.addWidget(self.reset_button, alignment=Qt.AlignCenter)
        controls.addWidget(self.toggle, alignment=Qt.AlignCenter)
        layout.addLayout(controls)
        
        spin_layout = QHBoxLayout()
        spin_layout.addWidget(QLabel("Part 3 Fields:"))
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setValue(3)  # Start with 3 fields
        spin_layout.addWidget(self.spin_box)
        layout.addLayout(spin_layout)

    def update_mode(self, dark_mode):
        base = """
            QFrame { border: 2px solid %s; border-radius: 8px; }
            QPushButton#closeButton { border: none; font-weight: bold; background: transparent; }
            QPushButton#resetButton { border-radius: 5px; padding: 8px 15px; }
            QSpinBox { padding: 2px; }"""
        
        if dark_mode:
            self.setStyleSheet(base % "#AAA" + """
                QFrame { background-color: #2D2D2D; color: white; }
                QPushButton#closeButton { color: white; }
                QPushButton#closeButton:pressed { background-color: #555; }
                QPushButton#resetButton { background-color: #4CAF50; color: white; }
                QPushButton#resetButton:hover { background-color: #45a049; }
                QSpinBox { background-color: #444; color: white; border: 1px solid #888; }
                QLabel { color: white; }""")
        else:
            self.setStyleSheet(base % "#888" + """
                QFrame { background-color: #f0f0f0; color: black; }
                QPushButton#closeButton { color: black; }
                QPushButton#closeButton:pressed { background-color: #ccc; }
                QPushButton#resetButton { background-color: #4CAF50; color: white; }
                QPushButton#resetButton:hover { background-color: #45a049; }
                QSpinBox { background-color: white; color: black; border: 1px solid #888; }
                QLabel { color: black; }""")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RapidPrompt")
        self.resize(1600, 900)
    
        # Color configurations
        self.light_bg = (255, 255, 255)
        self.dark_bg = (45, 45, 45)
        self.light_text = (0, 0, 0)
        self.dark_text = (220, 220, 220)
        self.current_bg = self.dark_bg
        self.current_text = self.dark_text
        self.textfield_bg_light = (255, 255, 255)
        self.textfield_bg_dark = (58, 58, 58)
        self.textfield_border_light = (204, 204, 204)
        self.textfield_border_dark = (85, 85, 85)
    
        self.animating = False
        self.timer = None
    
        self.init_ui()
        self.update_stylesheet(self.current_bg, self.current_text)
        self.update_text_field_styles_dynamic(self.current_bg)
    
        # Instantiate settings menu and connect dark/light toggle signal
        self.settings_menu = SettingsMenu(self.central)
        self.settings_menu.hide()
        self.settings_menu.toggle.toggled.connect(self.handle_mode_change)

    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        main_layout = QVBoxLayout(self.central)
        main_layout.setContentsMargins(10, 10, 10, 10)
    
        # --- Create a vertical splitter to divide top and bottom sections ---
        vertical_splitter = QSplitter(Qt.Vertical)
    
        # --- Top Section: Horizontal splitter with Part 1 and Part 2 ---
        top_splitter = CustomSplitter(Qt.Horizontal)
        top_splitter.setHandleWidth(15)
    
        # Part 1 (Left): Text Input without extra outline
        scroll1 = QScrollArea()
        part1 = QWidget()  # Use plain QWidget instead of CustomOutlineFrame
        scroll1.setWidget(part1)
        scroll1.setWidgetResizable(True)
        self.text_input = QTextEdit()  # Your text field with its own styling
        self.text_input.setMinimumWidth(200)
        layout1 = QVBoxLayout(part1)
        layout1.setContentsMargins(0, 0, 0, 0)
        layout1.addWidget(self.text_input, alignment=Qt.AlignCenter)
        top_splitter.addWidget(scroll1)
    
        # Part 2 (Right): Text Display without extra outline
        scroll2 = QScrollArea()
        part2 = QWidget()  # Use plain QWidget
        scroll2.setWidget(part2)
        scroll2.setWidgetResizable(True)
        self.text_display = QLabel()
        self.text_display.setAlignment(Qt.AlignCenter)
        layout2 = QVBoxLayout(part2)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.addWidget(self.text_display, alignment=Qt.AlignCenter)
        top_splitter.addWidget(scroll2)
    
        vertical_splitter.addWidget(top_splitter)
    
        # --- Bottom Section: Part 3 spanning full width ---
        scroll3 = QScrollArea()
        part3 = QWidget()  # Use plain QWidget to avoid an extra outline
        scroll3.setWidget(part3)
        scroll3.setWidgetResizable(True)
    
        self.part3_container = QWidget()
        self.part3_layout = QHBoxLayout(self.part3_container)
        self.part3_layout.setContentsMargins(0, 0, 0, 0)
        self.part3_layout.setSpacing(10)
    
        self.part3_fields = []
        for _ in range(3):  # Start with 3 fields
            self.add_part3_field()
    
        layout3 = QVBoxLayout(part3)
        layout3.setContentsMargins(0, 0, 0, 0)
        layout3.addWidget(self.part3_container)
    
        vertical_splitter.addWidget(scroll3)
    
        main_layout.addWidget(vertical_splitter)
    
        # Settings icon at the bottom
        bottom_bar = QVBoxLayout()
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        bottom_bar.addWidget(line)
    
        self.settings_icon = ClickableLabel("⚙")
        self.settings_icon.clicked.connect(self.show_settings_menu)
        bottom_bar.addWidget(self.settings_icon, alignment=Qt.AlignLeft)
    
        main_layout.addLayout(bottom_bar)
    
        self.central.installEventFilter(self)

    def add_part3_field(self):
        field = TextFieldWithHeader()
        field.setMinimumWidth(220)
        self.part3_fields.append(field)
        self.part3_layout.addWidget(field)

    def adjust_part3_layout(self):
        available_width = self.part3_container.width()
        min_field_width = 220  # 200 + margins
        fields_per_row = max(1, available_width // min_field_width)
        
        # Clear and re-add fields with wrapping
        while self.part3_layout.count():
            item = self.part3_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                
        current_row = QHBoxLayout()
        current_row.setSpacing(10)
        for i, field in enumerate(self.part3_fields):
            if i % fields_per_row == 0 and i != 0:
                self.part3_layout.addLayout(current_row)
                current_row = QHBoxLayout()
                current_row.setSpacing(10)
            current_row.addWidget(field)
        self.part3_layout.addLayout(current_row)

    def update_part3_fields(self, count):
        # Adjust number of fields based on spin box value
        while len(self.part3_fields) > count:
            field = self.part3_fields.pop()
            self.part3_layout.removeWidget(field)
            field.deleteLater()
        while len(self.part3_fields) < count:
            self.add_part3_field()
        self.update_text_field_styles_dynamic(self.current_bg)

    def show_settings_menu(self):
        menu_width = int(self.width() * 0.4)
        menu_height = int(self.height() * 0.4)
        self.settings_menu.setFixedSize(menu_width, menu_height)
        x = (self.width() - menu_width) // 2
        y = (self.height() - menu_height) // 2
        self.settings_menu.move(x, y)
        self.settings_menu.show()

    def eventFilter(self, obj, event):
        if obj == self.central and event.type() == QEvent.MouseButtonPress:
            if self.settings_menu.isVisible() and not self.settings_menu.geometry().contains(event.pos()):
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

    def handle_mode_change(self, dark_mode):
        if self.animating:
            return
        # Lock toggle during transition
        self.settings_menu.toggle.lock(True)
        target_bg = self.dark_bg if dark_mode else self.light_bg
        target_text = self.dark_text if dark_mode else self.light_text
        self.animating = True
        self.animate_color_change(self.current_bg, target_bg, self.current_text, target_text, 500)
        self.settings_menu.update_mode(dark_mode)

    def animate_color_change(self, start_bg, end_bg, start_text, end_text, duration):
        steps = 20
        interval = duration // steps
        self.step = 0

        def update():
            factor = self.step / steps
            new_bg = interpolate_color(start_bg, end_bg, factor)
            new_text = interpolate_color(start_text, end_text, factor)
            self.update_stylesheet(new_bg, new_text)
            self.update_text_field_styles_dynamic(new_bg)
            self.step += 1
            if self.step > steps:
                self.timer.stop()
                self.current_bg = end_bg
                self.current_text = end_text
                self.animating = False
                # Unlock toggle after animation
                self.settings_menu.toggle.lock(False)

        self.timer = QTimer(self)
        self.timer.timeout.connect(update)
        self.timer.start(interval)

    def update_text_field_styles_dynamic(self, bg_color):
        # Calculate factor: 0 for light_bg, 1 for dark_bg
        factor = (255 - bg_color[0]) / (255 - 45)
        new_bg = interpolate_color(self.textfield_bg_light, self.textfield_bg_dark, factor)
        new_border = interpolate_color(self.textfield_border_light, self.textfield_border_dark, factor)
        new_text_color = interpolate_color((0, 0, 0), (255, 255, 255), factor)
        bg_hex = '#%02x%02x%02x' % new_bg
        border_hex = '#%02x%02x%02x' % new_border
        text_hex = '#%02x%02x%02x' % new_text_color
        style = f"""
            QTextEdit {{
                background-color: {bg_hex};
                border: 1px solid {border_hex};
                border-radius: 8px;
                color: {text_hex};
            }}
        """
        self.text_input.setStyleSheet(style)
        for field in self.part3_fields:
            field.text_edit.setStyleSheet(style)

    def update_stylesheet(self, bg_color, text_color):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]});
                color: rgb({text_color[0]}, {text_color[1]}, {text_color[2]});
                font-size: 14px;
            }}
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
