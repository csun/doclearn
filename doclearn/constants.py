import os


def _absolute_path_from_relative(rel_path):
    return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            rel_path)


VERSION_NUMBER = '0.1'

CLASSIFIER_DIR = _absolute_path_from_relative('model_data/trained')
NLTK_DATA_DIR = _absolute_path_from_relative('model_data/nltk')
SPACY_DATA_DIR = _absolute_path_from_relative('model_data/spacy')
