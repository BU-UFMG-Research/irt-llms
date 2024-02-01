import os

"""
LLAMA2 model config (7B, 13B, 70B):
GenerationConfig {
  "bos_token_id": 1,
  "do_sample": true,
  "eos_token_id": 2,
  "max_length": 4096,
  "pad_token_id": 0,
  "temperature": 0.6,
  "top_p": 0.9
}
"""

# Transform args into multiple for loops
models = ["llama2", "mistral"]
model_sizes = ["7b"]
temperatures = ["0.6"]
system_prompt_types = ["few-shot"]
enem_exams = ["ENEM_2022_LC_CO_PROVA_1072", "ENEM_2022_MT_CO_PROVA_1082", "ENEM_2022_CN_CO_PROVA_1092", "ENEM_2022_CH_CO_PROVA_1062", "ENEM_2021_CH_CO_PROVA_886", "ENEM_2021_CN_CO_PROVA_916", "ENEM_2021_LC_CO_PROVA_896", "ENEM_2021_MT_CO_PROVA_906", "ENEM_2020_CH_CO_PROVA_574", "ENEM_2020_CN_CO_PROVA_604", "ENEM_2020_LC_CO_PROVA_584", "ENEM_2020_MT_CO_PROVA_594", "ENEM_2019_CH_CO_PROVA_520", "ENEM_2019_CN_CO_PROVA_519", "ENEM_2019_LC_CO_PROVA_521", "ENEM_2019_MT_CO_PROVA_522"]
#exam_types = ["default"]
exam_types = ["shuffle-0", "shuffle-1", "shuffle-2", "shuffle-3", "shuffle-4", "shuffle-5", "shuffle-6", "shuffle-7", "shuffle-8", "shuffle-9", "shuffle-10", "shuffle-11", "shuffle-12", "shuffle-13", "shuffle-14", "shuffle-15", "shuffle-16", "shuffle-17", "shuffle-18", "shuffle-19", "shuffle-20", "shuffle-21", "shuffle-22", "shuffle-23", "shuffle-24", "shuffle-25", "shuffle-26", "shuffle-27", "shuffle-28", "shuffle-29"]
question_orders = ["original"]
languages = ["en", "pt-br"]
number_options = ["5"]
seeds = ["2724839799"]
#seeds = [2724839799, 224453832, 1513448043, 745130168, 730262723, 4040595804, 362978403, 418235748, 444231693, 3113980281]
count = 0

for model in models:
    for model_size in model_sizes:
        for temperature in temperatures:
            for system_prompt_type in system_prompt_types:
                for enem_exam in enem_exams:
                    for exam_type in exam_types:
                        for question_order in question_orders:
                            for language in languages:
                                for number_options in number_options:
                                    for seed in seeds:
                                        filename = f"enem-experiments-results/{model}-{model_size}-{temperature}-{system_prompt_type}-{enem_exam}-{exam_type}-{question_order}-{language}-{number_options}-{seed}.parquet"
                                        if not os.path.exists(filename):
                                            count += 1
                                            f = open("rerun-enem-exam.sh", "a")
                                            f.write(f"""
for model in "{model}"
do
    for model_size in "{model_size}"
    do
        for temperature in "{temperature}"
        do
            for system_prompt_type in "{system_prompt_type}"
            do
                for enem_exam in "{enem_exam}"
                do
                    for exam_type in "{exam_type}"
                    do
                        for question_order in "{question_order}"
                        do
                            for language in "{language}"
                            do
                                for number_options in "{number_options}"
                                do
                                    for seed in "{seed}"
                                    do
                                        params[idx]=$model$IFS$model_size$IFS$temperature$IFS$system_prompt_type$IFS$enem_exam$IFS$exam_type$IFS$question_order$IFS$language$IFS$number_options$IFS$seed
                                        ((idx++))
                                    done
                                done
                            done
                        done
                    done 
                done 
            done
        done
    done
done""")
                                            f.close()
print(f"COUNT: {count}")