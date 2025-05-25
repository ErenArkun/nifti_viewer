from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
import os

class NiftiViewer(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.selected_file_path = None  # Hafıza için değişken
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        open_button = QPushButton("NIfTI Dosyası Aç", self)
        open_button.clicked.connect(self.select_nifti_file)
        layout.addWidget(open_button)

        self.label = QLabel("Yüklenen dosya: Yok", self)
        layout.addWidget(self.label)

    def select_nifti_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "NIfTI Dosyası Aç", "", "NIfTI Files (*.nii *.nii.gz)")
        if file_path:
            self.selected_file_path = file_path  # Hafızaya alma
            self.label.setText(f"Yüklenen dosya: {os.path.basename(file_path)}")
            print(f"Yüklenen dosya: {file_path}")
            # main_window'da varsa handle_nifti_file metodunu çağır
            
            try:
                if self.main_window:
                    self.main_window.load_nifti(file_path)
                else:
                    print("Ana pencere tanımlı değil, dosya yüklenemedi.")
            except Exception as e:
                print(f"Dosya yüklenirken hata oluştu: {e}")
                self.label.setText("Yüklenen dosya: Hata oluştu")
                