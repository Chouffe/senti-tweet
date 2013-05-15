#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tokenizer import Tokenizer
import psycopg2
import sys
import csv
import os
import random
import pickle
from sklearn import svm
import time


class ClassifierManager:
    """
    Handle the classifier
    It is possible to train it, to save it and to load it
    """
    def train(self, classifier, training_set):
        """
        Trains the classifier given the training set
        Input: classifier (SVM, ...)
               training_set
        Output: classifier
        """
        classifier.fit(training_set.X, training_set.Y)
        return classifier

    def save(self, classifier, f):
        """
        Saves the classifier into the file f
        Input: Classifier and file f
        Output: None
        """
        pickle.dump(classifier, f)
        return True

    def load(self, f):
        """
        Loads a classifier given the file
        Input: file f
        Output: classifier
        """
        return pickle.load(f)

    def perf(self, classifiers, testingSet):
        """
        Evals the perf of a given testing set over a voting procedure
        Input : list of classifiers
                testingSet
        Output : float (0,100)
        """
        perf = 0
        for i, x in enumerate(testingSet.X):
            if self._vote(classifiers, x) == testingSet.Y[i]:
                perf += 1
        return float(perf) / float(len(testingSet)) * 100.

    def _vote(self, classifiers, x):
        """
        Vote made between the classifiers on the data point x
        Input : List of classifiers
                datapoint x
        Output : {-1,0,1}
        """
        predictions = {'neg': 0, 'neut': 0, 'pos': 0}

        for classifier in classifiers:
            prediction = classifier.predict(x)[0]

            if prediction == -1:
                predictions['neg'] += 1
            elif prediction == 0:
                predictions['neut'] += 1
            else:
                predictions['pos'] += 1

        # print predictions
        result = max(predictions.iterkeys(), key=(lambda k: predictions[k]))
        if result == 'neg':
            return -1
        elif result == 'neut':
            return 0
        else:
            return 1


class SetManager:
    """
    Handles the operation on a set
    """

    def __init__(self, csv_path, tweets_path):
        self.csv_path = csv_path
        self.tweets_path = tweets_path
        self.X, self.Y = [], []
        self.tweets = {'positive': [], 'negative': [], 'neutral': []}

    def load(self, feature_extractor, number_pos, number_neg, number_neut):
        """
        Load into X, Y the data points
        Input  : number of pos/neg/neut tweets
        Output : Set built with X and Y
        """
        l = self._load_csv_set()
        self.tweets['positive'] = self._get_tweets(l['positive'])
        self.tweets['negative'] = self._get_tweets(l['negative'])
        self.tweets['neutral'] = self._get_tweets(l['neutral'])
        self._extract_data_points(feature_extractor, number_pos,
                                  number_neg, number_neut)
        return Set(self.X, self.Y)

    def splitTrainingAndTestingSet(self, s, proportionTrainingSet):
        """
        Splits into training and testing and returns them
        Input  : proportion in the range (0,1) of trainig points
                 s is a set to split
        Output : TrainingSet and TestingSet
        """
        assert proportionTrainingSet >= 0. and proportionTrainingSet <= 1.

        # Shuffle the set s
        s = self._shuffleSet(s)

        # Build training and testing sets
        limit = int(proportionTrainingSet * len(s))

        X_training = s.X[:limit]
        Y_training = s.Y[:limit]
        X_testing = s.X[limit:]
        Y_testing = s.Y[limit:]

        return Set(X_training, Y_training), Set(X_testing, Y_testing)

    def _shuffleSet(self, s):
        """
        Shuffles the set s
        """
        indexes = range(len(s))
        random.shuffle(indexes)

        s.X = [s.X[i] for i in indexes]
        s.Y = [s.Y[i] for i in indexes]
        return s

    def _load_csv_set(self):
        """
        Loads the csv file and store it into a dict
        Input  : void
        Output : return the dict
        """

        result = {'positive': [], 'negative': [], 'neutral': []}

        with open(self.csv_path) as f:

            for row in csv.reader(f, delimiter=',', skipinitialspace=True):
                tweet_id = row[2]
                tweet_polarity = row[1]
                tweet = self.tweets_path + tweet_id + '.json'

                if os.path.exists(tweet):
                    with open(tweet) as json_data:
                        data = json.load(json_data)
                        # Get only the english tweets
                        if 'lang' in data and data['lang'] == 'en':
                            if tweet_polarity == 'positive':
                                result['positive'].append(tweet_id)
                            elif tweet_polarity == 'negative':
                                result['negative'].append(tweet_id)
                            else:
                                result['neutral'].append(tweet_id)
        return result

    def _get_tweets(self, id_list):
        """
        Retrieve the tweets according to their ids in the id_list
        Output: List of strings (List of Tweets)
        """
        result = []
        for tweet_id in id_list:
                tweet = self.tweets_path + tweet_id + '.json'
                if os.path.exists(tweet):
                    with open(tweet) as json_data:
                        data = json.load(json_data)
                        result.append(data['text'])
        return result

    def _shuffle_tweets(self):
        """
        Shuffle the tweets
        """
        random.shuffle(self.tweets['positive'])
        random.shuffle(self.tweets['negative'])
        random.shuffle(self.tweets['neutral'])

    def _extract_data_points(self, feature_extractor, num_pos, num_neg,
                             num_neut, shuffle=True):
        """
        Input: number of pos/neg/neut tweets for the training
        Output: X, Y
        Main function returning the Data Points X, Y
        """
        if shuffle:
            self._shuffle_tweets()

        # Limits the number of tweets
        pos = self.tweets['positive'][:num_pos]
        neg = self.tweets['negative'][:num_neg]
        neut = self.tweets['neutral'][:num_neut]

        # Extracts features from the DB
        X_pos = [feature_extractor.extract(s) for s in pos]
        X_neg = [feature_extractor.extract(s) for s in neg]
        X_neut = [feature_extractor.extract(s) for s in neut]

        Y_pos = [1 for i in xrange(len(X_pos))]
        Y_neut = [0 for i in xrange(len(X_neut))]
        Y_neg = [-1 for i in xrange(len(X_neg))]

        X_pos, Y_pos = self._clean_unrelevant(X_pos, Y_pos)
        X_neg, Y_neg = self._clean_unrelevant(X_neg, Y_neg)

        # Builds X and Y
        X = X_pos + X_neg + X_neut
        Y = Y_pos + Y_neg + Y_neut

        # We clean the non-relevant points
        # print X, len(X)
        # print Y, len(Y)

        self.X = X
        self.Y = Y

    def _clean_unrelevant(self, X, Y):

        to_remove = []
        for i, x in enumerate(X):
            if sum(x) == 0:
                to_remove.append(i)

        _X = [x for i, x in enumerate(X) if i not in to_remove]
        _Y = [y for i, y in enumerate(Y) if i not in to_remove]

        return _X, _Y


