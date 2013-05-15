#!/usr/bin/python
# -*- coding: utf-8 -*-

from tools import Tokenizer, ClassifierManager, SetManager, FeatureExtractor, load_database
import argparse
import psycopg2
import sys
from sklearn import svm


# Extract Info from the command line
parser = argparse.ArgumentParser(description='Process the SVM training')
parser.add_argument('-p', '--number_pos',
                    help='number of positive tweets used for the training',
                    default=10,
                    type=int)
parser.add_argument('-n', '--number_neg',
                    help='number of negative tweets used for the training',
                    default=10,
                    type=int)
parser.add_argument('-e', '--number_neut',
                    help='number of neutral tweets used for the training',
                    default=10,
                    type=int)
parser.add_argument('-c', '--csv_path',
                    help='CSV path',
                    default='data/corpus.csv',
                    type=str)
parser.add_argument('-t', '--tweets_path',
                    help='tweets path',
                    default='data/rawdata/',
                    type=str)
parser.add_argument('-f', '--dest_file',
                    help='File where is stored the model',
                    default='classifier',
                    type=str)
args = parser.parse_args()


# Process the training of the model
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

try:
    db, usr, pwd = load_database('database.properties')
    con = psycopg2.connect(database=db, user=usr, host='localhost')

    print "Loading the Training Set"
    fe = FeatureExtractor(tokenizer, con, sentiments)
    mySet = s.load(fe, args.number_pos, args.number_pos, args.number_neut)
    training, testing = s.splitTrainingAndTestingSet(mySet, .8)

    print "Training the Models"

    # RBF: gamma varies
    classifier_rbf_gamma_01 = svm.SVC(kernel='rbf', gamma=.1)
    classifier_rbf_gamma_02 = svm.SVC(kernel='rbf', gamma=.2)
    classifier_rbf_gamma_03 = svm.SVC(kernel='rbf', gamma=.3)
    classifier_rbf_gamma_05 = svm.SVC(kernel='rbf', gamma=.5)
    classifier_rbf_gamma_08 = svm.SVC(kernel='rbf', gamma=.8)
    classifier_rbf_gamma_15 = svm.SVC(kernel='rbf', gamma=1.5)
    classifier_rbf_gamma_3 = svm.SVC(kernel='rbf', gamma=3)
    classifier_rbf_gamma_10 = svm.SVC(kernel='rbf', gamma=10)
    classifier_rbf_gamma_25 = svm.SVC(kernel='rbf', gamma=25)

    # Sigmoid
    classifier_sigmoid = svm.SVC(kernel='sigmoid')

    # Polynomial: degree varies
    classifier1 = svm.SVC(kernel='linear')
    classifier2 = svm.SVC(kernel='poly', degree=2)
    classifier3 = svm.SVC(kernel='poly', degree=3)
    classifier4 = svm.SVC(kernel='poly', degree=4)
    classifier5 = svm.SVC(kernel='poly', degree=5)
    classifier6 = svm.SVC(kernel='poly', degree=6)
    classifier7 = svm.SVC(kernel='poly', degree=7)
    classifier8 = svm.SVC(kernel='poly', degree=8)
    classifier9 = svm.SVC(kernel='poly', degree=9)
    classifier10 = svm.SVC(kernel='poly', degree=10)

    # Add the classifiers into classifiers[]
    classifiers['rbf_gamma_01'] = classifier_rbf_gamma_01
    classifiers['rbf_gamma_02'] = classifier_rbf_gamma_02
    classifiers['rbf_gamma_03'] = classifier_rbf_gamma_03
    classifiers['rbf_gamma_05'] = classifier_rbf_gamma_05
    classifiers['rbf_gamma_08'] = classifier_rbf_gamma_08
    classifiers['rbf_gamma_15'] = classifier_rbf_gamma_15
    classifiers['rbf_gamma_3'] = classifier_rbf_gamma_3
    classifiers['rbf_gamma_10'] = classifier_rbf_gamma_10
    classifiers['rbf_gamma_25'] = classifier_rbf_gamma_25

    classifiers['sigmoid'] = classifier_sigmoid

    classifiers['linear'] = classifier1
    classifiers['d2'] = classifier2
    classifiers['d3'] = classifier3
    classifiers['d4'] = classifier4
    classifiers['d5'] = classifier5
    classifiers['d6'] = classifier6
    classifiers['d7'] = classifier7
    classifiers['d8'] = classifier8
    classifiers['d9'] = classifier9
    classifiers['d10'] = classifier10

    for c in classifiers.itervalues():
        cm.train(c, training)

    perf = {}
    for n, c in classifiers.iteritems():
        perf[n] = cm.perf([c], testing)

    print "Performances"
    print perf

    best_classifier_name = max(perf.iterkeys(), key=(lambda k: perf[k]))
    print "Best classifier: ", best_classifier_name, " -> ", perf[best_classifier_name]

    print "Saving the model"
    with open(args.dest_file, 'w') as f:
        cm.save(classifiers[best_classifier_name], f)

except psycopg2.DatabaseError, e:
    print 'Error %s' % e
    sys.exit(1)

finally:
    if con:
        con.close()
