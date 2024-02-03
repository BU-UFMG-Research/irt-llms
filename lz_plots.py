import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load lz data
# df_humans = pd.read_parquet("scripts/calculate-irt/lz-humans-ENEM_2022_CH_CO_PROVA_1062.parquet")
# df_llms = pd.read_parquet("scripts/calculate-irt/lz-llms-ENEM_2022_CH_CO_PROVA_1062.parquet")
df_humans = pd.read_parquet("enem-experiments-results-processed-with-irt-lz-humans_ENEM_2019_CH_CO_PROVA_520.parquet")
df_humans.rename(columns={"PFscores": "LZ_SCORE"}, inplace=True)
df_llms = pd.read_parquet("enem-experiments-results-processed-with-irt-lz.parquet")
df_llms = df_llms[df_llms.CO_PROVA == "520"]

# Plot lz data (same plot for both)
sns.histplot(df_humans["LZ_SCORE"], color="blue", kde=True, stat="density", label="Humans")
sns.histplot(df_llms["LZ_SCORE"], color="red", kde=True, stat="density", label="LLMS")
plt.legend()
#plt.title("CDF of LZ scores - 2022 Humanities")
plt.tight_layout()
# plt.savefig("lz-cdf-2022-CH.png", dpi=800)
plt.show()




