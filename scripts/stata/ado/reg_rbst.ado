program reg_rbst

insheet using ${tmp}book-level-stella.csv, clear

gen books3 = in_books3 == "True"

gen treat = 0
replace treat = 1 if pub_year> 2011 & pub_year < 2020
egen popid = group(popularity)

gen treatvar = treat

est clear
foreach x in gpt35 gpt4o gemini llama8b llama70b claude {
    qui reg `x'_score 1.treatvar, robust
    eststo mo_`x'_treat
    qui estadd local popfe "No"
    qui estadd local ctrls "No"
}

replace treatvar = books3

foreach x in gpt35 gpt4o gemini llama8b llama70b claude {
    qui ivreg2 `x'_score (1.treatvar=share) i.popid, robust
    qui estadd local popfe "Yes"
    qui estadd local ctrls "No"
    eststo mo_`x'_pop1

    qui ivreg2 `x'_score (1.treatvar=share) i.popid num_reviews num_ratings avg_rating, robust
    qui estadd local popfe "Yes"
    qui estadd local ctrls "Yes"
    eststo mo_`x'_pop2
}


local x1 "mo_gpt35_treat mo_gpt35_pop1 mo_gpt35_pop2 mo_gpt4o_treat mo_gpt4o_pop1 mo_gpt4o_pop2"

local x2 "mo_llama8b_treat mo_llama8b_pop1 mo_llama8b_pop2 mo_llama70b_treat mo_llama70b_pop1 mo_llama70b_pop2"

local x3 "mo_claude_treat mo_claude_pop1 mo_claude_pop2 mo_gemini_treat mo_gemini_pop1 mo_gemini_pop2"

esttab `x1' using ${tables}reg_rbst_1.tex, keep(1.treatvar) se stats(N popfe ctrls,labels("N" "Pop. FE" "Ctrls")) label replace booktabs star(+ 0.15 * 0.10 ** 0.05 *** 0.01) coeflabels(1.treatvar Books3) mgroups("GPT3.5" "GPT4o", pattern(1 0 0 1 0 0)prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span})) mtitles("OLS" "IV" "IV" "OLS" "IV" "IV") nonum nonotes

esttab `x2' using ${tables}reg_rbst_2.tex, keep(1.treatvar) se stats(N popfe ctrls,labels("N" "Pop. FE" "Ctrls")) label replace booktabs star(+ 0.15 * 0.10 ** 0.05 *** 0.01) coeflabels(1.treatvar Books3) mgroups("Llama 8b" "Llama 70b", pattern(1 0 0 1 0 0)prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span})) mtitles("OLS" "IV" "IV" "OLS" "IV" "IV") nonum nonotes

esttab `x3' using ${tables}reg_rbst_3.tex, keep(1.treatvar) se stats(N popfe ctrls,labels("N" "Pop. FE" "Ctrls")) label replace booktabs star(+ 0.15 * 0.10 ** 0.05 *** 0.01) coeflabels(1.treatvar Books3) mgroups("Claude" "Gemini", pattern(1 0 0 1 0 0)prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span})) mtitles("OLS" "IV" "IV" "OLS" "IV" "IV") nonum


end




// event study
