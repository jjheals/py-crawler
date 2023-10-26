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
        
        existing_feeds = json.load(open(f'{Paths.FEEDS_JSON}/{RSS_Feed.json_filename}', 'r'))
        existing_feeds[self.feed_link] = d
        json.dump(existing_feeds, open(f'{Paths.FEEDS_JSON}/{RSS_Feed.json_filename}', 'w'), indent=4)