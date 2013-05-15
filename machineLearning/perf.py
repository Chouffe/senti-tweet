#!/usr/bin/python
# -*- coding: utf-8 -*-

from tools import Tokenizer, ClassifierManager, SetManager, FeatureExtractor, load_database
import argparse
import psycopg2
import sys
import os

# Extract Info from the command line
parser = argparse.ArgumentParser(description='Process the SVM training')
parser.add_argument('-p', '--number_pos',
                    help='number of positive tweets used for the training',
                    default=100,
                    type=int)
parser.add_argument('-n', '--number_neg',
                    help='number of negative tweets used for the training',
                    default=100,
                    type=int)
parser.add_argument('-e', '--number_neut',
                    help='number of neutral tweets used for the training',
                    default=100,
                    type=int)
parser.add_argument('-c', '--csv_path',
                    help='CSV path',
                    default='data/corpus.csv',
                    type=str)
parser.add_argument('-t', '--tweets_path',
                    help='tweets path',
                    default='data/rawdata/',
                    type=str)
parser.add_argument('-f', '--origin_path',
                    help='File where are stored the classifiers',
                    default='classifiers',
                    type=str)


def vote(classifiers, x):

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
    return max(predictions.iterkeys(), key=(lambda k: predictions[k]))
    # return predictions

args = parser.parse_args()

print "Initialization"
s = SetManager(args.csv_path, args.tweets_path)
tokenizer = Tokenizer(preserve_case=False)
cm = ClassifierManager()

# List of the sentiments used (feature space)
sentiments = ['Virtue', 'Weak', 'HU', 'Hostile', 'EnlTot', 'ComForm',
              'Passive', 'Pstv', 'Ngtv', 'PowTot', 'Strong', 'Positiv',
              'IAV', 'Active', 'Negativ']
sentiments.reverse()
classifiers = {}

print "DB connexion"
con = None
testingSet = None

try:
    db, usr, pwd = load_database('database.properties')
    con = psycopg2.connect(database=db, user=usr, host='localhost')

    print "Loading the Testing Set"
    fe = FeatureExtractor(tokenizer, con, sentiments)
    mySet = s.load(fe, args.number_pos, args.number_pos, args.number_neut)
    testingSet, _ = s.splitTrainingAndTestingSet(mySet, 1)

    # print testingSet.X, testingSet.Y

except psycopg2.DatabaseError, e:
    print 'Error %s' % e
    sys.exit(1)

finally:
    if con:
        con.close()

# Testing the performance
# Loading the classifiers
path = args.origin_path
list_classifier_filename = os.listdir(path)
classifiers = []

# Retrieve the classifiers
for classifier_filename in list_classifier_filename:

    with open(path + '/' + classifier_filename, 'r') as f:

        cm = ClassifierManager()
        classifier = cm.load(f)
        classifiers.append(classifier)

# Evaluate the perfs
print "Performance: ", cm.perf(classifiers, testingSet)
