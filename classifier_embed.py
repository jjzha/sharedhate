#!/usr/bin/python3

# Team Grunn2019
# classifier_embed.py
# --file doing classification with SVMClassifier and Embeddings
# 25-09-2018


from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC, LinearSVC
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score
from collections import defaultdict
from gensim.models import KeyedVectors
import numpy as np

# embeddings with results on dev set with preprocess        # acc   - f1
embeddings = 'glove.840B.300d.txt'                        # 0.726 - 0.727
# embeddings = 'glove.twitter.27B.25d.txt'                  # 0.680 - 0.675
# embeddings = 'en.100'                                       # 0.716 - 0.711
# embeddings = 'en.400'                                     # 0.719 - 0.717

def open_embeddings():
    print('Using embeddings: ', embeddings)
    if embeddings[-3:] != 'txt':
        w2v = KeyedVectors.load_word2vec_format(embeddings, binary=True, unicode_errors='ignore')
    else:
        w2v = {}
        f = open(embeddings)
        for line in f:
            values = line.split()
            word = values[0]
            try:
                float(values[1])
            except ValueError:
                continue
            coefs = np.asarray(values[1:], dtype='float')
            w2v[word] = coefs
        f.close()
    return w2v

# transform documents to vector-embeddings
def create_embeds(x, embeds):

    embedded_features = []
    for document in x:
        features = []
        for token in document:
            try:
                vector = embeds[token.lower()]
                # print('try', vector)
            except:
                vector = embeds['unk']
                # print('unknown', vector)
            features.append(vector)
        if features:
            features = np.average(features, axis=0)
        else:
            features = embeds['unk']
        embedded_features.append(features)
    return np.array(embedded_features)

# a tokenizer for character n-grams
def tokenizer(x):
    return ' '.join(x)

# a dummy function that just returns its input
def identity(x):
    return x

def train_test_embed(xtrain, ytrain, xtest, ytest, task):

    embeds = open_embeddings()
    xtrain = create_embeds(xtrain, embeds)
    xtest = create_embeds(xtest, embeds)

    classifier = Pipeline([
        ('cls', SVC(kernel='linear', probability=True, class_weight='balanced', random_state=1337))
    ])

    # fit the traindata and the trainlabels to the classifier
    classifier.fit(xtrain, ytrain)

    # get the predicted y's(labels)
    yguess = classifier.predict(xtest)

    probas = classifier.predict_proba(xtest)
    # probas = 0

    with open ('output_testset/yguess_embed_' + task + '.txt', 'w+') as yguess_output:
        for line in yguess:
            yguess_output.write('%s\n' % line)

    with open ('output_testset/probas_embed_' + task + '.txt', 'w+') as probas_output:
        for line in probas:
            probas_output.write('%s\t%s\n' % (line[0],line[1]))

    if ytest != '':
        accuracy = accuracy_score(ytest, yguess)
        precision, recall, f1score, support = precision_recall_fscore_support(ytest, yguess, average='weighted')
        report = classification_report(ytest, yguess)
        print('SVMClassifier + Embeddings Results:')
        return yguess, accuracy, f1score, report, probas
    else:
        print('Finished predicting labels!')
        exit()
