# https://stats.stackexchange.com/questions/34119/estimating-ability-using-irt-when-the-model-parameters-are-known
# https://rdrr.io/cran/mirtCAT/man/generate.mirt_object.html
#install.packages("mirtCAT")
library(mirtCAT)
library(arrow)
library(PerFit)

# # LLMs performance
# response_pattern_filepath <- "../../enem-experiments-results-processed-with-irt.parquet"
# response_patterns <- read_parquet(response_pattern_filepath)
# response_patterns$ID <- 1:nrow(response_patterns)
# # Initialize the LZ_SCORE column
# response_patterns$LZ_SCORE <- NA

# print("Compute lz scores for LLMs")
# for (year in 2019:2022) {
#   print(paste0("Processing year: ", year))

#   # Filter in response_patterns: ENEM_EXAM contains 2022 substring
#   response_patterns_year <- subset(response_patterns, grepl(year, ENEM_EXAM))
#   # print unique ENEM_EXAM
#   enem_exams <- unique(response_patterns_year$ENEM_EXAM)
#   co_provas <- unique(response_patterns_year$CO_PROVA)
  
#   # Item params
#   file_itens_prova <- paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/ITENS_PROVA_", year, ".csv")
#   item_params <- read.csv(file_itens_prova, header = TRUE, sep=';')
#   # Skip English itens.
#   item_params <- subset(item_params, TP_LINGUA != "0" | is.na(TP_LINGUA))
#   item_params <- item_params[order(item_params$CO_POSICAO, decreasing = FALSE), ]

#   item_params_mirt <- data.frame(matrix(ncol = 9, nrow = 0))
#   colnames(item_params_mirt) <- c("CO_PROVA", "CO_POSICAO", "a1", "d", "g", "u", "NU_PARAM_A", "NU_PARAM_B", "NU_PARAM_C")

#   for (i in 1:nrow(item_params)) {
#     row <- item_params[i, ]
#     mirt_input <- traditional2mirt(c('a'=row$NU_PARAM_A, 'b'=row$NU_PARAM_B, 'g'=row$NU_PARAM_C, 'u'=1), cls='3PL')

#     item_params_mirt[i, ] <- c(row$CO_PROVA, row$CO_POSICAO, mirt_input, row$NU_PARAM_A, row$NU_PARAM_B, row$NU_PARAM_C)
#   }

#   item_params <- item_params_mirt

#   model_list <- list()

#   # for each CO_PROVA, create a model
#   for (co_prova in co_provas) {
#       if (is.null(model_list[[toString(co_prova)]])) {
#         item_params_prova <- subset(item_params, CO_PROVA == co_prova)

#         # Sort item_params_prova by CO_POSICAO
#         item_params_prova <- item_params_prova[order(item_params_prova$CO_POSICAO, decreasing = FALSE), ]

#         # Load the model
#         item_params_df <- data.frame(a1 = item_params_prova$a1,
#                                           d = item_params_prova$d,
#                                           g =  item_params_prova$g)
              
#         model_list[[toString(co_prova)]] <- generate.mirt_object(item_params_df, itemtype = '3PL')

#         print("Loaded model")
#     }

#     # # Filter in response_patterns: CO_PROVA == CO_PROVA
#     response_patterns_co_prova <- subset(response_patterns_year, CO_PROVA == co_prova)

#     # Getting the exam subject (unique per CO_PROVA)
#     exam_subject <- unique(response_patterns_co_prova$EXAM_SUBJECT)

#     # Getting the enem_exam (unique per CO_PROVA)
#     enem_exam <- unique(response_patterns_co_prova$ENEM_EXAM)

#     # print("Computing lz scores for LLMs")
#     # Compute lz scores for LLMs
#     llm_item_scores_matrix <- matrix(nrow = nrow(response_patterns_co_prova), ncol = 45)
#     for (i in 1:nrow(response_patterns_co_prova)) {
#       str_response_pattern <- response_patterns_co_prova$RESPONSE_PATTERN[i]
#       # Split the string into individual characters
#       char_vector <- unlist(strsplit(str_response_pattern, ""))
#       # Convert the characters to numeric values (0 or 1)
#       response_pattern <- as.numeric(char_vector)
#       for (j in 1:length(response_pattern)) {
#         llm_item_scores_matrix[i, j] <- response_pattern[j]
#       }
#     }

#     irt_scores <- c()

#     for (i in 1:nrow(response_patterns_co_prova)) {
#       irt_scores[i] <- response_patterns_co_prova$IRT_SCORE[i]
#     }

#     irt_scores <- as.numeric(irt_scores)

#     itests <- coef(model_list[[toString(co_prova)]], IRTpars = TRUE, simplify = TRUE)$items[, c("a", "b", "g")]
#     na_indexes <- which(is.na(itests[, c("a")]))

