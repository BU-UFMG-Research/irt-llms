# https://stats.stackexchange.com/questions/34119/estimating-ability-using-irt-when-the-model-parameters-are-known
# https://rdrr.io/cran/mirtCAT/man/generate.mirt_object.html
#install.packages("mirtCAT")
library(mirtCAT)
library(arrow)
library(PerFit)

# LLMs performance
# response_pattern_filepath <- "../../enem-experiments-results-processed-cot-with-irt.parquet"
# filename <- "../../enem-experiments-results-processed-cot-with-irt-lz.parquet"

response_pattern_filepath <- "../../enem-experiments-results-processed-with-irt.parquet"
filename <- "../../enem-experiments-results-processed-with-irt-lz.parquet"
# response_pattern_filepath <- "../../enem-experiments-results-shuffle-processed-with-irt.parquet"
# filename <- "../../enem-experiments-results-shuffle-processed-with-irt-lz.parquet"
response_patterns <- read_parquet(response_pattern_filepath)
response_patterns$ID <- 1:nrow(response_patterns)
# Initialize the LZ_SCORE column
response_patterns$LZ_SCORE <- NA

print("Compute lz scores for LLMs")
#for (year in 2019:2022) {
for (year in 2022) {
  print(paste0("Processing year: ", year))

  # Filter in response_patterns: ENEM_EXAM contains 2022 substring
  response_patterns_year <- subset(response_patterns, grepl(year, ENEM_EXAM))
  # print unique ENEM_EXAM
  enem_exams <- unique(response_patterns_year$ENEM_EXAM)
  co_provas <- unique(response_patterns_year$CO_PROVA)
  
  # Item params
  file_itens_prova <- paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/ITENS_PROVA_", year, ".csv")
  item_params <- read.csv(file_itens_prova, header = TRUE, sep=';')
  # Skip English itens.
  item_params <- subset(item_params, TP_LINGUA != "0" | is.na(TP_LINGUA))
  item_params <- item_params[order(item_params$CO_POSICAO, decreasing = FALSE), ]

  item_params_mirt <- data.frame(matrix(ncol = 9, nrow = 0))
  colnames(item_params_mirt) <- c("CO_PROVA", "CO_POSICAO", "a1", "d", "g", "u", "NU_PARAM_A", "NU_PARAM_B", "NU_PARAM_C")

  for (i in 1:nrow(item_params)) {
    row <- item_params[i, ]
    mirt_input <- traditional2mirt(c('a'=row$NU_PARAM_A, 'b'=row$NU_PARAM_B, 'g'=row$NU_PARAM_C, 'u'=1), cls='3PL')

    item_params_mirt[i, ] <- c(row$CO_PROVA, row$CO_POSICAO, mirt_input, row$NU_PARAM_A, row$NU_PARAM_B, row$NU_PARAM_C)
  }

  item_params <- item_params_mirt

  model_list <- list()

  # for each CO_PROVA, create a model
  for (co_prova in co_provas) {
      if (is.null(model_list[[toString(co_prova)]])) {
        item_params_prova <- subset(item_params, CO_PROVA == co_prova)

        # Sort item_params_prova by CO_POSICAO
        item_params_prova <- item_params_prova[order(item_params_prova$CO_POSICAO, decreasing = FALSE), ]

        # Load the model
        item_params_df <- data.frame(a1 = item_params_prova$a1,
                                          d = item_params_prova$d,
                                          g =  item_params_prova$g)
              
        model_list[[toString(co_prova)]] <- generate.mirt_object(item_params_df, itemtype = '3PL')

        print("Loaded model")
    }

    # # Filter in response_patterns: CO_PROVA == CO_PROVA
    response_patterns_co_prova <- subset(response_patterns_year, CO_PROVA == co_prova)

    # Getting the exam subject (unique per CO_PROVA)
    exam_subject <- unique(response_patterns_co_prova$EXAM_SUBJECT)

    # Getting the enem_exam (unique per CO_PROVA)
    enem_exam <- unique(response_patterns_co_prova$ENEM_EXAM)

    # print("Computing lz scores for LLMs")
    # Compute lz scores for LLMs
    llm_item_scores_matrix <- matrix(nrow = nrow(response_patterns_co_prova), ncol = 45)
    for (i in 1:nrow(response_patterns_co_prova)) {
      str_response_pattern <- response_patterns_co_prova$RESPONSE_PATTERN[i]
      # Split the string into individual characters
      char_vector <- unlist(strsplit(str_response_pattern, ""))
      # Convert the characters to numeric values (0 or 1)
      response_pattern <- as.numeric(char_vector)
      for (j in 1:length(response_pattern)) {
        llm_item_scores_matrix[i, j] <- response_pattern[j]
      }
    }

    irt_scores <- c()

    for (i in 1:nrow(response_patterns_co_prova)) {
      irt_scores[i] <- response_patterns_co_prova$IRT_SCORE[i]
    }

    irt_scores <- as.numeric(irt_scores)

    itests <- coef(model_list[[toString(co_prova)]], IRTpars = TRUE, simplify = TRUE)$items[, c("a", "b", "g")]
    na_indexes <- which(is.na(itests[, c("a")]))

    # Remove the indexes with NA values
    if (length(na_indexes) > 0) {
      print("Removing NA indexes")
      itests <- itests[-na_indexes, ]
      llm_item_scores_matrix <- llm_item_scores_matrix[, -na_indexes]
    }

    # Compute lz scores for LLMs
    lz_stat <- lz(llm_item_scores_matrix, Ability=irt_scores, IP=itests)

    # Convert lz_stat$PFscores to a plain list without the PFscores name

    # Addind it back to response_patterns using the ID from response_patterns_co_prova
    for (i in 1:nrow(response_patterns_co_prova)) {
      id_current <- response_patterns_co_prova$ID[i]
      # Find index where response_patterns$ID == id_current
      idx <- which(response_patterns$ID == id_current)
      response_patterns$LZ_SCORE[idx] <- lz_stat$PFscores[i, ]
    }
  }
}

# Save response_patterns with LZ_SCORE
write_parquet(response_patterns, filename)