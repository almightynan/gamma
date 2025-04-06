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

import logging
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QMessageBox,
    QCheckBox,
    QSizePolicy,
    QLabel,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import requests

API_URL = "https://free-chatgpt-api.p.rapidapi.com/chat-completion-one"
API_HEADERS = {
    "x-rapidapi-key": "b9e9dcda9bmsh796ec3704f15252p130e4cjsn07aa203b0e20",
    "x-rapidapi-host": "free-chatgpt-api.p.rapidapi.com",
}

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)


class AdminDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing Admin Dashboard UI components.")
        self.setWindowTitle("Admin Dashboard")
        self.center_window()
        self.setWindowIcon(QIcon("assets/gamma.ico"))
        self.setGeometry(400, 300, 800, 600)
        self.setStyleSheet("background-color: #111; color: #fff;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        header_label = QLabel("Admin Dashboard")
        header_label.setFont(QFont("Arial", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(
            "color: #fff; border-bottom: 2px dashed #555; padding-bottom: 10px;"
        )
        main_layout.addWidget(header_label)

        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Enter keywords here...")
        self.keyword_input.setStyleSheet(
            "background-color: #222; color: #fff; border: 1px solid #555; border-radius: 5px; padding: 10px; font-size: 14px;"
        )
        main_layout.addWidget(self.keyword_input)

        query_group = QGroupBox("Include SQL Queries")
        query_layout = QFormLayout()

        self.create_query_checkbox = QCheckBox("Include CREATE query?", self)
        self.create_query_checkbox.setChecked(True)
        self.insert_query_checkbox = QCheckBox("Include INSERT query?", self)
        self.insert_query_checkbox.setChecked(True)
        self.update_query_checkbox = QCheckBox("Include UPDATE query?", self)
        self.delete_query_checkbox = QCheckBox("Include DELETE query?", self)
        self.alter_query_checkbox = QCheckBox("Include ALTER query?", self)
        self.drop_query_checkbox = QCheckBox("Include DROP query?", self)

        query_layout.addWidget(self.create_query_checkbox)
        query_layout.addWidget(self.insert_query_checkbox)
        query_layout.addWidget(self.update_query_checkbox)
        query_layout.addWidget(self.delete_query_checkbox)
        query_layout.addWidget(self.alter_query_checkbox)
        query_layout.addWidget(self.drop_query_checkbox)

        query_group.setLayout(query_layout)
        main_layout.addWidget(query_group)

        function_group = QGroupBox("Include SQL Functions")
        function_layout = QFormLayout()

        self.aggregate_checkbox = QCheckBox("Use aggregate functions?", self)
        self.aggregate_checkbox.setChecked(False)
        self.string_functions_checkbox = QCheckBox("Use string functions?", self)
        self.string_functions_checkbox.setChecked(True)
        self.numeric_functions_checkbox = QCheckBox("Use numeric functions?", self)
        self.numeric_functions_checkbox.setChecked(True)
        self.date_functions_checkbox = QCheckBox("Use date functions?", self)
        self.date_functions_checkbox.setChecked(True)

        function_layout.addWidget(self.aggregate_checkbox)
        function_layout.addWidget(self.string_functions_checkbox)
        function_layout.addWidget(self.numeric_functions_checkbox)
        function_layout.addWidget(self.date_functions_checkbox)

        function_group.setLayout(function_layout)
        main_layout.addWidget(function_group)

        rows_columns_group = QGroupBox("Rows and Columns Settings")
        rows_columns_layout = QFormLayout()

        self.rows_input = QSpinBox(self)
        self.rows_input.setRange(1, 50)
        self.rows_input.setValue(10)
        self.columns_input = QSpinBox(self)
        self.columns_input.setRange(1, 50)
        self.columns_input.setValue(5)
        self.detailed_data_checkbox = QCheckBox("Detailed data?", self)

        rows_columns_layout.addRow("Rows:", self.rows_input)
        rows_columns_layout.addRow("Columns:", self.columns_input)
        rows_columns_layout.addRow(self.detailed_data_checkbox)

        rows_columns_group.setLayout(rows_columns_layout)
        main_layout.addWidget(rows_columns_group)

        self.request_button = QPushButton("Get SQL Code", self)
        self.request_button.setStyleSheet(
            """
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
        )
        self.request_button.clicked.connect(self.get_sql_code_from_api)
        main_layout.addWidget(self.request_button)

        self.response_area = QWebEngineView(self)
        self.response_area.settings().setAttribute(
            QWebEngineSettings.JavascriptCanAccessClipboard, True
        )
        self.response_area.settings().setAttribute(
            QWebEngineSettings.JavascriptCanPaste, True
        )
        self.response_area.setMinimumHeight(300)
        self.response_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.response_area)

        self.setLayout(main_layout)

    def center_window(self):
        """Center the window on the screen."""
        screen_geometry = QDesktopWidget().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

    def get_sql_code_from_api(self):
        keywords = self.keyword_input.text().strip()

        if not keywords:
            QMessageBox.warning(
                self, "Input Error", "Please enter some keywords to generate a query."
            )
            logger.warning("Input Error: User did not enter any keywords.")
            return

        selected_queries = []
        if self.create_query_checkbox.isChecked():
            selected_queries.append("CREATE")
        if self.insert_query_checkbox.isChecked():
            selected_queries.append("INSERT")
        if self.update_query_checkbox.isChecked():
            selected_queries.append("UPDATE")
        if self.delete_query_checkbox.isChecked():
            selected_queries.append("DELETE")
        if self.alter_query_checkbox.isChecked():
            selected_queries.append("ALTER")
        if self.drop_query_checkbox.isChecked():
            selected_queries.append("DROP")

        selected_functions = []
        if self.aggregate_checkbox.isChecked():
            selected_functions.append("aggregate functions")
        if self.string_functions_checkbox.isChecked():
            selected_functions.append("string functions")
        if self.numeric_functions_checkbox.isChecked():
            selected_functions.append("numeric functions")
        if self.date_functions_checkbox.isChecked():
            selected_functions.append("date functions")

        num_rows = self.rows_input.value()
        num_columns = self.columns_input.value()
        detailed_data = (
            "detailed" if self.detailed_data_checkbox.isChecked() else "basic"
        )
        querystring = {
            "prompt": f"""
    Your task is to write SQL queries based on the requests. It should never include complex functions and keywords. 
    You will only consider the following clauses to return the query:
    {', '.join(selected_queries)}

    The query you create will only include the following keywords and the following keywords only:
    {keywords}

    You will also meet the following requirements:
    Include queries for {', '.join(selected_functions)}.
    The query will only have {num_rows} rows and {num_columns} columns.
    Include realistic random values when creating the table or inserting the data, preferably assign a name to the table related to the given keywords.
    The data provided will be very {detailed_data} on the given keywords.

    IMPORTANT NOTE: NEVER ADD ANY TEXT, ONLY RETURN THE CODE AS **SEPARATE CODEBLOCKS**. ONLY RETURN CODE RELATED TO THE GIVEN INSTRUCTION SET AND NEVER ADD EXTRA QUERIES. ONLY DO WHAT IS ASKED.
    """
        }

        try:
            logger.info(f"Sending request to API...")
            response = requests.get(API_URL, headers=API_HEADERS, params=querystring)
            response.raise_for_status()

            response_json = response.json()
            if "response" in response_json:
                raw_sql_code = response_json["response"]
                formatted_code = self.format_code_blocks(raw_sql_code)
                self.response_area.setHtml(formatted_code)
                logger.info(f"Received SQL code from API")
            else:
                self.response_area.setHtml(
                    "<p>No valid response from API, contact the developer for help.</p>"
                )
                logger.error("No valid response from API.")
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {e}")

    def format_code_blocks(self, raw_sql_code):
        """
        Parse and format SQL code blocks with HTML and CSS.
        """
        import re

        code_block_pattern = r"```sql(.*?)```"
        matches = re.findall(code_block_pattern, raw_sql_code, re.DOTALL)

        css_style = """
        <style>
            .code-container {
                position: relative;
                background-color: #2d2d2d;
                color: white;
                font-family: monospace;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                overflow: auto;
            }
            .copy-button {
                position: absolute;
                top: 5px;
                right: 5px;
                background: #444;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                cursor: pointer;
                font-size: 12px;
            }
            .code-block {
                margin: 0;
                padding: 10px;
            }
        </style>
        """

        js_script = """
        <script>
            function copyCode(button) {
                const codeElement = button.nextElementSibling;
                const codeText = codeElement.textContent;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(codeText)
                        .then(() => {
                            const originalText = button.textContent;
                            button.textContent = "Copied! ✅";
                            button.disabled = true;
                            setTimeout(() => {
                                button.textContent = originalText;
                                button.disabled = false;
                            }, 4000);
                        })
                        .catch(err => {
                            console.error('failed to copy code: ', err);
                        });
                } else {
                    const textarea = document.createElement('textarea');
                    textarea.value = codeText;
                    document.body.appendChild(textarea);
                    textarea.select();
                    try {
                        document.execCommand('copy');
                        const originalText = button.textContent;
                        button.textContent = "Copied! ✅";
                        button.disabled = true;

                        setTimeout(() => {
                            button.textContent = originalText;
                            button.disabled = false; 
                        }, 4000);
                    } catch (err) {
                        console.error('fallback failed: ', err);
                    }
                    document.body.removeChild(textarea);
                }
            }
        </script>
        """
        html_template = """
        <div class="code-container">
            <button class="copy-button" onclick="copyCode(this)">Copy Code</button>
            <pre class="code-block">{code}</pre>
        </div>
        """
        final_html = "<html><head>" + css_style + js_script + "</head><body>"

        for match in matches:
            sql_code = match.strip()
            formatted_block = html_template.format(code=sql_code)
            final_html += formatted_block

        final_html += "</body></html>"
        return final_html
