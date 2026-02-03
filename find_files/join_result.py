import pandas as pd
import glob


def join_result(path):
	all_files = glob.glob(path)
	print(all_files)

	dataframes = []

	for filename in all_files:
		df = pd.read_csv(filename, header=None)
		df.columns = ['table_name']
		dataframes.append(df)

	combined_df = pd.concat(dataframes, ignore_index=True)
	combined_df = combined_df.drop_duplicates()

	combined_df.to_csv('result.csv', index=False, header=False)


if __name__ == '__main__':
	path_files = './*.csv'
	join_result(path_files)
