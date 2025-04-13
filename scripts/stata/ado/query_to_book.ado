program query_to_book

insheet using ${filedata}query-level.csv, clear

rename map_file_name bookid
rename goodread pub_year

//preserve
//keep if bookid == "theconfessionjohngrisham"
//export excel using tmp/grisham_confession.xlsx if , replace

//drop if pub_year == .
//drop if pub_year == -1

merge m:1 pub_year using ../filedata/shares, keep(master match)

replace share = 0 if _m==1

foreach x in gpt4o gpt35 gemini llama8 llama70 claude {
    gen scr_`x' = strlower(`x')==strlower(correct)
}

foreach x in gpt4o gpt35 gemini llama8 llama70 claude {
bysort bookid: egen avg_scr_`x' = mean(scr_`x')
}

gen books3 = in_books3 == "True"
gen qry_len = strlen(query)
bysort bookid: egen avg_qry_len = mean(qry_len)

bysort bookid : gen numq = _N
bysort bookid: gen btag = _n==1

keep if btag 

keep bookid avg_scr* shares pub_year numq avg_qry avg_rating num_rating num_reviews books3 book_title author genres

save ${filedata}book-level, replace

//outsheet using ../filedata/books-level-tmp.csv, replace


end
