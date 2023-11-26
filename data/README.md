## Data directory

This directory contains all the data collected from the Crawler.

### Contents

    data/
    |-- README.md
    |-- article_contents/
    |   |-- 0.txt
    |   |-- 1.txt
    |   |-- ... 
    |-- jsons/
    |   |-- articles.json
    |   |-- index.json
    |   |-- seen_article_links.json

### Directories, Files & Data Formats

#### DIRECTORY: article_contents/

The article_contents/ directory contains the raw, non-tokenized content for each article that the crawler parses. When the crawler parses an article, it will save the tokenized content in the [index](#####index.json)

#### DIRECTORY: jsons/

##### articles.json

##### index.json

##### seen_article_links.json