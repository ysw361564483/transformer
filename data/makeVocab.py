def getAllWord(input_file, word_set):
	with open(input_file, 'r', encoding="utf-8") as fin:
		while True:
			line = fin.readline()
			if line == None or line.strip() == "":
				break
			line = line.strip()
			words = line.split()
			for word in words:
				word_set.add(word)

def makeDictFromSet(word_set):
	word_num_dict = {}
	for w in word_set:
		word_num_dict[w] = 0
	return word_num_dict


def countWordNum(input_file, word_num_dict):
	with open(input_file, 'r', encoding="utf-8") as fin:
		while True:
			line = fin.readline()
			if line == None or line.strip() == "":
				break
			line = line.strip()
			words = line.split()
			for word in words:
				word_num_dict[word] += 1

def makeVocab(input_files, output_file):
	word_set = set()
	for input_file in input_files:
		getAllWord(input_file, word_set)
	
	word_num_dict = makeDictFromSet(word_set)

	for input_file in input_files:
		countWordNum(input_file, word_num_dict)

	sorted_word_num_dict_items = sorted(word_num_dict.items(), key=lambda d: d[1], reverse=True)

	with open(output_file, 'w', encoding="utf-8") as fout:
		for item in sorted_word_num_dict_items:
			fout.write(item[0] + " " + str(item[1]) + "\n")




if __name__ == "__main__":
	makeVocab(["./train.en"], "./allvocab.en")
	makeVocab(["./train.zh"], "./allvocab.zh")