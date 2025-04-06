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

from datetime import datetime
import json
import os
import socket
import sys
import subprocess
import pymysql
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QDesktopWidget,
    QMessageBox,
    QListWidget,
    QLabel,
    QHBoxLayout,
    QCheckBox,
    QListWidgetItem,
    QLineEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QMessageBox,
    QSizePolicy,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QMessageBox,
    QLabel,
    QSpacerItem,
)
from PyQt5.QtCore import Qt, QDateTime
import psutil
import logging

import requests
from classes.pages.adminDashboard import AdminDashboard
from classes.pages.metricsWindow import MetricsWindow
from classes.pages.sqlDetailsWindow import TableDetailsWindow
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTime

API_URL = "https://free-chatgpt-api.p.rapidapi.com/chat-completion-one"
API_HEADERS = {
    "x-rapidapi-key": "b9e9dcda9bmsh796ec3704f15252p130e4cjsn07aa203b0e20",
    "x-rapidapi-host": "free-chatgpt-api.p.rapidapi.com",
}


class MySQLManagementWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MySQL Management")
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.setGeometry(400, 200, 600, 400)
        self.center_window()
        self.databases_list = QListWidget(self)
        self.tables_list = QListWidget(self)
        self.label_databases = QLabel(
            "Select a database and a list of tables will appear."
        )
        self.label_databases.setFont(QFont("Arial", 10, QFont.Bold))
        self.label_databases.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.show_builtin_checkbox = QCheckBox("Show SQL Built-in Databases?", self)
        self.show_builtin_checkbox.setChecked(False)
        self.show_builtin_checkbox.stateChanged.connect(self.load_databases)
        self.databases_list.clicked.connect(self.load_tables)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        layout = QVBoxLayout()
        db_layout = QHBoxLayout()
        db_layout.addWidget(self.databases_list)
        db_layout.addWidget(self.tables_list)

        layout.addWidget(self.label_databases)
        layout.addLayout(db_layout)
        layout.addWidget(self.show_builtin_checkbox)

        self.setLayout(layout)
        self.connection = None
        self.load_databases()
        self.open_table_button = QPushButton("Open Table", self)
        self.open_table_button.setEnabled(False)
        self.open_table_button.clicked.connect(self.open_table_details)

        layout.addWidget(self.open_table_button)
        self.tables_list.itemSelectionChanged.connect(self.toggle_open_button)
        self.custom_button_styles()

    def custom_button_styles(self):
        """Apply custom styling to buttons."""
        self.open_table_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;  /* Green */
                font-size: 12px;   
                color: white;
                padding: 8px;
                border-radius: 8px;
                border: 1px solid #45a049;  /* Darker green border */
            }
            QPushButton:hover {
                background-color: #45a049;  /* Darker green on hover */
            }
            QPushButton:pressed {
                background-color: #388E3C;  /* Even darker green on press */
            }
        """
        )
        self.show_builtin_checkbox.setStyleSheet(
            """
            QCheckBox {
                font-size: 14px;
                color: #ffffff;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """
        )

    def center_window(self):
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

    def connect_to_mysql(self):
        """Establish a persistent connection to MySQL."""
        try:
            if self.connection is None or not self.connection.open:
                self.connection = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="",
                )
            logging.debug("MySQL connection established using PyMySQL.")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to MySQL:\n{e}")
            logging.error(f"MySQL connection error: {e}")
            self.connection = None

    def load_databases(self):
        """Load the list of databases."""
        self.connect_to_mysql()
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SHOW DATABASES;")
                databases = cursor.fetchall()

                self.databases_list.clear()

                show_builtin = self.show_builtin_checkbox.isChecked()
                for db in databases:
                    db_name = db[0]
                    item = QListWidgetItem(db_name)

                    if db_name in [
                        "information_schema",
                        "performance_schema",
                        "mysql",
                        "sys",
                    ]:
                        item.setBackground(Qt.black)
                        item.setForeground(Qt.yellow)
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        item.setToolTip(f"{db_name} is a built-in MySQL database.")

                        if not show_builtin:
                            continue

                    self.databases_list.addItem(item)

                cursor.close()
                logging.debug("Databases loaded successfully.")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Error", f"Failed to load databases:\n{e}")
                logging.error(f"Error loading databases: {e}")

    def load_tables(self):
        """Load tables from the selected database."""
        selected_item = self.databases_list.currentItem()
        if not selected_item:
            logging.warning("No database selected.")
            return

        selected_database = selected_item.text()
        self.connect_to_mysql()
        if self.connection:
            try:
                self.connection.select_db(selected_database)
                cursor = self.connection.cursor()
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()

                self.tables_list.clear()
                for table in tables:
                    self.tables_list.addItem(table[0])

                cursor.close()
                logging.debug(f"Tables loaded for database: {selected_database}")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Error", f"Failed to load tables:\n{e}")
                logging.error(f"Error loading tables for {selected_database}: {e}")

    def toggle_open_button(self):
        """Enable or disable the 'Open Table' button based on table selection."""
        if self.tables_list.selectedItems():
            self.open_table_button.setEnabled(True)
        else:
            self.open_table_button.setEnabled(False)

    def open_table_details(self):
        """Open the window showing details of the selected table."""
        selected_item = self.tables_list.currentItem()
        if selected_item:
            table_name = selected_item.text()
            available_tables = [
                self.tables_list.item(i).text() for i in range(self.tables_list.count())
            ]

            table_details_window = TableDetailsWindow(
                table_name,
                self.get_table_description(table_name),
                self.get_table_data(table_name),
                available_tables,
                self,
                self,
            )
            table_details_window.show()

    def get_table_description(self, table_name):
        """Query the database to get the description of the table (e.g., field, type, etc.)."""
        query = f"DESCRIBE {table_name};"
        return self.execute_query(query)

    def get_table_data(self, table_name):
        """Query the database to get the data from the table."""
        query = f"SELECT * FROM {table_name};"
        return self.execute_query(query)

    def execute_query(self, query):
        """Execute a query on the MySQL database and return the results."""
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def closeEvent(self, event):
        """Ensure the connection is closed when the window is closed."""
        if self.connection:
            self.connection.close()
        event.accept()


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login as Admin")
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.setGeometry(400, 300, 300, 200)
        self.center_window()
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.username_field = QLabel("Username:", self)
        self.username_input = QLineEdit(self)
        self.password_field = QLabel("Password:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.username_field)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_field)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)
        self.custom_ui_styles()

    def custom_ui_styles(self):
        """Apply simple, clean styles to the login window components."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #000000;  /* Light background */
            }
            QLabel {
                font-size: 12px;
                color: #ffffff;
            }
            QLineEdit {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #333;  /* Green button */
                color: white;
                font-size: 12px;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #222;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """
        )

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        response = requests.get(
            "http://gamma-backend.onrender.com/api",
            params={"login": username, "password": password},
        )
        print(response)
        if response.status_code == 200:
            self.parent().current_user = {
                "username": username,
                "login_time": QDateTime.currentDateTime().toString(),
            }
            QMessageBox.information(self, "Logged In", f"Logged in as {username}")
            self.accept()
        elif response.status_code == 401:
            QMessageBox.warning(self, "Error", "Invalid username or password.")
        else:
            QMessageBox.warning(
                self, "Error", "An error occurred. Please try again later."
            )

    def center_window(self):
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)


