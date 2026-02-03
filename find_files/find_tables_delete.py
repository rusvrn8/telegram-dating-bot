import pandas as pd


def find_tables_delete(file_path):
	df = pd.read_excel(file_path)

	# Фильтрация по значениям в колонке 'db'
	filtered_df = df[df['DB HIVE'].isin(["011_012_0003", "011_012_0000", "011_012_0001", "011_012_0002"])]

	# Объединение значений колонок 'db' и 'table' в новую колонку 'table_name'
	filtered_df['table_name'] = filtered_df['DB HIVE'] + '.' + filtered_df['Табл. в HIVE'].astype(str)

	# Оставляем только колонку 'table_name'
	result_df = filtered_df[['table_name']]

	# Вывод результата
	print(result_df.head(3))
	result_df.to_csv('delete_words.csv', index=False)


if __name__ == '__main__':
	find_tables_delete('delete_list.xlsx')
