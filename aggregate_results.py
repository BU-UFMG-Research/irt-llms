import glob
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

files = glob.glob("enem-experiments-results/*pt-br.parquet")
files.sort()

new_df = None
for file in files:
    df = pd.read_parquet(file)
    if new_df is None:
        new_df = df
    else:
        # Concatenate dataframes
        new_df = pd.concat([new_df, df]).reset_index(drop=True)

new_df.to_parquet("enem-experiments-results-processed.parquet")

print(new_df)