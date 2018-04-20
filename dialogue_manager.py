import os

import pip

pip.main(['install', 'sklearn'])
pip.main(['install', 'chatterbot'])
pip.main(['install', 'numpy'])

from sklearn.metrics.pairwise import pairwise_distances_argmin

import numpy as np

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

from utils import text_prepare, load_embeddings, question_to_vec, unpickle_file


class ThreadRanker(object):
    def __init__(self, paths):
        self.word_embeddings, self.embeddings_dim = load_embeddings(paths['WORD_EMBEDDINGS'])
        self.thread_embeddings_folder = paths['THREAD_EMBEDDINGS_FOLDER']

    def __load_embeddings_by_tag(self, tag_name):
        embeddings_path = os.path.join(self.thread_embeddings_folder, tag_name + ".pkl")
        thread_ids, thread_embeddings = unpickle_file(embeddings_path)
        return thread_ids, thread_embeddings

    def get_best_thread(self, question, tag_name):
        """ Returns id of the most similar thread for the question.
            The search is performed across the threads with a given tag.
        """
        thread_ids, thread_embeddings = self.__load_embeddings_by_tag(tag_name)

        # HINT: you have already implemented a similar routine in the 3rd assignment.

        #### YOUR CODE HERE ####
        question_vec = question_to_vec(question, self.word_embeddings, self.embeddings_dim)

        #### YOUR CODE HERE ####
        best_thread = pairwise_distances_argmin(np.array(question_vec).reshape(1, -1), thread_embeddings)[0]

        return thread_ids[best_thread]


class DialogueManager(object):
    def __init__(self, paths):
        # print("Loading resources...")

        # Intent recognition:
        self.intent_recognizer = unpickle_file(paths['INTENT_RECOGNIZER'])
        self.tfidf_vectorizer = unpickle_file(paths['TFIDF_VECTORIZER'])

        self.ANSWER_TEMPLATE = 'I think its about %s\n This thread might help you: ' \
                               'https://stackoverflow.com/questions/%s '

        # Goal-oriented part:
        self.tag_classifier = unpickle_file(paths['TAG_CLASSIFIER'])
        self.thread_ranker = ThreadRanker(paths)

    def create_chitchat_bot(self):
        """Initializes self.chitchat_bot with some conversational model."""

        # Hint: you might want to create and train chatterbot.ChatBot here.

        ########################
        #### YOUR CODE HERE ####
        ########################

        self.chatbot = ChatBot('Training Example')

        # Training chatbot

        # self.chatbot.set_trainer(ChatterBotCorpusTrainer)
        
        # self.chatbot.train("chatterbot.corpus.english")

    def generate_answer(self, question):
        """Combines stackoverflow and chitchat parts using intent recognition."""

        # Recognize intent of the question using `intent_recognizer`.
        # Don't forget to prepare question and calculate features for the question.

        #### YOUR CODE HERE ####
        prepared_question = text_prepare(question)
        #### YOUR CODE HERE ####
        features = self.tfidf_vectorizer.transform([prepared_question])
        #### YOUR CODE HERE ####
        intent = self.intent_recognizer.predict(features)

        # Chit-chat part:   
        if intent == 'dialogue':
            # Pass question to chitchat_bot to generate a response.
            #### YOUR CODE HERE ####
            response = self.chatbot.get_response(question)
            return response.text

        # Goal-oriented part:
        else:
            # Pass features to tag_clasifier to get predictions.
            #### YOUR CODE HERE ####
            tag = self.tag_classifier.predict(features)[0]
            tag = 'c++' if (tag == 'c\c++') else tag
            # Pass prepared_question to thread_ranker to get predictions.
            #### YOUR CODE HERE ####
            thread_id = self.thread_ranker.get_best_thread(prepared_question, tag)

            return self.ANSWER_TEMPLATE % (tag, thread_id)
