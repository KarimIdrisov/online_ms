import sys

import psycopg2
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMainWindow, QDialog
from psycopg2 import sql

import shop
import order
import dev_order
import datetime


class Shop(QMainWindow, shop.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.dev_order = uic.loadUi('dev_order.ui')
        self.order = uic.loadUi('order.ui')
        self.setupUi(self)

        self.conn = psycopg2.connect(
            database="shop",
            user="postgres",
            password="",
            host="127.0.0.1",
            port="5432"
        )

        self.cursor = self.conn.cursor()

        self.pushButton_med.clicked.connect(self.find_medicines)
        self.pushButton_stock.clicked.connect(self.find_stock)
        self.new_order.clicked.connect(self.make_order)
        self.new_dev_order.clicked.connect(self.make_dev_order)
        self.change_table()
        self.comboBox.currentIndexChanged.connect(self.change_table)

    def change_table(self):

        field = self.comboBox.currentText()
        field = str(field).lower().replace(" ", "_")
        request = sql.SQL('SELECT * FROM {}').format(sql.Identifier(field))
        self.cursor.execute(request)
        fields = self.cursor.fetchall()
        num_fields = len(self.cursor.description)
        field_names = [i[0].title() for i in self.cursor.description]
        for i in range(num_fields):
            field_names[i] = str(field_names[i]).replace('_', ' ')
        self.table.setColumnCount(num_fields)
        self.table.setHorizontalHeaderLabels(field_names)
        self.table.setRowCount(0)
        for i in range(len(fields)):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j in range(num_fields):
                self.table.setItem(i, j, QTableWidgetItem(str(fields[i][j])))
        self.table.resizeColumnsToContents()

    def find_medicines(self):

        self.comboBox.setCurrentText("Medicines")
        self.change_table()

        medicine = self.lineEdit_med.text()
        self.cursor.execute('SELECT med_name FROM medicines')
        medicines = self.cursor.fetchall()
        medicines = [i[0] for i in medicines]
        medicines = [i.lower() for i in medicines]
        if medicine.lower() in medicines:
            self.cursor.execute("SELECT * FROM medicines WHERE med_name = %s", (medicine.title(),))
            fields = self.cursor.fetchall()
            num_fields = len(self.cursor.description)
            field_names = [i[0].title() for i in self.cursor.description]
            for i in range(num_fields):
                field_names[i] = str(field_names[i]).replace('_', ' ')
            self.table.setColumnCount(num_fields)
            self.table.setHorizontalHeaderLabels(field_names)
            self.table.setRowCount(0)
            for i in range(len(fields)):
                self.table.setRowCount(self.table.rowCount() + 1)
                for j in range(num_fields):
                    self.table.setItem(i, j, QTableWidgetItem(str(fields[i][j])))
            self.table.resizeColumnsToContents()

    def find_stock(self):
        self.comboBox.setCurrentText("Stock")
        self.change_table()

        stock_name = self.lineEdit_stock.text()
        self.cursor.execute('SELECT stock_name, id FROM list_of_stocks')
        list_of_stocks = self.cursor.fetchall()
        stocks = [i[0] for i in list_of_stocks]
        stocks = [i.lower() for i in stocks]
        stocks_id = [i[1] for i in list_of_stocks]
        for i in range(len(stocks)):
            if stock_name == stocks[i]:
                id = stocks_id[i]
                self.cursor.execute('SELECT * FROM stock WHERE stock_id = %s', (id,))
                fields = self.cursor.fetchall()
                num_fields = len(self.cursor.description)
                field_names = [i[0].title() for i in self.cursor.description]
                for i in range(num_fields):
                    field_names[i] = str(field_names[i]).replace('_', ' ')
                self.table.setColumnCount(num_fields)
                self.table.setHorizontalHeaderLabels(field_names)
                self.table.setRowCount(0)
                for i in range(len(fields)):
                    self.table.setRowCount(self.table.rowCount() + 1)
                    for j in range(num_fields):
                        self.table.setItem(i, j, QTableWidgetItem(str(fields[i][j])))
                self.table.resizeColumnsToContents()

    def make_order(self):
        self.order.cancel.clicked.connect(self.order.close)
        self.order.accept.clicked.connect(self.commit_order)
        self.order.show()
        self.order.exec_()

    def commit_order(self):
        order_id = self.order.id.value()
        med_weight = self.order.med_weight.currentText()
        med, weight = med_weight.split()
        stock = self.order.stock.currentText()
        med_count = self.order.med_count.value()
        pharmacy = self.order.pharmacy.currentText()
        order_date = self.order.order_date.date()
        order_date = order_date.toString("dd-MM-yyyy")
        dep_date = self.order.departure_date.date()
        dep_date = dep_date.toString("dd-MM-yyyy")
        values = [(med, str(weight), str(med_count), pharmacy, stock, order_date, dep_date, str(order_id))]

        insert = sql.SQL('INSERT INTO orders '
                         '(med_name, weight, count, pharmacy, stock, order_date, departure_date, order_id) '
                         'VALUES {}').format(sql.SQL(',').join(map(sql.Literal, values)))
        self.cursor.execute(insert)
        self.conn.commit()
        self.order.close()

    def make_dev_order(self):
        self.dev_order.cancel.clicked.connect(self.dev_order.close)
        self.dev_order.accept.clicked.connect(self.commit_dev_order)
        self.dev_order.show()
        self.dev_order.exec_()

    def commit_dev_order(self):
        order_id = self.dev_order.id.value()
        med_weight = self.dev_order.med_weight.currentText()
        med, weight = med_weight.split()
        stock = self.dev_order.stock.currentText()
        med_count = self.dev_order.med_count.value()
        supplier = self.dev_order.supplier.currentText()
        order_date = self.dev_order.order_date.date()
        order_date = order_date.toString("dd-MM-yyyy")
        dep_date = self.dev_order.departure_date.date()
        dep_date = dep_date.toString("dd-MM-yyyy")
        values = [(str(med_count), med, str(weight), supplier, stock, order_date, dep_date, str(order_id))]

        insert = sql.SQL('INSERT INTO delivery_orders '
                         '(count, med_name, weight, supplier, stock_name, order_date, departure_date, order_id) '
                         'VALUES {}').format(sql.SQL(',').join(map(sql.Literal, values)))
        self.cursor.execute(insert)
        self.conn.commit()
        self.dev_order.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Shop()
    ex.show()
    sys.exit(app.exec_())
