import datetime

from string import punctuation
from pymystem3 import Mystem

from backend.schemas.flag import Flag
from backend.deploy.config import FILTER_WORDS, FLAGS


class Analyzer:
    def __init__(self, sentence: str):
        self.sentence: str = sentence

    @staticmethod
    def is_unixtime_today(unixtime):
        today = datetime.datetime.utcnow().date()
        unixtime_date = datetime.datetime.fromtimestamp(unixtime).date()
        return today == unixtime_date

    def lemmatizer(self) -> str:
        mystem = Mystem()
        lemmas = mystem.lemmatize(self.sentence)
        return ' '.join(
            [lemma for lemma in lemmas if
             lemma != ' ' and lemma.strip() not in punctuation and lemma not in FILTER_WORDS])

    def check_for_flag(self) -> Flag | None:
        lemmatized_sentence = self.lemmatizer().lower()

        for redflag in FLAGS["redflags"]:
            if redflag in lemmatized_sentence:
                return Flag.redflag
        else:
            yellowflags_count = 0
            for yellowflag in FLAGS["yellowflags"]:
                if yellowflag in lemmatized_sentence:
                    yellowflags_count += 1
                if yellowflags_count > 5:
                    return Flag.yellowflag
            else:
                return None
