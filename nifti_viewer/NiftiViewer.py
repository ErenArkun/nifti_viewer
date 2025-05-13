import os
import nibabel as nib
import numpy as np
from PyQt6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt


class NiftiViewer(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        openButton = QPushButton("NIfTI Dosyası Aç", self)
        openButton.clicked.connect(self.load_nifti)
        layout.addWidget(openButton)

        self.label = QLabel("Yüklenen dosya: Yok", self)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def load_nifti(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "NIfTI Dosyası Aç", "", "NIfTI Files (*.nii *.nii.gz)")
        if file_path:
            self.label.setText(f"Yüklenen dosya: {os.path.basename(file_path)}")
            img = nib.load(file_path)
            data = img.get_fdata()
            self.display_slices(data)

    def display_slices(self, data):
        mid_slices = {
            "Axial": data[:, :, data.shape[2] // 2],
            "Coronal": data[:, data.shape[1] // 2, :],
            "Sagital": data[data.shape[0] // 2, :, :]
        }

        for widget in self.main_window.findChildren(QWidget):
            if widget.objectName() == "imageViewer":
                slice_type = widget.toolTip()
                if slice_type in mid_slices:
                    slice_data = mid_slices[slice_type]
                    image = self.convert_to_qimage(slice_data)

                    def create_paint_event(img):
                        def paintEvent(event):
                            painter = QPainter(widget)
                            rect = widget.rect()
                            scaled_img = img.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            x = (rect.width() - scaled_img.width()) // 2
                            y = (rect.height() - scaled_img.height()) // 2
                            painter.drawImage(x, y, scaled_img)
                        return paintEvent

                    widget.paintEvent = create_paint_event(image)
                    widget.update()

    def convert_to_qimage(self, data):
        norm_data = (255 * (data - np.min(data)) / (np.max(data) - np.min(data))).astype(np.uint8)
        h, w = norm_data.shape
        return QImage(norm_data.data, w, h, w, QImage.Format.Format_Grayscale8).copy()


def show_plugin(main_window):
    from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

    plugin_widget = QWidget()
    plugin_layout = QVBoxLayout(plugin_widget)

    viewer = NiftiViewer(main_window=main_window)
    plugin_layout.addWidget(viewer)

    image_layout = QHBoxLayout()

    for name in ["Axial", "Coronal", "Sagital"]:
        w = QWidget()
        w.setObjectName("imageViewer")
        w.setToolTip(name)
        w.setMinimumSize(300, 300)
        image_layout.addWidget(w)

    plugin_layout.addLayout(image_layout)
    main_window.setCentralWidget(plugin_widget)
