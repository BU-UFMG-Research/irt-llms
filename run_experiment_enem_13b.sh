#!/bin/bash -l

# Set SCC project

# Submit an array job with 22 tasks
#$ -t 1-8

# Specify hard time limit for the job.
#   The job will be aborted if it runs longer than this time.
#   The default time is 12 hours
#$ -l h_rt=4:00:00

# Give job a name
#$ -N llm-enem-13b

#$ -pe omp 16
#$ -l mem_per_core=2G

# Request 1 GPU 
#$ -l gpus=1

# Specify the minimum GPU compute capability. 
#$ -l gpu_c=8.0

declare -a params
idx=0
IFS=' ' # space is set as delimiter

# for model in "llama2"
# do
#     for model_size in "13b"
#     do
#         for temperature in "0.6"
#         do
#             for system_prompt_type in "simple" "cot"
#             do
#                 for enem_exam in "ENEM_2023_CH_CO_PROVA_0" "ENEM_2023_CN_CO_PROVA_0" "ENEM_2023_LC_CO_PROVA_0" "ENEM_2023_MT_CO_PROVA_0" "ENEM_2022_MT_CO_PROVA_1082" "ENEM_2022_LC_CO_PROVA_1072" "ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_CH_CO_PROVA_1062" "ENEM_2017_CH_CO_PROVA_408" "ENEM_2017_CN_CO_PROVA_407" "ENEM_2017_LC_CO_PROVA_409" "ENEM_2017_MT_CO_PROVA_410" "ENEM_2018_CH_CO_PROVA_464" "ENEM_2018_CN_CO_PROVA_463" "ENEM_2018_LC_CO_PROVA_465" "ENEM_2018_MT_CO_PROVA_466"
#                 do
#                     for exam_type in "default"
#                     do
#                         for question_order in "original"
#                         do
#                             for language in "pt-br" "en"
#                             do
#                                 for number_options in "5"
#                                 do
#                                     for seed in "2724839799" "224453832" "1513448043" "745130168" "730262723"
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

for model in "llama2" 
do
    for model_size in "13b"
    do
        for temperature in "0.6"
        do
            for system_prompt_type in "few-shot"
            do
                for enem_exam in "ENEM_2022_LC_CO_PROVA_1072" "ENEM_2022_MT_CO_PROVA_1082" "ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_CH_CO_PROVA_1062"
                do
                    for exam_type in "default"
                    do
                        for question_order in "original"
                        do
                            for language in "en" "pt-br"
                            do
                                for number_options in "5"
                                do
                                    for seed in "2724839799"
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
done

index=$(($SGE_TASK_ID-1))
read -ra taskinput <<< "${params[$index]}" # str is read into an array as tokens separated by IFS

source .bashrc
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
