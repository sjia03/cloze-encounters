program reg_baseline

program reg_baseline
//use ${tmp}book-level, clear
insheet using ${tmp}book-level-stella.csv, clear

gen books3 = in_books3 == "True"

est clear
foreach x in gpt35 gpt4o llama8b llama70b claude gemini{
    eststo: qui ivreg2 `x'_score (books3=share), robust savefirst savefprefix(first) 
mat first=e(first)
local FStat = round(first[4,1],0.01)
estadd local FStat `FStat'
}

esttab est1 est2 est3, keep(books3) p stats(N FStat)
esttab est4 est5 est6, keep(books3) p stats(N FStat)

label variable books3 "Books3"

esttab est1 est2 est3 est4 est5 est6 using ${tables}baseline_iv.tex, keep(books3) se stats(N FStat,labels("N" "F-Stat")) label replace booktabs star(* 0.10 ** 0.05 *** 0.01) mtitles("GPT3.5 Turbo" "GPT 4o" "Llama 8b" "Llama 70b" "Claude" "Gemini")

end
