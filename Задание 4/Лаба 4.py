import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QTableView, QLineEdit, QPushButton, QMessageBox, QFormLayout, QDialog, QSpinBox, QTextEdit, QDialogButtonBox
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel


# Создание базы данных и таблицы, если они отсутствуют
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
    # Добавление тестовых данных, если таблица пустая
    cursor.execute("SELECT COUNT(*) FROM posts")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO posts (user_id, title, body)
            VALUES (?, ?, ?)
        """, [
            (1, "First Post", "This is the first test post."),
            (2, "Second Post", "This is another test post."),
            (3, "Hello World", "Hello, this is a sample post!")
        ])
    connection.commit()
    connection.close()


# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite GUI на PyQt")
        self.resize(800, 600)

        # Подключение к базе данных SQLite
        self.database = self.connect_to_db()
        self.model = self.create_model()

        # Виджеты интерфейса
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по заголовку...")

        self.refresh_button = QPushButton("Обновить")
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")

        # Разметка интерфейса
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        main_layout.addWidget(self.search_field)
        main_layout.addWidget(self.table_view)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Подключение сигналов
        self.refresh_button.clicked.connect(self.refresh_table)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.delete_button.clicked.connect(self.delete_selected_record)
        self.search_field.textChanged.connect(self.search_records)

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


# Диалог для добавления записей
class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")

        # Поля формы
        self.user_id_field = QSpinBox()
        self.user_id_field.setMinimum(1)
        self.title_field = QLineEdit()
        self.body_field = QTextEdit()

        # Кнопки OK и Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Разметка формы
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

        # Получаем доступ к текущему подключению к базе данных
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


# Основная функция
def main():
    initialize_database()  # Создаем базу данных, если её нет
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()