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
import logging
import psutil
import platform
import socket
import pymysql
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QFrame,
    QTableWidgetItem,
    QDesktopWidget,
    QLabel,
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

logger = logging.getLogger()


class MetricsFetcherThread(QThread):
    """Thread for fetching performance metrics without blocking the main UI thread."""

    metrics_fetched = pyqtSignal(dict)

    def run(self):
        metrics = {}

        metrics["Server Uptime"] = self.get_server_uptime()
        metrics["Active Connections"] = self.get_threads_connected()
        metrics["Slow Queries"] = self.get_slow_queries()
        metrics["Queries Per Second (QPS)"] = self.get_queries_per_second()
        metrics["Open Tables"] = self.get_open_tables()

        metrics["CPU Usage"] = f"{self.get_cpu_usage()}%"
        metrics["CPU Core Usage"] = self.get_cpu_core_usage()
        metrics["Architecture"] = self.get_architecture()
        metrics["Operating System"] = self.get_os()
        metrics["Hostname"] = self.get_hostname()
        metrics["System Uptime"] = self.get_system_uptime()
        metrics["Memory Usage"] = self.get_memory_usage()
        metrics["Disk I/O"] = self.get_disk_io()
        metrics["Network Traffic"] = self.get_network_traffic()

        self.metrics_fetched.emit(metrics)

    def get_server_uptime(self):
        try:
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="mysql"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW STATUS WHERE `Variable_name` = 'Uptime';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            uptime = int(result[1]) if result else 0
            logger.debug(f"Fetched server uptime: {uptime} seconds.")
            return f"{uptime} seconds"
        except pymysql.MySQLError as e:
            logger.error(f"Failed to fetch server uptime: {e}")
            return "SQL console must be opened to view this metric."

    def get_threads_connected(self):
        """Get the number of threads connected to MySQL."""
        try:
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="mysql"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW STATUS WHERE `Variable_name` = 'Threads_connected';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            logger.debug(f"Fetched threads connected: {result[1] if result else 'N/A'}")
            return result[1] if result else "N/A"
        except pymysql.MySQLError as e:
            logger.error(f"Failed to fetch threads connected: {e}")
            return "SQL console must be opened to view this metric."

    def get_slow_queries(self):
        """Get the number of slow queries."""
        try:
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="mysql"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW STATUS WHERE `Variable_name` = 'Slow_queries';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            logger.debug(
                f"Fetched slow queries count: {result[1] if result else 'N/A'}"
            )
            return result[1] if result else "N/A"
        except pymysql.MySQLError as e:
            logger.error(f"Failed to fetch slow queries count: {e}")
            return "SQL console must be opened to view this metric."

    def get_queries_per_second(self):
        """Get queries per second (QPS)."""
        try:
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="mysql"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW STATUS WHERE `Variable_name` = 'Queries';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            total_queries = int(result[1]) if result else 0
            qps = total_queries / 60
            logger.debug(f"Fetched queries per second: {qps:.2f} QPS")
            return f"{qps:.2f} QPS"
        except pymysql.MySQLError as e:
            logger.error(f"Failed to fetch queries per second: {e}")
            return "SQL console must be opened to view this metric."

    def get_open_tables(self):
        """Get the number of open tables in MySQL."""
        try:
            connection = pymysql.connect(
                host="localhost", user="root", password="", database="mysql"
            )
            cursor = connection.cursor()
            cursor.execute("SHOW STATUS WHERE `Variable_name` = 'Open_tables';")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            logger.debug(f"Fetched open tables count: {result[1] if result else 'N/A'}")
            return result[1] if result else "N/A"
        except pymysql.MySQLError as e:
            logger.error(f"Failed to fetch open tables count: {e}")
            return "SQL console must be opened to view this metric."

    def get_cpu_usage(self):
        """Get the CPU usage of the server."""
        cpu_usage = psutil.cpu_percent(interval=1)
        logger.debug(f"Fetched CPU usage: {cpu_usage}%")
        return cpu_usage

    def get_cpu_core_usage(self):
        """Get CPU usage per core."""
        core_usage = [f"{x}%" for x in psutil.cpu_percent(interval=1, percpu=True)]
        logger.debug(f"Fetched CPU core usage: {core_usage}")
        return core_usage

    def get_architecture(self):
        """Get system architecture."""
        architecture = platform.architecture()[0]
        logger.debug(f"Fetched system architecture: {architecture}")
        return architecture

    def get_os(self):
        """Get the operating system."""
        os_info = platform.system()
        logger.debug(f"Fetched operating system: {os_info}")
        return os_info

    def get_hostname(self):
        """Get the hostname of the machine."""
        hostname = socket.gethostname()
        logger.debug(f"Fetched hostname: {hostname}")
        return hostname

    def get_system_uptime(self):
        """Get the system uptime."""
        boot_time = psutil.boot_time()
        system_uptime = self.format_uptime(boot_time)
        logger.debug(f"Fetched system uptime: {system_uptime}")
        return system_uptime

    def format_uptime(self, timestamp):
        """Convert timestamp to a human-readable format."""
        from datetime import datetime

        current_time = datetime.now()
        uptime = current_time - datetime.fromtimestamp(timestamp)
        return str(uptime).split(".")[0]

    def get_memory_usage(self):
        """Get the system memory usage."""
        memory = psutil.virtual_memory()
        logger.debug(f"Fetched memory usage: {memory.percent}%")
        return f"{memory.percent}%"

    def get_disk_io(self):
        """Get the disk I/O stats."""
        disk_io = psutil.disk_io_counters()
        logger.debug(
            f"Fetched disk I/O: Read: {disk_io.read_bytes / (1024**2):.2f} MB, Write: {disk_io.write_bytes / (1024**2):.2f} MB"
        )
        return f"Read: {disk_io.read_bytes / (1024**2):.2f} MB, Write: {disk_io.write_bytes / (1024**2):.2f} MB"

    def get_network_traffic(self):
        """Get the network traffic (sent and received bytes)."""
        net_io = psutil.net_io_counters()
        logger.debug(
            f"Fetched network traffic: Sent: {net_io.bytes_sent / (1024**2):.2f} MB, Received: {net_io.bytes_recv / (1024**2):.2f} MB"
        )
        return f"Sent: {net_io.bytes_sent / (1024**2):.2f} MB, Received: {net_io.bytes_recv / (1024**2):.2f} MB"


class MetricsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Performance Metrics")
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.setGeometry(400, 200, 800, 600)
        self.center_window()
        self.apply_theme()
        self.header_label = QLabel("Performance Metrics")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setFont(QFont("Arial", 18, QFont.Bold))

        self.metrics_table = QTableWidget(self)
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.setRowCount(0)
        self.metrics_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #333;
                color: white;
                border: none;
                gridline-color: #444;
                font-size: 14px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #333; /* Match table background */
                color: white; /* Text color for headers */
                padding: 4px;
                font-weight: bold;
                border: none; /* Remove header border */
            }
            QTableWidget::item:alternate {
                background-color: #444; /* Slightly lighter background for alternating rows */
            }
        """
        )

        self.metrics_table.setAlternatingRowColors(True)
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.horizontalHeader().setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.header_label)
        layout.addWidget(self.metrics_table)
        self.setLayout(layout)

        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        self.metrics_table.setColumnWidth(0, 300)
        self.metrics_table.setColumnWidth(1, 450)
        self.metrics_table.setSelectionMode(QTableWidget.NoSelection)
        self.metrics_table.setFrameStyle(QFrame.NoFrame)

        self.fetcher_thread = MetricsFetcherThread()
        self.fetcher_thread.metrics_fetched.connect(self.update_metrics_table)
        self.fetcher_thread.start()

    def apply_theme(self):
        """Apply the dark theme to the window."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #222;
                border: 1px solid #444;
                border-radius: 10px;
            }
        """
        )
        self.setFont(QFont("Arial", 12))

    def center_window(self):
        """Center the window on the screen."""
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

    def update_metrics_table(self, metrics):
        """Update the table with the fetched metrics."""
        self.metrics_table.setRowCount(0)

        for row, (metric, value) in enumerate(metrics.items()):
            self.metrics_table.insertRow(row)
            metric_item = QTableWidgetItem(metric)
            value_item = QTableWidgetItem(str(value))

            metric_item.setForeground(QColor("white"))
            value_item.setForeground(QColor("white"))
            metric_item.setFlags(Qt.ItemIsEnabled)
            value_item.setFlags(Qt.ItemIsEnabled)

            self.metrics_table.setItem(row, 0, metric_item)
            self.metrics_table.setItem(row, 1, value_item)


if __name__ == "__main__":
    app = QApplication([])
    window = MetricsWindow()
    window.show()
    app.exec_()
