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

class CustomOutlineFrame(QFrame):
    def __init__(self, position="middle", parent=None):
        super().__init__(parent)
        self.position = position
        self.border_color = QColor("#e0e0e0")
        self.pen_width = 1
        self.radius = 8
        self.inset = 5  # Reduced inset for balanced spacing
        self.setContentsMargins(5, 5, 5, 5)  # Balanced margins

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(self.border_color, self.pen_width))
        
        # Draw single outer rounded rectangle
        main_rect = self.rect().adjusted(0, 0, -1, -1)
        p.drawRoundedRect(main_rect, self.radius, self.radius)
        
        # Create splitter handle gap with balanced spacing
        gap = 14
        gap_offset = gap // 2
        bg_color = self.palette().window().color()
        p.setPen(QPen(bg_color, self.pen_width))
        
        if self.position in ["middle", "right"]:
            x = main_rect.left() + self.inset
            center_y = main_rect.center().y()
            p.drawLine(x, center_y - gap_offset, x, center_y + gap_offset)
            
        if self.position in ["left", "middle"]:
            x = main_rect.right() - self.inset
            center_y = main_rect.center().y()
            p.drawLine(x, center_y - gap_offset, x, center_y + gap_offset)
        p.end()

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

    def mousePressEvent(self, event):
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
        line_thickness = 2
        center_x = self.width() // 2
        line_length = 20
        y_start = (self.height() - line_length) // 2
        
        p.fillRect(center_x-5-line_thickness, y_start, line_thickness, line_length, Qt.gray)
        p.fillRect(center_x+5, y_start, line_thickness, line_length, Qt.gray)
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
        
        # Text field styles
        self.textfield_bg_light = "#ffffff"
        self.textfield_border_light = "#cccccc"
        self.textfield_bg_dark = "#3a3a3a"
        self.textfield_border_dark = "#555555"
        
        self.animating = False
        self.timer = None
        
        self.init_ui()
        self.update_stylesheet(self.current_bg, self.current_text)
        self.update_text_field_styles()

    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Main splitter
        self.splitter = CustomSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(15)  # Wider handles
        
        # Part 1 (Left)
        scroll1 = QScrollArea()
        part1 = CustomOutlineFrame("left")
        scroll1.setWidget(part1)
        scroll1.setWidgetResizable(True)
        self.text_input = QTextEdit()  # Empty initial text
        self.text_input.setMinimumWidth(200)
        part1.setLayout(QVBoxLayout())
        part1.layout().addWidget(self.text_input, alignment=Qt.AlignCenter)
        self.splitter.addWidget(scroll1)
        
        # Part 2 (Middle)
        scroll2 = QScrollArea()
        part2 = CustomOutlineFrame("middle")
        scroll2.setWidget(part2)
        scroll2.setWidgetResizable(True)
        self.text_display = QLabel()
        self.text_display.setAlignment(Qt.AlignCenter)
        part2.setLayout(QVBoxLayout())
        part2.layout().addWidget(self.text_display, alignment=Qt.AlignCenter)
        self.splitter.addWidget(scroll2)
        
        # Part 3 (Right) with dynamic layout
        scroll3 = QScrollArea()
        part3 = CustomOutlineFrame("right")
        scroll3.setWidget(part3)
        scroll3.setWidgetResizable(True)
        
        self.part3_container = QWidget()
        self.part3_layout = QHBoxLayout(self.part3_container)
        self.part3_layout.setContentsMargins(0, 0, 0, 0)
        self.part3_layout.setSpacing(10)
        
        self.part3_fields = []
        for _ in range(3):  # Start with 3 fields
            self.add_part3_field()
            
        part3.setLayout(QVBoxLayout())
        part3.layout().addWidget(self.part3_container)
        self.splitter.addWidget(scroll3)
        
        layout.addWidget(self.splitter, 1)
        self.text_input.textChanged.connect(lambda: self.text_display.setText(self.text_input.toPlainText()))
        self.splitter.splitterMoved.connect(self.adjust_part3_layout)
        
        # Bottom bar
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)
        
        self.settings_icon = ClickableLabel("⚙")
        self.settings_icon.clicked.connect(self.show_settings_menu)
        layout.addWidget(self.settings_icon, alignment=Qt.AlignLeft)
        
        # Settings menu
        self.settings_menu = SettingsMenu(self.central)
        self.settings_menu.hide()
        self.settings_menu.reset_button.clicked.connect(self.reset_splitter)
        self.settings_menu.toggle.toggled.connect(self.handle_mode_change)
        self.settings_menu.spin_box.valueChanged.connect(self.update_part3_fields)
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
        
        # Clear existing layout
        while self.part3_layout.count():
            item = self.part3_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                
        # Re-add fields with wrapping
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
        while len(self.part3_fields) > count:
            field = self.part3_fields.pop()
            field.deleteLater()
        while len(self.part3_fields) < count:
            self.add_part3_field()
        self.adjust_part3_layout()
        self.update_text_field_styles()

    def show_settings_menu(self):
        menu_width = int(self.width() * 0.4)
        menu_height = int(self.height() * 0.4)
        self.settings_menu.setFixedSize(menu_width, menu_height)
        x = (self.width() - menu_width) // 2
        y = (self.height() - menu_height) // 2
        self.settings_menu.move(x, y)
        self.settings_menu.show()

    def update_part3_fields(self, count):
        while len(self.part3_fields) > count:
            field = self.part3_fields.pop()
            self.part3_layout.removeWidget(field)
            field.deleteLater()
        while len(self.part3_fields) < count:
            field = TextFieldWithHeader()
            self.part3_fields.append(field)
            self.part3_layout.addWidget(field)
        self.update_text_field_styles()

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

    def reset_splitter(self):
        total = sum(self.splitter.sizes())
        sizes = [total // self.splitter.count()] * self.splitter.count()
        self.splitter.setSizes(sizes)

    def handle_mode_change(self, dark_mode):
        if self.animating:
            return
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
            self.step += 1
            if self.step > steps:
                self.timer.stop()
                self.current_bg = end_bg
                self.current_text = end_text
                self.animating = False
                self.update_text_field_styles()

        self.timer = QTimer(self)
        self.timer.timeout.connect(update)
        self.timer.start(interval)

    def update_text_field_styles(self):
        bg = self.textfield_bg_dark if self.current_bg == self.dark_bg else self.textfield_bg_light
        border = self.textfield_border_dark if self.current_bg == self.dark_bg else self.textfield_border_light
        text_color = "white" if self.current_bg == self.dark_bg else "black"
        style = f"""
            QTextEdit {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
                color: {text_color};
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