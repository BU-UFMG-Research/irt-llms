#Seed experiments
for model in "gpt-3.5-turbo-0613" 
do
    for temperature in "0.6"
    do
        #for system_prompt_type in "few-shot"
        for system_prompt_type in "zs-cot"
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
                                #for seed in "2724839799" "224453832" "1513448043" "745130168" "730262723" 
                                for seed in "4040595804" "362978403" "418235748" "444231693" "3113980281"
                                #for seed in "2605605301" "872077901" "67119269" "57679137" "3533806160"
                                #for seed in "1687551200" "1875420408" "3728085373" "1223747668" "1140049751" 
                                #"107052334" "1153836798" "4015636583" "2147626109" "2692512316" 
                                #"2486590341" "3937635227" "131726768" "4291993814" "199464437"
                                do
                                    python3 run_enem_exam.py --model $model --temperature $temperature --system_prompt_type $system_prompt_type --enem_exam $enem_exam --exam_type $exam_type --question_order $question_order --language $language --number_options $number_options --seed $seed
                                done
                            done
                        done
                    done
                done
            done 
        done 
    done
done

# #Shuffle experiments
# for model in "gpt-3.5-turbo-0613" 
# do
#     for temperature in "0.6"
#     do
#         for system_prompt_type in "few-shot"
#         do
#             for enem_exam in "ENEM_2022_LC_CO_PROVA_1072" "ENEM_2022_MT_CO_PROVA_1082" "ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_CH_CO_PROVA_1062" "ENEM_2021_CH_CO_PROVA_886" "ENEM_2021_CN_CO_PROVA_916" "ENEM_2021_LC_CO_PROVA_896" "ENEM_2021_MT_CO_PROVA_906" "ENEM_2020_CH_CO_PROVA_574" "ENEM_2020_CN_CO_PROVA_604" "ENEM_2020_LC_CO_PROVA_584" "ENEM_2020_MT_CO_PROVA_594" "ENEM_2019_CH_CO_PROVA_520" "ENEM_2019_CN_CO_PROVA_519" "ENEM_2019_LC_CO_PROVA_521" "ENEM_2019_MT_CO_PROVA_522"
#             do
#                 for exam_type in "shuffle-0" "shuffle-1" "shuffle-2" "shuffle-3" "shuffle-4" "shuffle-5" "shuffle-6" "shuffle-7" "shuffle-8" "shuffle-9" "shuffle-10" "shuffle-11" "shuffle-12" "shuffle-13" "shuffle-14" "shuffle-15" "shuffle-16" "shuffle-17" "shuffle-18" "shuffle-19" "shuffle-20" "shuffle-21" "shuffle-22" "shuffle-23" "shuffle-24" "shuffle-25" "shuffle-26" "shuffle-27" "shuffle-28" "shuffle-29"
#                 do
#                     for question_order in "original"
#                     do
#                         for language in "en" "pt-br"
#                         do
#                             for number_options in "5"
#                             do
#                                 for seed in "2724839799"
#                                 do
#                                     python3 run_enem_exam.py --model $model --temperature $temperature --system_prompt_type $system_prompt_type --enem_exam $enem_exam --exam_type $exam_type --question_order $question_order --language $language --number_options $number_options --seed $seed
#                                 done
#                             done
#                         done
#                     done
#                 done
#             done 
#         done 
#     done
# done

