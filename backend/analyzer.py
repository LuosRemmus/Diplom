import datetime

from string import punctuation
from pymystem3 import Mystem

from backend.deploy.config import FILTER_WORDS, KEYWORDS


class Analyzer:
    def __init__(self, sentence: str, unixtime: int, keywords: list):
        self.sentence = sentence
        self.lemm_sentence = self.lemmatizer()
        self.unixtime = unixtime
        self.keywords = keywords

    def is_unixtime_today(self):
        today = datetime.datetime.utcnow().date()
        unixtime_date = datetime.datetime.fromtimestamp(self.unixtime).date()
        return today == unixtime_date

    def lemmatizer(self) -> str:
        mystem = Mystem()
        lemmas = mystem.lemmatize(self.sentence)
        return ' '.join(
            [lemma for lemma in lemmas if
             lemma != ' ' and lemma.strip() not in punctuation and lemma not in FILTER_WORDS])

    def is_contains_keywords(self) -> bool:
        for keyword in self.keywords:
            if keyword in self.lemm_sentence.lower():
                return True
        return False
