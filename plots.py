import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import re
df = pd.read_csv("experiments-with-irt.csv", index_col=0)
df.drop(columns=["Unnamed: 0"], inplace=True)

# concat MODEL_NAME and MODEL_SIZE in one column
df["FULL_MODEL"] = df["MODEL_NAME"].astype(str) + " " + df["MODEL_SIZE"].astype(str)

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
plt.savefig("irt-scores-language.png")
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
plt.savefig("irt-scores-language-enem.png")
plt.close()