class ProfileWindow(QDialog):
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Profile")
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.setGeometry(400, 300, 300, 200)
        self.current_user = current_user
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        layout = QVBoxLayout()
        user_info = QLabel(
            f"Username: {current_user['username']}\n"
            f"Logged in at: {current_user['login_time']}"
        )
        user_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(user_info)

        logout_button = QPushButton("Logout", self)
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        self.setLayout(layout)
        self.custom_ui_styles()

    def custom_ui_styles(self):
        """Apply simple, clean styles to the profile window components."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #000000;  /* Light background */
            }
            QLabel {
                font-size: 12px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #333;  /* Green button */
                color: white;
                font-size: 12px;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #222;
            }
            QPushButton:pressed {
                background-color: #444;
            }

        """
        )

    def logout(self):
        self.parent().current_user = None
        QMessageBox.information(self, "Logged Out", "You have been logged out.")
        self.accept()


def get_ipv6_address():
    try:
        hostname = socket.gethostname()
        addresses = socket.getaddrinfo(hostname, None)
        for addr in addresses:
            if addr[1] == socket.SOCK_STREAM and addr[0] == socket.AF_INET6:
                return addr[4][0]
    except Exception as e:
        return None


def send_recs_request():
    ipv6_address = get_ipv6_address()
    if ipv6_address:
        try:
            pcname = socket.gethostname()
            url = f"http://gamma-backend.onrender.com/recs?pcname={pcname}&downloaddate={datetime.now().strftime("%Y-%m-%d")}&pubip={ipv6_address}"
            print(pcname, ipv6_address)
            response = requests.get(url)
            if response.status_code == 200:
                pass
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")


class GammaWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gamma")
        send_recs_request()
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("background-color: #111; color: #fff;")
        self.center_window()
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.current_user = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        header_label = QLabel("gamma")
        header_label.setFont(QFont("Arial", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(
            "color: #fff; border-bottom: 2px dashed #555; padding-bottom: 10px;"
        )
        main_layout.addWidget(header_label)

        current_time = QTime.currentTime()
        welcome_label = QLabel()
        if current_time >= QTime(0, 0) and current_time < QTime(8, 0):
            welcome_label.setText("Good morning, human.  Early isn't it?")
        elif current_time >= QTime(8, 0) and current_time < QTime(12, 0):
            welcome_label.setText("Good morning, human.")
        elif current_time >= QTime(12, 0) and current_time < QTime(16, 0):
            welcome_label.setText("Good afternoon, human.")
        elif current_time >= QTime(16, 0) and current_time < QTime(23, 0):
            welcome_label.setText("Good evening, human.")
        else:
            welcome_label.setText("Hey, haven't slept yet?")
        welcome_label.setFont(QFont("Arial", 16))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #aaa;")
        main_layout.addWidget(welcome_label)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        button_style = """
            QPushButton {
                background-color: #222;
                color: #fff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #333;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """

        self.mysql_button = QPushButton("Open MySQL Console")
        self.mysql_button.setStyleSheet(button_style)
        self.mysql_button.clicked.connect(self.start_mysql_and_close)
        button_layout.addWidget(self.mysql_button)

        self.management_button = QPushButton("Open MySQL Management")
        self.management_button.setStyleSheet(button_style)
        self.management_button.clicked.connect(self.open_mysql_management)
        button_layout.addWidget(self.management_button)

        self.metrics_button = QPushButton("View Performance Metrics")
        self.metrics_button.setStyleSheet(button_style)
        self.metrics_button.clicked.connect(self.open_metrics_window)
        button_layout.addWidget(self.metrics_button)

        adminbutton_style = """
            QPushButton {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2a3627;
            }
            QPushButton:pressed {
                background-color: #1e241c;
            }
            QPushButton:disabled {
                background-color: #A9A9A9;  /* Grey color when disabled */
                color: #111;  /* Light grey text when disabled */
            }
        """

        self.admin_button = QPushButton("Admin Dashboard")
        self.admin_button.setStyleSheet(button_style)
        self.admin_button.setEnabled(self.current_user is not None)

        if not self.admin_button.isEnabled():
            self.admin_button.setStyleSheet(adminbutton_style)

        self.admin_button.clicked.connect(self.open_admin_dashboard)
        button_layout.addWidget(self.admin_button)

        self.login_button = QPushButton("Login as admin")
        self.login_button.setStyleSheet(button_style)
        self.login_button.clicked.connect(self.open_login_window)
        button_layout.addWidget(self.login_button)

        self.profile_button = QPushButton(f"🔧 Logged in as admin", self)
        self.profile_button.setStyleSheet(button_style)

        self.profile_button.setIcon(QIcon("path_to_user_icon.png"))
        self.profile_button.clicked.connect(self.open_profile_window)
        self.profile_button.setVisible(False)
        button_layout.addWidget(self.profile_button)

        main_layout.addLayout(button_layout)

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(0)
        footer_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        footer_label = QLabel("--   gamma by almightynan, © 2024 - 2025   --")
        footer_label.setFont(QFont("Arial", 10))
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #555;")
        footer_layout.addWidget(footer_label)

        footer_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        main_layout.addLayout(footer_layout)

        self.setLayout(main_layout)

        self.tray_icon = QSystemTrayIcon(QIcon("path_to_tray_icon.png"), self)
        self.tray_icon.setToolTip("Gamma Application")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.tray_menu = QMenu()
        open_action = QAction("Open Gamma", self)
        open_action.triggered.connect(self.show)
        self.tray_menu.addAction(open_action)

        quit_action = QAction("Exit Gamma", self)
        quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        """Override the close event to minimize to the system tray."""
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    def quit_application(self):
        """Quit the application."""
        # self.tray_icon.hide()
        self.close()
        os._exit(0)

    def center_window(self):
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

    def open_login_window(self):
        login_window = LoginWindow(self)
        if login_window.exec_() == QDialog.Accepted:
            self.login_button.setVisible(False)
            self.profile_button.setVisible(True)
            self.admin_button.setEnabled(True)

    def open_profile_window(self):
        if self.current_user:
            profile_window = ProfileWindow(self.current_user, self)
            if profile_window.exec_() == QDialog.Accepted:
                self.login_button.setVisible(True)
                self.profile_button.setVisible(False)
                self.admin_button.setEnabled(False)

    def open_admin_dashboard(self):
        admin_dashboard = AdminDashboard(self)
        admin_dashboard.exec_()

    def open_metrics_window(self):
        """Open the Performance Metrics window."""
        self.metrics_window = MetricsWindow(self)
        self.metrics_window.show()

    def start_mysql_and_close(self):
        if not self.is_mysql_running():
            self.start_mysql()
        else:
            self.ask_to_force_kill()

    def open_mysql_management(self):
        self.management_window = MySQLManagementWindow(self)
        self.management_window.show()

    def is_mysql_running(self):
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            if "mysql.exe" in proc.info["name"]:
                return proc
        return None

    def start_mysql(self):
        try:
            input_dialog = CustomInputDialog(
                self,
                "MySQL Login",
                """

Enter MySQL username to connect to a user on localhost instance, if       
you are trying to connect to the local server or unsure about what to     
select, just press enter.

""",
                "root",
            )
            center_window(input_dialog)
            if input_dialog.exec() == QDialog.Accepted:
                username = input_dialog.get_input()
            else:
                return

            script_dir = os.path.dirname(os.path.abspath(__file__))
            mysql_base_dir = os.path.join(
                os.path.dirname(script_dir), "mysql5.7.40", "bin"
            )
            mysqld_path = os.path.join(mysql_base_dir, "mysqld.exe")
            mysql_path = os.path.join(mysql_base_dir, "mysql.exe")

            subprocess.Popen(
                [mysqld_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            subprocess.Popen(
                ["start", "cmd", "/k", mysql_path, "-u", username, "-p"],
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

        except Exception as e:
            self.show_custom_message("Error", f"Failed to start MySQL:\n{e}")
            logging.error(f"Failed to start MySQL: {e}")

    def show_custom_message(self, title, message):
        """Show a custom styled message box."""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(
            """
            QMessageBox {
                background-color: #f4f4f9;
            }
            QMessageBox QLabel {
                color: #333;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
            QMessageBox QPushButton:pressed {
                background-color: #388E3C;
            }
        """
        )
        msg.exec_()

    def ask_to_force_kill(self):
        answer = QMessageBox.question(
            self,
            "Force Kill MySQL",
            "MySQL is already running. Do you want to force kill it?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            proc = self.is_mysql_running()
            proc.kill()
            logging.debug("MySQL process killed.")


class CustomInputDialog(QDialog):
    def __init__(
        self, parent=None, title="Input", label_text="Enter Value:", default_text="root"
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(400, 300, 400, 150)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setStyleSheet(
            """
                QDialog {
                background-color: #000000;  /* Light background */
            }
                QLabel {
                font-size: 14px;
                color: #ffffff;
            }
                QLineEdit {
                    background-color: #000000;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 5px;
                    font-size: 12px;
                }
            QPushButton {
                background-color: #333;  /* Green button */
                color: white;
                font-size: 12px;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #222;
            }
            QPushButton:pressed {
                background-color: #444;
            }
            """
        )

        self.input_value = ""

        self.label = QLabel(label_text, self)
        self.input_field = QLineEdit(self)
        self.input_field.setText(default_text)

        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_input(self):
        """Return the input value when the dialog is accepted."""
        return self.input_field.text().strip()


def center_window(self):
    screen_geometry = QDesktopWidget().availableGeometry()
    window_geometry = self.geometry()
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2
    self.move(x, y)


def main():
    app = QApplication(sys.argv)
    gamma_window = GammaWindow()
    gamma_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
