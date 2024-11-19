from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QDateEdit
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
import psycopg2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Система учета клиентов и истории заказов')
        self.setWindowIcon(QIcon('icon.png'))  # Укажите путь к иконке

        # Поля для клиента
        self.client_name_input = QLineEdit(self)
        self.contact_info_input = QLineEdit(self)
        self.add_client_button = QPushButton('Добавить клиента', self)

        # Поля для заказа
        self.product_input = QLineEdit(self)
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.total_amount_input = QLineEdit(self)
        self.add_order_button = QPushButton('Добавить заказ', self)

        # Таблица заказов
        self.orders_table = QTableWidget(self)

        # Кнопка для загрузки заказов
        self.load_orders_button = QPushButton('Загрузить заказы', self)

        # Создание макета
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Имя клиента:'))
        layout.addWidget(self.client_name_input)
        layout.addWidget(QLabel('Контактная информация:'))
        layout.addWidget(self.contact_info_input)
        layout.addWidget(self.add_client_button)

        layout.addWidget(QLabel('Продукты:'))
        layout.addWidget(self.product_input)
        layout.addWidget(QLabel('Дата заказа:'))
        layout.addWidget(self.date_input)
        layout.addWidget(QLabel('Сумма:'))
        layout.addWidget(self.total_amount_input)
        layout.addWidget(self.add_order_button)

        layout.addWidget(self.load_orders_button)
        layout.addWidget(self.orders_table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Подключение кнопок к методам
        self.add_client_button.clicked.connect(self.add_client)
        self.add_order_button.clicked.connect(self.add_order)
        self.load_orders_button.clicked.connect(self.load_orders)

    def get_db_connection(self):
        """Подключение к базе данных PostgreSQL."""
        return psycopg2.connect(
            dbname='postgres',  # Замените на вашу БД
            user='postgres',       # Ваше имя пользователя PostgreSQL
            password='student-pro',  # Ваш пароль
            host='localhost',       # Хост (localhost для локального)
            port='5432'             # Порт PostgreSQL (по умолчанию 5432)
        )

    def add_client(self):
        """Добавление клиента в базу данных."""
        name = self.client_name_input.text()
        contact_info = self.contact_info_input.text()
        if name:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO clients (name, contact_info) VALUES (%s, %s)', (name, contact_info))
            conn.commit()
            conn.close()

    def add_order(self):
        """Добавление заказа для клиента."""
        client_name = self.client_name_input.text()
        products = self.product_input.text()
        order_date = self.date_input.date().toString('yyyy-MM-dd')
        total_amount = float(self.total_amount_input.text())

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Получение ID клиента
        cursor.execute('SELECT id FROM clients WHERE name = %s', (client_name,))
        client = cursor.fetchone()

        if client:
            client_id = client[0]
            cursor.execute(
                'INSERT INTO orders (client_id, products, order_date, total_amount) VALUES (%s, %s, %s, %s)',
                (client_id, products, order_date, total_amount)
            )
            conn.commit()

        conn.close()

    def load_orders(self):
        """Загрузка всех заказов в таблицу с сортировкой по дате."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT clients.name, orders.products, orders.order_date, orders.total_amount
            FROM orders
            JOIN clients ON orders.client_id = clients.id
            ORDER BY orders.order_date DESC
        ''')
        orders = cursor.fetchall()

        self.orders_table.setRowCount(len(orders))
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(['Клиент', 'Продукты', 'Дата', 'Сумма'])

        for row, order in enumerate(orders):
            for col, data in enumerate(order):
                self.orders_table.setItem(row, col, QTableWidgetItem(str(data)))

        conn.close()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()