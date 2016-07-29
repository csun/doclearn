import os
import nltk

from . import constants


nltk_data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        constants.NLTK_DATA_DIR)
nltk.data.path.append(nltk_data_path)

