import json
from Paths import Paths

class RSS_Feed: 

    json_filename:str = 'feeds.json'
    
    feed_title:str
    feed_link:str
    feed_desc:str
    
    def __init__(self, feed_title:str, feed_link:str, feed_desc:str): 
        self.feed_title = feed_title
        self.feed_link = feed_link
        self.feed_desc = feed_desc
        
    def to_json(self, indent:int=4):     
        d:dict = { 
            'feed_title': self.feed_title,
            'feed_link': self.feed_link,
            'feed_desc': self.feed_desc
        }
        
        existing_feeds = json.load(open(Paths.FEEDS_JSON, 'r'))
        existing_feeds[self.feed_link] = d
        json.dump(existing_feeds, open(Paths.FEEDS_JSON, 'w'), indent=indent)
        
class RSS_Article: 
    
    # STATIC ATTRIBUTES
    dict_title = "article_title"
    dict_link = "article_link"
    dict_pub_date = "article_pub_date"
    dict_num_terms = "article_num_terms"
    dict_outlinks = "article_outlinks"
    
    # DYNAMIC ATTRIBUTES
    article_link:str
    article_title:str
    article_pub_date:str
    num_terms:int
    outbound_links:list[str]
    
    def __init__(self, title:str, link:str, pub_date:str, out_links:list[str], num_terms:int=0): 
        self.article_title = title
        self.article_link = link
        self.article_pub_date = pub_date
        self.num_terms = num_terms
        self.outbound_links = out_links
    
    @staticmethod
    def article_from_dict(d:dict): 
        return RSS_Article(d[RSS_Article.dict_title], d[RSS_Article.dict_link], d[RSS_Article.dict_pub_date], [], num_terms=d[RSS_Article.dict_num_terms])
    
    def to_dict(self) -> dict: 
        return {
            RSS_Article.dict_title: self.article_title,
            RSS_Article.dict_link: self.article_link,
            RSS_Article.dict_pub_date: self.article_pub_date,
            RSS_Article.dict_num_terms: self.num_terms,
            RSS_Article.dict_outlinks: self.outbound_links
        }
        
    def to_string(self) -> str:
        return f"ARTICLE: \"{self.article_title}\"\n\tLink: {self.article_link}\n\tNum Terms: {self.num_terms}\n\tNum Outlinks: {len(self.outbound_links)}"