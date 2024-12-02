import sys
import sqlite3
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QTableView, QLineEdit, QPushButton, QMessageBox, QFormLayout,
    QDialog, QSpinBox, QTextEdit, QDialogButtonBox, QProgressBar
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import QTimer, QThread, pyqtSignal


# БД
def initialize_database():
    connection = sqlite3.connect("posts.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            body TEXT
        );
    """)
    connection.commit()
    connection.close()


# Загрузка на фоне
class BackgroundWorker(QThread):
    progress = pyqtSignal(int)
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            response = requests.get("https://jsonplaceholder.typicode.com/posts", timeout=10)
            response.raise_for_status()
            data = response.json()

            for i, _ in enumerate(data, 1):
                QThread.msleep(50)  # Задержка для симуляции загрузки
                self.progress.emit(int(i / len(data) * 100))

            self.data_loaded.emit(data)
        except requests.RequestException as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка загрузки данных: {str(e)}")


# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite GUI на PyQt")
        self.resize(800, 600)

        # Подключение к базе
        self.database = self.connect_to_db()
        self.model = self.create_model()

        # Все элементы интерфейса(почти)
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по заголовку...")

        self.refresh_button = QPushButton("Обновить")
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.load_button = QPushButton("Загрузить данные")
        self.progress_bar = QProgressBar()

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        main_layout.addWidget(self.search_field)
        main_layout.addWidget(self.table_view)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.load_button)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.refresh_button.clicked.connect(self.refresh_table)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.delete_button.clicked.connect(self.delete_selected_record)
        self.load_button.clicked.connect(self.load_data)
        self.search_field.textChanged.connect(self.search_records)

        # Таймер до обновления
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_refresh_data)
        self.timer.start(30000)
        self.worker_thread = None

    def connect_to_db(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("posts.db")
        if not db.open():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных.")
            sys.exit(1)
        return db

    def create_model(self):
        model = QSqlTableModel()
        model.setTable("posts")
        model.select()
        model.setHeaderData(0, 0, "ID")
        model.setHeaderData(1, 0, "User ID")
        model.setHeaderData(2, 0, "Title")
        model.setHeaderData(3, 0, "Body")
        return model

    def refresh_table(self):
        self.model.select()

    def open_add_dialog(self):
        dialog = AddDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def delete_selected_record(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления.")
            return

        confirmation = QMessageBox.question(
            self, "Подтверждение", "Вы действительно хотите удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            for index in selected:
                self.model.removeRow(index.row())
            self.model.submitAll()
            self.refresh_table()

    def search_records(self, text):
        filter_str = f"title LIKE '%{text}%'"
        self.model.setFilter(filter_str)
        self.model.select()

    def load_data(self):
        if self.worker_thread is not None and self.worker_thread.isRunning():
            QMessageBox.information(self, "Информация", "Загрузка уже выполняется.")
            return

        self.worker_thread = BackgroundWorker()
        self.worker_thread.progress.connect(self.progress_bar.setValue)
        self.worker_thread.data_loaded.connect(self.save_data)
        self.worker_thread.start()

    def save_data(self, data):
        connection = sqlite3.connect("posts.db")
        cursor = connection.cursor()

        for post in data:
            cursor.execute("""
                INSERT OR IGNORE INTO posts (id, user_id, title, body)
                VALUES (?, ?, ?, ?)
            """, (post["id"], post["userId"], post["title"], post["body"]))

        connection.commit()
        connection.close()
        self.refresh_table()

    def auto_refresh_data(self):
        self.load_data()

    def closeEvent(self, event):
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
        super().closeEvent(event)


# ДОБАВИТЬ
class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")

        self.user_id_field = QSpinBox()
        self.user_id_field.setMinimum(1)
        self.title_field = QLineEdit()
        self.body_field = QTextEdit()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("User ID:", self.user_id_field)
        form_layout.addRow("Title:", self.title_field)
        form_layout.addRow("Body:", self.body_field)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept(self):
        user_id = self.user_id_field.value()
        title = self.title_field.text()
        body = self.body_field.toPlainText()

        if not title or not body:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        db = QSqlDatabase.database()
        if not db.isOpen():
            QMessageBox.critical(self, "Ошибка", "База данных не подключена.")
            return

        query = db.exec(
            f"""
            INSERT INTO posts (user_id, title, body)
            VALUES ({user_id}, '{title}', '{body}');
            """
        )
        if not query.isActive():
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись: {query.lastError().text()}")
            return

        super().accept()


def main():
    initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
