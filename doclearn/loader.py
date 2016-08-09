import json

from . import constants
from .vectorizer import Vectorizer


class Loader(object):
    """
    Loads data from samples file into a list of vectors and targets.
    """

    def __init__(self, filename):
        with open(filename, 'r') as f:
            self._samples = json.loads(f.read())

        self.feature_names = []
        self.vectors = []
        self.targets = []
        self._processSamples()

    def _processSamples(self):
        for sample in self._samples:
            vectorizer = Vectorizer(sample['description'],
                                    sample['documentation'],
                                    sample['snippet_lines'])

            for substring_indices in sample['related_lines']:
                split_substring_indices = substring_indices.split(',')

                self.vectors.extend(vectorizer.generateVectorsForDescriptionSubstring(
                        int(split_substring_indices[0]),
                        int(split_substring_indices[1])))
                self._generateTargets(sample, substring_indices)

            # NOTE in theory, these should be the same for all vectorizers created.
            self.feature_names = vectorizer.feature_names

    def _generateTargets(self, sample, substring_indices):
        line_count = len(sample['snippet_lines'])
        related_lines = sample['related_lines'][substring_indices]

        for i in range(line_count):
            if i in related_lines:
                self.targets.append(1)
            else:
                self.targets.append(0)
