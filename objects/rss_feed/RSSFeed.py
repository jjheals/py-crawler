import json


class RSSFeed: 
        
    feed_title:str
    feed_link:str
    feed_desc:str
    
    def __init__(self, feed_title:str, feed_link:str, feed_desc:str): 
        self.feed_title = feed_title
        self.feed_link = feed_link
        self.feed_desc = feed_desc
        
        
    def to_dict(self):     
        """Convert this RSSFeed to a dictionary."""
        return { 
            'feed_title': self.feed_title,
            'feed_link': self.feed_link,
            'feed_desc': self.feed_desc
        }
        
        