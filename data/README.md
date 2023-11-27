# Data directory

This directory contains all the data collected from the Crawler. Note that the data structures are all dictionaries/json for efficiency purposes; the only potential downside is loading the data into memory at runtime, though the time for this is negligant comapred to the time to collect the data. In short, we are sacrificing storage for efficiency since storage is essentially endless (at least for the purposes of this application). 

## Contents

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

## Directories, Files & Data Formats

### article_contents/

The article_contents/ directory contains the raw, non-tokenized content for each article that the crawler parses. When the crawler parses an article, it will save the tokenized content in the [index](####index.json) and will save the raw content to a file in article_contents/[feed_title]/[article_id].txt where "feed_title" represents the title of the RSS feed that the article is from (see [feeds.json](../rss_feed/feeds.json) and "article_id" represents the index in [articles.json](jsons/articles.json) (and subsequently in [seen_article_links.json](jsons/seen_article_links.json)).  

### jsons/

The [jsons/](jsons/) dictionary contains various json files with data structures for different elements of data. 

#### articles.json

[articles.json](jsons/articles.json) contains a list of dictionaries (serialized into json format for storage) where each dictionary corresponds to an RSS_Article object (see [RSS.py](../rss_feed/RSS.py) for more context). The index for each dictionary (for each article) represents that article's ID for the rest of the data structures. This saves storage space and improves efficiency by allowing an arbitrary number of articles to be stored and referenced with a single integer.

The format of articles.json is as follows: 

    [ 
        {
            "article_title" : "article 1 title",
            "article_link" : "https://feed.com/article1",
            "article_pub_date": "Sat, 25 Dec 2023 15:16:54 -0500",
            "article_num_terms": 1000,
            "article_outlinks" : [
                                    "https://.../",
                                    "https://.../",
                                    ...
                                ]
            },
        ...
    ]


#### index.json

[index.json](jsons/index.json) is an inverted index of all the terms seen in all parsed articles (all articles in [articles.json](####articles.json)) in the following format: 

    { 
        "term1" : { 
                    "x" : term1/x,
                    "y" : term1/y,
                    ...
                },
        "term2" : { 
                    "i" : term2/i,
                    "j" : term2/j,
                    "x" : term2/x,
                    ...
                },
        ...
    }

    Where: 
        termX       => (str) an arbitrary term in the index, i.e. any term seen in at least one article
        x,y,i,j,... => ((str) int) article IDs, i.e. indices in articles.json, for articles containing at least one occurance of the respective term
        termX/P     => (int) the number of times that termX appears in article P (where P is an arbitrary article ID as described above)

The structure of the index can be thought of a 2-tiered dictionary, where the outer dictionary contains keys with the terms and the inner dictionary contains keys as integers (in string format, i.e. wrapped in " ") representing article IDs, and the terminating values (the innermost values, i.e. the values of the inner dictionary) represent the number of times that the outer key (term) appears in the inner key (article). 

Using dictionaries has immense benefits over other data structures, since under-the-hood, python dictionaries are hash tables and can be queried in O(1) (constant) time. Thus, when querying the index, a user can retrieve the article IDs and corresponding term frequencies (to be used for ranking) for a given term in constant time. 

#### seen_article_links.json

[seen_article_links.json](jsons/seen_article_links.json) contains a single 1-dimensional list of all the seen and parsed article links. This is leveraged primarily to quickly check if an article has been seen before to avoid unnecessary re-parsing of articles at runtime. 








