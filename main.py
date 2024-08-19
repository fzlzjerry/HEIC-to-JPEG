import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QProgressBar, \
    QMessageBox
from PyQt5.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QMimeData
from PIL import Image
import pillow_heif
import os

pillow_heif.register_heif_opener()


class HEICConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('HEIC to JPEG Converter')
        self.setWindowIcon(QIcon('icon.png'))
        self.setAcceptDrops(True)  # 允许拖放操作
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
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
        """)

        layout = QVBoxLayout()

        self.label = QLabel('Drag and drop HEIC files here or click the button below', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 14))
        layout.addWidget(self.label)

        self.btn = QPushButton('Select HEIC Files', self)
        self.btn.clicked.connect(self.select_and_convert)
        layout.addWidget(self.btn)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.setGeometry(400, 200, 500, 250)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls if url.toLocalFile().lower().endswith('.heic')]
        if files:
            self.convert_files(files)

    def select_and_convert(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select HEIC Files", "", "HEIC Files (*.heic);;All Files (*)",
                                                options=options)

        if files:
            self.convert_files(files)

    def convert_files(self, files):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            output_dir = os.path.dirname(files[0])  # 如果没有选择输出目录，使用文件所在目录

        self.progress.setValue(0)
        total_files = len(files)

        for i, heic_file_path in enumerate(files):
            self.convert_heic_to_jpeg(heic_file_path, output_dir)
            self.progress.setValue(int((i + 1) / total_files * 100))

        self.show_message("Conversion Completed", f"All files have been converted and saved to {output_dir}.")

    def convert_heic_to_jpeg(self, heic_file_path, output_dir):
        try:
            image = Image.open(heic_file_path)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            file_name = os.path.basename(heic_file_path).replace('.heic', '.jpg')
            output_file_path = os.path.join(output_dir, file_name)

            image.save(output_file_path, "JPEG")
        except Exception as e:
            print(f"Failed to convert {heic_file_path}: {e}")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = HEICConverter()
    converter.show()
    sys.exit(app.exec_())