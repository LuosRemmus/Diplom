import json

from dotenv import load_dotenv
from os import environ

load_dotenv()

ACCESS_TOKEN = environ.get("ACCESS_TOKEN")
API_VERSION = environ.get("API_VERSION")

API_ID = int(environ.get("API_ID"))
API_HASH = environ.get("API_HASH")
SESSION_NAME = environ.get("SESSION_NAME")

with open("data_files/filterwords.txt", encoding="utf-8") as file:
    FILTER_WORDS = [line.strip() for line in file.readlines()]

with open("data_files/flags.json", encoding="utf-8") as file:
    FLAGS = json.load(file)
