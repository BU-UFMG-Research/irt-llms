from collections import defaultdict
import pandas as pd

'''
Read all ENEM files containing human scores
'''
def read_human_data():

    dic_human_scores = defaultdict(dict)
    dic_human_itens = defaultdict(dict)
    dic_average_human_thetas_df = defaultdict(dict)

    # CH
    human_ch_2022_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2022/thetas/thetas_humans_CH_2022.csv")
    human_ch_2021_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2021/thetas/thetas_humans_CH_2021.csv")
    human_ch_2020_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2020/thetas/thetas_humans_CH_2020.csv")
    human_ch_2019_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2019/thetas/thetas_humans_CH_2019.csv")

    dic_human_scores['CH'][2022] = human_ch_2022_thetas_df
    dic_human_scores['CH'][2021] = human_ch_2021_thetas_df
    dic_human_scores['CH'][2020] = human_ch_2020_thetas_df
    dic_human_scores['CH'][2019] = human_ch_2019_thetas_df

    dic_average_human_thetas_df['CH'][2022] = human_ch_2022_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['CH'][2021] = human_ch_2021_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['CH'][2020] = human_ch_2020_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['CH'][2019] = human_ch_2019_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()

    human_itens_ch_2022_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2022/itens/human_itens_CH_1062_2022.csv")
    human_itens_ch_2021_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2021/itens/human_itens_CH_886_2021.csv")
    human_itens_ch_2020_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2020/itens/human_itens_CH_574_2020.csv")
    human_itens_ch_2019_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2019/itens/human_itens_CH_520_2019.csv")

    dic_human_itens['CH'][2022] = human_itens_ch_2022_df
    dic_human_itens['CH'][2021] = human_itens_ch_2021_df
    dic_human_itens['CH'][2020] = human_itens_ch_2020_df
    dic_human_itens['CH'][2019] = human_itens_ch_2019_df

    # MT
    human_mt_2022_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2022/thetas/thetas_humans_MT_2022.csv", low_memory=False)
    human_mt_2021_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2021/thetas/thetas_humans_MT_2021.csv")
    human_mt_2020_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2020/thetas/thetas_humans_MT_2020.csv")
    human_mt_2019_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2019/thetas/thetas_humans_MT_2019.csv")

    dic_human_scores['MT'][2022] = human_mt_2022_thetas_df
    dic_human_scores['MT'][2021] = human_mt_2021_thetas_df
    dic_human_scores['MT'][2020] = human_mt_2020_thetas_df
    dic_human_scores['MT'][2019] = human_mt_2019_thetas_df

    dic_average_human_thetas_df['MT'][2022] = human_mt_2022_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['MT'][2021] = human_mt_2021_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['MT'][2020] = human_mt_2020_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['MT'][2019] = human_mt_2019_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()

    human_itens_mt_2022_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2022/itens/human_itens_MT_1082_2022.csv")
    human_itens_mt_2021_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2021/itens/human_itens_MT_906_2021.csv")
    human_itens_mt_2020_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2020/itens/human_itens_MT_594_2020.csv")
    human_itens_mt_2019_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2019/itens/human_itens_MT_522_2019.csv")

    dic_human_itens['MT'][2022] = human_itens_mt_2022_df
    dic_human_itens['MT'][2021] = human_itens_mt_2021_df
    dic_human_itens['MT'][2020] = human_itens_mt_2020_df
    dic_human_itens['MT'][2019] = human_itens_mt_2019_df

    # CN
    human_cn_2022_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2022/thetas/thetas_humans_CN_2022.csv", low_memory=False)
    human_cn_2021_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2021/thetas/thetas_humans_CN_2021.csv", low_memory=False)
    human_cn_2020_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2020/thetas/thetas_humans_CN_2020.csv", low_memory=False)
    human_cn_2019_thetas_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2019/thetas/thetas_humans_CN_2019.csv", low_memory=False)

    dic_human_scores['CN'][2022] = human_cn_2022_thetas_df
    dic_human_scores['CN'][2021] = human_cn_2021_thetas_df
    dic_human_scores['CN'][2020] = human_cn_2020_thetas_df
    dic_human_scores['CN'][2019] = human_cn_2019_thetas_df

    dic_average_human_thetas_df['CN'][2022] = human_cn_2022_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['CN'][2021]= human_cn_2021_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['CN'][2020] = human_cn_2020_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()
    dic_average_human_thetas_df['CN'][2019] = human_cn_2019_thetas_df.groupby('CTT_SCORE')['IRT_SCORE'].mean().reset_index()

    human_itens_cn_2022_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2022/itens/human_itens_CN_1092_2022.csv")
    human_itens_cn_2021_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2021/itens/human_itens_CN_916_2021.csv")
    human_itens_cn_2020_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2020/itens/human_itens_CN_604_2020.csv")
    human_itens_cn_2019_df = pd.read_csv("C:/Users/pedro/Downloads/TRI/test_responses_humans/2019/itens/human_itens_CN_519_2019.csv")

    dic_human_itens['CN'][2022] = human_itens_cn_2022_df
    dic_human_itens['CN'][2021] = human_itens_cn_2021_df
    dic_human_itens['CN'][2020] = human_itens_cn_2020_df
    dic_human_itens['CN'][2019] = human_itens_cn_2019_df

    return dic_human_scores, dic_human_itens, dic_average_human_thetas_df

