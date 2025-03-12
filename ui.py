import sys
from PyQt5.QtCore import Qt, QTimer, QEvent, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMainWindow,
                             QSplitter, QScrollArea, QPushButton, QFrame, QSplitterHandle, QSpinBox,
                             QTextEdit, QLineEdit, QSizePolicy)
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient

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
        self.setContentsMargins(5, 5, 5, 5)
        self.setFrameStyle(QFrame.NoFrame)

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 20)
        self._checked = True
        self._circle_pos = 3 if not self._checked else (self.width() - self.height() + 3)
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
        start_value = self._circle_pos
        end_value = (self.width() - self.height() + 3) if self._checked else 3
        self.animation.setStartValue(start_value)
        self.animation.setEndValue(end_value)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        if not self._checked:
            gradient.setColorAt(0, QColor(220, 220, 220))
            gradient.setColorAt(1, QColor(180, 180, 180))
        else:
            gradient.setColorAt(0, QColor(170, 170, 170))
            gradient.setColorAt(1, QColor(130, 130, 130))
        p.setPen(Qt.NoPen)
        p.setBrush(gradient)
        p.drawRoundedRect(self.rect(), self.height()/2, self.height()/2)
        circle_diameter = self.height() - 6
        circle_rect = QRect(self._circle_pos, 3, circle_diameter, circle_diameter)
        circle_color = QColor(255, 255, 255) if not self._checked else QColor(80, 80, 80)
        p.setPen(QPen(QColor(50, 50, 50), 3))
        p.setBrush(circle_color)
        p.drawEllipse(circle_rect)
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
        line_length = 20
        if self.orientation() == Qt.Horizontal:
            center_x = self.width() // 2
            y_start = (self.height() - line_length) // 2
            p.fillRect(center_x - 2 - line_thickness, y_start, line_thickness, line_length, Qt.gray)
            p.fillRect(center_x + 2, y_start, line_thickness, line_length, Qt.gray)
            p.setPen(QPen(Qt.gray, 1))
            p.drawLine(center_x, 0, center_x, self.height())
        else:
            center_y = self.height() // 2
            x_start = (self.width() - line_length) // 2
            p.fillRect(x_start, center_y - 2 - line_thickness, line_length, line_thickness, Qt.gray)
            p.fillRect(x_start, center_y + 2, line_length, line_thickness, Qt.gray)
            p.setPen(QPen(Qt.gray, 1))
            p.drawLine(0, center_y, self.width(), center_y)
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

