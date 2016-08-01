import os
import nltk

from . import constants


nltk_data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.pardir,
        constants.NLTK_DATA_DIR)

if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)
