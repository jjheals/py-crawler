
class Paths: 
    
    # File containing the RSS feeds to index in json format
    FEEDS_JSON:str = 'config/feeds.json'
    
    # File for the index of terms from articles in json format
    INDEX_JSON:str = 'data/jsons/index.json'
    
    # File for all parsed articles as a list of dictionaries in json format
    ARTICLES_JSON:str = 'data/jsons/articles.json'
    
    # File for a list of all previously seen (and parsed) article links in json format 
    SEEN_ARTICLES_JSON:str = 'data/jsons/seen_article_links.json'
    
    # Directory containing the raw contents for all parsed articles. Note that the files for
    # each article are stored in subdirectories by RSS feed, where each subdirectory contains
    # a file for each article from that feed, where the filename is the article's index in 
    # Paths.ARTICLES_JSON (and the filename corresponds to an index in Paths.INDEX_JSON)
    ARTICLE_CONTENTS_DIR:str = 'data/article_contents/'