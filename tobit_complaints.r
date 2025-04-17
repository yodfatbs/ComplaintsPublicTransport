install.packages("censReg")
library("censReg")
install.packages("writexl")
library(writexl)

#resolution 3 - routeid-direction
df3 <- read.csv("outputs//res3.csv")
    
   # "outputs//res3.csv")
df3$regional_sevice <- ifelse(df3$service_types == 2, 1, 0)
df3$intercity_sevice <- ifelse(df3$service_types == 1, 1, 0)
df3$innercity_sevice <- ifelse(df3$service_types == 3, 1, 0)

# reference: injlm, type1

colnames(df3)


m3 <- censReg(number_of_complaints ~  East_JLM_lines  + intercity_sevice + innercity_sevice+ passengersnumber_thousands
 + Directness_measurements + percent_problematic_trips + Settlements_lines + InJerusalem_lines
,  data = df3)
results <- summary(m3)
print(results)
#to excel
coefficients <- results$estimate  # This typically contains the coefficients and statistics
coeff_names <- rownames(coefficients)

results_df <- as.data.frame(coefficients)
results_df$Coefficient <- coeff_names

# Reorder columns to put Coefficient names first
results_df <- results_df[, c("Coefficient", colnames(results_df)[-ncol(results_df)])]
print(results)
write_xlsx(results_df, "outputs//results_res3.xlsx")


#######################################################################################

#resolution 2 - routeid-direction_alternative

df2 <- read.csv("outputs//res2.csv")


colnames(df2)
df2$regional_sevice <- ifelse(df2$service_types == 2, 1, 0)
df2$intercity_sevice <- ifelse(df2$service_types == 1, 1, 0)
df2$innercity_sevice <- ifelse(df2$service_types == 3, 1, 0)

# reference: injlm, type1

m2 <- censReg(number_of_complaints ~  East_JLM_lines  + intercity_sevice + innercity_sevice+ passengersnumber_thousands
 + Directness_measurements + percent_problematic_trips + Settlements_lines + InJerusalem_lines
,  data = df2)
results <- summary(m2)

coefficients <- results$estimate  # This typically contains the coefficients and statistics
coeff_names <- rownames(coefficients)

results_df <- as.data.frame(coefficients)
results_df$Coefficient <- coeff_names

# Reorder columns to put Coefficient names first
results_df <- results_df[, c("Coefficient", colnames(results_df)[-ncol(results_df)])]
print(results)
write_xlsx(results_df, "outputs//results_res2.xlsx")
write_xlsx(results_df, "outputs//results_res2.xlsx")



#######################################################################################

#resolution 1 - routeid-direction_alternative-day period
df1 <- read.csv("outputs//res1.csv")


colnames(df1)
df1$regional_sevice <- ifelse(df1$service_types == 2, 1, 0)
df1$intercity_sevice <- ifelse(df1$service_types == 1, 1, 0)
df1$innercity_sevice <- ifelse(df1$service_types == 3, 1, 0)

df1$rush_morning <- ifelse(df1$day_period == 2, 1, 0)
df1$low <- ifelse(df1$day_period == 1, 1, 0)
df1$rush_afternoon <- ifelse(df1$day_period == 3, 1, 0)

# reference: injlm, type1

m1 <- censReg(number_of_complaints ~  rush_morning+rush_afternoon+East_JLM_lines  + intercity_sevice 
+ innercity_sevice+ passengersnumber_thousands
 + Directness_measurements + percent_problematic_trips + Settlements_lines + InJerusalem_lines   
,  data = df1)
results <- summary(m1)

coefficients <- results$estimate  # This typically contains the coefficients and statistics
coeff_names <- rownames(coefficients)

results_df <- as.data.frame(coefficients)
results_df$Coefficient <- coeff_names

# Reorder columns to put Coefficient names first
results_df <- results_df[, c("Coefficient", colnames(results_df)[-ncol(results_df)])]
print(results)
write_xlsx(results_df, "outputs//results_res1A.xlsx")

