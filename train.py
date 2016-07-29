import json
import os
import pickle
import sys
import time

import nltk
from sklearn import svm
from doclearn.vectorizer import Vectorizer


OUTPUT_DIR = 'trained_classifiers'
VERSION_NUMBER = '0.1'


def load_samples():
    if len(sys.argv) != 2:
        print 'Please pass the samples filename as an argument to this script.'
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        return json.loads(f.read())


def train(classifier, samples):
    all_vectors = []
    all_targets = []

    for sample in samples:
        vectorizer = Vectorizer(sample['description'],
                                sample['documentation'],
                                sample['snippet_lines'])

        for substring_indices in sample['related_lines']:
            split_substring_indices = substring_indices.split(',')

            all_vectors.extend(vectorizer.generateVectorsForDescriptionSubstring(
                    int(split_substring_indices[0]),
                    int(split_substring_indices[1])))
            all_targets.extend(generate_targets(
                    len(sample['snippet_lines']),
                    sample['related_lines'][substring_indices]))

    classifier.fit(all_vectors, all_targets)


def generate_targets(line_count, related_lines):
    targets = []

    for i in range(line_count):
        if i in related_lines:
            targets.append(1)
        else:
            targets.append(0)

    return targets


def save(classifier):
    output_filename = '%s/classifier_%s_%d' % (
            OUTPUT_DIR, VERSION_NUMBER, time.time())
    with open(output_filename, 'w') as f:
        f.write(pickle.dumps(classifier))


def main():
    # Sets up nltk so we can find data in the local path
    nltk_data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
    nltk.data.path.append(nltk_data_path)

    samples = load_samples()

    classifier = svm.SVC(probability=True)

    train(classifier, samples)
    save(classifier)


if __name__ == '__main__':
    main()
