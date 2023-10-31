from os import environ

from dotenv import load_dotenv

"""
По хорошему, для конфигурации есть несколько библиотек

Dynaconf - https://www.dynaconf.com/
Pydantic Settings - https://docs.pydantic.dev/latest/concepts/pydantic_settings/
Traitlets (тут пока сам не очень понял идею, но выглядит интересно) - https://traitlets.readthedocs.io/en/stable/index.html
"""

load_dotenv()

ACCESS_TOKEN = environ.get("ACCESS_TOKEN")
API_VERSION = environ.get("API_VERSION")

with open("data_files/filterwords.txt", encoding="utf-8") as file:
    FILTER_WORDS = [line.strip() for line in file.readlines()]

with open("data_files/keywords.txt", encoding="utf-8") as file:
    KEYWORDS = [line.strip() for line in file.readlines()]
