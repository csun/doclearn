import nltk
import sputnik
import spacy

from doclearn import constants

nltk_packages = ['averaged_perceptron_tagger', 'punkt', 'wordnet']
print 'Installing nltk data to path: %s' % constants.NLTK_DATA_DIR
print 'Downloading the following nltk packages: %s' % nltk_packages

nltk_downloader = nltk.downloader.Downloader(
        download_dir=constants.NLTK_DATA_DIR)
nltk_downloader.download(nltk_packages)


print 'Installing spacy to path: %s' % constants.SPACY_DATA_DIR
sputnik.install('spacy', spacy.about.__version__, 'en_default',
        data_path=constants.SPACY_DATA_DIR)
