# py-crawler

## Description

The goal with py-crawler is to efficiently gather meaningful information from desired sources to enable better information correlation, analysis, and faster querying for specific information when needed. By collecting the content of articles from various sources and feeds, py-crawler can then use natural language processing (NLP) to find related articles, even if those relations are subtle. This results in better information correlation across platforms and increases the general scope of information gathering. Additionally, py-crawler can use pre-saved data to answer queries from users looking for specific information. With its index, py-crawler can search for queried terms and tell the user where to look for more information, as well as provide more related sources of information by using NLP and other methods. 

## Methodology

Py-crawler started as a project to provide better correlation among analysts and researchers looking for information on specific topics and from the same sources, and to automate the grunt work of parsing through articles for information. 

The initial crawling phase gathers general information about articles from the feeds defined in [feeds.json](rss_feed/feeds.json). From there, the crawler visits each of the articles from the feeds to get the raw content, as well as any links off that page to potentially related articles. Notably, (at this time) the crawler does not go further than 1 level deep, i.e. it only visits and gets content from articles directly off the original RSS feed; although it gets outbound links from these articles, these links are to provide the user with quick access to related resources on the topic queried. 

For each article visited, after getting the outbound links, the crawler tokenizes the raw content and adds the respective data to the [index](data/jsons/index.json) (more information on the index can be found in the [README](data/README.md) of the data folder). Importantly, the crawler also saves the non-tokenized raw content to the data/raw_contents/ directory, since the vast majority of NLP models consider the location of a word in a document, not just the frequency, and thus require the raw content with the word placements preserved. 

To improve efficiency at runtime, the crawler stores additional information in the other files in the data/ directory. the [README](data/README.md) in the data/ directory contains more details on these files and their purposes.

## File System Structure

    py-crawler
    |-- crawler/
    |   |-- crawler_exceptions.py
    |   |-- Crawler.py
    |-- data/
    |   |-- article_contents/
    |   |   |-- feed1/
    |   |   |   |-- 0.txt
    |   |   |   |-- ... 
    |   |   |-- ... 
    |   |-- jsons/
    |   |   |-- index.json
    |   |   |-- articles.json
    |   |   |-- index.json
    |   |   |-- seen_article_links.json
    |   |-- README.md
    |-- data_analysis/
    |   |-- Analyzer.py
    |   |-- Indexer.py
    |-- rss_feed/
    |   |-- feeds.json
    |   |-- RSS.py
    |-- Paths.py
    |-- README.md
    |-- requirements.txt
    |-- testing.ipynb
    

## Requirements

The NLTK stopwords package is required for the stemming portion of tokenization. To install:  

    #!/usr/bin/env python3
    
    import nltk
    import ssl

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('stopwords')