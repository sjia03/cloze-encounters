program reg_fiction

//use ${tmp}book-level, clear
insheet using ${tmp}book-level-stella.csv, clear

gen books3 = in_books3 == "True"


est clear
foreach x in gpt35 gpt4o gemini claude llama8b llama70b{
    eststo: qui ivreg2 `x'_score (1.books3=shares) if fiction==1, robust
}

esttab est1 est2 est3, keep(1.books3) p
esttab est4 est5 est6, keep(1.books3) p


end
