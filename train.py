import sys

from doclearn import learning
from doclearn.loader import Loader


def main():
    if len(sys.argv) != 2:
        print 'Please pass the samples filename as an argument to this script.'
        sys.exit(1)

    loader = Loader(sys.argv[1])

    classifier = learning.create_classifier()
    classifier.fit(loader.vectors, loader.targets)

    learning.save_classifier(classifier)


if __name__ == '__main__':
    main()
