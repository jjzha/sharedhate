# from nltk.tokenize import word_tokenize
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score

def get_tweet_sent_score(text, ytest):

	# import scores [v]alence, [a]rousal or [d]ominance
	# [v] 0.45 [a] 0.93 [d] -
	with open('vad_scores/a.scores') as scores:
		param = scores.name[-8]
		docs = {}
		for line in scores:
			[word,valence] = line.rstrip().split('\t')
			docs[word] = valence

	for i in range(1,100):

		vad_list = []
		threshold = i/100
		for line in text:
			valence = 0
			count = 0
			for word in line:
				if word in docs:
					count += 1
					valence += float(docs[word])
			if count != 0 and valence/count > threshold:
				vad_list.append('1')
			else:
				vad_list.append('0')

		accuracy = accuracy_score(ytest, vad_list)
		precision, recall, f1score, support = precision_recall_fscore_support(ytest, vad_list, average="weighted")
		report = classification_report(ytest, vad_list)

		print(i, accuracy)

	# return valence/count if count else 0
