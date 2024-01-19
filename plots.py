import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import re

from exam import ENEM
df = pd.read_csv("experiments-with-irt.csv", index_col=0)
df.drop(columns=["Unnamed: 0"], inplace=True)

# concat MODEL_NAME and MODEL_SIZE in one column
df["FULL_MODEL"] = df["MODEL_NAME"].astype(str) + " " + df["MODEL_SIZE"].astype(str)

# Plot heatmap of models x questions sorted by difficulty
df_items = pd.read_csv("data/raw-enem-exams/microdados_enem_2022/DADOS/ITENS_PROVA_2022.csv", sep=";", encoding="latin-1")

fig, axes = plt.subplots(4, 2, figsize=(10, 5))
# Set fontsize
plt.rcParams.update({"font.size": 8})
fig.suptitle("Heatmap per ENEM Exam")
for i, enem_exam in enumerate(df.ENEM_EXAM.unique()):
    sample_df = df[df.ENEM_EXAM == enem_exam]
    matrix_response_pattern = []
    idx_name = []
    exam = df_items[df_items.CO_PROVA == sample_df.iloc[0, :].CO_PROVA].sort_values(by="CO_POSICAO").reset_index(drop=True)
    exam["IDX_POSICAO"] = exam.index
    exam.sort_values(by="NU_PARAM_B", inplace=True)
    exam.dropna(subset=["NU_PARAM_B"], inplace=True)
    #print(exam[["NU_PARAM_B", "CO_POSICAO", "IDX_POSICAO"]])
    for row in sample_df.itertuples():
        response_pattern = np.array(list(row.RESPONSE_PATTERN)).astype(int)
        response_pattern = response_pattern[exam.IDX_POSICAO.values]
        matrix_response_pattern.append(response_pattern)
        idx_name.append(row.FULL_MODEL + " " + row.LANGUAGE)
    
    axes[1 if i < 2 else 3, i % 2].imshow(matrix_response_pattern, cmap="binary")
    axes[1 if i < 2 else 3, i % 2].set_xticks(np.arange(len(exam.IDX_POSICAO.values)), labels=exam.IDX_POSICAO.values)
    axes[1 if i < 2 else 3, i % 2].set_yticks(np.arange(len(idx_name)), labels=idx_name, fontsize=6)
    axes[1 if i < 2 else 3, i % 2].set_xticklabels([])

    axes[0 if i < 2 else 2, i % 2].plot(range(len(exam.IDX_POSICAO.values)), exam.NU_PARAM_B.values, "-")
    axes[0 if i < 2 else 2, i % 2].set_title(enem_exam)

plt.tight_layout()
plt.savefig("plots/response-pattern-heatmap.png", dpi=800)
plt.close()

df["ENEM_EXAM"].replace(
    {
        "ENEM_2022_CH_CO_PROVA_1062": "2022 Humanities",
        "ENEM_2022_CN_CO_PROVA_1092": "2022 Natural Sciences",
        "ENEM_2022_LC_CO_PROVA_1072": "2022 Languages and Codes",
        "ENEM_2022_MT_CO_PROVA_1082": "2022 Mathematics",
    },
    inplace=True,
)

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
plt.savefig("plots/irt-scores-language.png", dpi=800)
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
# # set title getting the col_name and finding CH, CN, LC, MT
# for ax in g.axes.flat:
#     ax.set_title(re.findall(r"(CH | CN | LC | MT).*", ax.get_title())[-1])
g.set_xticklabels(rotation=10)
plt.savefig("plots/irt-scores-language-enem.png", dpi=800)
plt.close()


