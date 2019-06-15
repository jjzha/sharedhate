#!/usr/bin/python3

# Team Grunn2019
# classifier_lr.py
# --file doing classification with Logistic Regression
# 25-09-2018
# revisions: 1

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score


def tokenizer(x):
    return ' '.join(x)

# a dummy function that just returns its input
def identity(x):
    return x

def train_test_lr(xtrain, ytrain, xtest, ytest, task):

    vec = TfidfVectorizer(ngram_range=(2,4), analyzer='char', preprocessor=tokenizer, tokenizer=tokenizer)

    # combine the vectorizer with a classifier
    classifier = Pipeline([('vec', vec),
                           ('cls', LogisticRegression())
                           ])

    # fit the traindata and the trainlabels to the classifier
    classifier.fit(xtrain, ytrain)

    # get the predicted y's(labels)
    yguess = classifier.predict(xtest)

    # https://stackoverflow.com/questions/15015710/how-can-i-know-probability-of-
    # class-predicted-by-predict-function-in-support-v
    probas = classifier.predict_proba(xtest)

    with open ('output_testset/yguess_lr_' + task + '.txt', 'w+') as yguess_output:
        for line in yguess:
            yguess_output.write('%s\n' % line)

    with open ('output_testset/probas_lr_' + task + '.txt', 'w+') as probas_output:
        for line in probas:
            probas_output.write('%s\t%s\n' % (line[0],line[1]))

    # print(classifier.classes_)

    if ytest != '':
        accuracy = accuracy_score(ytest, yguess)
        precision, recall, f1score, support = precision_recall_fscore_support(ytest, yguess, average='weighted')
        report = classification_report(ytest, yguess)
        print('LogisticRegressionClassifier Results:')
        return yguess, accuracy, f1score, report, probas
    else:
        print('Finished predicting labels!')
        exit()