# https://stats.stackexchange.com/questions/34119/estimating-ability-using-irt-when-the-model-parameters-are-known
# https://rdrr.io/cran/mirtCAT/man/generate.mirt_object.html
#install.packages("mirtCAT")
library(mirtCAT)
library(arrow)
library(PerFit)

response_pattern_filepath = "../../enem-experiments-results-processed-with-irt.parquet"
response_patterns <- read_parquet(response_pattern_filepath)
response_patterns$ID <- 1:nrow(response_patterns)

year = 2022
co_prova = 1082

file_itens_prova = paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/ITENS_PROVA_", year, ".csv")

files_students_performance = paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/MICRODADOS_ENEM_", year, ".csv")

students_performance <- read.csv(files_students_performance, header = TRUE, sep=';')
# Removing NA values of CO_PROVA_MT
students_performance <- subset(students_performance, !is.na(CO_PROVA_MT) & !is.na(TX_RESPOSTAS_MT) & !is.na(NU_NOTA_MT))

item_params <- read.csv(file_itens_prova, header = TRUE, sep=';')
# Skip English itens.
item_params <- subset(item_params, TP_LINGUA != '0' | is.na(TP_LINGUA))
item_params <- item_params[order(item_params$CO_POSICAO, decreasing = FALSE), ]

item_params_mirt <- data.frame(matrix(ncol = 9, nrow = 0))
colnames(item_params_mirt) <- c("CO_PROVA", "CO_POSICAO", "a1", "d", "g", "u", "NU_PARAM_A", "NU_PARAM_B", "NU_PARAM_C")

for (i in 1:nrow(item_params)) {
  row <- item_params[i, ]
  mirt_input <- traditional2mirt(c('a'=row$NU_PARAM_A, 'b'=row$NU_PARAM_B, 'g'=row$NU_PARAM_C, 'u'=1), cls='3PL')

  item_params_mirt[i, ] <- c(row$CO_PROVA, row$CO_POSICAO, mirt_input, row$NU_PARAM_A, row$NU_PARAM_B, row$NU_PARAM_C)
}

item_params <- item_params_mirt

# Getting the params for the specific exam (CO_PROVA)
item_params_prova <- subset(item_params, CO_PROVA == co_prova)

# Sort item_params_prova by CO_POSICAO
item_params_prova <- item_params_prova[order(item_params_prova$CO_POSICAO, decreasing = FALSE), ]

# Load the model
item_params_df <- data.frame(a1 = item_params_prova$a1,
                                  d = item_params_prova$d,
                                  g =  item_params_prova$g)
      
model3PL <- generate.mirt_object(item_params_df, itemtype = '3PL')

#########################################################
  
# # Filter in response_patterns: ENEM_EXAM contains year substring
response_patterns_current_year <- subset(response_patterns, grepl(year, ENEM_EXAM))

# # Filter in response_patterns: CO_PROVA == CO_PROVA
response_patterns_current_year <- subset(response_patterns_current_year, CO_PROVA == co_prova)


# Create a data matrix of dichotomous item scores: Persons as rows, items as columns (items are in the RESPONSE_PATTERN column as a str), item scores are either 0 or 1, missing values allowed.
# TODO: probably this has to be created with the whole data (including the humans)
# llm_item_scores_matrix = matrix(nrow = nrow(response_patterns_current_year), ncol = 45)
# for (i in 1:nrow(response_patterns_current_year)) {
#   str_response_pattern = response_patterns_current_year$RESPONSE_PATTERN[i]
#   # Split the string into individual characters
#   char_vector <- unlist(strsplit(str_response_pattern, ""))
#   # Convert the characters to numeric values (0 or 1)
#   response_pattern <- as.numeric(char_vector)
#   for (j in 1:length(response_pattern)) {
#     llm_item_scores_matrix[i, j] <- response_pattern[j]
#   }
# }

llm_item_scores_matrix = matrix(nrow = nrow(students_performance) + nrow(response_patterns_current_year), ncol = 45)
for (i in 1:nrow(students_performance)) {
  str_response_pattern = students_performance$TX_RESPOSTAS_MT[i]
  correct_response_pattern = students_performance$TX_GABARITO_MT[i]
  # Computing the 0/1 response pattern
  response_pattern = c()
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
    llm_item_scores_matrix[i, j] <- response_pattern[j]
  }
}

# Create a numeric vector to store the IRT scores
irt_scores = c()

