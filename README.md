# 📚 Cloze Encounters: Impact of Pirated Data on LLM Performance

This repository contains the full data pipeline and analysis code for the paper **“Cloze Encounters: Impact of Pirated Data on LLM Performance”**. We investigate the effects of training data access—especially from copyrighted corpora—on large language model (LLM) performance, using the Books3 dataset and the name cloze task.

---

## 🧪 Overview

The project combines data collection, cloze task generation, large-scale LLM inference, and econometric analysis. We focus on whether LLMs perform better on books included in the Books3 training dataset and how this relates to copyright and model transparency debates.

---

## 🔁 Pipeline Overview

### 1. Get the Data

- **Books3 metadata**: Provided as a `.tar.gz` archive.
- **Non-Books3 books**: Queried using ISBNdb.
- **Libgen**: Searched and optionally downloaded.
- **Goodreads**: Scraped via HTML or parsed from public UCSD dataset (WIP).

### 2. Generate Name Cloze Tasks

- Run BookNLP on raw text files to extract `.token` and `.entities` files.
- Generate `.name_cloze.txt` passages using Bamman et al.’s template.

### 3. Run LLMs

- OpenAI (GPT-3.5 / GPT-4)
- Meta (LLaMA 3.1 - 8B and 70B via OpenRouter)
- Anthropic Claude Haiku
- Google Gemini 2.0 Flash (via OpenRouter)

### 4. Analyze Results

- Combine query-level and book-level outputs.
- Run regression analysis (OLS and IV) in Stata.
- View interactive results via Streamlit.

---

## 🛠️ Setup

### Requirements

- Python 3.8+
- Stata (for final regression)
- [BookNLP](https://github.com/booknlp/booknlp) by David Bamman
- API keys for OpenAI, Anthropic, and OpenRouter
- (Optional) Access to Dropbox or remote servers for large datasets
