import requests 
from bs4 import BeautifulSoup
from re import sub, compile
import json
from Paths import Paths 
from rss_feed.RSS import *

class Crawler: 
    
    # STATIC ATTRIBUTES 
    url_regex_pattern:str = r'https?://[^\s/$.?#].[^\s]*'   # Regex pattern that a valid URL must match 
    headers:dict[str,str] = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'              
            }
    
    # json filenames 
    index_json:str = 'index.json'
    articles_json:str = 'articles.json'
    seen_article_links_json:str = 'seen_article_links.json'
    
    # DYNAMIC ATTRIBUTES 
    index:dict[str,dict[int,int]]   # Index of terms with values as a dictionary of {key,val} -> {url_id,term_freq}
    articles:list[RSS_Article]      # List of articles as RSS_Article objects
    seen_article_links:list[str]    # List of all article links that have been parsed
    
    def __init__(self, load_storage:str=Paths.JSONS_DIR, auto_index_feeds:bool=False):
        self.index = {}             
        self.page_ranks = []        
        self.articles = []      
        self.outbound_links = {}  
        self.seen_article_links = []
        
        if load_storage:
            self.index = json.load(open(f'{load_storage}/{Crawler.index_json}', 'r'))  
                
            tmp_articles = json.load(open(f'{load_storage}/{Crawler.articles_json}', 'r'))
            for a in tmp_articles: self.articles.append(RSS_Article())
            
            self.num_terms = json.load(open(f'{load_storage}/{Crawler.num_terms_json}', 'r'))
            self.outbound_links = json.load(open(f'{load_storage}/{Crawler.outbound_links_json}', 'r'))
        
        if auto_index_feeds: 
            feeds:dict = json.load(open(Paths.FEEDS_JSON, 'r'))
            for l,f in feeds.items(): 
                print(f"Indexing {f['feed_title']} ({l})")
                self.index_url(l, tag=f["article_link_tag"])
        
              
    ''' index_url(url)

        PURPOSE: 
            Visit the index url and then all frontiers off it. DO NOT visit links off frontiers.
            NOTE: assumes the index is an xml (i.e. an RSS feed)
            
        PARAMETERS: 
            url (str) - base (index) url
            *tag (str) - optional specify the name of the tag in the XML content that denotes links to articles. default = 'link'
                         
        RETURNS: 
            The number of pages indexed (int)    
    '''
    def index_url(self, url, tag:str='link') -> int:
        orig_num_articles = len(self.articles)  # Number of URLS originally to calc how many new ones we index
        
        # Get all the frontiers off the index
        try: 
            response = requests.get(url, headers=Crawler.headers)   # Fetch the HTML content
            response.raise_for_status()                             # Check if the request was successful
            soup = BeautifulSoup(response.text, 'xml')              # Parse the HTML

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the content for {url}: {e}")
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []
                
        # Find items (articles) in the content 
        # NOTE: this can be used later to create article objects for easier access and searching,
        #       similar to how the previous RSS feed script did. The attributes can then be stored 
        #       for faster lookup and a more detailed summary with returns from indexing 
        tmp_articles = [RSS_Article(a.title.text, a.link.text, a.pubDate.text, []) for a in soup.find_all('item')]
                
        # Visit all the hyperlinks off this page and parse the content
        # NOTE: parse_url_content adds the outbound links from the frontier to self.outbound_links
        for a in tmp_articles: self.parse_article_content(a)

        # Return the length of the first value in self.outbound_links, since that is the number of urls off the index
        return len(self.articles) - orig_num_articles
    
    ''' parse_article_content(article) 
        
        PURPOSE: 
            Add the content from the URL to self.index and get the links off the page

        PARAMETERS: 
            article (RSS_Article) - the article to parse the content of
        
        RETURNS: 
            (int) The article id in self.articles, i.e. the index, if successful; -1 if error
    '''
    def parse_article_content(self, article:RSS_Article) -> int: 
        
        # Check if we've seen this URL before - return if we have
        if article.article_link in self.seen_article_links: return -1
        
        # Define the regex pattern for valid URLs
        pattern = compile(Crawler.url_regex_pattern)
        
        try: 
            response = requests.get(article.article_link, headers=Crawler.headers) # Fetch the HTML content
            response.raise_for_status()                           # Check if the request was successful
            soup = BeautifulSoup(response.text, 'html.parser')    # Parse the HTML
            article_id:int = len(self.articles)                   # Save this article's id
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the content for \"{article.article_link}\": {e}")
            return -1
        except Exception as e:
            print(f"Error: {e}")
            return -1
        
        # Find links in the content
        frontiers = [f"{link.get('href')}" for link in soup.find_all('a') if pattern.match(str(link.get('href')))]
        
        frontiers = list(set(frontiers))       # Remove duplicates in the frontiers list by casting to a set and back to list  
        article.outbound_links = frontiers     # Add the outbound links for this frontier to self.outbound_links
        
        # ---- Tokenization ---- #
        tokens:list[str] = self.tokenize(soup.text)     # Tokenize the content 
        article.num_terms = len(tokens)                 # Record the number of terms
        
        # Add the tokens and corresponding term freqs to self.index
        for t in tokens: 
            if t in self.index:             # If token exists in the index  
                if article_id in self.index[t]:     # If this url id exists for this token
                        self.index[t][article_id] += 1  # Increment term count 
                else:                           # If this url id does note exist for this token
                    self.index[t][article_id] = 1       # Add it w/ term frequency of 1
            else:                           # If token does not exist in the index
                self.index[t] = {article_id:1}      # Add it with a dictionary containing just this url id and 1 for term frequency 
        
        # Append the article to self.articles
        self.articles.append(article)
        self.seen_article_links.append(article.article_link)
        
        return article_id
    
    ''' tokenize(text)
        
        PURPOSE: 
            Convert a string of terms into a list of terms 
    
        PARAMETERS: 
            text (str) - a single string to be tokenized
            
        RETURNS: 
            A list of terms contained within the text
    '''
    @staticmethod
    def tokenize(text):
        tokens = []
        
        # Replace any special chars in the content with spaces to act as delimeters 
        pattern:str = r'[^a-zA-Z0-9\s]+'     # Pattern of plaintext characters (a-z, A-Z, 0-9, no special chars)
        text = sub(pattern, ' ', text)     # Substitute all matches with spaces  
        text = sub(r'html\r\n', ' ', text)
        text = sub(r'\n+', ' ', text)
        
        # Split the text on spaces, convert to lower, and strip whitespace from each token 
        tokens = [s.lower().strip() for s in text.split(' ') if s.strip()]
        
        return tokens
    
    ''' to_jsons(dir)
    
        PURPOSE: 
            Convert the local data in the crawler to jsons in the specified directory
        
        PARAMETERS: 
            dir (str) - directory path to save the jsons
            *indent (int) - optional specify the indent for the json dumps. default = 4
            
        RETURNS: 
            None
    '''
    def to_jsons(self, dir:str, indent:int=4) -> None:
        json.dump(self.index, open(f'{dir}/{Crawler.index_json}', 'w'), indent=indent)                              # Saving self.index
        json.dump(self.seen_article_links, open(f'{dir}/{Crawler.seen_article_links_json}', 'w'), indent=indent)    # Saving self.seen_article_links
        
        # Saving self.articles
        articles_as_dicts = [a.to_dict() for a in self.articles]
        json.dump(articles_as_dicts, open(f'{dir}/{Crawler.articles_json}', 'w'), indent=indent)  
        
        