program iv_scatter

// show the first stage
use ${tmp}book-level, clear

binscatter books3 shares, nq(8) ytitle("% Books3") xtitle("Books3 Year Share")
graph export ${tables}bin_books3_shares.pdf, replace


// show the second stage
use ${tmp}book-level, clear

foreach x in gpt35 gpt4o llama8 llama70 gemini claude{
    binscatter avg_scr_`x' pub_year if pub_year>2000, rd(2012 2020) discrete xtitle(Pub Year) ytitle(LLM Score)

    graph export ${tables}scatter_`x'.pdf, replace
}

end



