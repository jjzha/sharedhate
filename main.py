#!/usr/bin/python3

# Team Grunn2019
# main.py
# --file to start classification
# 25-09-2018
# revisions: 4

# command example:
# python3 main.py public_development_en/train_en.tsv public_development_en/dev_en.tsv -rf -p
# python3 main.py [trainset] [testset] [-rf, -svm, -lstm, -embed] [-p]

# "public_development_en/train_en.tsv"
# "public_development_en/dev_en.tsv"

import argparse
from read_data import read_corpus
from classifier_rf import train_test_rf
from classifier_svm import train_test_svm
from classifier_embed import train_test_embed
from classifier_lr import train_test_lr
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score
# from BiLSTM import biLSTM

task = 'A'
# task = 'B'
# task = 'C'

def joint():
    # int (0,1)
    yguess_ens_bin = []

    yguess_lr = open('output_testset_spanish/yguess_lr_' + task + '.txt', 'r')
    yguess_rf = open('output_testset_spanish/yguess_rf_' + task + '.txt', 'r')
    yguess_svm = open('output_testset_spanish/yguess_svm_' + task + '.txt', 'r')
    # yguess_embed = open('output_testset/yguess_embed_' + task + '.txt', 'r')
    # yguess_lstm = open('output_testset/yguess_lstm_' + task + '.txt', 'r')
    for lr, rf, svm, embed, lstm in zip(yguess_lr, yguess_rf, yguess_svm, yguess_embed, yguess_lstm):
        # if int(lr.strip('\n'))+int(rf.strip('\n'))+int(svm.strip('\n'))+int(embed.strip('\n'))+int(lstm.strip('\n')) >= 3:
        if int(lr.strip('\n'))+int(rf.strip('\n'))+int(svm.strip('\n')) >= 2:
            yguess_ens_bin.append('1')
        else:
            yguess_ens_bin.append('0')

    # accuracy = accuracy_score(ytest, yguess_ens_bin)
    # precision, recall, f1score, support = precision_recall_fscore_support(ytest, yguess_ens_bin, average="weighted")
    # report = classification_report(ytest, yguess_ens_bin)
    #
    # print_output(accuracy, f1score, report, "")
    with open('output_testset_spanish/yguess_ens_bin_' + task + '.txt','w') as f1:
        for i in yguess_ens_bin:
            f1.write(i+"\n")
    # for line in open('yguess_ens_bin_'+task+'.txt','r'):
    #     print(line)
    f1.close()

def print_output(accuracy, f1score, report, probas=""):

    print('Done!!!!!!')

    print("## accuracy and f1_score:")
    print("accuracy: {:.3}".format(accuracy))
    print("f1_score: {:.3}".format(f1score))

    print("\n## classification report:")
    print(report)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Shared task classification task arguments')
    parser.add_argument('trainset', metavar='[trainset in .tsv format]', type=str,
                        help='File containing training data.')
    parser.add_argument('testset', nargs='?', default='', type=str,
                        help='File containing test data, if not given, uses dev data to test.')
    parser.add_argument('-svm', '--SVM', action='store_true',
                        help='Only use SVM Classifier.')
    parser.add_argument('-rf', '--RandomForest', action='store_true',
                        help='Only use RandomForestClassifier.')
    parser.add_argument('-lr', '--LogisticRegression', action='store_true',
                        help='Only use LogisticRegressionClassifier.')
    parser.add_argument('-lstm', '--BiLSTM', action='store_true',
                        help='Only use the BiLSTM.')
    parser.add_argument('-embed', '--Embeddings', action='store_true',
                        help='Only use the SVM with Embeddings.')
    parser.add_argument('-j', '--joint', action='store_true',
                        help='Use all three systems for a majority vote system.')
    parser.add_argument('-p', '--preprocess', action='store_true',
                        help='Preprocess the data, by default keeps raw tokens as training data.')
    args = parser.parse_args()

    # Check which pre-processing is necessary
    if args.BiLSTM and args.preprocess:
        flag = 'biLSTM'
    elif not args.preprocess:
        flag = False
    else:
        flag = True

    if args.testset:
    # Read in the data and embeddings
        xtrain, ytrain = read_corpus(args.trainset, flag, task, False)
        xtest = read_corpus(args.testset, flag, task, True)
        ytest = ''
    else:
        xtrain, ytrain = read_corpus(args.trainset, flag, task, False)
        xtest, ytest = read_corpus('public_development_en/dev_en.tsv', flag, task, False)

    if args.SVM:
        yguess, accuracy, f1score, report, probas = train_test_svm(xtrain, ytrain, xtest, ytest, task)
        print_output(accuracy, f1score, report, probas)
    elif args.RandomForest:
        yguess, accuracy, f1score, report, probas = train_test_rf(xtrain, ytrain, xtest, ytest, task)
        print_output(accuracy, f1score, report, probas)
    elif args.LogisticRegression:
        yguess, accuracy, f1score, report, probas = train_test_lr(xtrain, ytrain, xtest, ytest, task)
        print_output(accuracy, f1score, report, probas)
    elif args.BiLSTM:
        training = False
        output = True
        yguess_bilstm, accuracy, f1score, report = biLSTM(xtrain, ytrain, xtest, ytest, training, output)
        print_output(accuracy, f1score, report)
    elif args.Embeddings:
        yguess, accuracy, f1score, report, probas = train_test_embed(xtrain, ytrain, xtest, ytest, task)
        print_output(accuracy, f1score, report, probas)
    elif args.joint:
        joint()
    else:
        parser.print_help()
