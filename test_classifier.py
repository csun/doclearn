import json
import os
import pickle
import sys

from sklearn.metrics import precision_score, recall_score, f1_score

from doclearn import learning
from doclearn import constants
from doclearn.loader import Loader


def save_test_data(filename, loader, predicted):
    test_data = {
        'predicted': predicted,
        'targets': loader.targets,
        'vectors': loader.vectors,
        'feature_names': loader.feature_names
    }
    filename = constants.TEST_DATA_DIR + '/' + filename
    with open(filename, 'w') as f:
        f.write(pickle.dumps(test_data))


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
    save_test_data(classifier_name.split('/')[-1], loader, predicted)

    print 'Predicted %d values.' % len(predicted)
    print 'Precision: %f' % precision_score(loader.targets, predicted)
    print 'Recall: %f' % recall_score(loader.targets, predicted)
    print 'F1 Score: %f' % f1_score(loader.targets, predicted)


if __name__ == '__main__':
    main()
