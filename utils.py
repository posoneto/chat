import sys
import nltk
import pickle
import re
import numpy as np

# nltk.download('stopwords')
from nltk.corpus import stopwords


sys.path.append("..")

# Paths for all resources for the bot.
RESOURCE_PATH = {
    'INTENT_RECOGNIZER': 'intent_recognizer.pkl',
    'TAG_CLASSIFIER': 'tag_classifier.pkl',
    'TFIDF_VECTORIZER': 'tfidf_vectorizer.pkl',
    'THREAD_EMBEDDINGS_FOLDER': 'thread_embeddings_by_tags',
    # 'WORD_EMBEDDINGS': 'word_embeddings.tsv',
    'WORD_EMBEDDINGS': 'data/modelSaveFile.tsv',
    'CHATBOT_TRAINED': 'chatbot_trained.pkl'
}


def text_prepare(text):
    """Performs tokenizing and simple prepossessing."""

    replace_by_space_re = re.compile('[/(){}\[\]\|@,;]')
    good_symbols_re = re.compile('[^0-9a-z #+_]')
    stopwords_set = set(stopwords.words('english'))

    text = text.lower()
    text = replace_by_space_re.sub(' ', text)
    text = good_symbols_re.sub('', text)
    text = ' '.join([x for x in text.split() if x and x not in stopwords_set])

    return text.strip()


def load_embeddings(embeddings_path):
    """Loads pre-trained word embeddings from tsv file.

    Args:
      embeddings_path - path to the embeddings file.

    Returns:
      embeddings - dict mapping words to vectors;
      embeddings_dim - dimension of the vectors.
    """

    # Hint: you have already implemented a similar routine in the 3rd assignment.
    # Note that here you also need to know the dimension of the loaded embedings.

    ########################
    #### YOUR CODE HERE ####
    ########################

    # pass

    starspace_embeddings = {}
    for line in open(embeddings_path, encoding='utf-8'):
        w, *d = line.split('\t')
        starspace_embeddings[w] = [float(x) for x in d]

    return starspace_embeddings, len(list(starspace_embeddings.values())[0])


def question_to_vec(question, embeddings, dim):
    """Transforms a string to an embedding by averaging word embeddings.
        
        question: a string
        embeddings: dict where the key is a word and a value is its' embedding
        dim: size of the representation

        result: vector representation for the question
    
    """

    # Hint: you have already implemented exactly this function n the 3rd assignment.

    ########################
    #### YOUR CODE HERE ####
    ########################

    #    pass
    result = np.zeros(dim)
    found = 0.0
    for q in question.split():
        try:
            r = embeddings[q]
            found += 1.0
        except KeyError:
            r = np.zeros(dim)

        result += r

    result = result / found if (found > 0) else result

    return result


def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)
