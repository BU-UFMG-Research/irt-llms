library(arrow)

for (year in 2019:2022) {
    file_itens_prova = paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/ITENS_PROVA_", year, ".csv")

    files_students_performance = paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/MICRODADOS_ENEM_", year, ".csv")

    students_performance <- read.csv(files_students_performance, header = TRUE, sep=';')
    # Print unique TP_LINGUA
    print("Loaded students performance")
    # # Keeping students that answered all the exams (TP_PRESENCA_MT, TP_PRESENCA_LC, TP_PRESENCA_CH, TP_PRESENCA_CN)
    students_performance <- subset(students_performance, TP_PRESENCA_MT == 1 & TP_PRESENCA_LC == 1 & TP_PRESENCA_CH == 1 & TP_PRESENCA_CN == 1)
    print("Filtered students performance")
    # Get only the columns that we need
    students_performance <- students_performance[, c("TX_RESPOSTAS_MT", "TX_GABARITO_MT", "NU_NOTA_MT", "TX_RESPOSTAS_LC", "TX_GABARITO_LC", "NU_NOTA_LC", "TP_LINGUA", "TX_RESPOSTAS_CH", "TX_GABARITO_CH", "NU_NOTA_CH", "TX_RESPOSTAS_CN", "TX_GABARITO_CN", "NU_NOTA_CN", "CO_PROVA_CN", "CO_PROVA_CH", "CO_PROVA_LC", "CO_PROVA_MT")]
    # Make the indexes start from 1
    rownames(students_performance) <- NULL
    # Save it to a parquet file
    print("Saving students performance")
    write_parquet(students_performance, paste0("../../data/raw-enem-exams/microdados_enem_", year, "/DADOS/MICRODADOS_ENEM_", year, "_filtered.parquet"))
}