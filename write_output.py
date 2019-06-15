import csv
from sklearn.metrics import accuracy_score, f1_score

def main():
    ids = []
    # gold_a = []
    # gold_b = []
    # gold_c = []

    with open('public_test_en/test_en.tsv', encoding='utf-8') as f:
        rd = csv.reader(f, delimiter='\t', quotechar="'")
        next(rd)
        for line in rd:
            ids.append(line[0].rstrip())

			# uncomment for dev
            # gold_a.append(line[2].rstrip())
            # gold_b.append(line[3].rstrip())
            # gold_c.append(line[4].rstrip())

    output_a = []
    with open ('output_testset_spanish/yguess_ens_bin_A.txt', 'r') as file:
        for line in file:
            output_a.append(line.rstrip())

    output_b = []
    with open ('output_testset_spanish/yguess_ens_bin_B.txt', 'r') as file:
        for line in file:
            output_b.append(line.rstrip())

    output_c = []
    with open ('output_testset_spanish/yguess_ens_bin_C.txt', 'r') as file:
        for line in file:
            output_c.append(line.rstrip())


    ''' write final output for subtask A'''
    with open ('output_testset_spanish/subtaskA.tsv', 'wt') as output:
        tsv_writer = csv.writer(output, delimiter='\t')
        for id, a in zip(ids, output_a):
            tsv_writer.writerow([id, a])

    old_a = []
    old_b = []
    old_c = []
    new_a = []
    new_b = []
    new_c = []
    ''' write final output for subtask B'''
    with open ('output_testset_spanish/subtaskB.tsv', 'wt') as output:
        tsv_writer = csv.writer(output, delimiter='\t')
        for id, a, b, c in zip(ids, output_a, output_b, output_c):
            old_a.append(a)
            old_b.append(b)
            old_c.append(c)
            if (b == '1' and c == '1'):
                a = '1'
            elif a == '0':
                b = '0'
                c = '0'
            new_a.append(a)
            new_b.append(b)
            new_c.append(c)

            tsv_writer.writerow([id, a, b, c])


    # print('results before swapping 0 and 1')
    # print(f1_score(gold_a, old_a, average='weighted'))
    # print(f1_score(gold_b, old_b, average='weighted'))
    # print(f1_score(gold_c, old_c, average='weighted'))
	#
    # print('\nresults after swapping 0 and 1')
    # print(f1_score(gold_a, new_a, average='weighted'))
    # print(f1_score(gold_b, new_b, average='weighted'))
    # print(f1_score(gold_c, new_c, average='weighted'))

if __name__ == '__main__':
    main()
