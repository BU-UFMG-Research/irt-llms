from copy import deepcopy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import argparse

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rc('font', size=6)

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

df = pd.read_parquet("enem-experiments-results-processed-with-irt-lz.parquet")
df = df[df.ENEM_EXAM.str.contains(f"{year}")]

# concat MODEL_NAME and MODEL_SIZE in one column
df["FULL_MODEL"] = df["MODEL_NAME"].astype(str) + " " + df["MODEL_SIZE"].astype(str)

df["ENEM_EXAM_YEAR"] = df["ENEM_EXAM"].apply(lambda x: x.split("_")[1])
df["ENEM_EXAM_CODE"] = df["ENEM_EXAM"].apply(lambda x: x.split("_")[2])

df["ENEM_EXAM"].replace(ENEM_MAPPING_NAME, inplace=True)

# Plot heatmap of models x questions sorted by difficulty
df_items = pd.read_csv(f"data/raw-enem-exams/microdados_enem_{year}/DADOS/ITENS_PROVA_{year}.csv", sep=";", encoding="latin-1")

#fig, axes = plt.subplots(4, 2, figsize=(7, 3.5), height_ratios=[0.5, 2, 0.5, 2])
for i, enem_exam in enumerate(df.ENEM_EXAM.unique()):
    fig, axes = plt.subplots(2, 1, figsize=(2.5, 1.75), height_ratios=[0.5, 1], gridspec_kw = {'hspace':0.3})
    # Set fontsize
    plt.rcParams.update({"font.size": 6})
    sample_df = deepcopy(df[df.ENEM_EXAM == enem_exam])
    sample_df["CO_PROVA"] = sample_df["CO_PROVA"].astype(int)
    matrix_response_pattern = []
    avg_lz_scores = []
    std_lz_scores = []
    idx_name = []
    exam = df_items[df_items.CO_PROVA == sample_df.iloc[0, :].CO_PROVA]
    # Remove english as foreign language questions
    exam = exam[exam.TP_LINGUA != 0].sort_values(by="CO_POSICAO").reset_index(drop=True)
    exam["IDX_POSICAO"] = exam.index
    exam.sort_values(by="NU_PARAM_B", inplace=True)
    # Remove questions with no difficulty (NaN)
    exam.dropna(subset=["NU_PARAM_B"], inplace=True)
    full_models = sample_df.FULL_MODEL.unique()
    # Change the order of the models (mixtral (last one) after GPT-3.5 (first one))
    full_models = list(full_models)
    full_models.insert(1, full_models.pop(-1))
    for full_model in full_models:
        for language in sample_df.LANGUAGE.unique():
            sample_df_model = sample_df[(sample_df.FULL_MODEL == full_model) & (sample_df.LANGUAGE == language)]
            avg_lz = sample_df_model.LZ_SCORE.mean()
            avg_lz_scores.append(avg_lz)
            std_lz = sample_df_model.LZ_SCORE.std()
            std_lz_scores.append(std_lz)
            response_pattern_matrix = np.array(list(sample_df_model.RESPONSE_PATTERN.apply(lambda x: list(x))))
            # Convert each response pattern to a list of integers
            response_pattern_matrix = response_pattern_matrix.astype(int)
            if response_pattern_matrix.shape != (30, 45):
                print(f"Error in {full_model} {language}")
                print(response_pattern_matrix.shape)
                print(response_pattern_matrix)
                raise SystemExit()
            # Compute the average of the response pattern divided by the number of executions (rows)
            response_pattern = np.mean(response_pattern_matrix, axis=0)
            # Sort the response pattern by the difficulty of the question
            response_pattern = response_pattern[exam.IDX_POSICAO.values]
            matrix_response_pattern.append(response_pattern)
            idx_name.append(full_model + " " + language)
        
    # Remapping idx_names to pretty names
    idx_name = [name.replace("gpt-3.5-turbo-0613 None en", "GPT-3.5 (EN)") for name in idx_name]
    idx_name = [name.replace("llama2 13b en", "LLaMA-13B (EN)") for name in idx_name]
    idx_name = [name.replace("llama2 7b en", "LLaMA-7B (EN)") for name in idx_name]
    idx_name = [name.replace("mistral 7b en", "Mistral-7B (EN)") for name in idx_name]
    idx_name = [name.replace("mistral 8x7b en", "Mixtral-8x7B (EN)") for name in idx_name]
    idx_name = [name.replace("gpt-3.5-turbo-0613 None pt-br", "GPT-3.5 (PT-BR)") for name in idx_name]
    idx_name = [name.replace("llama2 13b pt-br", "LLaMA-13B (PT-BR)") for name in idx_name]
    idx_name = [name.replace("llama2 7b pt-br", "LLaMA-7B (PT-BR)") for name in idx_name]
    idx_name = [name.replace("mistral 7b pt-br", "Mistral-7B (PT-BR)") for name in idx_name]
    idx_name = [name.replace("mistral 8x7b pt-br", "Mixtral-8x7B (PT-BR)") for name in idx_name]

    n_questions = len(exam.IDX_POSICAO.values)
    min_item_difficulty = np.min(exam.NU_PARAM_B.values)
    max_item_difficulty = np.max(exam.NU_PARAM_B.values)
    
    axes[1].imshow(matrix_response_pattern, cmap="gray_r", aspect="auto")
    axes[1].set_xticks(np.arange(len(exam.IDX_POSICAO.values)), labels=exam.IDX_POSICAO.values)
    # axes[1].set_xticklabels(range(1, n_questions+1, 1), fontsize=6)
    # axes[1].set_xlim(xmin=1, xmax=n_questions)
    axes[1].set_yticks(np.arange(len(idx_name)), labels=idx_name, fontsize=6)
    axes[1].set_xticklabels([])
    axes[1].set_xlabel("Question", fontsize=6, labelpad=-3)

    # Hide some of the xtickslabels
    for idx, label in enumerate(axes[1].xaxis.get_ticklabels()):
        if idx == 0 or idx == n_questions-1:
            continue
        label.set_visible(False)


    # Add the average lz scores as text in the end of each row of the heatmap
    for j, (avg_lz, std_lz) in enumerate(zip(avg_lz_scores, std_lz_scores)):
        if avg_lz < 0:
            axes[1].text(n_questions+1, j, f"{avg_lz:.2f} ({std_lz:.2f})", fontsize=6, va="center")
        else:
            axes[1].text(n_questions+1, j, f" {avg_lz:.2f} ({std_lz:.2f})", fontsize=6, va="center")
        
    axes[0].plot(range(1, n_questions+1), exam.NU_PARAM_B.values, "-")
    axes[0].set_xticks(range(1, n_questions+1, 1))
    axes[0].set_xticklabels(range(1, n_questions+1, 1), fontsize=6)
    axes[0].set_yticks(axes[0].get_yticks())
    axes[0].set_yticklabels(axes[0].get_yticks(), fontsize=6)
    axes[0].set_ylabel("Item\nDifficulty", fontsize=6)
    axes[0].set_xlim(xmin=1, xmax=n_questions)
    axes[0].set_ylim(ymin=min_item_difficulty, ymax=max_item_difficulty)

    # Hide some of the xtickslabels
    for idx, label in enumerate(axes[0].xaxis.get_ticklabels()):
        if idx == 0 or idx == n_questions-1:
            continue
        label.set_visible(False)

    # Both are unique in this case
    if len(sample_df.ENEM_EXAM_CODE.unique()) > 1:
        print("More than one code")
        raise SystemExit()

    if len(sample_df.ENEM_EXAM_YEAR.unique()) > 1:
        print("More than one year")
        raise SystemExit()

    enem_code = sample_df.ENEM_EXAM_CODE.unique()[0]
    enem_year = sample_df.ENEM_EXAM_YEAR.unique()[0]

    plt.savefig(f"plots/response-pattern-heatmap-{enem_year}-{enem_code}.pdf", bbox_inches='tight', pad_inches=0.05, dpi=800)
    plt.close()

