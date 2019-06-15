#!/usr/bin/python3

# Team Grunn2019
# read_data.py
# --file doing preprocessing
# 12-12-2018
# revisions: 3

# read hatespeech corpus, append tweets and label
# class 1 corresponds as hatespeech, 0 not

import csv, re, emoji, string
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords

stopwords_list = stopwords.words('spanish')
whitelist = ["why", "not", "no", "n't", "against", "!", "?"]

def url_replacer(text):
    url = [r"http\S+", r"\S+https", r"\S+http"]
    for item in url:
        text = re.sub(item, '<URL>', text)
    return text

def preprocess_data(text):
    # URL replacer
    text = url_replacer(text)

    # split into words
    tknzr = TweetTokenizer()
    tokens = tknzr.tokenize(text)

    # replace mentions to _user
    tokens = [word.replace(word, '<USERNAME>') if word[0] == '@' else word for word in tokens]

    # convert to lower case
    tokens = [x.lower() for x in tokens]

    # filter out stop words
    # tokens = [word for word in tokens if (word not in stopwords_list or word in whitelist)]
    tokens = [word for word in tokens if word not in stopwords_list]

    # removing characters (excluding emojis)
    tokens = [token for token in tokens if (len(token) > 1 or token in emoji.UNICODE_EMOJI)]

    return tokens

def preprocess_data_biLSTM(text):
    # URL replacer
    text = url_replacer(text)

    # split into words
    tknzr = TweetTokenizer()
    tokens = tknzr.tokenize(text)

    # replace mentions to _user
    tokens = [word.replace(word, '<USERNAME>') if word[0] == '@' else word for word in tokens]

    return tokens

def read_corpus(corpus_file, flag, task, type):
    column = ord(task) - 63     # ascii number minus 63
    documents = []
    labels = []
    count = 0
    with open(corpus_file, encoding='utf-8') as f:
        for line in f:
            tok = line.strip().split('\t')
            if not tok[0].isnumeric():# to skip column headers
                continue
            text = tok[1]
            if flag == True:
                tokens = preprocess_data(text)
            elif flag == 'biLSTM':
                tokens = preprocess_data_biLSTM(text)
            else:
                tokens = line[1]

            if type == False:
                labels.append(tok[column])
                documents.append(tokens)
            else:
                documents.append(tokens)

            count += 1

    if type == False:
        return documents, labels
    else:
        return documents
