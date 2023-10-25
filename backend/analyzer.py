import datetime

from string import punctuation
from pymystem3 import Mystem

from backend.config import KEYWORDS, FILTER_WORDS


def is_unixtime_today(unixtime: int):
    today = datetime.datetime.utcnow().date()
    unixtime_date = datetime.datetime.fromtimestamp(unixtime).date()
    return today == unixtime_date


def lemmatizer(sentence: str) -> str:
    mystem = Mystem()
    lemmas = mystem.lemmatize(sentence)
    return ' '.join(
        [lemma for lemma in lemmas if lemma != ' ' and lemma.strip() not in punctuation and lemma not in FILTER_WORDS])


def is_contains_keywords(sentence: str) -> bool:
    for keyword in KEYWORDS:
        if keyword in sentence.lower():
            print(keyword)
            return True
    return False


def is_target_text(sentence: str):
    lemmatized_sentence = lemmatizer(sentence)
    return is_contains_keywords(lemmatized_sentence)