######################################################

def read_dir(directory_path):
    # Get a list of all files in the directory
    file_list = os.listdir(directory_path)
    # Initialize an empty DataFrame to store the data
    combined_data = pd.DataFrame()

    # Loop through each file in the directory
    dfs = []
    for file in file_list:
        # Construct the full file path
        file_path = os.path.join(directory_path, file)

        # Check if the item is a file (not a subdirectory)
        if os.path.isfile(file_path):
            # Read the file into a DataFrame
            current_data = pd.read_csv(file_path)  # Adjust the read method based on your file type (e.g., pd.read_excel for Excel files)

            dfs.append(current_data)
            # Append the current DataFrame to the combined DataFrame
    combined_data = pd.concat(dfs, ignore_index=True, axis=0)
    return combined_data
    
############################################################
import pandas as pd
import os
from collections import defaultdict

def read_llm_data(filepath):

    dic_scores = defaultdict(defaultdict)
    dic_itens = defaultdict(defaultdict)
    dic_logs = defaultdict(defaultdict)
    dic_test_responses = defaultdict(defaultdict)

    dic_average_theta_by_ctt_score = defaultdict(defaultdict)
    dic_average_theta_by_ctt_random_score = defaultdict(defaultdict)

    dic_random_scores = defaultdict(dict)

    for llm in ['mistral', 'llama2']:
        dic_scores[llm] = defaultdict(defaultdict)
        dic_itens[llm] = defaultdict(dict)
        dic_logs[llm] = defaultdict(dict)
        dic_average_theta_by_ctt_score[llm] = defaultdict(dict)
        dic_average_theta_by_ctt_random_score[llm] = defaultdict(dict)
        dic_test_responses[llm] = defaultdict(dict)
        dic_random_scores[llm] = defaultdict(dict)
    
        for exam in ["CH", "MT", "CN", "LC"]:
            dic_scores[llm][exam] = defaultdict(dict)
            for language in ["pt-br", "en"]:
                for prompt in ['simple-zero-shot', 'paper-nunes-2023-zero-shot']:
                    for year in [2020, 2021, 2022]:
     
                        if not os.path.exists(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/average_theta_by_score_random_sample.csv"):
                            continue
                        print('Loading...', exam, year, llm, prompt)
                
                        scores_df = pd.read_csv(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/samples_with_irt.csv")
                        itens_df = pd.read_csv(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/itens.csv")
                        average_theta_by_score_random_df = pd.read_csv(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/average_theta_by_score_random_sample.csv")
                        average_theta_by_score_df = pd.read_csv(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/average_theta_by_score_sample.csv")
                        random_scores_df = pd.read_csv(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/random_samples_with_irt.csv")

                        test_responses_df = pd.read_csv(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/aggregated/test_responses.csv")

                        log_dfs = read_dir(f"{filepath}/{exam}/{language}/{year}/{llm}/{prompt}/logs") 
        
                        dic_scores[llm][exam][prompt][year] = scores_df
                        dic_itens[llm][exam][year] = itens_df
                        dic_logs[llm][exam][year] = log_dfs

                        dic_average_theta_by_ctt_score[llm][exam][year] = average_theta_by_score_df
                        dic_average_theta_by_ctt_random_score[llm][exam][year] = average_theta_by_score_random_df
        
                        dic_test_responses[llm][exam][year] = test_responses_df
        
                        dic_random_scores[llm][exam][year] = random_scores_df
                   
    return dic_scores, dic_random_scores, dic_itens, dic_logs, dic_test_responses, dic_average_theta_by_ctt_score, dic_average_theta_by_ctt_random_score

