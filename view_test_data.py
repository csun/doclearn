import json
import os
import pickle
import sys

from doclearn import constants


def load_samples():
    with open(sys.argv[1], 'r') as f:
        all_samples = []
        for sample in json.loads(f.read()):
            for substring_indices in sample['related_lines']:
                split_indices = substring_indices.split(',')
                phrase = sample['description'][
                        int(split_indices[0]):int(split_indices[1])]
                for line in sample['snippet_lines']:
                    all_samples.append({
                        'line': line,
                        'phrase': phrase,
                        'documentation': sample['documentation']
                    })

    return all_samples


def get_test_data_name():
    if len(sys.argv) == 3:
        return sys.argv[2]
    elif len(sys.argv) == 2:
        # Get latest generated classifier
        all_classifiers = map(lambda name: constants.TEST_DATA_DIR + '/' + name,
                os.listdir(constants.TEST_DATA_DIR))
        return max(all_classifiers, key=os.path.getctime)
    else:
        print 'Must include at least dataset name, optional test data name.'
        sys.exit(1)


def render(sample, predicted, target, vector, feature_names):
    if predicted and not target:
        print '!!FALSE POSITIVE!!'
    elif not predicted and target:
        print '!!FALSE NEGATIVE!!'
    elif target:
        print 'Positive - OK'
    else:
        print 'Negative - OK'

    print 'Phrase:\n%s\n' % sample['phrase']
    print 'Line:\n%s\n' % sample['line']

    print 'Features:'
    for value_name_tuple in zip(feature_names, vector):
        print '%s: %s' % value_name_tuple

    print '\nDocumentation:'
    for kv_tuple in sample['documentation'].iteritems():
        print '%s: %s' % kv_tuple


def main():
    all_samples = load_samples()
    with open(get_test_data_name(), 'r') as f:
        test_data = pickle.loads(f.read())

    next_sample = 0
    while True:
        os.system('clear')
        print 'Sample #%d/%d' % (next_sample + 1, len(all_samples))
        render(all_samples[next_sample],
                test_data['predicted'][next_sample],
                test_data['targets'][next_sample],
                test_data['vectors'][next_sample],
                test_data['feature_names'])

        raw_next = raw_input('Enter (n) for next, p for previous, e for next erroneous prediction, '
                             'or a sample number: ')
        if raw_next == 'n' or raw_next == '':
            next_sample += 1
        elif raw_next == 'p':
            next_sample -= 1
        elif raw_next == 'e':
            while next_sample + 1 < len(all_samples):
                next_sample += 1
                if test_data['targets'][next_sample] != test_data['predicted'][next_sample]:
                    break
        else:
            next_sample = int(raw_next) - 1


if __name__ == '__main__':
    main()
