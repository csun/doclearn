import sys
import os

from sklearn.metrics import precision_score, recall_score, f1_score

from doclearn import learning
from doclearn import constants
from doclearn.loader import Loader


def main():
    if len(sys.argv) == 3:
        classifier_name = sys.argv[2]
    elif len(sys.argv) == 2:
        # Get latest generated classifier
        all_classifiers = map(lambda name: constants.CLASSIFIER_DIR + '/' + name,
                os.listdir(constants.CLASSIFIER_DIR))
        classifier_name = max(all_classifiers, key=os.path.getctime)
    else:
        print 'Must include at least dataset name, optional classifier name.'
        sys.exit(1)

    loader = Loader(sys.argv[1])

    print 'Using classifier: %s' % classifier_name
    classifier = learning.load_classifier(classifier_name)

    predicted = classifier.predict(loader.vectors)

    print 'Predicted %d values.' % len(predicted)
    print 'Precision: %d' % precision_score(loader.targets, predicted)
    print 'Recall: %d' % recall_score(loader.targets, predicted)
    print 'F1 Score: %d' % f1_score(loader.targets, predicted)


if __name__ == '__main__':
    main()
