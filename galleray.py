#!/usr/bin/env python3
"""Gall-array - A simple minimalist image gallery for Linux."""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSizePolicy, QStackedWidget,
    QListWidget, QListWidgetItem, QScrollArea, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QSize, QUrl, QEvent, QTimer
from PyQt5.QtGui import QPixmap, QKeyEvent, QDesktopServices, QIcon

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
QPushButton:checked {
    background-color: #4a4a4a;
    border: 1px solid #666;
}
QLabel {
    color: #a0a0a0;
}
QListWidget {
    background-color: #252525;
    border: none;
    border-radius: 4px;
    padding: 8px;
}
QListWidget::item {
    color: #e0e0e0;
    padding: 8px 12px;
    border-radius: 4px;
}
QListWidget::item:hover {
    background-color: #3d3d3d;
}
QListWidget::item:selected {
    background-color: #4a4a4a;
}
QScrollArea {
    background-color: #1e1e1e;
    border: none;
}
"""


class ThumbnailLabel(QLabel):
    """Thumbnail with hover magnification."""

    def __init__(self, image_path, index, gallery, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.index = index
        self.gallery = gallery
        self.setFixedSize(150, 150)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel:hover {
                background-color: #3d3d3d;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.load_thumbnail()

    def load_thumbnail(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)

    def enterEvent(self, event):
        self.gallery.show_magnified(self.image_path, self.index)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.gallery.hide_magnified()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.gallery.current_index = self.index
            self.gallery.set_view_mode('gallery')
        super().mousePressEvent(event)


class GalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = []
        self.current_index = 0
        self.current_view = 'gallery'
        self.thumbnail_widgets = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gall-array")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(DARK_STYLE)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'galleray.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

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

        top_bar.addSpacing(20)

        # View mode buttons
        self.gallery_btn = QPushButton("Gallery")
        self.gallery_btn.setCheckable(True)
        self.gallery_btn.setChecked(True)
        self.gallery_btn.clicked.connect(lambda: self.set_view_mode('gallery'))
        top_bar.addWidget(self.gallery_btn)

        self.list_btn = QPushButton("List")
        self.list_btn.setCheckable(True)
        self.list_btn.clicked.connect(lambda: self.set_view_mode('list'))
        top_bar.addWidget(self.list_btn)

        self.grid_btn = QPushButton("Grid")
        self.grid_btn.setCheckable(True)
        self.grid_btn.clicked.connect(lambda: self.set_view_mode('grid'))
        top_bar.addWidget(self.grid_btn)

        top_bar.addStretch()

        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("font-size: 14px;")
        top_bar.addWidget(self.counter_label)
        layout.addLayout(top_bar)

        # Stacked widget for different views
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Gallery view (original)
        self.gallery_widget = QWidget()
        gallery_layout = QVBoxLayout(self.gallery_widget)
        gallery_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel("Select a folder to view images")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("font-size: 16px; color: #666;")
        gallery_layout.addWidget(self.image_label, 1)

        self.filename_label = QLabel("")
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("font-size: 12px; color: #888;")
        gallery_layout.addWidget(self.filename_label)

        # Navigation buttons
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
        gallery_layout.addLayout(nav_layout)

        self.stack.addWidget(self.gallery_widget)

        # List view
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.list_item_clicked)
        self.stack.addWidget(self.list_widget)

        # Grid view container
        self.grid_container = QWidget()
        grid_container_layout = QHBoxLayout(self.grid_container)
        grid_container_layout.setContentsMargins(0, 0, 0, 0)
        grid_container_layout.setSpacing(15)

        # Grid scroll area
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_content = QWidget()
        self.grid_layout = QGridLayout(self.grid_content)
        self.grid_layout.setSpacing(10)
        self.grid_scroll.setWidget(self.grid_content)
        grid_container_layout.addWidget(self.grid_scroll, 2)

        # Magnified preview panel
        self.magnified_panel = QFrame()
        self.magnified_panel.setFixedWidth(350)
        self.magnified_panel.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 8px;
            }
        """)
        magnified_layout = QVBoxLayout(self.magnified_panel)

        self.magnified_label = QLabel("Hover over a thumbnail")
        self.magnified_label.setAlignment(Qt.AlignCenter)
        self.magnified_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.magnified_label.setStyleSheet("color: #666;")
        magnified_layout.addWidget(self.magnified_label)

        self.magnified_name = QLabel("")
        self.magnified_name.setAlignment(Qt.AlignCenter)
        self.magnified_name.setStyleSheet("font-size: 11px; color: #888; padding: 8px;")
        self.magnified_name.setWordWrap(True)
        magnified_layout.addWidget(self.magnified_name)

        grid_container_layout.addWidget(self.magnified_panel)

        self.stack.addWidget(self.grid_container)

        # Footer branding
        footer = QHBoxLayout()
        footer.addStretch()

        website_link = QLabel('<a href="https://anarchygames.org" style="color: #666; text-decoration: none;">anarchygames.org</a>')
        website_link.setOpenExternalLinks(True)
        website_link.setStyleSheet("font-size: 11px;")
        footer.addWidget(website_link)

        separator = QLabel("  |  ")
        separator.setStyleSheet("font-size: 11px; color: #444;")
        footer.addWidget(separator)

        donate_link = QLabel('<a href="https://ko-fi.com/O5O71TOKUE" style="color: #666; text-decoration: none;">Support on Ko-fi</a>')
        donate_link.setOpenExternalLinks(True)
        donate_link.setStyleSheet("font-size: 11px;")
        footer.addWidget(donate_link)

        footer.addStretch()
        layout.addLayout(footer)

    def set_view_mode(self, mode):
        self.current_view = mode
        self.gallery_btn.setChecked(mode == 'gallery')
        self.list_btn.setChecked(mode == 'list')
        self.grid_btn.setChecked(mode == 'grid')

        if mode == 'gallery':
            self.stack.setCurrentIndex(0)
            if self.images:
                self.show_image()
        elif mode == 'list':
            self.stack.setCurrentIndex(1)
        elif mode == 'grid':
            self.stack.setCurrentIndex(2)

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
            self.populate_list()
            self.populate_grid()
            self.counter_label.setText(f"{len(self.images)} images")
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("No images found in folder")
            self.counter_label.setText("")
            self.filename_label.setText("")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.list_widget.clear()
            self.clear_grid()

    def populate_list(self):
        self.list_widget.clear()
        for i, path in enumerate(self.images):
            item = QListWidgetItem(f"{i + 1}. {os.path.basename(path)}")
            item.setData(Qt.UserRole, i)
            self.list_widget.addItem(item)

    def list_item_clicked(self, item):
        self.current_index = item.data(Qt.UserRole)
        self.set_view_mode('gallery')

    def clear_grid(self):
        for widget in self.thumbnail_widgets:
            widget.deleteLater()
        self.thumbnail_widgets.clear()

    def populate_grid(self):
        self.clear_grid()
        cols = 4
        for i, path in enumerate(self.images):
            thumb = ThumbnailLabel(path, i, self)
            self.thumbnail_widgets.append(thumb)
            row, col = divmod(i, cols)
            self.grid_layout.addWidget(thumb, row, col)

    def show_magnified(self, path, index):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.magnified_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.magnified_label.setPixmap(scaled)
        self.magnified_name.setText(f"{index + 1}. {os.path.basename(path)}")

    def hide_magnified(self):
        self.magnified_label.clear()
        self.magnified_label.setText("Hover over a thumbnail")
        self.magnified_name.setText("")

    def show_image(self):
        if not self.images:
            return

        path = self.images[self.current_index]
        pixmap = QPixmap(path)

        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

        self.counter_label.setText(f"{self.current_index + 1} / {len(self.images)}")
        self.filename_label.setText(os.path.basename(path))
        self.update_nav_state()

    def update_nav_state(self):
        has_images = len(self.images) > 0
        self.prev_btn.setEnabled(has_images and self.current_index > 0)
        self.next_btn.setEnabled(has_images and self.current_index < len(self.images) - 1)

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image()

    def keyPressEvent(self, event: QKeyEvent):
        if self.current_view == 'gallery':
            if event.key() in (Qt.Key_Left, Qt.Key_A):
                self.prev_image()
            elif event.key() in (Qt.Key_Right, Qt.Key_D):
                self.next_image()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.images and self.current_view == 'gallery':
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
