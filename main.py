import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
                             QLabel, QProgressBar, QMessageBox, QComboBox, QHBoxLayout, QListWidget, QListWidgetItem,
                             QDialog, QFormLayout, QLineEdit)
from PyQt5.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent, QImage
from PyQt5.QtCore import Qt, QMimeData, QSize
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Settings')
        layout = QFormLayout()

        self.output_dir_edit = QLineEdit(self.settings.get('last_output_dir', ''))
        layout.addRow('Default Output Directory:', self.output_dir_edit)

        self.setLayout(layout)

    def get_settings(self):
        return {
            'last_output_dir': self.output_dir_edit.text()
        }


class HEICConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.settings_file = 'settings.json'
        self.settings = self.load_settings()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('HEIC to JPEG Converter')
        self.setWindowIcon(QIcon('icon.png'))
        self.setAcceptDrops(True)  # 允许拖放操作
        self.setStyleSheet(self.get_stylesheet(self.settings.get('theme', 'light')))

        layout = QVBoxLayout()

        self.label = QLabel('Drag and drop HEIC files here or click the button below', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 14))
        layout.addWidget(self.label)

        self.btn = QPushButton('Select HEIC Files', self)
        self.btn.clicked.connect(self.select_and_convert)
        layout.addWidget(self.btn)

        self.file_list = QListWidget(self)
        layout.addWidget(self.file_list)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.format_selector = QComboBox(self)
        self.format_selector.addItems(['JPEG', 'PNG', 'TIFF'])
        layout.addWidget(self.format_selector)

        self.settings_btn = QPushButton('Settings', self)
        self.settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_btn)

        self.theme_switch = QPushButton('Switch Theme', self)
        self.theme_switch.clicked.connect(self.switch_theme)
        layout.addWidget(self.theme_switch)

        self.setLayout(layout)
        self.setGeometry(400, 200, 600, 400)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if all(url.toLocalFile().lower().endswith('.heic') for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls if url.toLocalFile().lower().endswith('.heic')]
        if files:
            self.file_list.clear()
            self.file_list.addItems(files)

    def select_and_convert(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select HEIC Files", "", "HEIC Files (*.heic);;All Files (*)",
                                                options=options)

        if files:
            self.file_list.clear()
            self.file_list.addItems(files)

        self.convert_files(files)

    def convert_files(self, files):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory",
                                                      self.settings.get('last_output_dir', ''))
        if not output_dir:
            output_dir = os.path.dirname(files[0])  # 如果没有选择输出目录，使用文件所在目录

        self.settings['last_output_dir'] = output_dir
        self.save_settings()

        self.progress.setValue(0)
        total_files = len(files)
        log = []

        for i, heic_file_path in enumerate(files):
            try:
                self.convert_heic_to_jpeg(heic_file_path, output_dir)
                log.append(f"Converted: {heic_file_path}")
            except Exception as e:
                log.append(f"Failed: {heic_file_path} ({e})")

            self.progress.setValue(int((i + 1) / total_files * 100))

        self.show_message("Conversion Completed", "\n".join(log))

    def convert_heic_to_jpeg(self, heic_file_path, output_dir):
        format_selected = self.format_selector.currentText().lower()
        image = Image.open(heic_file_path)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_name = os.path.basename(heic_file_path).replace('.heic', f'.{format_selected}')
        output_file_path = os.path.join(output_dir, file_name)

        image.save(output_file_path, format_selected.upper())

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_():
            self.settings.update(dialog.get_settings())
            self.save_settings()

    def switch_theme(self):
        current_theme = self.settings.get('theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        self.settings['theme'] = new_theme
        self.save_settings()
        self.setStyleSheet(self.get_stylesheet(new_theme))

    def get_stylesheet(self, theme):
        if theme == 'dark':
            return """
                QWidget {
                    background-color: #2e2e2e;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #555555;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    border-radius: 5px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QLabel {
                    color: #f0f0f0;
                    font-size: 18px;
                }
                QProgressBar {
                    border: 1px solid #4CAF50;
                    border-radius: 5px;
                    text-align: center;
                }
                QComboBox {
                    background-color: #555555;
                    color: white;
                    padding: 5px;
                    border-radius: 5px;
                }
                QListWidget {
                    background-color: #333333;
                    color: #f0f0f0;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    border-radius: 5px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QLabel {
                    color: #333333;
                    font-size: 18px;
                }
                QProgressBar {
                    border: 1px solid #4CAF50;
                    border-radius: 5px;
                    text-align: center;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #333333;
                    padding: 5px;
                    border-radius: 5px;
                }
                QListWidget {
                    background-color: #ffffff;
                    color: #333333;
                }
            """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = HEICConverter()
    converter.show()
    sys.exit(app.exec_())
