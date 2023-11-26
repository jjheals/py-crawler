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

The article_contents/ directory contains the raw, non-tokenized content for each article that the crawler parses. When the crawler parses an article, it will save the tokenized content in the [index](#####index.json) and will save the raw content to a file in article_contents/[feed_title]/[article_id].txt where "feed_title" represents the title of the RSS feed that the article is from (see [feeds.json](../rss_feed/feeds.json) and "article_id" represents the index in [articles.json](jsons/articles.json) (and subsequently in [seen_article_links.json](jsons/seen_article_links.json)).  

#### DIRECTORY: jsons/

The [jsons/](jsons/) dictionary contains various json files with data structures for different elements of data. 

##### articles.json

[articles.json](jsons/articles.json) contains a list of dictionaries (serialized into json format for storage) where each dictionary corresponds to an RSS_Article object (see [RSS.py](../rss_feed/RSS.py) for more context). The index for each dictionary (for each article) represents that article's ID for the rest of the data structures. This saves storage space and improves efficiency by allowing an arbitrary number of articles to be stored and referenced with a single integer.

##### index.json

##### seen_article_links.json
