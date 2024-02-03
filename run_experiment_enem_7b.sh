#!/bin/bash -l

# Set SCC project

# Submit an array job with 44 tasks
#$ -t 1-5

# Specify hard time limit for the job.
#   The job will be aborted if it runs longer than this time.
#   The default time is 12 hours
#$ -l h_rt=4:00:00

# Give job a name
#$ -N llm-enem-7b

#$ -pe omp 16
#$ -l mem_per_core=2G

# Request 1 GPU 
#$ -l gpus=1

# Specify the minimum GPU compute capability. 
#$ -l gpu_c=8.0

declare -a params
idx=0
IFS=' ' # space is set as delimiter

# #Seed experiments
# for model in "mistral" "llama2" 
# do
#     for model_size in "7b"
#     do
#         for temperature in "0.6"
#         do
#             for system_prompt_type in "zs-cot" #"few-shot"
#             do
#                 for enem_exam in "ENEM_2022_LC_CO_PROVA_1072" "ENEM_2022_MT_CO_PROVA_1082" "ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_CH_CO_PROVA_1062" "ENEM_2021_CH_CO_PROVA_886" "ENEM_2021_CN_CO_PROVA_916" "ENEM_2021_LC_CO_PROVA_896" "ENEM_2021_MT_CO_PROVA_906" "ENEM_2020_CH_CO_PROVA_574" "ENEM_2020_CN_CO_PROVA_604" "ENEM_2020_LC_CO_PROVA_584" "ENEM_2020_MT_CO_PROVA_594" "ENEM_2019_CH_CO_PROVA_520" "ENEM_2019_CN_CO_PROVA_519" "ENEM_2019_LC_CO_PROVA_521" "ENEM_2019_MT_CO_PROVA_522"
#                 do
#                     for exam_type in "default"
#                     do
#                         for question_order in "original"
#                         do
#                             for language in "en" "pt-br"
#                             do
#                                 for number_options in "5"
#                                 do
#                                     for seed in "2724839799" "224453832" "1513448043" "745130168" "730262723" "4040595804" "362978403" "418235748" "444231693" "3113980281" "2605605301" "872077901" "67119269" "57679137" "3533806160" "1687551200" "1875420408" "3728085373" "1223747668" "1140049751" "107052334" "1153836798" "4015636583" "2147626109" "2692512316" "2486590341" "3937635227" "131726768" "4291993814" "199464437"
#                                     do
#                                         params[idx]=$model$IFS$model_size$IFS$temperature$IFS$system_prompt_type$IFS$enem_exam$IFS$exam_type$IFS$question_order$IFS$language$IFS$number_options$IFS$seed
#                                         ((idx++))
#                                     done
#                                 done
#                             done
#                         done
#                     done
#                 done 
#             done 
#         done
#     done
# done

# # Shuffle experiments
# for model in "mistral" "llama2" 
# do
#     for model_size in "7b"
#     do
#         for temperature in "0.6"
#         do
#             for system_prompt_type in "few-shot"
#             do
#                 for enem_exam in "ENEM_2022_LC_CO_PROVA_1072" "ENEM_2022_MT_CO_PROVA_1082" "ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_CH_CO_PROVA_1062" "ENEM_2021_CH_CO_PROVA_886" "ENEM_2021_CN_CO_PROVA_916" "ENEM_2021_LC_CO_PROVA_896" "ENEM_2021_MT_CO_PROVA_906" "ENEM_2020_CH_CO_PROVA_574" "ENEM_2020_CN_CO_PROVA_604" "ENEM_2020_LC_CO_PROVA_584" "ENEM_2020_MT_CO_PROVA_594" "ENEM_2019_CH_CO_PROVA_520" "ENEM_2019_CN_CO_PROVA_519" "ENEM_2019_LC_CO_PROVA_521" "ENEM_2019_MT_CO_PROVA_522"
#                 do
#                     for exam_type in "shuffle-0" "shuffle-1" "shuffle-2" "shuffle-3" "shuffle-4" "shuffle-5" "shuffle-6" "shuffle-7" "shuffle-8" "shuffle-9" "shuffle-10" "shuffle-11" "shuffle-12" "shuffle-13" "shuffle-14" "shuffle-15" "shuffle-16" "shuffle-17" "shuffle-18" "shuffle-19" "shuffle-20" "shuffle-21" "shuffle-22" "shuffle-23" "shuffle-24" "shuffle-25" "shuffle-26" "shuffle-27" "shuffle-28" "shuffle-29"
#                     do
#                         for question_order in "original"
#                         do
#                             for language in "en" "pt-br"
#                             do
#                                 for number_options in "5"
#                                 do
#                                     for seed in "2724839799"
#                                     do
#                                         params[idx]=$model$IFS$model_size$IFS$temperature$IFS$system_prompt_type$IFS$enem_exam$IFS$exam_type$IFS$question_order$IFS$language$IFS$number_options$IFS$seed
#                                         ((idx++))
#                                     done
#                                 done
#                             done
#                         done
#                     done
#                 done 
#             done 
#         done
#     done
# done

index=$(($SGE_TASK_ID-1))
read -ra taskinput <<< "${params[$index]}" # str is read into an array as tokens separated by IFS

module load python3/3.10.12
module load gcc/12.2
module load cuda/11.8
source /project/mcnet/venv3.10/bin/activate
cd /projectnb/mcnet/irt-llms

python3 run_enem_exam.py --model ${taskinput[0]} --model_size ${taskinput[1]} --temperature ${taskinput[2]} --system_prompt_type ${taskinput[3]} --enem_exam ${taskinput[4]} --exam_type ${taskinput[5]} --question_order ${taskinput[6]} --language ${taskinput[7]} --number_options ${taskinput[8]} --seed ${taskinput[9]}

# index=1
# for i in "${params[@]}"; do # access each element of array
#    echo "$index: $i"
#    index=$((index+1))
# done