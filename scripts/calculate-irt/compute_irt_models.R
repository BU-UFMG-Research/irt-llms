# https://stats.stackexchange.com/questions/34119/estimating-ability-using-irt-when-the-model-parameters-are-known
# https://rdrr.io/cran/mirtCAT/man/generate.mirt_object.html
#install.packages("mirtCAT")
library(mirtCAT)
library(arrow)

# response_pattern_filepath = "../../enem-experiments-results-processed-cot.parquet"
# filename <- "../../enem-experiments-results-processed-cot-with-irt.parquet"
response_pattern_filepath = "../../enem-experiments-results-processed.parquet"
filename <- "../../enem-experiments-results-processed-with-irt.parquet"
# response_pattern_filepath = "../../enem-experiments-results-shuffle-processed.parquet"
# filename <- "../../enem-experiments-results-shuffle-processed-with-irt.parquet"
response_patterns <- read_parquet(response_pattern_filepath)
response_patterns$ID <- 1:nrow(response_patterns)

for (year in 2019:2022) {
  print(paste0("Processing year: ", year))

  file_itens_prova = paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/ITENS_PROVA_", year, ".csv")

  item_params <- read.csv(file_itens_prova, header = TRUE, sep=';')
  # Skip English itens.
  item_params <- subset(item_params, TP_LINGUA != '0' | is.na(TP_LINGUA))
  item_params <- item_params[order(item_params$CO_POSICAO, decreasing = FALSE), ]

  print("Loaded item params")
  dim(item_params)

  item_params_mirt <- data.frame(matrix(ncol = 9, nrow = 0))
  colnames(item_params_mirt) <- c("CO_PROVA", "CO_POSICAO", "a1", "d", "g", "u", "NU_PARAM_A", "NU_PARAM_B", "NU_PARAM_C")

  for (i in 1:nrow(item_params)) {
    row <- item_params[i, ]
    mirt_input <- traditional2mirt(c('a'=row$NU_PARAM_A, 'b'=row$NU_PARAM_B, 'g'=row$NU_PARAM_C, 'u'=1), cls='3PL')

    item_params_mirt[i, ] <- c(row$CO_PROVA, row$CO_POSICAO, mirt_input, row$NU_PARAM_A, row$NU_PARAM_B, row$NU_PARAM_C)
  }

  item_params <- item_params_mirt

  #########################################################

  print("Loading response patterns...")
  
  # Filter in response_patterns: ENEM_EXAM contains 2022 substring
  response_patterns_current_year <- subset(response_patterns, grepl(year, ENEM_EXAM))

  # PROVA is in ENEM_EXAM attribute from response_patterns
  PROVA <- response_patterns_current_year$CO_PROVA

  print("Colnames Response Patterns")
  colnames(response_patterns_current_year)

  print("Dimensions response patterns")
  dim(response_patterns_current_year)

  ###########################################################
  model_list <- list()
  
  for (i in 1:nrow(response_patterns_current_year)) {    
    enem_irt_score = response_patterns_current_year$NU_NOTA[i]
    str_response_pattern = response_patterns_current_year$RESPONSE_PATTERN[i]
    ctt_score = response_patterns_current_year$CTT_SCORE[i]
    CODIGO_PROVA = response_patterns_current_year$CO_PROVA[i]
    
    item_params_prova <- subset(item_params, CO_PROVA == CODIGO_PROVA)

    # Sort item_params_prova by CO_POSICAO
    item_params_prova <- item_params_prova[order(item_params_prova$CO_POSICAO, decreasing = FALSE), ]
    
    if (is.null(model_list[[toString(CODIGO_PROVA)]]))
    {
      # discrimination, easiness, and guessing values
      item_params_df <- data.frame(a1 = item_params_prova$a1,
                                  d = item_params_prova$d,
                                  g =  item_params_prova$g)
      
      model_list[[toString(CODIGO_PROVA)]] <- generate.mirt_object(item_params_df, itemtype = '3PL')
      print("LOADED MODEL")
    }
    
    # Split the string into individual characters
    char_vector <- unlist(strsplit(str_response_pattern, ""))
    # Convert the characters to numeric values (0 or 1)
    response_pattern <- as.numeric(char_vector)

    min_correct_b = 1000
    max_correct_b = -1000
    
    correct_bs <- c()
    count_correct_bs = 0
    
    incorrect_bs <- c()
    count_incorrect_bs = 0
    
    for (r_idx in 1:length(response_pattern)) {
      r = response_pattern[r_idx]
      nu_param_b = item_params_prova$NU_PARAM_B[r_idx]

      if(!is.na(nu_param_b)) {
      
        if (r == 1){
          count_correct_bs =  count_correct_bs + 1
          correct_bs[count_correct_bs] <- nu_param_b
        }
        if (r == 0){
          count_incorrect_bs =  count_incorrect_bs + 1
          incorrect_bs[count_incorrect_bs] <- nu_param_b
        }
        
        if (r == 1 & nu_param_b > max_correct_b) {
          max_correct_b = nu_param_b
        }
        if (r == 1 & nu_param_b < min_correct_b) {
          min_correct_b = nu_param_b
        }
      }
    }

    score_and_error = fscores(model_list[[toString(CODIGO_PROVA)]], method="EAP", response.pattern = response_pattern)  

    # if enem_irt_score is NULL, then use the score_and_error[1] * 100 + 500
    if (is.null(enem_irt_score)) {
      enem_irt_score = score_and_error[1] * 100 + 500
    }

    # Add them to the response_patterns dataframe, using the ID to index
    id_current = response_patterns_current_year$ID[i]
    response_patterns$ENEM_IRT_SCORE[id_current] <- enem_irt_score
    response_patterns$CTT_SCORE[id_current] <- ctt_score
    response_patterns$IRT_SCORE[id_current] <- score_and_error[1]
    response_patterns$IRT_SCORE_SE[id_current] <- score_and_error[2]
    response_patterns$MIN_CORRECT_B[id_current] <- min_correct_b
    response_patterns$MAX_CORRECT_B[id_current] <- max_correct_b
    response_patterns$MEAN_CORRECT_B[id_current] <- mean(correct_bs)
    response_patterns$MEAN_INCORRECT_B[id_current] <- mean(incorrect_bs)  
  }
}

print("Saving response patterns with IRT scores...")
# Remove ID column
response_patterns$ID <- NULL
# Save response_patterns with IRT scores
write_parquet(response_patterns, filename)




