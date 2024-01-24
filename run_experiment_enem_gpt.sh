for model in "gpt-3.5-turbo-0613" 
do
    for temperature in "0.6"
    do
        for system_prompt_type in "few-shot"
        do
            for enem_exam in "ENEM_2022_LC_CO_PROVA_1072" "ENEM_2022_MT_CO_PROVA_1082" "ENEM_2022_CN_CO_PROVA_1092" "ENEM_2022_CH_CO_PROVA_1062" "ENEM_2021_CH_CO_PROVA_886" "ENEM_2021_CN_CO_PROVA_916" "ENEM_2021_LC_CO_PROVA_896" "ENEM_2021_MT_CO_PROVA_906" "ENEM_2020_CH_CO_PROVA_574" "ENEM_2020_CN_CO_PROVA_604" "ENEM_2020_LC_CO_PROVA_584" "ENEM_2020_MT_CO_PROVA_594" "ENEM_2019_CH_CO_PROVA_520" "ENEM_2019_CN_CO_PROVA_519" "ENEM_2019_LC_CO_PROVA_521" "ENEM_2019_MT_CO_PROVA_522"
            do
                for exam_type in "default"
                do
                    for question_order in "original"
                    do
                        for language in "en" "pt-br"
                        do
                            for number_options in "5"
                            do
                                for seed in "2724839799" "224453832" "1513448043" "745130168" "730262723" "4040595804" "362978403" "418235748" "444231693" "3113980281"
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
