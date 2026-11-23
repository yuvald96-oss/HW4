import os
import platform
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

HERE = Path(__file__).parent
GITHUB_URL = "https://github.com/yuvald96-oss/HW4"
TABLE_ROWS = 50


class GradesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ''

        self.setWindowTitle("Grade Correction")
        self.resize(640, 760)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Grade Correction")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Load a grades file, add bonus points, and save it back.")
        subtitle.setObjectName("subtitleLabel")
        root.addWidget(title)
        root.addWidget(subtitle)

        top = QHBoxLayout()
        self.load_button = QPushButton("Load Students File")
        self.load_button.setObjectName("primaryButton")
        self.load_button.clicked.connect(self.on_load_clicked)
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.on_about_clicked)
        top.addWidget(self.load_button)
        top.addWidget(self.file_label, 1)
        top.addWidget(self.about_button)
        root.addLayout(top)

        self.table = QTableWidget(TABLE_ROWS, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Original Grades", "Corrected Grades"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        root.addWidget(self.table, 1)

        bottom = QHBoxLayout()
        points_label = QLabel("Correction points (press Enter):")
        self.points_spin = QSpinBox()
        self.points_spin.setRange(0, 100)
        self.points_spin.setKeyboardTracking(False)
        self.points_spin.lineEdit().returnPressed.connect(self.on_points_entered)
        self.update_button = QPushButton("Update File")
        self.update_button.setObjectName("primaryButton")
        self.update_button.clicked.connect(self.on_update_file_clicked)
        bottom.addWidget(points_label)
        bottom.addWidget(self.points_spin)
        bottom.addStretch(1)
        bottom.addWidget(self.update_button)
        root.addLayout(bottom)

        self.setCentralWidget(central)

    def refresh_table(self):
        self.table.clearContents()
        for row in range(min(len(self.student_ids), TABLE_ROWS)):
            values = (self.student_ids[row], self.original_grades[row], self.corrected_grades[row])
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def on_load_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select students file", str(HERE / "data"), "CSV files (*.csv);;All files (*)"
        )
        if not file_name:
            return
        self.file_label.setText(os.path.basename(file_name))
        self.selected_file = file_name
        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        with open(self.selected_file, 'r') as f:
            lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            if line == '':
                continue
            parts = line.split(',')
            self.student_ids.append(parts[0])
            self.original_grades.append(int(parts[1]))
            self.corrected_grades.append(int(parts[1]))

        self.refresh_table()

    def on_points_entered(self):
        points = self.points_spin.value()
        for i in range(len(self.original_grades)):
            new_grade = self.original_grades[i] + points
            if new_grade > 100:
                new_grade = 100
            self.corrected_grades[i] = new_grade

        self.refresh_table()

    def on_update_file_clicked(self):
        if not self.selected_file:
            QMessageBox.warning(self, "No file", "Please load a students file first.")
            return
        with open(self.selected_file, 'r') as f:
            header = f.readline().strip()

        lines = [header]
        for i in range(len(self.student_ids)):
            lines.append(self.student_ids[i] + ',' + str(self.corrected_grades[i]))

        with open(self.selected_file, 'w') as f:
            f.write('\n'.join(lines))

        open_file_externally(self.selected_file)

    def on_about_clicked(self):
        QMessageBox.about(
            self,
            "About",
            "<h3>Grade Correction</h3>"
            "<p>Advanced Coding - Files &amp; Graphs exercise.</p>"
            "<p>Author: Yuval Dekel</p>"
            f'<p>Source code: <a href="{GITHUB_URL}">{GITHUB_URL}</a></p>',
        )


def open_file_externally(path):
    system = platform.system()
    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet((HERE / "grades.qss").read_text(encoding="utf-8"))
    window = GradesWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