#     # Remove the indexes with NA values
#     if (length(na_indexes) > 0) {
#       print("Removing NA indexes")
#       itests <- itests[-na_indexes, ]
#       llm_item_scores_matrix <- llm_item_scores_matrix[, -na_indexes]
#     }

#     # Compute lz scores for LLMs
#     lz_stat <- lz(llm_item_scores_matrix, Ability=irt_scores, IP=itests)

#     # Convert lz_stat$PFscores to a plain list without the PFscores name

#     # Addind it back to response_patterns using the ID from response_patterns_co_prova
#     for (i in 1:nrow(response_patterns_co_prova)) {
#       id_current <- response_patterns_co_prova$ID[i]
#       # Find index where response_patterns$ID == id_current
#       idx <- which(response_patterns$ID == id_current)
#       response_patterns$LZ_SCORE[idx] <- lz_stat$PFscores[i, ]
#     }
#   }
# }

# # Save response_patterns with LZ_SCORE
# write_parquet(response_patterns, "../../enem-experiments-results-processed-with-irt-lz.parquet")


# Compute lz scores for humans

humans_lz <- data.frame(matrix(ncol = 6, nrow = 0))
colnames(humans_lz) <- c("LZ_SCORE", "IRT_SCORE", "CO_PROVA", "EXAM_SUBJECT", "EXAM_YEAR")

print("Compute lz scores for humans")

