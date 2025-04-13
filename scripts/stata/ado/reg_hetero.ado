program reg_hetero

//use ${tmp}book-level, clear
insheet using ${tmp}book-level-stella.csv, clear

gen books3 = in_books3 == "True"
egen popid = group(popularity)

eststo clear

* Run the 16 regressions and store estimates
foreach x in gpt35 gpt4o gemini claude llama8b llama70b{
    forvalues i=1/4 {
        qui ivreg2 `x'_score (1.books3=shares) if popid==`i', robust
        eststo model_`x'_`i'
    }
}

* Create a coefficient plot with 16 regressions displayed

foreach x in gpt35 gpt4o gemini claude llama8b llama70b{
    coefplot (model_`x'_1, keep(1.books3) label("0-10 reviews")) (model_`x'_2, keep(1.books3) label("10-100 reviews")) (model_`x'_3, keep(1.books3) label("100-1000 reviews")) (model_`x'_4, keep(1.books3) label("1000+ reviews")), xline(0) xtitle("Estimated Coefficient") scheme(plotplainblind) ytitle("") coeflabels(1.books3 = "Pop Bins")
graph export ${tables}pop_`x'.pdf, replace

}

end