for (i in 1:nrow(students_performance)) {
  response_pattern = llm_item_scores_matrix[i, ]
  irt_scores[i] <- fscores(model3PL, method="EAP", response.pattern = response_pattern, )[1]
}

# Adding rows to the llm_item_scores_matrix respective to LLMs
current_row = nrow(llm_item_scores_matrix) - nrow(response_patterns_current_year) + 1
for (i in 1:nrow(response_patterns_current_year)) {
  str_response_pattern = response_patterns_current_year$RESPONSE_PATTERN[i]
  # Split the string into individual characters
  char_vector <- unlist(strsplit(str_response_pattern, ""))
  # Convert the characters to numeric values (0 or 1)
  response_pattern <- as.numeric(char_vector)
  for (j in 1:length(response_pattern)) {
    llm_item_scores_matrix[current_row, j] <- response_pattern[j]
  }
  current_row = current_row + 1
}

current_row = nrow(llm_item_scores_matrix) - nrow(response_patterns_current_year) + 1
for (i in 1:nrow(response_patterns_current_year)) {
  irt_scores[current_row] <- response_patterns_current_year$IRT_SCORE[i]
  current_row = current_row + 1
}

print("dim(llm_item_scores_matrix)")
print(dim(llm_item_scores_matrix))

# Convert to a list
# ability_list = as.vector(ability_list)

irt_scores = as.numeric(irt_scores)

itests = coef(model3PL, IRTpars = TRUE, simplify = TRUE)$items[, c("a", "b", "g")]
# Fint the indexes with NA values
na_indexes = which(is.na(itests[, c("a")]))

# Remove the indexes with NA values
itests <- itests[-na_indexes, ]
##itests <- itests[-c(22, 25, 42), ]
# Now, remove the same items from llm_item_scores_matrix
#llm_item_scores_matrix <- llm_item_scores_matrix[, -c(22, 25, 42)]
llm_item_scores_matrix <- llm_item_scores_matrix[, -na_indexes]

lzstar_stat = lzstar(llm_item_scores_matrix, IRT.PModel = "3PL", Ability=irt_scores, IP=itests)
# # cuttoff
# lzstarcut_05 = cuttoff(lzstar_stat, ModelFit="Parametric", Blvl:.05)
# FlgdCase_lzstar = flagged.resp(lzstar_stat, cuttoff=lzstarcut_05, scores=T)
# FlgdCases = FlgdCase_lzstar$Scores
# print(FlgdCases)

# Plot the last len(response_patterns_current_year) positions
for (i in 1:nrow(response_patterns_current_year)) {
  PRFplot(llm_item_scores_matrix, respID=nrow(llm_item_scores_matrix) - i + 1, IP=itests, Ability=irt_scores)
}

# PRFplot(llm_item_scores_matrix, respID=6784, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6785, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6786, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6787, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6788, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6789, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6790, IP=itests, Ability=irt_scores)
# PRFplot(llm_item_scores_matrix, respID=6791, IP=itests, Ability=irt_scores)

# Print response_patterns_current_year columns: MODEL_NAME, MODEL_SIZE, LANGUAGE
print(response_patterns_current_year[, c("MODEL_NAME", "MODEL_SIZE", "LANGUAGE", "IRT_SCORE")])


###########################################################
#   model_list <- list()
#   #for (i in 1:nrow(response_patterns)) {
#   # Iterate over the response patterns indexed

#   ability <- list()
  
#   for (i in 1:nrow(response_patterns_current_year)) {    
#     enem_irt_score = response_patterns_current_year$NU_NOTA[i]
#     str_response_pattern = response_patterns_current_year$RESPONSE_PATTERN[i]
#     ctt_score = response_patterns_current_year$CTT_SCORE[i]
#     CODIGO_PROVA = response_patterns_current_year$CO_PROVA[i]
    
#     item_params_prova <- subset(item_params, CO_PROVA == CODIGO_PROVA)

#     # Sort item_params_prova by CO_POSICAO
#     item_params_prova <- item_params_prova[order(item_params_prova$CO_POSICAO, decreasing = FALSE), ]
    
#     if (is.null(model_list[[toString(CODIGO_PROVA)]]))
#     {
#       # discrimination, easiness, and guessing values
#       item_params_df <- data.frame(a1 = item_params_prova$a1,
#                                   d = item_params_prova$d,
#                                   g =  item_params_prova$g)
      
