import os

import nltk
from sklearn import svm
from doclearn.vectorizer import Vectorizer


documentation = {
    'delete': 'Removes the given file from the filesystem',
    'open': 'Opens a file so that you can read it',
    'log_file': 'A file containing all log information',
    'settings_file': 'Has all the settings for the program'
}
code_samples = [
    'delete(log_file)',
    'delete(settings_file)',
    'open(log_file)'
]
phrases = {
    'deletes the log file': [0],
    'removes the log file': [0],
    'deletes the settings file': [1],
    'removes the settings file': [1],
    'deletes a file': [0,1],
    'removes a file': [0,1],

    'opens the log file': [2],
    'opens the file containing the logs': [2],
    'opens a file': [2],
}


classifier = svm.SVC(probability=True)


def train():
    vectorizer = Vectorizer()

    targets = []
    for phrase, related_indices in phrases.iteritems():
        for code_sample_index, code_sample in enumerate(code_samples):
            vectorizer.addMeasurement(
                    code_sample, documentation, phrase)
            targets.append(int(code_sample_index in related_indices))

    vectors_array = vectorizer.toArray()
    classifier.fit(vectors_array, targets)


def testSinglePoint(code, phrase, expected):
    vectorizer = Vectorizer()
    vectorizer.addMeasurement(code, documentation, phrase)
    print 'Testing on (%s, %s)' % (code, phrase)

    if classifier.predict(vectorizer.toArray())[0] == expected:
        print 'PASSED'
    else:
        print 'FAILED'


def test():
    testSinglePoint('open(settings_file)', 'opens the settings file', 1)
    testSinglePoint('open(log_file)', 'opens the settings file', 0)
    testSinglePoint('open(log_file)', 'opens the log file', 1)
    testSinglePoint('open(settings_file)', 'opens a file', 1)
    testSinglePoint('delete(settings_file)', 'opens a file', 0)
    testSinglePoint('delete(settings_file)', 'removes a file', 1)
    testSinglePoint('delete(settings_file)', 'expunges a file', 1)


def main():
    # Sets up nltk so we can find data in the local path
    nltk_data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
    nltk.data.path.append(nltk_data_path)

    train()
    test()

    # TODO go over to test recall / precision or whatever.
    # TODO output the weights

if __name__ == '__main__':
    main()
