library(mirtCAT)

# RASCH MODEL. Total score = total information

params <- data.frame(a1 = c(1,1,1,1,1),
                   # d = -b   
                   d = c(-2,-1,0,1,2) * -1,
                   g = c(0,0,0,0,0))
model <- generate.mirt_object(params, itemtype = '3PL')


fscores(model, response.pattern = c(0,1,1,1,1))
fscores(model, response.pattern = c(1,1,1,1,0))

# 3 PL MODEL. Missing the easy question penalizes more.

params <- data.frame(a1 = c(1,1,1,1,1),
                     # d = -b   
                     d = c(-2,-1,0,1,20) * -1,
                     g = c(0.1,0.1,0.1,0.1,0.1))
model <- generate.mirt_object(params, itemtype = '3PL')


fscores(model, response.pattern = c(0,1,1,1,1))
fscores(model, response.pattern = c(1,1,1,1,0))


# 3 PL MODEL. Hardest question

params <- data.frame(a1 = c(1,1,1,1,1),
                     # d = -b   
                     d = c(-2,-1,0,1,20) * -1,
                     g = c(0.1,0.1,0.1,0.1,0.1))
model <- generate.mirt_object(params, itemtype = '3PL')


fscores(model, response.pattern = c(1,1,1,1,1))
fscores(model, response.pattern = c(1,1,1,1,0))
