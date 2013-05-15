#!/usr/bin/python
# -*- coding: utf-8 -*-

from tools import *
import os

# Extract Info from the command line
# parser = argparse.ArgumentParser(description='Process the SVM predicting')
# parser.add_argument('classifier', type=str, help="filename of the classifier")
# args = parser.parse_args() parser.parse_args()
# parser.parse_args() 


def predict(tweet):

    # print "tweet", tweet

    tokenizer = Tokenizer(preserve_case=False)
    cm = ClassifierManager()
    path = 'classifiers'
    sentiments = ['Virtue', 'Weak', 'HU', 'Hostile', 'EnlTot', 'ComForm',
                  'Passive', 'Pstv', 'Ngtv', 'PowTot', 'Strong', 'Positiv',
                  'IAV', 'Active', 'Negativ']

    list_classifier_filename = os.listdir(path)
    predictions = {'neg':0, 'neut':0, 'pos':0}
    # print "list of classifiers: ", list_classifier_filename

    try:
        db, usr, pwd = load_database('database.properties')
        con = psycopg2.connect(database=db, user=usr, host='localhost')
        fe = FeatureExtractor(tokenizer, con, sentiments)

        for classifier_filename in list_classifier_filename:

            with open(path + '/' + classifier_filename, 'r') as f:

                cm = ClassifierManager()
                classifier = cm.load(f)
                #print "classifier"
                #print classifier

                X = fe.extract(tweet)
                #print "Feature Vector: ", X
                prediction = classifier.predict(X)[0]
                if prediction == -1:
                    predictions['neg'] += 1
                elif prediction == 0:
                    predictions['neut'] += 1
                else:
                    predictions['pos'] += 1

        # print "predictions: ", predictions
        result = max(predictions.iterkeys(), key=(lambda k: predictions[k]))
        if result == 'neg':
            return -1
        elif result == 'neut':
            return 0
        else:
            return 1

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()

if __name__ == '__main__':
    #print predict("hate die hard bitch virtue, positive")
    pass
