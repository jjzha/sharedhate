from sklearn.metrics import accuracy_score, f1_score

file1 = open('yguess_embed.txt', 'r')
file2 = open('yguess_svm.txt', 'r')

xlist = []
ylist = []
for x, y in zip(file1, file2):
	xlist.append(x.rstrip())
	ylist.append(y.rstrip())

print(accuracy_score(xlist, ylist))

file1.close()
file2.close()
