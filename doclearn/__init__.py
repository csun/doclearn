import os
import nltk

from . import constants


if constants.NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.append(constants.NLTK_DATA_DIR)
