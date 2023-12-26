# https://stats.stackexchange.com/questions/34119/estimating-ability-using-irt-when-the-model-parameters-are-known
# https://rdrr.io/cran/mirtCAT/man/generate.mirt_object.html
#install.packages("mirtCAT")
library(mirtCAT)

print("Running...")

file_itens_prova = "../microdados/microdados_enem_2022/DADOS/ITENS_PROVA_2022.csv"

item_params <- read.csv(file_itens_prova, header = TRUE, sep=';')  
item_params <- item_params[order(item_params$CO_POSICAO, decreasing = FALSE), ]

print("Loaded item params")

file_path <- "../mirt_params.csv"
file_conn <- file(file_path, "w")

cat("CO_PROVA CO_POSICAO a1 d g u", file = file_conn, "\n")
for (i in 1:nrow(item_params)) {
  row <- item_params[i, ]
  mirt_input <- traditional2mirt(c('a'=row$NU_PARAM_A, 'b'=row$NU_PARAM_B, 'g'=row$NU_PARAM_C, 'u'=1), cls='3PL')
  
  #print(mirt_input)
  
  cat(row$CO_PROVA, file = file_conn, "")
  cat(row$CO_POSICAO, file = file_conn, "")
  cat(mirt_input, file = file_conn, "\n")
}
close(file_conn)

print("mirt_params.csv Written.")
item_params <- read.csv("../mirt_params.csv", header = TRUE, sep=" ") 

#########################################################

print("Loading response patterns...")


response_patterns <-  read.csv(paste(response_pattern_filepath, sep=""),  colClasses=c("RESPONSE_PATTERN"="character"), header = TRUE, sep =',')  
PROVA <- substr(regmatches(response_pattern_filepath, regexpr("_([[:alnum:]]{2})\\.csv", response_pattern_filepath)), 2, 3)

colnames(response_patterns)
dim(response_patterns)

###########################################################

file_path <- paste(theta_file, sep="")
file_conn <- file(file_path, "w")
cat("ENEM_IRT_SCORE,CTT_SCORE,IRT_SCORE,IRT_SCORE_SE", file = file_conn, "\n")

model_list <- list()
for (i in 1:nrow(response_patterns)) {
  
  enem_irt_score = response_patterns$NU_NOTA[i]  
  str_response_pattern = response_patterns$RESPONSE_PATTERN[i]
  ctt_score = response_patterns$CTT_SCORE[i]
  CODIGO_PROVA =response_patterns$CO_PROVA[i]
  
  item_params_prova <- subset(item_params, CO_PROVA == CODIGO_PROVA)
  
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
  
  #print(response_pattern)
  
  score_and_error = fscores(model_list[[toString(CODIGO_PROVA)]], method="EAP", response.pattern = response_pattern)
  
  #print(enem_irt_score)
  #print(ctt_score)
  #print(score_and_error)
  
  cat(enem_irt_score, file = file_conn, ",")
  cat(ctt_score, file = file_conn, ",")
  cat(score_and_error[1], file = file_conn, ",")
  cat(score_and_error[2], file = file_conn, "\n")
  
  
  #print("FINISHED")
  
  
  #print("----------")
  
}

close(file_conn)




