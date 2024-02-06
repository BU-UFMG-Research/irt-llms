import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

EXAM_SUBJECT_MAPPING = {
    "CN": "Natural Sciences",
    "CH": "Humanities",
    "LC": "Languages and Codes",
    "MT": "Mathematics"
}

MODEL_NAME_SIZE_MAPPING = {
    "gpt-3.5-turbo-0613 None": "GPT-3.5",
    "llama2 13b": "LLAMA2-13B",
    "llama2 7b": "LLAMA2-7B",
    "mistral 7b": "Mistral-7B",
}

# Increase font size
plt.rcParams.update({"font.size": 10})

# Load lz data
df_llms = pd.read_parquet("enem-experiments-results-processed-with-irt-lz.parquet")
# Removing shuffle exams (for now)
df_llms = df_llms[df_llms["ENEM_EXAM_TYPE"] == "default"] 
df_humans = pd.read_parquet("full-humans-irt-lz.parquet")

# Removing "bugged" exam as Pedro did in his analysis (CO_PROVA == 693)
df_humans = df_humans[df_humans["CO_PROVA"] != 693] 
# Renaming PFscores to LZ_SCORE
df_humans = df_humans.rename(columns={"PFscores": "LZ_SCORE"})

# Combine 'EXAM_YEAR' and 'EXAM_SUBJECT' in a column
df_llms["EXAM_YEAR_SUBJECT"] = df_llms["EXAM_YEAR"].astype(str) + " " + df_llms["EXAM_SUBJECT"].map(EXAM_SUBJECT_MAPPING)
df_humans["EXAM_YEAR_SUBJECT"] = df_humans["EXAM_YEAR"].astype(str) + " " + df_humans["EXAM_SUBJECT"].map(EXAM_SUBJECT_MAPPING)

# Combine 'MODEL_NAME' and 'MODEL_SIZE in a column
df_llms["MODEL_NAME_SIZE"] = df_llms["MODEL_NAME"] + " " + df_llms["MODEL_SIZE"].astype(str)
df_llms["MODEL_NAME_SIZE"] = df_llms["MODEL_NAME_SIZE"].map(MODEL_NAME_SIZE_MAPPING)

# Constant columns for humans
df_humans["MODEL_NAME_SIZE"] = "Humans"
df_humans["LANGUAGE"] = "pt-br"

# Adding the source to both dataframes
df_llms["SOURCE"] = "LLMs"
df_humans["SOURCE"] = "Humans"

# Combine the data in a single dataframe using a subset of columns and a new column to identify the source
df_llms = df_llms[["LZ_SCORE", "EXAM_YEAR_SUBJECT", "MODEL_NAME_SIZE", "EXAM_YEAR", "LANGUAGE"]]
df_humans = df_humans[["LZ_SCORE", "EXAM_YEAR_SUBJECT", "MODEL_NAME_SIZE", "EXAM_YEAR", "LANGUAGE"]]
df = pd.concat([df_llms, df_humans])

# Casting EXAM_YEAR to int
df["EXAM_YEAR"] = df["EXAM_YEAR"].astype(int)

# Plot lz data
# Each EXAM_YEAR_SUBJECT is a plot
# Each Source is a hue in the plot
# Plot everything together for each year
for year in df["EXAM_YEAR"].unique():
    print(f"Plotting year {year}")
    df_year = df[(df["EXAM_YEAR"] == year)]
    g = sns.displot(df_year, x="LZ_SCORE", hue="MODEL_NAME_SIZE", row="EXAM_YEAR_SUBJECT", col="LANGUAGE", kind="kde", common_norm=False, common_grid=True)
    g.set_axis_labels("LZ Score", "Density")
    g.set_titles("{row_name}\n{col_name}")
    # Making all the x-axis labels appear
    for ax in g.axes.flat:
        ax.set_xticks(ax.get_xticks(), labels=[f"{x:.2f}" for x in ax.get_xticks()])
    plt.savefig(f"plots/lz_plots_{year}.pdf", dpi=800)
    plt.close()



