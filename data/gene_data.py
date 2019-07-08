import os
from makeVocab import makeVocab
def read_data(input_file):
	with open(input_file, 'r', encoding="utf-8") as fin:
		lines = fin.readlines()

	#print(len(lines))
	line_num = len(lines)
	assert line_num % 5 == 0
	data_num = line_num // 5

	to_ret = []

	for ii in range(0, data_num):
		single_data = []
		data_lines = lines[5 * ii : 5 * ii + 4]

		assert lines[5 * ii + 4].strip() == "=================================================="

		for line in data_lines:
			line = line.strip()
			tag, value = line.split("\t")
			single_data.append(value)

		to_ret.append(single_data)


	return to_ret

def rewrite_raw(input_file, output_dir):
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	data_list = read_data(input_file)

	output_question_path = os.path.join(output_dir, "question_raw.txt")
	output_logical_form_path = os.path.join(output_dir, "logical_form_raw.txt")
	output_parameters_path = os.path.join(output_dir, "parameters_raw.txt")
	output_question_type_path = os.path.join(output_dir, "question_type_raw.txt")

	with open(output_question_path, 'w', encoding="utf-8") as fout_ques, open(output_logical_form_path, 'w', encoding="utf-8") as fout_logic,\
	 open(output_parameters_path, 'w', encoding="utf-8") as fout_para, open(output_question_type_path, 'w', encoding="utf-8") as fout_ques_type:
		for single_data in data_list:
			fout_ques.write(single_data[0] + "\n")
			fout_logic.write(single_data[1] + "\n")
			fout_para.write(single_data[2] + "\n")
			fout_ques_type.write(single_data[3] + "\n")


def tokenize_totally(input_file, output_file):
	with open(input_file, 'r', encoding="utf-8") as fin:
		lines = fin.readlines()

	with open(output_file, 'w', encoding="utf-8") as fout:
		for line in lines:
			line = line.strip()
			new_line = ""
			for char in line:
				if char in [".", ":", "_"]:
					new_line += " @" + char + "@ "
				else:
					new_line += char
			fout.write(new_line + "\n")


def tokenize_just_some_underline(input_file, output_file):
	with open(input_file, 'r', encoding="utf-8") as fin:
		lines = fin.readlines()

	with open(output_file, 'w', encoding="utf-8") as fout:
		for line in lines:
			line = line.strip()
			
			new_items = []

			items = line.split()

			for item in items:
				if "_" in item and "." not in item:
					item = item.replace("_", " @_@ ")
					new_items.append(item)
				else:
					new_items.append(item)


			fout.write(" ".join(new_items) + "\n")

def tokenize_underline(input_file, output_file):
	with open(input_file, 'r', encoding="utf-8") as fin:
		lines = fin.readlines()

	with open(output_file, 'w', encoding="utf-8") as fout:
		for line in lines:
			line = line.strip()
			
			new_items = []

			items = line.split()

			for item in items:
				if "_" in item and "." not in item:
					item = item.replace("_", " @_@ ")
					new_items.append(item)
				elif "_" in item and "." in item:
					sub_items = item.split(".")
					if "_" in sub_items[-1]:
						item = ".".join(sub_items[0 : -1]) + ". " + sub_items[-1].replace("_", " @_@ ")
					
					new_items.append(item)

				else:
					new_items.append(item)


			fout.write(" ".join(new_items) + "\n")

def test():
	dd = read_data("MSParS.train")
	print(dd[0])
	print(dd[-1])


def make_all_vocab():
	if not os.path.exists("./vocab"):
		os.mkdir("./vocab")
	makeVocab(['./train.src.txt'], './train.vocab.src.txt')
	makeVocab(['./train.tgt.txt'], './train.vocab.tgt.txt')
	makeVocab(['./valid.src.txt'], './valid.vocab.src.txt')
	makeVocab(['./valid.tgt.txt'], './valid.vocab.tgt.txt')
	# makeVocab(["train/question_raw.txt"], "train/vocab/vocab_for_question_raw.txt")
	# makeVocab(["train/logical_form_raw.txt"], "train/vocab/vocab_for_logical_form_raw.txt")
	# makeVocab(["train/logical_form_totally_tokenize.txt"], "train/vocab/vocab_for_logical_form_totally_tokenize.txt")
	# makeVocab(["train/logical_form_tokenize_just_some_underline.txt"], "train/vocab/vocab_for_logical_form_tokenize_just_some_underline.txt")
	# makeVocab(["train/logical_form_tokenize_underline.txt"], "train/vocab/vocab_for_logical_form_tokenize_underline.txt")


	# if not os.path.exists("dev/vocab"):
	# 	os.mkdir("dev/vocab")

	# makeVocab(["dev/question_raw.txt"], "dev/vocab/vocab_for_question_raw.txt")
	# makeVocab(["dev/logical_form_raw.txt"], "dev/vocab/vocab_for_logical_form_raw.txt")
	# makeVocab(["dev/logical_form_totally_tokenize.txt"], "dev/vocab/vocab_for_logical_form_totally_tokenize.txt")
	# makeVocab(["dev/logical_form_tokenize_just_some_underline.txt"], "dev/vocab/vocab_for_logical_form_tokenize_just_some_underline.txt")
	# makeVocab(["dev/logical_form_tokenize_underline.txt"], "dev/vocab/vocab_for_logical_form_tokenize_underline.txt")


def main():
	# rewrite_raw("MSParS.train", "train")
	# rewrite_raw("MSParS.dev", "dev")

	# tokenize_totally("train/logical_form_raw.txt", "train/logical_form_totally_tokenize.txt")
	# tokenize_totally("dev/logical_form_raw.txt", "dev/logical_form_totally_tokenize.txt")

	# tokenize_just_some_underline("train/logical_form_raw.txt", "train/logical_form_tokenize_just_some_underline.txt")
	# tokenize_just_some_underline("dev/logical_form_raw.txt", "dev/logical_form_tokenize_just_some_underline.txt")

	# tokenize_underline("train/logical_form_raw.txt", "train/logical_form_tokenize_underline.txt")
	# tokenize_underline("dev/logical_form_raw.txt", "dev/logical_form_tokenize_underline.txt")

	make_all_vocab()

if __name__ == "__main__":
	main()
	

