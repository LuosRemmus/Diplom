import json

from dotenv import load_dotenv
from os import environ

load_dotenv()

ACCESS_TOKEN = environ.get("ACCESS_TOKEN")
API_VERSION = environ.get("API_VERSION")

with open("data_files/filterwords.txt", encoding="utf-8") as file:
    FILTER_WORDS = [line.strip() for line in file.readlines()]

with open("data_files/keywords.txt", encoding="utf-8") as file:
    FLAGS = json.load(file)