class Set:
    """
    Represents a Set
    """
    def __init__(self, X, Y):
        assert len(X) == len(Y)
        self.X = X
        self.Y = Y

    def __len__(self):
        return len(self.X)


class FeatureExtractor:
    """
    Can extract the features from the tweets
    """

    def __init__(self, tokenizer, connexion,
                 sentiments=['positive', 'negative', 'neutral']):

        """
        Input: Tokenizer, BDD connexion
        """
        self.tokenizer = tokenizer
        self.connexion = connexion
        self.sentiments = sentiments

    def extract(self, tweet):
        """
        Extract the features out of the given tweet
        Input: Tweet
        Output: [feature1, feature2, ...] -> where feature i = 0 || 1 (No ||
        Yes)
        """
        # Build the feature dictionnary sentiment -> score
        features = {}
        for sentiment in self.sentiments:
            features[sentiment] = 0.

        # First step: tokenization of the tweet
        tokens = self._tokenize_tweet(tweet)

        # Second step: get the score of each token in the DB
        for token in tokens:

            # Bug with the socket
            if token == '\\':
                continue

            score = self._request_score(token, self.sentiments)
            if score is not None:
                # Add the scores to the feature dictionnary
                for key, value in score.iteritems():
                    features[key] += value

        # Build the feature Vector
        # print features
        featureVector = []
        for e in self.sentiments:
            featureVector.append(features[e])

        return featureVector

    def _request_score(self, token, columns):
        """
        Case insensitive SELECT Query
        Input: Token, columns used
        Output: score of the word in the DB
                return None if not in the DB
        """
        # Mac!!!
        try:
            token.decode('utf8').encode('utf8')
        except:
            token=''

        cur = self.connexion.cursor()
        cur.execute("""SELECT {}
                     FROM public.sentiments
                     WHERE upper(entry) LIKE %(word)s""".format(
                    ', '.join(columns)),
                    {'word': '%' + token.upper() + '%'})
        row = cur.fetchone()

        # print row
        # Build the result vector
        if row is not None:
            result = {}
            for i, e in enumerate(row):
                if e is not None:
                    if len(e) > 0:
                        result[columns[i]] = 1
                    else:
                        result[columns[i]] = 0
            return result
        else:
            return None

    def _tokenize_tweet(self, tweet):
        """
        Input: tweet (String)
        Output: List of tokens
        """
        tok = Tokenizer(preserve_case=False)
        return tok.tokenize(tweet)


def load_database(file_name):
    """
    Input: file_name f containing the database login connection
    Output: database, user, password
    """
    with open(file_name) as f:

        lines = [line.strip() for line in f.readlines()]
        db = lines[0].split('=')[1]
        usr = lines[1].split('=')[1]
        pwd = lines[2].split('=')[1]
        return db, usr, pwd

if __name__ == '__main__':

    ts = SetManager('data/corpus.csv', 'data/rawdata/')
    tokenizer = Tokenizer(preserve_case=False)
    con = None

    try:
        db, usr, pwd = load_database('database.properties')
        con = psycopg2.connect(database=db, user=usr, host='localhost')
        sentiments = ['Virtue', 'Weak', 'HU', 'Hostile', 'EnlTot', 'ComForm',
                      'Passive', 'Pstv', 'Ngtv', 'PowTot', 'Strong', 'Positiv',
                      'IAV', 'Active', 'Negativ']
        sentiments.reverse()
        fe = FeatureExtractor(tokenizer, con, sentiments)
        print "Trying to score one word"
        print fe._request_score('LoVe', sentiments)
        time.sleep(2)
        print "Trying to score one tweet"
        print fe.extract("hate, cool, awesome, joy, pain :) love")
        print fe.extract("love twitter that rocks!")
        time.sleep(2)
        print "Trying to load the dataset"
        ts.load(fe, 10, 10, 10)
        print ts.X, len(ts.X)
        print ts.Y, len(ts.Y)
        classifier = svm.SVC(kernel='rbf')
        cm = ClassifierManager()
        # print classifier
        classifierTrained = cm.train(classifier, ts)
        # print classifierTrained
        # print request_score('LovE', con)
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()
