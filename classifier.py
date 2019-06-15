#!/usr/bin/python3

# Team Grunn2019
# classifier.py
# --file making baseline
# 25-09-2018
# revisions: 1

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.svm import SVC, LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# a dummy function that just returns its input
def identity(x):
    return x


def train_test(xtrain, ytrain, xtest, ytest):

    vec = TfidfVectorizer(ngram_range=(1, 3), analyzer='char', preprocessor=identity)

    # combine the vectorizer with a classifier
    classifier = Pipeline([('vec', vec),
                           # ('cls', SVC(kernel='linear', probability=True, class_weight='balanced'))
                           # ('cls', LogisticRegression(solver='liblinear', class_weight='balanced'))
                           ('cls', RandomForestClassifier(n_estimators=750, criterion='entropy', class_weight='balanced'))
                           ])

    # fit the traindata and the trainlabels to the classifier
    classifier.fit(xtrain, ytrain)

    # get the predicted y's(labels)
    yguess = classifier.predict(xtest)

    # https://stackoverflow.com/questions/15015710/how-can-i-know-probability-of-class-predicted-by-predict-function-in-support-v
    probas = classifier.predict_proba(xtest)

    # compare yguess with ytest, calculate and return results
    accuracy = accuracy_score(ytest, yguess)
    precision, recall, f1score, support = precision_recall_fscore_support(ytest, yguess, average="weighted")
    report = classification_report(ytest, yguess)

    # print(classifier.classes_)

    return accuracy, precision, recall, f1score, support, report, probas