class Part1Container(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumWidth(200)
        layout.addWidget(self.text_edit)

class Part2Container(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

class Part3Container(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.fields = []
        for _ in range(3):
            self.add_field()

    def add_field(self):
        field = TextFieldWithHeader()
        field.setMinimumWidth(220)
        self.fields.append(field)
        self.layout.addWidget(field)

    def update_field_count(self, count):
        current_count = len(self.fields)
        if count > current_count:
            for _ in range(count - current_count):
                self.add_field()
        elif count < current_count:
            for _ in range(current_count - count):
                field = self.fields.pop()
                self.layout.removeWidget(field)
                field.deleteLater()

class SettingsMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: #f0f0f0; border: 2px solid #888; border-radius: 8px; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(5)
        layout.addStretch()
        self.export_button = QPushButton("Export Layout")
        self.export_button.setStyleSheet("padding: 8px;")
        self.export_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.export_button)
        self.import_button = QPushButton("Import Layout")
        self.import_button.setStyleSheet("padding: 8px;")
        self.import_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.import_button)
        layout.addSpacing(15)
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output Fields:")
        output_layout.addWidget(self.output_label)
        self.output_spin_box = QSpinBox()
        self.output_spin_box.setMinimum(1)
        self.output_spin_box.setValue(3)
        self.output_spin_box.setStyleSheet("""
            QSpinBox {
                padding: 4px;
                font-size: 13px;
                border: 1px solid #aaa;
                border-radius: 4px;
                background: #fff;
                color: #333;
            }
            QSpinBox::up-button {
                background: #ddd;
                border: none;
                border-bottom: 1px solid #bbb;
                width: 16px;
            }
            QSpinBox::down-button {
                background: #ddd;
                border: none;
                border-top: 1px solid #bbb;
                width: 16px;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)
        output_layout.addWidget(self.output_spin_box)
        layout.addLayout(output_layout)
        layout.addSpacing(15)
        self.reset_button = QPushButton("Reset Layout")
        self.reset_button.setStyleSheet("padding: 8px; background-color: #aaa; color: black;")
        self.reset_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.reset_button)
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("padding: 8px; background-color: #aaa; color: black;")
        self.close_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.close_button)
        layout.addStretch()
        self.reset_button.clicked.connect(lambda: self.parentWidget().parentWidget().reset_layout())
        self.close_button.clicked.connect(self.hide)
    
    def update_mode(self, dark_mode):
        if dark_mode:
            self.setStyleSheet("QFrame { background-color: #2d2d2d; border: 2px solid #aaa; border-radius: 8px; color: #ddd; }")
            self.export_button.setStyleSheet("padding: 8px; background-color: #444; color: #ddd;")
            self.import_button.setStyleSheet("padding: 8px; background-color: #444; color: #ddd;")
            self.reset_button.setStyleSheet("padding: 8px; background-color: #555; color: #ddd;")
            self.close_button.setStyleSheet("padding: 8px; background-color: #555; color: #ddd;")
            self.output_spin_box.setStyleSheet("""
                QSpinBox {
                    padding: 4px;
                    font-size: 13px;
                    border: 1px solid #555;
                    border-radius: 4px;
                    background: #444;
                    color: #ddd;
                }
                QSpinBox::up-button {
                    background: #666;
                    border: none;
                    border-bottom: 1px solid #555;
                    width: 16px;
                }
                QSpinBox::down-button {
                    background: #666;
                    border: none;
                    border-top: 1px solid #555;
                    width: 16px;
                }
                QSpinBox::up-arrow, QSpinBox::down-arrow {
                    width: 10px;
                    height: 10px;
                }
            """)
        else:
            self.setStyleSheet("QFrame { background-color: #f0f0f0; border: 2px solid #888; border-radius: 8px; color: #333; }")
            self.export_button.setStyleSheet("padding: 8px; background-color: #ddd; color: #333;")
            self.import_button.setStyleSheet("padding: 8px; background-color: #ddd; color: #333;")
            self.reset_button.setStyleSheet("padding: 8px; background-color: #aaa; color: black;")
            self.close_button.setStyleSheet("padding: 8px; background-color: #aaa; color: black;")
            self.output_spin_box.setStyleSheet("""
                QSpinBox {
                    padding: 4px;
                    font-size: 13px;
                    border: 1px solid #aaa;
                    border-radius: 4px;
                    background: #fff;
                    color: #333;
                }
                QSpinBox::up-button {
                    background: #ddd;
                    border: none;
                    border-bottom: 1px solid #bbb;
                    width: 16px;
                }
                QSpinBox::down-button {
                    background: #ddd;
                    border: none;
                    border-top: 1px solid #bbb;
                    width: 16px;
                }
                QSpinBox::up-arrow, QSpinBox::down-arrow {
                    width: 10px;
                    height: 10px;
                }
            """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RapidPrompt")
        self.resize(1600, 900)
    
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
        self.initial_reset_done = False
    
        self.init_ui()
        self.update_stylesheet(self.current_bg, self.current_text)
        self.update_text_field_styles_dynamic(self.current_bg)
    
        self.settings_menu = SettingsMenu(self.central)
        self.settings_menu.hide()
        self.settings_menu.update_mode(self.current_bg == self.dark_bg)
        self.settings_menu.output_spin_box.valueChanged.connect(self.update_part3_fields)
    
        self.installEventFilter(self)
    
    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        main_layout = QVBoxLayout(self.central)
        main_layout.setContentsMargins(10, 10, 10, 10)
    
        self.vertical_splitter = CustomSplitter(Qt.Vertical)
        self.vertical_splitter.setHandleWidth(15)
    
        self.top_splitter = CustomSplitter(Qt.Horizontal)
        self.top_splitter.setHandleWidth(15)
    
        self.part1_container = Part1Container()
        scroll1 = QScrollArea()
        scroll1.setFrameStyle(QFrame.NoFrame)
        scroll1.setWidget(self.part1_container)
        scroll1.setWidgetResizable(True)
        self.top_splitter.addWidget(scroll1)
    
        self.part2_container = Part2Container()
        scroll2 = QScrollArea()
        scroll2.setFrameStyle(QFrame.NoFrame)
        scroll2.setWidget(self.part2_container)
        scroll2.setWidgetResizable(True)
        self.top_splitter.addWidget(scroll2)
    
        self.part1_container.text_edit.textChanged.connect(
            lambda: self.part2_container.label.setText(self.part1_container.text_edit.toPlainText()))
    
        self.vertical_splitter.addWidget(self.top_splitter)
    
        self.part3_container = Part3Container()
        scroll3 = QScrollArea()
        scroll3.setFrameStyle(QFrame.NoFrame)
        scroll3.setWidget(self.part3_container)
        scroll3.setWidgetResizable(True)
        self.vertical_splitter.addWidget(scroll3)
    
        main_layout.addWidget(self.vertical_splitter)
    
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(separator, alignment=Qt.AlignHCenter)
    
        # Bottom area wrapper with a darker background and reduced height.
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(60)
        bottom_frame.setStyleSheet("background-color: #2a2a2a;")
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        bottom_layout.setSpacing(5)
    
        self.settings_icon = ClickableLabel("⚙")
        self.settings_icon.setFixedSize(40, 40)
        self.settings_icon.clicked.connect(self.show_settings_menu)
        bottom_layout.addWidget(self.settings_icon)
    
        mode_container = QHBoxLayout()
        self.mode_label = QLabel("Dark Mode" if self.current_bg == self.dark_bg else "Light Mode")
        mode_container.addWidget(self.mode_label)
        self.mode_toggle = ToggleSwitch()
        self.mode_toggle.toggled.connect(self.handle_mode_change)
        mode_container.addWidget(self.mode_toggle)
        bottom_layout.addLayout(mode_container)
    
        main_layout.addWidget(bottom_frame)
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self.initial_reset_done:
            QTimer.singleShot(0, self.reset_layout)
            self.initial_reset_done = True
    
    def reset_layout(self):
        total_v = sum(self.vertical_splitter.sizes())
        self.vertical_splitter.setSizes([total_v // 2, total_v - total_v // 2])
        total_h = sum(self.top_splitter.sizes())
        if total_h == 0:
            total_h = 1000
        self.top_splitter.setSizes([total_h // 3, total_h - total_h // 3])
    
    def update_part3_fields(self, count):
        self.part3_container.update_field_count(count)
        self.update_text_field_styles_dynamic(self.current_bg)
    
    def show_settings_menu(self):
        menu_width = int(self.height() * 0.4)
        menu_height = int(self.width() * 0.3)
        self.settings_menu.setFixedSize(menu_width, menu_height)
        x = (self.width() - menu_width) // 2
        y = (self.height() - menu_height) // 2
        self.settings_menu.move(x, y)
        self.settings_menu.show()
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and self.settings_menu.isVisible():
            global_rect = QRect(self.settings_menu.mapToGlobal(self.settings_menu.rect().topLeft()),
                                self.settings_menu.size())
            if not global_rect.contains(event.globalPos()):
                self.settings_menu.hide()
        return super().eventFilter(obj, event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.settings_menu.isVisible():
            menu_width = int(self.height() * 0.4)
            menu_height = int(self.width() * 0.3)
            self.settings_menu.setFixedSize(menu_width, menu_height)
            x = (self.width() - menu_width) // 2
            y = (self.height() - menu_height) // 2
            self.settings_menu.move(x, y)
    
    def handle_mode_change(self, dark_mode):
        if self.animating:
            return
        self.mode_toggle.lock(True)
        target_bg = self.dark_bg if dark_mode else self.light_bg
        target_text = self.dark_text if dark_mode else self.light_text
        self.mode_label.setText("Dark Mode" if dark_mode else "Light Mode")
        self.animating = True
        self.animate_color_change(self.current_bg, target_bg, self.current_text, target_text, 500, dark_mode)
    
    def animate_color_change(self, start_bg, end_bg, start_text, end_text, duration, dark_mode):
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
                self.mode_toggle.lock(False)
                self.settings_menu.update_mode(dark_mode)
        self.timer = QTimer(self)
        self.timer.timeout.connect(update)
        self.timer.start(interval)
    
    def update_text_field_styles_dynamic(self, bg_color):
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
                font-size: 13px;
            }}
        """
        self.part1_container.text_edit.setStyleSheet(style)
        for field in self.part3_container.fields:
            field.text_edit.setStyleSheet(style)
    
    def update_stylesheet(self, bg_color, text_color):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]});
                color: rgb({text_color[0]}, {text_color[1]}, {text_color[2]});
                font-size: 13px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]});
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgb({min(bg_color[0]+20,255)}, {min(bg_color[1]+20,255)}, {min(bg_color[2]+20,255)});
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]});
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: rgb({min(bg_color[0]+20,255)}, {min(bg_color[1]+20,255)}, {min(bg_color[2]+20,255)});
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
            }}
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