for (year in 2019:2022) {
  print(paste0("Processing year: ", year))
  # ENEM performance (students)
  students_performance <- read_parquet(paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/MICRODADOS_ENEM_", year, "_filtered.parquet"))

  # Item params
  file_itens_prova <- paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/ITENS_PROVA_", year, ".csv")
  item_params <- read.csv(file_itens_prova, header = TRUE, sep=';')
  # Skip English itens.
  item_params <- subset(item_params, TP_LINGUA != "0" | is.na(TP_LINGUA))
  item_params <- item_params[order(item_params$CO_POSICAO, decreasing = FALSE), ]

  if (year == 2020) {
    # Remove TP_VERSAO_DIGITAL == 0
    item_params <- subset(item_params, TP_VERSAO_DIGITAL != 0 | is.na(TP_VERSAO_DIGITAL))
  }

  item_params_mirt <- data.frame(matrix(ncol = 9, nrow = 0))
  colnames(item_params_mirt) <- c("CO_PROVA", "CO_POSICAO", "a1", "d", "g", "u", "NU_PARAM_A", "NU_PARAM_B", "NU_PARAM_C")

  for (i in 1:nrow(item_params)) {
    row <- item_params[i, ]
    mirt_input <- traditional2mirt(c('a'=row$NU_PARAM_A, 'b'=row$NU_PARAM_B, 'g'=row$NU_PARAM_C, 'u'=1), cls='3PL')

    item_params_mirt[i, ] <- c(row$CO_PROVA, row$CO_POSICAO, mirt_input, row$NU_PARAM_A, row$NU_PARAM_B, row$NU_PARAM_C)
  }

  item_params <- item_params_mirt

  model_list <- list()
  itests_list <- list()

  for (exam_subject in c("MT", "CH", "CN", "LC")) {
      print(paste0("Processing year: ", year, " and exam_subject: ", exam_subject))
      if (exam_subject == "LC") {
        # Remove the students with TP_LINGUA == 0 (English as foreign language)
        students_performance <- subset(students_performance, TP_LINGUA != 0)
      }

      # Compute the LZ scores for humans
      students_item_scores_matrix <- matrix(nrow = nrow(students_performance), ncol = 45)
      for (i in 1:nrow(students_performance)) {
        if (exam_subject == "MT") {
          str_response_pattern <- students_performance$TX_RESPOSTAS_MT[i]
          correct_response_pattern <- students_performance$TX_GABARITO_MT[i]
        } else if (exam_subject == "LC") {
            str_response_pattern <- students_performance$TX_RESPOSTAS_LC[i]
            correct_response_pattern <- students_performance$TX_GABARITO_LC[i]
            # Removing the first 5 characters from the response pattern
            str_response_pattern <- substr(str_response_pattern, 6, nchar(str_response_pattern))
            correct_response_pattern <- substr(correct_response_pattern, 6, nchar(correct_response_pattern))
        } else if (exam_subject == "CH") {
          str_response_pattern <- students_performance$TX_RESPOSTAS_CH[i]
          correct_response_pattern <- students_performance$TX_GABARITO_CH[i]
        } else if (exam_subject == "CN") {
          str_response_pattern <- students_performance$TX_RESPOSTAS_CN[i]
          correct_response_pattern <- students_performance$TX_GABARITO_CN[i]
        }
        # Computing the 0/1 response pattern
        response_pattern <- c()
        str_response_pattern_vector <- unlist(strsplit(str_response_pattern, ""))
        correct_response_pattern_vector <- unlist(strsplit(correct_response_pattern, ""))
        for (j in 1:length(str_response_pattern_vector)) {
          if (str_response_pattern_vector[j] == correct_response_pattern_vector[j]) {
            response_pattern[j] <- 1
          } else {
            response_pattern[j] <- 0
          }
        }
        for (j in 1:length(response_pattern)) {
          students_item_scores_matrix[i, j] <- response_pattern[j]
        }
      }

      # Compute the irt scores for humans
      irt_scores <- c()

      for (i in 1:nrow(students_performance)) {
        response_pattern <- students_item_scores_matrix[i, ]
        if (exam_subject == "MT") {
          co_prova <- students_performance$CO_PROVA_MT[i]
        } else if (exam_subject == "LC") {
          co_prova <- students_performance$CO_PROVA_LC[i]
        } else if (exam_subject == "CH") {
          co_prova <- students_performance$CO_PROVA_CH[i]
        } else if (exam_subject == "CN") {
          co_prova <- students_performance$CO_PROVA_CN[i]
        }

        if (is.null(model_list[[toString(co_prova)]]))
        {
          item_params_prova <- subset(item_params, CO_PROVA == co_prova)

          # Sort item_params_prova by CO_POSICAO
          item_params_prova <- item_params_prova[order(item_params_prova$CO_POSICAO, decreasing = FALSE), ]

          # discrimination, easiness, and guessing values
          item_params_df <- data.frame(a1 = item_params_prova$a1,
                                      d = item_params_prova$d,
                                      g =  item_params_prova$g)
          
          model_list[[toString(co_prova)]] <- generate.mirt_object(item_params_df, itemtype = '3PL')

          itests_list[[toString(co_prova)]] = coef(model_list[[toString(co_prova)]], IRTpars = TRUE, simplify = TRUE)$items[, c("a", "b", "g")]
        }
        # IRT
        irt_scores[i] <- fscores(model_list[[toString(co_prova)]], method="EAP", response.pattern = response_pattern, )[1]
      }

      # # for each unique CO_PROVA
      if (exam_subject == "MT") {
        co_provas <- unique(students_performance$CO_PROVA_MT)
      } else if (exam_subject == "LC") {
        co_provas <- unique(students_performance$CO_PROVA_LC)
      } else if (exam_subject == "CH") {
        co_provas <- unique(students_performance$CO_PROVA_CH)
      } else if (exam_subject == "CN") {
        co_provas <- unique(students_performance$CO_PROVA_CN)
      }

      # print("Unique CO_PROVA")
      # print(co_provas)

      for (co_prova in co_provas) {
        # Get the indexes of the students_performance with CO_PROVA == co_prova
        if (exam_subject == "MT") {
          indexes <- which(students_performance$CO_PROVA_MT == co_prova)
        } else if (exam_subject == "LC") {
          indexes <- which(students_performance$CO_PROVA_LC == co_prova)
        } else if (exam_subject == "CH") {
          indexes <- which(students_performance$CO_PROVA_CH == co_prova)
        } else if (exam_subject == "CN") {
          indexes <- which(students_performance$CO_PROVA_CN == co_prova)
        }


        students_item_scores_matrix_co_prova <- students_item_scores_matrix[indexes, ]
        irt_scores_co_prova <- irt_scores[indexes]

        if (length(indexes) == 1) {
            students_item_scores_matrix_co_prova <- as.matrix(students_item_scores_matrix_co_prova)
            # Transpose the matrix
            students_item_scores_matrix_co_prova <- t(students_item_scores_matrix_co_prova)
            N <- dim(students_item_scores_matrix_co_prova)[1]
            I <- dim(students_item_scores_matrix_co_prova)[2]
            print("Indexes size 1")
        }

        na_indexes <- which(is.na(itests_list[[toString(co_prova)]][, c("a")]))
        # Remove the indexes with NA values
        if (length(na_indexes) > 0) {
          itests_list[[toString(co_prova)]] <- itests_list[[toString(co_prova)]][-na_indexes, ]
          if (length(indexes) == 1) {
            students_item_scores_matrix_co_prova <- students_item_scores_matrix_co_prova[-na_indexes]
            students_item_scores_matrix_co_prova <- as.matrix(students_item_scores_matrix_co_prova)
            # Transpose the matrix
            students_item_scores_matrix_co_prova <- t(students_item_scores_matrix_co_prova)
          } else {
            students_item_scores_matrix_co_prova <- students_item_scores_matrix_co_prova[, -na_indexes]
          }
        }

        lz_stat <- lz(students_item_scores_matrix_co_prova, Ability=irt_scores_co_prova, IP=itests_list[[toString(co_prova)]])
        #print(lz_stat)
        humans_lz <- rbind(humans_lz, data.frame(LZ_SCORE = lz_stat$PFscores, IRT_SCORE = irt_scores_co_prova, CO_PROVA = co_prova, EXAM_SUBJECT = exam_subject, EXAM_YEAR = year))
      }
  }
}

# Save humans_lz to a parquet file
write_parquet(humans_lz, "../../humans-irt-lz.parquet")
