#!/usr/bin/python3

# Team Grunn2019
# classifier_svm.py
# --file doing classification with SVMClassifier
# 25-09-2018
# revisions: 1

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC, LinearSVC
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score
from sklearn.model_selection import GridSearchCV

# a dummy function that just returns its input
def tokenizer(x):
    return ' '.join(x)

def identity(x):
    return x

def train_test_svm(xtrain, ytrain, xtest, ytest, task):

    char = TfidfVectorizer( analyzer='char',
                            preprocessor = tokenizer,
                            tokenizer = tokenizer,
                            ngram_range = (2, 4))
    word = TfidfVectorizer( analyzer='word',
                            preprocessor = identity,
                            tokenizer = identity,
                            ngram_range = (1, 2))


    classifier = Pipeline([
        ('features', FeatureUnion([
            # ('tfidf_word', word),
            ('tfidf_char', char),
        ])),
            ('cls', SVC(kernel='linear', probability=True, class_weight='balanced', random_state=1337))
        ])

    parameters = {
            'features__tfidf_word__ngram_range': [(1,1), (1,2), (1,3), (1,4)],
            'features__tfidf_char__ngram_range': [(2,3), (2,4), (1,3), (1,4)],
        }

    gridsearch = False
    if gridsearch:
        grid = GridSearchCV(classifier, param_grid=parameters)
        grid.fit(xtrain, ytrain)
        print(grid.best_params_)
        print(grid.best_score_)
        exit()
    else:
        # fit the traindata and the trainlabels to the classifier
        classifier.fit(xtrain, ytrain)

        # get the predicted y's(labels)
        yguess = classifier.predict(xtest)

        # https://stackoverflow.com/questions/15015710/how-can-i-know-probability-of-
        # class-predicted-by-predict-function-in-support-v
        probas = classifier.predict_proba(xtest)
        # probas = 0

        with open ('output_testset/yguess_svm_' + task + '.txt', 'w+') as yguess_output:
            for line in yguess:
                yguess_output.write('%s\n' % line)

        with open ('output_testset/probas_svm_' + task + '.txt', 'w+') as probas_output:
            for line in probas:
                probas_output.write('%s\t%s\n' % (line[0],line[1]))

        # print(classifier.classes_)

        if ytest != '':
            accuracy = accuracy_score(ytest, yguess)
            precision, recall, f1score, support = precision_recall_fscore_support(ytest, yguess, average='weighted')
            report = classification_report(ytest, yguess)
            print('SVMClassifier Results:')
            return yguess, accuracy, f1score, report, probas
        else:
            print('Finished predicting labels!')
            exit()
