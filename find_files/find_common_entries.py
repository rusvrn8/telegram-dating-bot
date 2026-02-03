import pandas as pd
import re


def find_common_entries(file1, file2, output_file):
	df1 = pd.read_csv(file1, header=0)
	df2 = pd.read_csv(file2, header=0)

	# Переименование колонок для удобства
	df1.columns = ['table_name']
	df2.columns = ['table_name']

	pattern = r'(prod|demo|test)?$'

	def clean_name(name):
		return re.sub(pattern, '', name)

	df1['cleaned_name'] = df1['table_name'].apply(clean_name)
	df2['cleaned_name'] = df2['table_name'].apply(clean_name)

	# df1 = df1[['cleaned_name']]
	# df2 = df2[['cleaned_name']]

	common_entries = pd.merge(df1, df2, on='cleaned_name', suffixes=('_df1', '_df2'))

	# common_entries = common_entries.drop_duplicates()
	common_entries = common_entries[['table_name_df1']]

	common_entries.to_csv(output_file, index=False, header=False)


if __name__ == '__main__':
	find_common_entries('delete_words.csv', 'words.csv', 'common_entries_mrkd_2.csv')
