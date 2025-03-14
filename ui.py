import sys
from PyQt5.QtCore import Qt, QTimer, QEvent, QRect, QRectF, QPropertyAnimation, pyqtSignal, QSize, QPoint, QUrl, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMainWindow,
                             QSplitter, QScrollArea, QPushButton, QFrame, QSplitterHandle, QSpinBox,
                             QTextEdit, QLineEdit, QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QPixmap, QPainterPath, QRegion, QIcon, QDesktopServices, QTextCursor, QTextCharFormat

def log_write(msg):
    with open("session.log", "a") as f:
        f.write(msg + "\n")

class TitleBarButton(QPushButton):
    def __init__(self, base_color, hover_icon, parent=None):
        super().__init__(parent)
        self.base_color = QColor(base_color)
        self.hover_icon = hover_icon
        self.setFixedSize(12, 12)
        self.setCursor(Qt.ArrowCursor)
        self.setStyleSheet("border: none;")
        self._hover = False

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        p.setPen(Qt.NoPen)
        p.setBrush(self.base_color)
        p.drawEllipse(rect)
        if self._hover:
            p.setPen(QPen(Qt.white, 1))
            font = QFont("Arial", 6, QFont.Bold)
            p.setFont(font)
            fm = QFontMetrics(font)
            txt = self.hover_icon
            txt_w = fm.width(txt)
            txt_h = fm.height()
            x = (rect.width() - txt_w) / 2
            y = (rect.height() + txt_h/2) / 2
            p.drawText(QPoint(int(x), int(y)), txt)
        p.end()

