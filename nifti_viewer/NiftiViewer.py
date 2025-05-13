import os
import numpy as np
import nibabel as nib
import cv2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap, QImage

class NiftiViewer(QWidget):  # Sınıf ismi dosya ismi ile aynı olmalı
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #A0A0A0;")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button = QPushButton("NIfTI Dosyası Yükle")
        self.button.clicked.connect(self.load_nifti_file)
        self.layout.addWidget(self.button)

    def load_nifti_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "NIfTI Dosyası Seç", "", "NIfTI Dosyaları (*.nii *.nii.gz)")
        if file_path:
            try:
                nifti_img = nib.load(file_path)
                data = nifti_img.get_fdata()
                self.display_slices(data)
            except Exception as e:
                print(f"[HATA] NIfTI dosyası yüklenemedi: {e}")

    def display_slices(self, data):
        # Verileri ortadan birer kesit olarak al
        axial = data[:, :, data.shape[2] // 2]
        sagital = data[data.shape[0] // 2, :, :]
        coronal = data[:, data.shape[1] // 2, :]

        # 8-bit'e çevir ve normalize et
        def prepare_image(slice_):
            slice_ = np.rot90(slice_)  # Doğru açıyla göstermek için
            slice_ = cv2.normalize(slice_, None, 0, 255, cv2.NORM_MINMAX)
            return slice_.astype(np.uint8)

        # Görselleri Qt formatına çevir
        def to_qpixmap(slice_):
            h, w = slice_.shape
            bytes_per_line = w
            q_image = QImage(slice_.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)
            return QPixmap.fromImage(q_image)

        axial_pixmap = to_qpixmap(prepare_image(axial))
        sagital_pixmap = to_qpixmap(prepare_image(sagital))
        coronal_pixmap = to_qpixmap(prepare_image(coronal))

        # Ana pencere sınıfındaki paint_image_viewer fonksiyonu kullanılacak
        # image değerini set etmek için ana pencerenin imageViewer widget'larına eriş
        for widget in self.parent().parent().findChildren(QWidget):
            if widget.objectName() == "imageViewer":
                layout = widget.layout()
                slider = layout.itemAt(1).widget() if layout.count() > 1 else None
                if slider:
                    layout.removeWidget(slider)
                    slider.setParent(None)

                if "Axial" in widget.toolTip() or "Axial" in widget.windowTitle():
                    image = axial_pixmap
                elif "Sagital" in widget.toolTip() or "Sagital" in widget.windowTitle():
                    image = sagital_pixmap
                elif "Coronal" in widget.toolTip() or "Coronal" in widget.windowTitle():
                    image = coronal_pixmap
                else:
                    image = None

                if image:
                    def paint(event, image=image, title=widget.windowTitle()):
                        from main import paint_image_viewer
                        paint_image_viewer(widget, title, is_empty=False, image=image)
                    widget.paintEvent = paint
                    widget.update()

