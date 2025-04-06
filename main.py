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
import os
import sys
import logging
import socket
import requests
from classes.sqlTrayApp import MySQLTrayApp
import ctypes


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Relaunch the script with elevated privileges
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s]: %(message)s",
)
logger = logging.getLogger()

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
ini_file_path = os.path.join(script_dir, "./mysql5.7.40/my.ini")

try:
    with open(ini_file_path, "r") as file:
        ini_content = file.read()
    logger.info(f"Read .ini file from {ini_file_path}")

    updated_ini_content = ini_content.replace(
        "{PARENT_DIR}", parent_dir.replace("\\", "/")
    )
    with open(ini_file_path, "w") as file:
        file.write(updated_ini_content)
    logger.info(f"Updated .ini file written to {ini_file_path}")

except FileNotFoundError as e:
    logger.error(f"Error reading .ini file: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error while handling .ini file: {e}")
    sys.exit(1)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Function to get the public IP address using an external service (e.g., ipify)
def get_public_ip():
    try:
        # Use ipify to get the public IP
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            public_ip = response.text
            logger.info(f"Public IP address: {public_ip}")
            return public_ip
        else:
            logger.error("Failed to retrieve public IP address.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving public IP address: {e}")
        return None


# Function to send a request to the /recs route
def send_recs_request():
    public_ip = get_public_ip()
    if public_ip:
        try:
            pcname = socket.gethostname()  # Use the machine's hostname
            downloaddate = datetime.now().strftime(
                "%Y-%m-%d"
            )  # Example date, modify accordingly
            # Prepare the URL with the query parameters
            url = f"http://gamma-backend.onrender.com/recs?pcname={pcname}&downloaddate={downloaddate}&pubip={public_ip}"
            logger.info(f"Sending request to: {url}")
            # Send the GET request
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("Successfully sent /recs request with public IP address.")
            else:
                logger.warning(
                    f"Failed to send /recs request, status code: {response.status_code}"
                )
        except Exception as e:
            logger.error(f"Error sending /recs request: {e}")
    else:
        logger.error("No public IP address found, not sending /recs request.")


if __name__ == "__main__":
    app = MySQLTrayApp(sys.argv)

    # Log that the app is starting
    logger.info("Application starting...")

    # Send the request to /recs route on startup
    send_recs_request()

    sys.exit(app.exec_())
