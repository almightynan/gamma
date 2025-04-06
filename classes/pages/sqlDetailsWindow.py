# Copyright (c) 2024 - <current year> AlmightyNan <almightynan@apollo-bot.xyz>
#
# This file is part of gamma.
#
# This file may be used only with explicit permission from AlmightyNan.
# Redistribution, modification, or commercial use without prior written
# consent is strictly prohibited.
#
# Proper credit must be given to AlmightyNan, and it must be displayed
# visibly without shortening or obscuring the text.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.

import csv
import json
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QDesktopWidget,
    QMessageBox,
    QLabel,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QSplitter,
    QWidget,
    QFrame,
    QComboBox,
    QLineEdit,
    QFileDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import logging


logger = logging.getLogger()


class TableDetailsWindow(QDialog):
    def __init__(
        self,
        table_name,
        table_description,
        table_data,
        available_tables,
        mysql_manager,
        parent=None,
    ):
        super().__init__(parent)
        self.mysql_manager = mysql_manager
        self.table_name = table_name
        self.table_data = table_data
        self.setWindowTitle(f"Details of {table_name}")
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.setGeometry(0, 0, 1000, 800)
        self.center_window()
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        logger.info(f"TableDetailsWindow initialized for table: {table_name}")

        self.setStyleSheet("background-color: #111; color: #fff;")

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Horizontal)

        description_layout = QVBoxLayout()
        description_label = QLabel("Table Description")
        description_label.setFont(QFont("Arial", 16))
        description_label.setStyleSheet("color: #fff;")

        self.description_table = QTableWidget(self)
        self.description_table.setRowCount(len(table_description))
        self.description_table.setColumnCount(4)
        self.description_table.setHorizontalHeaderLabels(
            ["Field", "Type", "Null", "Key"]
        )

        for row, desc in enumerate(table_description):
            for col, value in enumerate(desc):
                item = QTableWidgetItem(str(value))
                self.description_table.setItem(row, col, item)

        self.description_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.description_table.setShowGrid(True)
        self.description_table.setFrameShape(QFrame.Box)
        self.description_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #222;
                color: #fff;
                border: 1px solid #555;
            }
            QTableWidget::item {
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #333;
                color: #fff;
            }
        """
        )

        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_table)

        description_widget = QWidget(self)
        description_widget.setLayout(description_layout)

        data_layout = QVBoxLayout()
        data_label = QLabel("Table Data")
        data_label.setFont(QFont("Arial", 16))
        data_label.setStyleSheet("color: #fff;")

        self.data_table = QTableWidget(self)
        self.data_table.setRowCount(len(table_data))
        self.data_table.setColumnCount(len(table_data[0]) if table_data else 0)

        for row, data in enumerate(table_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(row, col, item)

        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.setShowGrid(True)
        self.data_table.setFrameShape(QFrame.Box)
        self.data_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #222;
                color: #fff;
                border: 1px solid #555;
            }
            QTableWidget::item {
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #333;
                color: #fff;
            }
        """
        )

        data_layout.addWidget(data_label)
        data_layout.addWidget(self.data_table)

        data_widget = QWidget(self)
        data_widget.setLayout(data_layout)

        splitter.addWidget(description_widget)
        splitter.addWidget(data_widget)
        splitter.setSizes([400, 600])

        controls_layout = QHBoxLayout()
        self.table_combobox = QComboBox(self)
        self.table_combobox.addItems(available_tables)
        self.table_combobox.currentTextChanged.connect(self.update_table)
        self.table_combobox.setStyleSheet(
            """
            QComboBox {
                background-color: #222;
                color: #fff;
                border: 1px solid #555;
                padding: 5px;
            }
            QComboBox:hover {
                border-color: #777;
            }
            QComboBox:editable {
                background-color: #444;
            }
        """
        )

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search table...")
        self.search_bar.textChanged.connect(self.filter_tables)
        self.search_bar.setStyleSheet(
            """
            QLineEdit {
                background-color: #222;
                color: #fff;
                border: 1px solid #555;
                padding: 5px;
            }
            QLineEdit:focus {
                border-color: #777;
            }
        """
        )

        controls_layout.addWidget(self.search_bar)
        controls_layout.addWidget(self.table_combobox)

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)

        export_button = QPushButton("Export Data", self)
        export_button.setStyleSheet(
            """
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 9px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #444;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """
        )
        export_button.clicked.connect(self.export_data)
        main_layout.addWidget(export_button)

        self.available_tables = available_tables

    def export_data(self):
        """Exports table data to a selected file format."""
        logger.info("Export data process started.")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx);;Text Files (*.txt);;HTML Files (*.html);;SQL Files (*.sql)",
        )
        if not file_path:
            logger.warning("Export cancelled by user.")
            return

        try:
            if file_path.endswith(".csv"):
                self.export_to_csv(file_path)
            elif file_path.endswith(".json"):
                self.export_to_json(file_path)
            elif file_path.endswith(".xlsx"):
                self.export_to_excel(file_path)
            elif file_path.endswith(".txt"):
                self.export_to_text(file_path)
            elif file_path.endswith(".html"):
                self.export_to_html(file_path)
            elif file_path.endswith(".sql"):
                self.export_to_sql(file_path)
            else:
                logger.error("Unsupported file format selected.")
                QMessageBox.warning(self, "Error", "Unsupported file format.")
        except Exception as e:
            logger.error(f"Error during export: {e}")
            QMessageBox.critical(
                self, "Export Failed", f"An error occurred while exporting: {e}"
            )

    def export_to_csv(self, file_path):
        """Exports table data to a CSV file."""
        logger.info(f"Exporting data to CSV: {file_path}")
        if not self.table_data:
            logger.warning("No data available for CSV export.")
            QMessageBox.warning(self, "Export Failed", "No data available for export.")
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                headers = []
                for col in range(self.data_table.columnCount()):
                    header_item = self.data_table.horizontalHeaderItem(col)
                    header_text = (
                        header_item.text() if header_item else f"Column {col+1}"
                    )
                    headers.append(header_text)
                writer.writerow(headers)

                for row in self.table_data:
                    writer.writerow([str(item) for item in row])

            QMessageBox.information(
                self, "Export Successful", f"Data exported to {file_path} successfully."
            )
            logger.info(f"CSV export successful: {file_path}")
        except Exception as e:
            logger.error(f"Error during CSV export: {e}")
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting data: {str(e)}",
            )

    def export_to_json(self, file_path):
        """Exports table data to a JSON file."""
        logger.info(f"Exporting data to JSON: {file_path}")
        if not self.table_data:
            logger.warning("No data available for JSON export.")
            QMessageBox.warning(self, "Export Failed", "No data available for export.")
            return

        try:
            headers = []
            for col in range(self.data_table.columnCount()):
                header_item = self.data_table.horizontalHeaderItem(col)
                header_text = header_item.text() if header_item else f"Column {col+1}"
                headers.append(header_text)

            json_data = [dict(zip(headers, row)) for row in self.table_data]

            with open(file_path, mode="w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4)

            QMessageBox.information(
                self, "Export Successful", f"Data exported to {file_path} successfully."
            )
            logger.info(f"JSON export successful: {file_path}")
        except Exception as e:
            logger.error(f"Error during JSON export: {e}")
            QMessageBox.critical(
                self, "Export Failed", f"An error occurred while exporting: {str(e)}"
            )

    def update_table(self):
        """Updates the description and data based on selected table."""
        selected_table = self.table_combobox.currentText()
        logger.info(f"Updating table to {selected_table or '[No Table Selected]'}")
        if selected_table:
            table_description = self.mysql_manager.get_table_description(selected_table)
            table_data = self.mysql_manager.get_table_data(selected_table)

            self.update_description(table_description)
            self.update_data(table_data)

    def update_description(self, table_description):
        """Update the table description in the left pane."""
        logger.info("Updating table description.")
        self.description_table.setRowCount(len(table_description))
        for row, desc in enumerate(table_description):
            for col, value in enumerate(desc):
                self.description_table.setItem(row, col, QTableWidgetItem(str(value)))

    def update_data(self, table_data):
        """Update the table data in the right pane."""
        logger.info("Updating table data.")
        self.data_table.setRowCount(len(table_data))
        for row, data in enumerate(table_data):
            for col, value in enumerate(data):
                self.data_table.setItem(row, col, QTableWidgetItem(str(value)))

    def filter_tables(self):
        """Filters available tables based on user input in the search bar."""
        search_text = self.search_bar.text().lower()
        filtered_tables = [
            table for table in self.available_tables if search_text in table.lower()
        ]
        self.table_combobox.clear()
        self.table_combobox.addItems(filtered_tables)

    def center_window(self):
        """Center the window on the screen."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
