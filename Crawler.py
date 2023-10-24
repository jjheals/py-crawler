import requests 
from bs4 import BeautifulSoup
from re import sub, compile
import json

from URLIndex import URLIndex

class Crawler: 
    
    # STATIC ATTRIBUTES 
    url_regex_pattern:str = r'https?://[^\s/$.?#].[^\s]*'   # Regex pattern that a valid URL must match 
    headers:dict[str,str] = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'              
            }
    tele_factor:int = 0.1
    
    # json filenames 
    index_json:str = 'index.json'
    urls_json:str = 'urls.json'
    num_terms_json:str = 'num_terms.json'
    outbound_links_json:str = 'outbound_links.json'
    
    # DYNAMIC ATTRIBUTES 
    index:dict[str,dict[int,int]]   # Index of terms with values as a dictionary of {key,val} -> {url_id,term_freq}
    urls:list[str]                  # List of URLs
    num_terms:list[int]             # List of the number of terms in each URL where indices correspond to self.urls
    outbound_links:list[list[str]]  # List of lists of outbound links off each URL in self.urls 
    
    def __init__(self):
        self.index = {}             
        self.page_rank_matrix = []   
        self.page_ranks = []        
        self.urls = []      
        self.num_terms = []
        self.outbound_links = {}        
        
        
    ''' index_url(url)

        PURPOSE: 
            Visit the index url and then all frontiers off it. DO NOT visit links off frontiers.
            
        PARAMETERS: 
            url (str) - base (index) url

        RETURNS: 
            The number of pages indexed (int)    
    '''
    def index_url(self, url, tag:str='link') -> int:
         
        # Get all the frontiers off the index
        try: 
            response = requests.get(url, headers=Crawler.headers)   # Fetch the HTML content
            response.raise_for_status()                             # Check if the request was successful
            soup = BeautifulSoup(response.text, 'xml')              # Parse the HTML
            self.urls.append(url)                                   # Save the index as the first URL in urls

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
        articles = soup.find_all('item')
                
        # Extract the links to the articles 
        frontiers = [l.find(tag).text for l in articles]
        
        print(f"FRONTIERS:")
        for f in frontiers: print(f)
        
        self.outbound_links[0] = frontiers.copy()   # Save the outbound links from the index in self.outbound_links
        
        # Visit all the hyperlinks off this page and parse the content
        # NOTE: parse_url_content adds the outbound links from the frontier to self.outbound_links
        while frontiers: self.parse_url_content(frontiers.pop())

        # Return the length of the first value in self.outbound_links, since that is the number of urls off the index
        return len(self.outbound_links[0])
    
    ''' parse_url_content(url) 
        
        PURPOSE: 
            Add the content from the URL to self.index and get the links off the page

        PARAMETERS: 
            url (str) - url 
        
        RETURNS: 
            (int) The URL id in self.urls, i.e. the index, if successful; -1 if error
    '''
    def parse_url_content(self, url) -> (int, list[str]): 
        
        # Check if we've seen this URL before - return if we have
        if url in self.urls: return -1
        
        # Define the regex pattern for valid URLs
        pattern = compile(Crawler.url_regex_pattern)
        
        try: 
            response = requests.get(url, headers=Crawler.headers) # Fetch the HTML content
            response.raise_for_status()                           # Check if the request was successful
            soup = BeautifulSoup(response.text, 'html.parser')    # Parse the HTML
            self.urls.append(url)                                 # Append the URL to self.documents 
            url_id:int = len(self.urls) - 1                       # Save this URL id
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the content for {url}: {e}")
            return -1
        except Exception as e:
            print(f"Error: {e}")
            return -1
        
        # Find links in the content
        frontiers = [f"{link.get('href')}" for link in soup.find_all('a') if pattern.match(str(link.get('href')))]
        
        frontiers = list(set(frontiers))            # Remove duplicates in the frontiers list by casting to a set and back to list  
        self.outbound_links[url_id] = frontiers     # Add the outbound links for this frontier to self.outbound_links
        
        # ---- Tokenization ---- #
        tokens:list[str] = self.tokenize(soup.text)     # Tokenize the content 
        self.num_terms.append(len(tokens))              # Record the number of terms in self.num_terms
        
        # Add the tokens and corresponding term freqs to self.index
        for t in tokens: 
            if t in self.index:             # If token exists in the index  
                if url_id in self.index[t]:     # If this url id exists for this token
                        self.index[t][url_id] += 1  # Increment term count 
                else:                           # If this url id does note exist for this token
                    self.index[t][url_id] = 1       # Add it w/ term frequency of 1
            else:                           # If token does not exist in the index
                self.index[t] = {url_id:1}      # Add it with a dictionary containing just this url id and 1 for term frequency 
                
        return url_id
    
    ''' tokenize(text)
        
        PURPOSE: 
            Convert a string of terms into a list of terms 
    
        PARAMETERS: 
            text (str) - a single string to be tokenized
            
        RETURNS: 
            A list of terms contained within the text
    '''
    def tokenize(self, text):
        tokens = []
        
        # Replace any special chars in the content with spaces to act as delimeters 
        pattern:str = r'[^a-zA-Z0-9\s]+'     # Pattern of plaintext characters (a-z, A-Z, 0-9, no special chars)
        text = sub(pattern, ' ', text)     # Substitute all matches with spaces  
        text = sub(r'html\r\n', '', text)
        text = sub(r'\n+', ' ', text)
        
        # Split the text on spaces, convert to lower, and strip whitespace from each token 
        tokens = [s.lower().strip() for s in text.split(' ') if s.strip()]
        
        return tokens
    
    ''' to_jsons(dir)
    
        PURPOSE: 
            Convert the local data in the crawler to jsons in the specified directory
        
        PARAMETERS: 
            (str) dir - directory path to save the jsons
            *(int) indent - optional specify the indent for the json dumps. default = 4
            
        RETURNS: 
            None
    '''
    def to_jsons(self, dir:str, indent:int=4) -> None:
        json.dump(self.index, open(f'{dir}/{Crawler.index_json}', 'w'), indent=indent)                      # Saving self.index
        json.dump(self.urls, open(f'{dir}/{Crawler.urls_json}', 'w'), indent=indent)                        # Saving self.urls
        json.dump(self.num_terms, open(f'{dir}/{Crawler.num_terms_json}', 'w'), indent=indent)              # Saving self.num_terms
        json.dump(self.outbound_links, open(f'{dir}/{Crawler.outbound_links_json}', 'w'), indent=indent)    # Saving self.outbound_links
        