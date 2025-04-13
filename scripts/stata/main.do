
qui adopath + "~/Dropbox/research/23.Copyright-LLMs/scripts/ado/"

ssc install blindschemes, replace all
set scheme plotplain, permanently

declare_global
cd ${path}

///////////////////
// Data Prep

// abhishek wrote this
//query_to_book


// 2. this converts query level to book level
get-book-level-data.py

///////////////////
// Analysis


// FIGURES

// 1. schematic figure

// 2. something that justifies the IV

// Fig 2. histogram of years
overlap_histogram

// Fig 2+3. IV scatterplots
// this gives a figure for first stage,
// and a figure that shows correlation for each of the outcomes with the pub year
iv_scatter

// 4. heterogeneous plots
reg_hetero

//////////////////////////
// TABLES

// 1. summary stats

// 2. baseline regression
reg_baseline

// interpret
//0.0284∗∗∗ 0.0231∗∗∗ 0.0110∗∗ 0.000796 0.0133∗∗∗ 0.0104∗

di "----"
di .0284/.1190
di .0231/.1098

di 0.000796/.0390488
di 0.0133/.1504216

di 0.0104/.143229
di 0.0110/.1583845

// 3. robustness
reg_rbst

// 4. heterogeneity by popularity + fiction/non fiction
// not doign this for now









