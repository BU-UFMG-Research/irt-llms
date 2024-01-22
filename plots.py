from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import argparse

ENEM_MAPPING_NAME = {
    #2022
    "ENEM_2022_CH_CO_PROVA_1062": "2022 Humanities",
    "ENEM_2022_CN_CO_PROVA_1092": "2022 Natural Sciences",
    "ENEM_2022_LC_CO_PROVA_1072": "2022 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2022_MT_CO_PROVA_1082": "2022 Mathematics",

    #2021
    "ENEM_2021_CH_CO_PROVA_886": "2021 Humanities",
    "ENEM_2021_CN_CO_PROVA_916": "2021 Natural Sciences",
    "ENEM_2021_LC_CO_PROVA_896": "2021 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2021_MT_CO_PROVA_906": "2021 Mathematics",

    #2020
    "ENEM_2020_CH_CO_PROVA_574": "2020 Humanities",
    "ENEM_2020_CN_CO_PROVA_604": "2020 Natural Sciences",
    "ENEM_2020_LC_CO_PROVA_584": "2020 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2020_MT_CO_PROVA_594": "2020 Mathematics",

    #2019
    "ENEM_2019_CH_CO_PROVA_520": "2019 Humanities",
    "ENEM_2019_CN_CO_PROVA_519": "2019 Natural Sciences",
    "ENEM_2019_LC_CO_PROVA_521": "2019 Languages and Codes (Spanish as Foreign Language)",
    "ENEM_2019_MT_CO_PROVA_522": "2019 Mathematics",
}

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--year", "-y", type=int, required=True, help="Year of ENEM exam")
args = parser.parse_args()
year = args.year

df = pd.read_parquet("enem-experiments-results-processed-with-irt.parquet")
df = df[df.ENEM_EXAM.str.contains(f"{year}")]

# concat MODEL_NAME and MODEL_SIZE in one column
df["FULL_MODEL"] = df["MODEL_NAME"].astype(str) + " " + df["MODEL_SIZE"].astype(str)

df["ENEM_EXAM"].replace(ENEM_MAPPING_NAME, inplace=True)

# Plot heatmap of models x questions sorted by difficulty
df_items = pd.read_csv(f"data/raw-enem-exams/microdados_enem_{year}/DADOS/ITENS_PROVA_{year}.csv", sep=";", encoding="latin-1")

fig, axes = plt.subplots(4, 2, figsize=(10, 5))
# Set fontsize
plt.rcParams.update({"font.size": 8})
fig.suptitle("Heatmap per ENEM Exam")
for i, enem_exam in enumerate(df.ENEM_EXAM.unique()):
    sample_df = deepcopy(df[df.ENEM_EXAM == enem_exam])
    sample_df["CO_PROVA"] = sample_df["CO_PROVA"].astype(int)
    matrix_response_pattern = []
    idx_name = []
    exam = df_items[df_items.CO_PROVA == sample_df.iloc[0, :].CO_PROVA]
    # Remove english as foreign language questions
    exam = exam[exam.TP_LINGUA != 0].sort_values(by="CO_POSICAO").reset_index(drop=True)
    exam["IDX_POSICAO"] = exam.index
    exam.sort_values(by="NU_PARAM_B", inplace=True)
    exam.dropna(subset=["NU_PARAM_B"], inplace=True)
    for row in sample_df.itertuples():
        response_pattern = np.array(list(row.RESPONSE_PATTERN)).astype(int)
        response_pattern = response_pattern[exam.IDX_POSICAO.values]
        matrix_response_pattern.append(response_pattern)
        idx_name.append(row.FULL_MODEL + " " + row.LANGUAGE)

    # Change the order of idx_name
    desired_order = [
        'gpt-3.5-turbo-0613 None en', 'llama2 13b en', 'llama2 7b en', 'mistral 7b en',
        'gpt-3.5-turbo-0613 None pt-br', 'llama2 13b pt-br', 'llama2 7b pt-br', 'mistral 7b pt-br'
    ]
    new_ordering = []
    for name in desired_order:
        new_ordering.append(idx_name.index(name))
    
    matrix_response_pattern = np.array(matrix_response_pattern)[new_ordering]
    idx_name = np.array(idx_name)[new_ordering]
    
    axes[1 if i < 2 else 3, i % 2].imshow(matrix_response_pattern, cmap="binary")
    axes[1 if i < 2 else 3, i % 2].set_xticks(np.arange(len(exam.IDX_POSICAO.values)), labels=exam.IDX_POSICAO.values)
    axes[1 if i < 2 else 3, i % 2].set_yticks(np.arange(len(idx_name)), labels=idx_name, fontsize=6)
    axes[1 if i < 2 else 3, i % 2].set_xticklabels([])

    axes[0 if i < 2 else 2, i % 2].plot(range(len(exam.IDX_POSICAO.values)), exam.NU_PARAM_B.values, "-")
    axes[0 if i < 2 else 2, i % 2].set_title(enem_exam)
    axes[0 if i < 2 else 2, i % 2].set_xticks(range(0, 46, 5))

plt.tight_layout()
plt.savefig(f"plots/response-pattern-heatmap-{year}.png", dpi=800)
plt.close()

sns.catplot(
    data=df,
    x="FULL_MODEL",
    y="IRT_SCORE",
    hue="LANGUAGE",
    kind="bar",
    height=4,
    aspect=2,
    palette="Set2",
    errorbar=None,
)

plt.tight_layout()
plt.savefig(f"plots/irt-scores-language-{year}.png", dpi=800)
plt.close()

# plot IRT_SCORES per model and exam type and language
g = sns.catplot(
    data=df,
    x="FULL_MODEL",
    y="IRT_SCORE",
    hue="LANGUAGE",
    col="ENEM_EXAM",
    kind="bar",
    height=4,
    aspect=1,
    palette="Set2",
    errorbar=None,
)

plt.tight_layout()
g.set_xticklabels(rotation=10)
plt.savefig(f"plots/irt-scores-language-enem-{year}.png", dpi=800)
plt.close()


