def re_single_sentence(ss):
	nn = ss.replace(" @.@ ", ".").replace(" @_@ ", "_").replace(" @:@ ", ":")
	nn = nn.replace("@.@ ", ".").replace("@_@ ", "_").replace("@:@ ", ":")
	nn = nn.replace(" @.@", ".").replace(" @_@", "_").replace(" @:@", ":")
	nn = nn.replace("@.@", ".").replace("@_@", "_").replace("@:@", ":")
	return nn

def re_based_on_file(input_file, output_file):
	with open(input_file, 'r', encoding="utf-8") as fin:
		lines = fin.readlines()

	with open(output_file, 'w', encoding="utf-8") as fout:
		for line in lines:
			fout.write(re_single_sentence(line.strip()) + "\n")

def test():
	re_based_on_file("./train/logical_form_totally_tokenize.txt", "tem.txt")

	with open("tem.txt", 'r', encoding="utf-8") as fin:
		lines1 = fin.readlines()

	with open("./train/logical_form_raw.txt", 'r', encoding="utf-8") as fin:
		lines2 = fin.readlines()

	for l1, l2 in zip(lines1, lines2):
		assert l1 == l2

if __name__ == "__main__":
	test()


