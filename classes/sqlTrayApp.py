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

import os
import subprocess
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QMessageBox,
    QLabel,
    QWidgetAction,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import time
import logging
from .gammaApp import GammaWindow
from datetime import datetime
from PyQt5.QtGui import QFontDatabase

logger = logging.getLogger()

script_dir = os.path.dirname(os.path.abspath(__file__))
MYSQLD_PATH = os.path.join(
    os.path.dirname(script_dir), "mysql5.7.40", "bin", "mysqld.exe"
)
MYSQL_PATH = os.path.join(
    os.path.dirname(script_dir), "mysql5.7.40", "bin", "mysql.exe"
)

is_running = False
mysqld_process = None
mysql_process = None


class MySQLTrayApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.tray_icon = QSystemTrayIcon(QIcon("assets/tray_stopped.png"), self)
        self.tray_icon.setToolTip("gamma")
        self.create_menu()
        self.tray_icon.show()
        self.gamma_window = None

        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        logger.info("MySQLTrayApp initialized.")

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Left-click
            self.create_menu()
            self.tray_icon.contextMenu().exec_(self.tray_icon.geometry().bottomRight())
        elif reason == QSystemTrayIcon.Context:  # Right-click
            self.tray_icon.setContextMenu(None)
        logger.info(f"Tray icon activated with reason: {reason}")

    def create_menu(self):
        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 10px;  /* Add curved edges */
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
                color: white;
            }
            QMenu::item:selected {
                background-color: #555;
                color: white;
                border-radius: 5px;  /* Smooth selection highlight */
            }
        """
        )

        # Title Section
        title_action = QWidgetAction(menu)
        title_label = QLabel("          gamma          ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet(
            """
            color: white;
            background-color: black;
            border-radius: 10px;
            padding: 5px;
        """
        )
        title_action.setDefaultWidget(title_label)
        menu.addAction(title_action)

        # Open Gamma Action
        open_gamma_action = QAction(">>      Open Gamma     ", self)
        open_gamma_action.triggered.connect(self.open_gamma)
        menu.addAction(open_gamma_action)

        menu.addSeparator()

        # MySQL Console
        mysql_console_action = QAction(">>      MySQL Console     ", self)
        mysql_console_action.triggered.connect(self.open_mysql_console)
        menu.addAction(mysql_console_action)

        menu.addSeparator()

        # Settings Submenu
        settings_menu = menu.addMenu(">>      Settings     ")
        open_logs_action = QAction("Open Logs", self)
        open_logs_action.triggered.connect(self.open_logs)
        mysql_config_action = QAction("MySQL Config", self)
        mysql_config_action.triggered.connect(self.open_mysql_config)
        settings_menu.addAction(open_logs_action)
        settings_menu.addAction(mysql_config_action)

        menu.addSeparator()

        # Credits Submenu
        credits_menu = menu.addMenu(">>      Credits     ")
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.open_help)
        licenses_action = QAction("Licenses", self)
        licenses_action.triggered.connect(self.open_licenses)
        website_action = QAction("Website", self)
        website_action.triggered.connect(self.open_website)
        credits_action = QAction("Credits", self)
        credits_action.triggered.connect(self.show_credits)
        credits_menu.addAction(help_action)
        credits_menu.addAction(licenses_action)
        credits_menu.addAction(website_action)
        credits_menu.addAction(credits_action)

        menu.addSeparator()

        close_window = QAction(">>      Close Gamma     ", self)
        close_window.triggered.connect(self.exit_app)
        menu.addAction(close_window)

        menu.addSeparator()

        now = datetime.now()
        current_day_date = now.strftime("%d %b, %Y")

        footer_action = QWidgetAction(menu)
        footer_label = QLabel(
            f"      gamma by AlmightyNan, © {datetime.now().year} - {datetime.now().year + 1}      "
        )
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Arial", 9, QFont.StyleItalic))
        footer_label.setStyleSheet(
            """
            color: #888888;
            background-color: #1e1e1e;
            padding: 5px;
        """
        )
        footer_action.setDefaultWidget(footer_label)
        menu.addAction(footer_action)

        self.tray_icon.setContextMenu(menu)

    def open_mysql_console(self):
        try:
            subprocess.Popen(
                [MYSQLD_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            subprocess.Popen(
                ["start", "cmd", "/k", MYSQL_PATH, "-u", "root", "-p"], shell=True
            )
            logger.info("MySQL Console opened.")
        except Exception as e:
            logger.error(f"Failed to open MySQL Console: {e}")
            QMessageBox.critical(None, "Error", f"Failed to open MySQL Console: {e}")

    def open_logs(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            logs_path = os.path.join(parent_dir, "debug.log")
            os.startfile(logs_path)
            logger.info("Logs folder opened.")
        except Exception as e:
            logger.error(f"Failed to open logs: {e}")
            QMessageBox.critical(None, "Error", f"Failed to open logs: {e}")

    def open_mysql_config(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            ini_file_path = os.path.join(parent_dir, "./mysql5.7.40/my.ini")
            os.startfile(ini_file_path)
            logger.info("MySQL configuration file opened.")
        except Exception as e:
            logger.error(f"Failed to open MySQL configuration: {e}")
            QMessageBox.critical(
                None, "Error", f"Failed to open MySQL configuration: {e}"
            )

    def open_help(self):
        try:
            import webbrowser

            webbrowser.open("https://gamma.almightynan.cc/help.html")
            logger.info("Website opened (help site).")
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to open website. Visit https://gamma.almightynan.cc/help.html manually. Apologies for the inconvenience.",
            )
            logger.error(f"Failed to open website: {e}")

    def open_licenses(self):
        try:
            import webbrowser

            webbrowser.open("https://gamma.almightynan.cc/license.html")
            logger.info("Website opened (license site).")
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to open website. Visit https://gamma.almightynan.cc/license.html manually. Apologies for the inconvenience.",
            )
            logger.error(f"Failed to open website: {e}")

    def open_website(self):
        try:
            import webbrowser

            webbrowser.open(
                "https://gamma.almightynan.cc",
            )
            logger.info("Website opened (main site).")
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to open website. Visit https://gamma.almightynan.cc manually. Apologies for the inconvenience.",
            )
            logger.error(f"Failed to open website: {e}")

    def show_credits(self):
        try:
            import webbrowser

            webbrowser.open("https://gamma.almightynan.cc/credits.html")
            logger.info("Website opened (credits site).")
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to open website. Visit https://gamma.almightynan.cc/credits.html manually. Apologies for the inconvenience.",
            )
            logger.error(f"Failed to open website: {e}")

    def start_mysql(self):
        global is_running, mysqld_process, mysql_process
        if not is_running:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                mysql_base_dir = os.path.join(
                    os.path.dirname(script_dir), "mysql5.7.40", "bin"
                )
                mysqld_path = os.path.join(mysql_base_dir, "mysqld.exe")
                mysql_path = os.path.join(mysql_base_dir, "mysql.exe")
                subprocess.Popen(
                    [mysqld_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                subprocess.Popen(
                    ["start", "cmd", "/k", mysql_path, "-u", "root", "-p"],
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                logger.info("MySQL server started.")
                self.tray_icon.setIcon(QIcon("assets/tray_running.png"))
                is_running = True
            except Exception as e:
                logger.error(f"Failed to start MySQL: {e}")
                QMessageBox.critical(None, "Error", f"Failed to start MySQL: {e}")
        else:
            logger.info("MySQL server is already running.")

    def stop_mysql(self):
        global is_running, mysqld_process, mysql_process
        if is_running:
            try:
                if mysqld_process:
                    mysqld_process.terminate()
                    mysqld_process.wait()

                if mysql_process:
                    os.system("taskkill /F /T /IM cmd.exe")

                logger.info("MySQL server stopped.")
                self.tray_icon.setIcon(QIcon("assets/tray_stopped.png"))
                is_running = False
            except Exception as e:
                logger.error(f"Failed to stop MySQL: {e}")
                QMessageBox.critical(None, "Error", f"Failed to stop MySQL: {e}")
        else:
            logger.info("MySQL server is not running.")

    def open_gamma(self):
        if not self.gamma_window:
            self.gamma_window = GammaWindow()
        self.gamma_window.show()
        logger.info("Gamma window opened.")

    def exit_app(self):
        self.stop_mysql()
        logger.info("Exiting application.")
        sys.exit()

    def closeEvent(self, event):
        event.ignore()
        self.tray_icon.showMessage("gamma", "Click on tray icon to quit or exit.")
        logger.info("Close event triggered, application continues running in tray.")
