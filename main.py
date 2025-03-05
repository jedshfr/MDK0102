import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QComboBox, QDialog, QLabel, QLineEdit, QTextEdit, QMessageBox
from PySide6.QtGui import QIcon

requests.packages.urllib3.disable_warnings()

class Cat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кошки")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("cat.png")) 

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все")
        self.layout.addWidget(self.filter_combo)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Происхождение", "Темперамент"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.open_cat_details)
        self.layout.addWidget(self.table)

        self.delete_button = QPushButton("Удалить котика :(")
        self.delete_button.clicked.connect(self.delete_cat)
        self.layout.addWidget(self.delete_button)

        self.cat_data = []
        self.load_cat()

    def load_cat(self):
        url = "https://api.thecatapi.com/v1/breeds"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            self.cat_data = response.json()
            self.update_table()
            self.update_filter()

    def update_table(self):
        self.table.setRowCount(0)
        for cat in self.cat_data:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(cat.get("name", "")))
            self.table.setItem(row_position, 1, QTableWidgetItem(cat.get("origin", "")))
            self.table.setItem(row_position, 2, QTableWidgetItem(cat.get("temperament", "")))

    def update_filter(self):
        origins = set(cat.get("origin", "") for cat in self.cat_data)
        self.filter_combo.clear()
        self.filter_combo.addItem("Все")
        for origin in sorted(origins):
            self.filter_combo.addItem(origin)
        self.filter_combo.currentTextChanged.connect(self.filter_table)

    def filter_table(self):
        selected_origin = self.filter_combo.currentText()
        if selected_origin == "Все":
            self.update_table()
        else:
            filtered_data = [cat for cat in self.cat_data if cat.get("origin", "") == selected_origin]
            self.table.setRowCount(0)
            for cat in filtered_data:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(cat.get("name", "")))
                self.table.setItem(row_position, 1, QTableWidgetItem(cat.get("origin", "")))
                self.table.setItem(row_position, 2, QTableWidgetItem(cat.get("temperament", "")))

    def open_cat_details(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            cat = self.cat_data[selected_row]
            dialog = CatDetailsDialog(cat, self)
            if dialog.exec() == QDialog.Accepted:  
                self.cat_data[selected_row] = dialog.cat  
                self.update_table()  

    def delete_cat(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(self, 'Удаление котика', 'Вы уверены, что хотите удалить этого кота?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.cat_data[selected_row]
                self.update_table()

class CatDetailsDialog(QDialog):
    def __init__(self, cat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Информация о коте")
        self.setModal(True)

        self.layout = QVBoxLayout(self)

        self.name_label = QLabel("Имя:")
        self.name_edit = QLineEdit(cat.get("name", ""))
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)

        self.origin_label = QLabel("Происхождение:")
        self.origin_edit = QLineEdit(cat.get("origin", ""))
        self.layout.addWidget(self.origin_label)
        self.layout.addWidget(self.origin_edit)

        self.temperament_label = QLabel("Характер:")
        self.temperament_edit = QTextEdit(cat.get("temperament", ""))
        self.layout.addWidget(self.temperament_label)
        self.layout.addWidget(self.temperament_edit)

        self.edit_button = QPushButton("Сохранить изменения")
        self.edit_button.clicked.connect(self.edit_cat)
        self.layout.addWidget(self.edit_button)
        self.cat = cat

    def edit_cat(self):
        self.cat["name"] = self.name_edit.text()
        self.cat["origin"] = self.origin_edit.text()
        self.cat["temperament"] = self.temperament_edit.toPlainText()
        QMessageBox.information(self, "Успех", "Информация о коте успешно обновлена.")
        self.accept()  

app = QApplication([])
window = Cat()
window.show()
app.exec()