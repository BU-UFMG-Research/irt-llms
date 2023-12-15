#!/bin/bash -l

# Set SCC project

# Submit an array job with 720 tasks
#$ -t 1-1

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

for model in "llama2"
do
    for model_size in "13b"
    do
        for enem_exam in "ENEM_2022_MT_CO_PROVA_1082"
		do
            for system_prompt_type in "cot"
            do
                params[idx]=$model$IFS$model_size$IFS$enem_exam$IFS$system_prompt_type
                ((idx++))
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

python3 run_enem_exam.py --model ${taskinput[0]} --model_size ${taskinput[1]} --enem_exam ${taskinput[2]} --system_prompt_type ${taskinput[3]} --max_time "600"

# index=1
# for i in "${params[@]}"; do # access each element of array
#    echo "$index: $i"
#    index=$((index+1))
# done
