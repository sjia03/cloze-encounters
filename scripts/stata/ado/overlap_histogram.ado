program overlap_histogram

//insheet using ${rawdata}isbndb.csv, clear

//use ~/Dropbox/research/7.books/more_data/books_in_print.dta, clear

// overall histogram for books3
insheet using ${rawdata}books3-clean.csv, clear

rename publication_year pub_year

bysort pub_year: gen numbooks = _N
bysort pub_year: drop if _n > 1
keep pub_year numbooks
drop if pub_year == .

set obs 129

replace numbooks = 0 if pub_year == .
replace pub_year = 2021 if _n==127
replace pub_year = 2022 if _n==128
replace pub_year = 2023 if _n==129

tw (bar numbooks pub_year if pub_year>1990, bcolor(sky)), ytitle("Num Books") xtitle("Publication Year") xlabel(1990 (3) 2023)
graph export ${tables}hist_books3.pdf, replace

// TODO: later add in the distribution in our sample

end
