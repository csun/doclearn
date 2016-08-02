import pickle
import time

from sklearn import naive_bayes

from . import constants


def create_classifier():
    return naive_bayes.GaussianNB()

def save_classifier(classifier):
    output_filename = '%s/classifier_%s_%d' % (
            constants.CLASSIFIER_DIR, constants.VERSION_NUMBER,
            time.time())
    with open(output_filename, 'w') as f:
        f.write(pickle.dumps(classifier))

def load_classifier(filename):
    with open(filename, 'r') as f:
        return pickle.loads(f.read())