class CustomTitleBar(QWidget):
    def __init__(self, parent=None, window_title="RapidPrompt", file_title="~Untitled"):
        super().__init__(parent)
        self.setFixedHeight(25)
        self.window_title = window_title
        self.file_title = file_title if file_title else "~Untitled"
        self._dragPos = None  # Initialize _dragPos to ensure safe usage

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_container = QWidget(self)
        left_layout = QHBoxLayout(self.left_container)
        left_layout.setContentsMargins(9, 0, 5, 0)
        self.iconLabel = QLabel(self)
        pix = QPixmap("icon.png")
        if pix.isNull():
            self.iconLabel.setText("ICON")
        else:
            scaled_pix = pix.scaledToHeight(self.height() - 4, Qt.SmoothTransformation)
            self.iconLabel.setPixmap(scaled_pix)
        left_layout.addWidget(self.iconLabel)
        self.windowTitleLabel = QLabel(self.window_title, self)
        self.windowTitleLabel.setStyleSheet("font: bold 10px; color: #E0E0E0; padding: 2px;")
        left_layout.addWidget(self.windowTitleLabel)

        self.right_container = QWidget(self)
        right_layout = QHBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 9, 0)
        right_layout.setSpacing(4)
        self.btn_min = TitleBarButton("#34C759", "–", self)
        self.btn_max = TitleBarButton("#FF9500", "▢", self)
        self.btn_close = TitleBarButton("#FF3B30", "✕", self)
        self.btn_min.clicked.connect(self.window().showMinimized)
        self.btn_max.clicked.connect(self.toggle_max_restore)
        self.btn_close.clicked.connect(self.window().close)
        right_layout.addWidget(self.btn_min)
        right_layout.addWidget(self.btn_max)
        right_layout.addWidget(self.btn_close)

        self.fileTitleLabel = QLabel(self.file_title, self)
        self.fileTitleLabel.setStyleSheet("font: 10px; color: #E0E0E0; padding: 2px;")
        self.fileTitleLabel.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self.left_container)
        main_layout.addStretch()
        main_layout.addWidget(self.fileTitleLabel)
        main_layout.addStretch()
        main_layout.addWidget(self.right_container)
    
    def toggle_max_restore(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragPos = event.globalPos() - self.window().frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._dragPos is not None:
            self.window().move(event.globalPos() - self._dragPos)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.toggle_max_restore()
        super().mouseDoubleClickEvent(event)

class LogLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        import os
        if os.path.exists("session.log"):
            QDesktopServices.openUrl(QUrl.fromLocalFile("session.log"))
        else:
            self.setText("Log File not found.")
        super().mousePressEvent(event)

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

class MarkableTextEdit(QTextEdit):
    def __init__(self, parent_container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_container = parent_container
        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.setFrameStyle(QTextEdit.NoFrame)
        self.setAlignment(Qt.AlignHCenter)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        if self.parent_container.current_mode == "mark":
            for spot in self.parent_container.marked_spots:
                existing_start = spot["start"]
                existing_end = spot["start"] + spot["length"]
                if start < existing_end and end > existing_start:
                    return
            marking_color = QColor(135, 206, 250, 51)
            new_fmt = QTextCharFormat()
            new_fmt.setBackground(marking_color)
            cursor.mergeCharFormat(new_fmt)
            length = end - start
            marked_text = cursor.selectedText()
            self.parent_container.marked_spots.append({
                "start": start,
                "length": length,
                "text": marked_text
            })
            self.parent_container.update_marked_counter()
            cursor.clearSelection()
            self.setTextCursor(cursor)
        elif self.parent_container.current_mode == "erase":
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()

            spots_to_remove = []
            for spot in self.parent_container.marked_spots:
                spot_start = spot["start"]
                spot_end = spot_start + spot["length"]
                if spot_start < sel_end and spot_end > sel_start:
                    spots_to_remove.append(spot)
                    
            if spots_to_remove:
                self.parent_container.marked_spots = [
                    spot for spot in self.parent_container.marked_spots if spot not in spots_to_remove
                ]
                full_cursor = QTextCursor(self.document())
                full_cursor.select(QTextCursor.Document)
                clear_fmt = QTextCharFormat()
                clear_fmt.setBackground(Qt.transparent)
                full_cursor.setCharFormat(clear_fmt)
                for spot in self.parent_container.marked_spots:
                    fmt = QTextCharFormat()
                    fmt.setBackground(QColor(135, 206, 250, 51))
                    temp_cursor = self.textCursor()
                    temp_cursor.setPosition(spot["start"])
                    temp_cursor.setPosition(spot["start"] + spot["length"], QTextCursor.KeepAnchor)
                    temp_cursor.mergeCharFormat(fmt)
                self.parent_container.update_marked_counter()
            
            cursor.clearSelection()
            self.setTextCursor(cursor)

class Part1Container(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        
        """self.input_label = QLabel("Input")
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setFixedHeight(25)
        self.input_label.setStyleSheet("QLineEdit { color: #555; font-size: 10px; border: none; font-weight: bold; }")
        layout.addWidget(self.input_label)"""
        
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

class Part2Container(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = None
        self.marked_spots = []
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(5)

        self.text_edit = MarkableTextEdit(self)
        self.text_edit.setMinimumHeight(100)
        self.text_edit.setAlignment(Qt.AlignHCenter)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.outer_layout.addWidget(self.text_edit, 1, alignment=Qt.AlignHCenter)

        self.marked_counter_label = QLabel("Marked: 0")
        self.marked_counter_label.setAlignment(Qt.AlignCenter)
        self.outer_layout.addWidget(self.marked_counter_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_mark = QPushButton("Mark")
        self.btn_erase = QPushButton("Erase")
        self.btn_clear = QPushButton("Clear")
        self.btn_eval = QPushButton("Eval")

        btn_size = QSize(80, 30)
        for btn in [self.btn_mark, self.btn_erase, self.btn_clear, self.btn_eval]:
            btn.setFixedSize(btn_size)
            btn.setStyleSheet("border-radius: 5px;")

        self.btn_mark.setCheckable(True)
        self.btn_erase.setCheckable(True)

        mark_erase_normal = """
            QPushButton {
                background-color: #808080;
                border: 1px solid #808080;
                border-radius: 5px;
                color: white;
            }
        """
        mark_erase_pressed = """
            QPushButton:checked {
                background-color: #505050;
                border: 3px solid #505050;
                border-radius: 5px;
                color: white;
            }
        """
        self.btn_mark.setStyleSheet(mark_erase_normal + mark_erase_pressed)
        self.btn_erase.setStyleSheet(mark_erase_normal + mark_erase_pressed)

        reset_style = """
            QPushButton {
                background-color: #505050;
                border: 3px solid #8B0000;
                border-radius: 5px;
                color: white;
            }
        """
        eval_style = """
            QPushButton {
                background-color: #505050;
                border: 3px solid #006400;
                border-radius: 5px;
                color: white;
            }
        """
        self.btn_clear.setStyleSheet(reset_style)
        self.btn_eval.setStyleSheet(eval_style)

        self.btn_mark.setChecked(False)
        self.btn_erase.setChecked(False)

        self.btn_mark.toggled.connect(self.on_mark_toggled)
        self.btn_erase.toggled.connect(self.on_erase_toggled)
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        self.btn_eval.clicked.connect(self.on_eval_clicked)

        btn_layout.addWidget(self.btn_mark)
        btn_layout.addWidget(self.btn_erase)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_eval)

        self.outer_layout.addLayout(btn_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.text_edit.setFixedWidth(int(self.width() / 2))

    def update_marked_counter(self):
        self.marked_counter_label.setText("Marked: " + str(len(self.marked_spots)))

    def on_mark_toggled(self, checked):
        if checked:
            self.btn_erase.setChecked(False)
            self.current_mode = "mark"
        else:
            if not self.btn_erase.isChecked():
                self.current_mode = None

    def on_erase_toggled(self, checked):
        if checked:
            self.btn_mark.setChecked(False)
            self.current_mode = "erase"
        else:
            if not self.btn_mark.isChecked():
                self.current_mode = None

    def on_clear_clicked(self):
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        default_format = QTextCharFormat()
        default_format.setBackground(Qt.transparent)
        cursor.setCharFormat(default_format)
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)
        self.marked_spots = []
        self.update_marked_counter()
        log_write("Clear: All highlights removed")

    def on_eval_clicked(self):
        import os, json
        self.marked_spots.sort(key=lambda spot: spot["start"])
    
        data = {"Marks": self.marked_spots}
    
        save_folder = "saves"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        json_path = os.path.join(save_folder, "session.json")
    
        with open(json_path, "w") as f:
           json.dump(data, f, indent=4)
    
        log_write("Eval: marked_spots sorted and saved to " + json_path)

    def update_text(self, new_text):
        self.text_edit.setPlainText(new_text)
        self.marked_spots = []
        self.update_marked_counter()


class Part3Container(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fields = []
        self.spacing = 10

        for _ in range(4):
            self.add_field()

    def add_field(self):
        field = TextFieldWithHeader()
        field.setMinimumWidth(200)
        field.setFixedHeight(250)
        self.fields.append(field)
        field.setParent(self)
        field.show()

    def update_field_count(self, count):
        current_count = len(self.fields)
        if count > current_count:
            for _ in range(count - current_count):
                self.add_field()
        elif count < current_count:
            for _ in range(current_count - count):
                field = self.fields.pop()
                field.setParent(None)
                field.deleteLater()
        self.relayout_fields()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_fields()

    def relayout_fields(self):
        total = len(self.fields)
        if total == 0:
            return

        spacing = self.spacing
        container_width = self.width()

        full_columns = 6
        rows = (total + full_columns - 1) // full_columns

        total_height = rows * 250 + (rows - 1) * spacing
        self.setMinimumHeight(int(total_height))

        for row in range(rows):
            start_index = row * full_columns
            if row == rows - 1:
                count_in_row = total - start_index
            else:
                count_in_row = full_columns

            if count_in_row > 0:
                cell_width = (container_width - (count_in_row - 1) * spacing) / count_in_row
            else:
                cell_width = container_width

            y = row * (250 + spacing)
            for i in range(count_in_row):
                index = start_index + i
                x = i * (cell_width + spacing)
                self.fields[index].setGeometry(int(x), int(y), int(cell_width), 250)

class ModalOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        self.setGeometry(parent.rect())
    
    def resizeEvent(self, event):
        self.setGeometry(self.parent().rect())
        super().resizeEvent(event)
    
    def mousePressEvent(self, event):
        event.accept()
        if self.parent() and hasattr(self.parent(), 'settings_menu'):
            self.parent().settings_menu.hide_with_fade()
        self.hide()

class SettingsMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: #2d2d2d; border: 2px solid #aaa; border-radius: 8px; color: #ddd; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        layout.addStretch() 
        
        self.standard_layout_button = QPushButton("Set Standard Layout")
        self.standard_layout_button.setStyleSheet("padding: 8px; border-radius: 0px; background-color: #444; color: #ddd;")
        self.standard_layout_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.standard_layout_button)

        self.export_button = QPushButton("Export Layout")
        self.export_button.setStyleSheet("padding: 8px; border-radius: 0px; background-color: #444; color: #ddd;")
        self.export_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.export_button)
        
        self.import_button = QPushButton("Import Layout")
        self.import_button.setStyleSheet("padding: 8px; border-radius: 0px; background-color: #444; color: #ddd;")
        self.import_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.import_button)
        
        layout.addSpacing(15)
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Number Outputs:")
        output_layout.addWidget(self.output_label)
        self.output_spin_box = QSpinBox()
        self.output_spin_box.setMinimum(1)
        self.output_spin_box.setValue(4)
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
        output_layout.addWidget(self.output_spin_box)
        layout.addLayout(output_layout)
        
        layout.addSpacing(15)
        self.reset_button = QPushButton("Reset Layout")
        self.reset_button.setStyleSheet("padding: 8px; border-radius: 0px; background-color: #555; color: #ddd;")
        self.reset_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.reset_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("padding: 8px; border-radius: 0px; background-color: #555; color: #ddd;")
        self.close_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.close_button)
        
        layout.addStretch()

        self.reset_button.clicked.connect(lambda: self.window().reset_layout())
        self.close_button.clicked.connect(self.hide_with_fade)
        
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0)

    def fade_in(self):
        self.show()
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(200)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def hide_with_fade(self):
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.effect.opacity())
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.hide)
        self.anim.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RapidPrompt")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1600, 900)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.dark_bg = (45, 45, 45)
        self.dark_text = (220, 220, 220)
        self.textfield_bg_dark = (58, 58, 58)
        self.textfield_border_dark = (85, 85, 85)
        self.dark_bottom = (51, 51, 51)

        self.current_bg = self.dark_bg
        self.current_text = self.dark_text

        self.animating = False
        self.timer = None
        self.initial_reset_done = False
        self.installEventFilter(self)
        self.init_ui()
        self.initialize_session_files()
        self.update_stylesheet(self.current_bg, self.current_text)

        self.style_timer = QTimer(self)
        self.style_timer.setSingleShot(True)
        self.style_timer.timeout.connect(self.update_text_field_styles_dynamic)
        self.style_timer.start(0)

        self.settings_menu = SettingsMenu(self.central_widget)
        self.settings_menu.hide()
        self.settings_menu.output_spin_box.valueChanged.connect(self.update_part3_fields)

    def init_ui(self):
        self.central_widget = QWidget()
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, "RapidPrompt")
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

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
            lambda: self.part2_container.text_edit.setText(self.part1_container.text_edit.toPlainText())
        )
        self.vertical_splitter.addWidget(self.top_splitter)

        self.part3_container = Part3Container()
        scroll3 = QScrollArea()
        scroll3.setFrameStyle(QFrame.NoFrame)
        scroll3.setWidget(self.part3_container)
        scroll3.setWidgetResizable(True)
        scroll3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.vertical_splitter.addWidget(scroll3)

        content_layout.addWidget(self.vertical_splitter)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(separator, alignment=Qt.AlignHCenter)

        self.bottom_bar_widget = QWidget(self)
        self.bottom_bar_widget.setMaximumHeight(50)
        self.bottom_bar_widget.setStyleSheet("background-color: rgb(%d, %d, %d);" % self.dark_bottom)
        bottom_layout = QHBoxLayout(self.bottom_bar_widget)
        bottom_layout.setSpacing(5)
        bottom_layout.setContentsMargins(5, 0, 5, 0)

        self.settings_icon = ClickableLabel("⚙")
        self.settings_icon.setFixedSize(20, 20)
        self.settings_icon.setStyleSheet("color: #ffffff;")
        self.settings_icon.clicked.connect(self.show_settings_menu)
        bottom_layout.addWidget(self.settings_icon)

        bottom_layout.addStretch()

        self.log_button = QPushButton("Open Log")
        self.log_button.setFixedSize(80, 18)
        self.log_button.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; color: #989898; border: none;")
        self.log_button.clicked.connect(self.open_log)
        bottom_layout.addWidget(self.log_button)

        self.run_button = QPushButton("Run")
        self.run_button.setFixedSize(100, 20)
        self.run_button.setStyleSheet("background-color: #006400; border-radius: 5px; color: #989898; border: 3px solid #004600;")
        bottom_layout.addWidget(self.run_button)

        main_layout.addWidget(content_widget)
        main_layout.addWidget(self.bottom_bar_widget)

        self.setCentralWidget(self.central_widget)
    
    def initialize_session_files(self):
        import os, json
        log_filename = "session.log"
        with open(log_filename, "w") as f:
            f.write("")

        save_folder = "saves"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        json_path = os.path.join(save_folder, "session.json")
        with open(json_path, "w") as f:
            json.dump({"Marks": []}, f, indent=4)

    def showEvent(self, event):
        super().showEvent(event)
        if not self.initial_reset_done:
            self.layout_reset_timer = QTimer(self)
            self.layout_reset_timer.setSingleShot(True)
            self.layout_reset_timer.timeout.connect(self.reset_layout)
            self.layout_reset_timer.start(0)
            self.initial_reset_done = True

    def closeEvent(self, event):
        if hasattr(self, 'style_timer') and self.style_timer.isActive():
            self.style_timer.stop()
        if hasattr(self, 'layout_reset_timer') and self.layout_reset_timer.isActive():
            self.layout_reset_timer.stop()
        event.accept()

    def reset_layout(self):
        if not hasattr(self, 'vertical_splitter'):
            return
        total_v = sum(self.vertical_splitter.sizes())
        self.vertical_splitter.setSizes([total_v // 2, total_v - total_v // 2])
    
        total_h = sum(self.top_splitter.sizes())
        if total_h == 0:
            total_h = 1000
        self.top_splitter.setSizes([total_h // 3, total_h - total_h // 3])

    def update_part3_fields(self, count):
        self.part3_container.update_field_count(count)
        self.update_text_field_styles_dynamic()

    def open_log(self):
        import os
        if os.path.exists("session.log"):
            QDesktopServices.openUrl(QUrl.fromLocalFile("session.log"))
        else:
            print("Log file not found.")

    def show_settings_menu(self):
        if not hasattr(self, 'overlay') or self.overlay is None:
            self.overlay = ModalOverlay(self.central_widget)
        self.overlay.show()
        self.overlay.raise_()
        
        self.settings_menu.setParent(self.overlay)
        self.settings_menu.adjustSize()
        self.settings_menu.setFixedSize(self.settings_menu.sizeHint())

        icon_pos = self.settings_icon.mapTo(self.central_widget, QPoint(0, 0))
        gap = 5
        menu_width = self.settings_menu.width()
        menu_height = self.settings_menu.height()

        new_x = icon_pos.x()
        new_y = icon_pos.y() - gap - menu_height
        self.settings_menu.move(new_x, new_y)

        self.settings_menu.fade_in()
        self.settings_menu.raise_()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and self.settings_menu.isVisible():
            geo = QRect(self.settings_menu.mapToGlobal(self.settings_menu.rect().topLeft()),
                        self.settings_menu.size())
            if not geo.contains(event.globalPos()):
                self.settings_menu.hide_with_fade()
                return True
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
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 8, 8)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        rect.adjust(0, 0, -1, -1)
        p.setPen(QPen(QColor("#444"), 1))
        p.setBrush(QColor(self.current_bg[0], self.current_bg[1], self.current_bg[2]))
        p.drawRoundedRect(rect, 8, 8)
        p.end()

    def update_text_field_styles_dynamic(self):
        new_bg = self.textfield_bg_dark
        new_border = self.textfield_border_dark
        new_text_color = (255, 255, 255)
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
        self.central_widget.setStyleSheet(f"""
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
    import sys
    app = QApplication(sys.argv)
    global main_win
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
