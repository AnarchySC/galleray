#!/usr/bin/env python3
"""Gall-array - A simple minimalist image gallery for Linux."""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QKeyEvent

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
}
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: none;
    padding: 12px 24px;
    font-size: 14px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #3d3d3d;
}
QPushButton:pressed {
    background-color: #4d4d4d;
}
QPushButton:disabled {
    background-color: #252525;
    color: #666666;
}
QLabel {
    color: #a0a0a0;
}
"""


class GalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = []
        self.current_index = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gall-array")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(DARK_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Top bar
        top_bar = QHBoxLayout()
        self.folder_btn = QPushButton("Open Folder")
        self.folder_btn.clicked.connect(self.open_folder)
        top_bar.addWidget(self.folder_btn)
        top_bar.addStretch()

        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("font-size: 14px;")
        top_bar.addWidget(self.counter_label)
        layout.addLayout(top_bar)

        # Image display
        self.image_label = QLabel("Select a folder to view images")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(self.image_label, 1)

        # Filename
        self.filename_label = QLabel("")
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(self.filename_label)

        # Navigation
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_image)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_image)
        self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)

        nav_layout.addStretch()
        layout.addLayout(nav_layout)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.load_images(folder)

    def load_images(self, folder):
        self.images = sorted([
            os.path.join(folder, f) for f in os.listdir(folder)
            if Path(f).suffix.lower() in SUPPORTED_FORMATS
        ])
        self.current_index = 0

        if self.images:
            self.show_image()
            self.update_nav_state()
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("No images found in folder")
            self.counter_label.setText("")
            self.filename_label.setText("")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)

    def show_image(self):
        if not self.images:
            return

        path = self.images[self.current_index]
        pixmap = QPixmap(path)

        if not pixmap.isNull():
            # Scale to fit while maintaining aspect ratio
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

        self.counter_label.setText(f"{self.current_index + 1} / {len(self.images)}")
        self.filename_label.setText(os.path.basename(path))

    def update_nav_state(self):
        has_images = len(self.images) > 0
        self.prev_btn.setEnabled(has_images and self.current_index > 0)
        self.next_btn.setEnabled(has_images and self.current_index < len(self.images) - 1)

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
            self.update_nav_state()

    def next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image()
            self.update_nav_state()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Left, Qt.Key_A):
            self.prev_image()
        elif event.key() in (Qt.Key_Right, Qt.Key_D):
            self.next_image()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.images:
            self.show_image()


def main():
    app = QApplication(sys.argv)
    gallery = GalleryApp()
    gallery.show()

    # If directory passed as argument, load it
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        gallery.load_images(sys.argv[1])

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
