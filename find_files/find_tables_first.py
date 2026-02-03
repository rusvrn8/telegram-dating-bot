import os
import re
import pandas as pd


def find_words_with_substrings(directory, substrings):
	pattern = re.compile(r'\b\w*(?:' + '|'.join(map(re.escape, substrings)) + r')\w*\b')

	words = []

	for root, dirs, files in os.walk(directory):
		for file in files:
			filepath = os.path.join(root, file)
			try:
				with open(filepath, 'r', encoding='utf-8') as f:
					for line_num, line in enumerate(f, 1):
						matches = pattern.findall(line)
						if matches:
							for word in matches:
								print(f'Файл: {filepath}, Строка: {line_num}, Слово: {word}')
								words.append(word)
			except (UnicodeDecodeError, PermissionError) as e:
				print(f'Не удалось прочитать файл: {filepath}. Ошибка: {e}')
	return words


if __name__ == "__main__":
	substrings_to_find = ["011_012_0003.", "011_012_0000.", "011_012_0001.", "011_012_0002."]
	directory_to_scan = './airflow'

	words = find_words_with_substrings(directory_to_scan, substrings_to_find)
	df = pd.DataFrame(words, columns=['word'])

	df.to_csv('words_airflow.csv', index=False)