#       model_list[[toString(CODIGO_PROVA)]] <- generate.mirt_object(item_params_df, itemtype = '3PL')
#       print("LOADED MODEL")
#     }
    
#     # Split the string into individual characters
#     char_vector <- unlist(strsplit(str_response_pattern, ""))
#     # Convert the characters to numeric values (0 or 1)
#     response_pattern <- as.numeric(char_vector)

#     min_correct_b = 1000
#     max_correct_b = -1000
    
#     correct_bs <- c()
#     count_correct_bs = 0
    
#     incorrect_bs <- c()
#     count_incorrect_bs = 0
    
#     for (r_idx in 1:length(response_pattern)) {
#       r = response_pattern[r_idx]
#       nu_param_b = item_params_prova$NU_PARAM_B[r_idx]

#       if(!is.na(nu_param_b)) {
      
#         if (r == 1){
#           count_correct_bs =  count_correct_bs + 1
#           correct_bs[count_correct_bs] <- nu_param_b
#         }
#         if (r == 0){
#           count_incorrect_bs =  count_incorrect_bs + 1
#           incorrect_bs[count_incorrect_bs] <- nu_param_b
#         }
        
#         if (r == 1 & nu_param_b > max_correct_b) {
#           max_correct_b = nu_param_b
#         }
#         if (r == 1 & nu_param_b < min_correct_b) {
#           min_correct_b = nu_param_b
#         }
#       }
#     }

#     score_and_error = fscores(model_list[[toString(CODIGO_PROVA)]], method="EAP", response.pattern = response_pattern, )

#     ability[i] <- score_and_error[1]

#     # if enem_irt_score is NULL, then use the score_and_error[1] * 100 + 500
#     if (is.null(enem_irt_score)) {
#       enem_irt_score = score_and_error[1] * 100 + 500
#     }

#     # Add them to the response_patterns dataframe, using the ID to index
#     id_current = response_patterns_current_year$ID[i]
#     response_patterns$ENEM_IRT_SCORE[id_current] <- enem_irt_score
#     response_patterns$CTT_SCORE[id_current] <- ctt_score
#     response_patterns$IRT_SCORE[id_current] <- score_and_error[1]
#     response_patterns$IRT_SCORE_SE[id_current] <- score_and_error[2]
#     response_patterns$MIN_CORRECT_B[id_current] <- min_correct_b
#     response_patterns$MAX_CORRECT_B[id_current] <- max_correct_b
#     response_patterns$MEAN_CORRECT_B[id_current] <- mean(correct_bs)
#     response_patterns$MEAN_INCORRECT_B[id_current] <- mean(incorrect_bs)  
#   }

#   # Create a data matrix of dichotomous item scores: Persons as rows, items as columns (items are in the RESPONSE_PATTERN column as a str), item scores are either 0 or 1, missing values allowed.
#   llm_item_scores_matrix = matrix(nrow = nrow(response_patterns_current_year), ncol = 45)
#   for (i in 1:nrow(response_patterns_current_year)) {
#     str_response_pattern = response_patterns_current_year$RESPONSE_PATTERN[i]
#     # Split the string into individual characters
#     char_vector <- unlist(strsplit(str_response_pattern, ""))
#     # Convert the characters to numeric values (0 or 1)
#     response_pattern <- as.numeric(char_vector)
#     for (j in 1:length(response_pattern)) {
#       llm_item_scores_matrix[i, j] <- response_pattern[j]
#     }
#   }

#   print(score_and_error)
#   itests = coef(model_list[[toString(CODIGO_PROVA)]], IRTpars = TRUE, simplify = TRUE)$items[, c("a", "b", "g")]
#   lzstar_stat = lzstar(llm_item_scores_matrix, IRT.PModel = "3PL", Ability=ability, IP = itests)
#   print(lzstar_stat)
#   # # cuttoff
#   # lzstarcut_05 = cuttoff(lzstar_stat, ModelFit="Parametric", Blvl:.05)
#   # FlgdCase_lzstar = flagged.resp(lzstar_stat, cuttoff=lzstarcut_05, scores=T)
#   # FlgdCases = FlgdCase_lzstar$Scores
#   # print(FlgdCases)
#   q()
# }




# #print("Saving response patterns with IRT scores...")
# # Remove ID column
# #response_patterns$ID <- NULL
# # Save response_patterns with IRT scores
# #write_parquet(response_patterns, "../../enem-experiments-results-processed-with-irt.parquet")




