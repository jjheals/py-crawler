import requests 
from bs4 import BeautifulSoup
import re
import nltk
import random as rand
from URLIndex import URLIndex

class Crawler: 
    
    base_url:str
    url_index:URLIndex
    tele_factor:int = 0.1
    
    def __init__(self, base_url:str):
        self.base_url = base_url
        self.url_index = URLIndex()
        
    @staticmethod
    def __process_text__(text:str) -> list[str]: 
        # Remove any "\"s to avoid errors with parsing the raw content 
        text = re.sub(r'\\', '', text) 
        
        processed_tokens:str = []     # Processed text as tokens to return 

        # Install the required packages from NLTK if needed 
        try: nltk.corpus.wordnet
        except LookupError: nltk.download('wordnet')
        
        try: nltk.data.find('tokenizers/punkt') 
        except LookupError: nltk.download('punkt')
        
        try: nltk.corpus.stopwords.words('english')
        except LookupError: nltk.download('stopwords') 

        # Init BS parser 
        soup = BeautifulSoup(text, 'html.parser')

        # Perform tokenization 
        # Replace any special chars in the content with spaces to act as delimeters 
        pattern:str = r'[^a-zA-Z0-9\s]'     # Pattern of plaintext characters (a-z, A-Z, 0-9, no special chars)
        text = re.sub(pattern, ' ', text)      # Substitute all matches with spaces  
            
        # Split the text on spaces, convert to lower, and strip whitespace from each token 
        tokens = [s.lower().strip() for s in text.split(' ') if not s.isspace()]
            
        # Perform stemming
        # DO SOMETHING 
        
        # Stop words
        stop_words = set(nltk.corpus.stopwords.words('english'))            # Get a set of stop words to remove (the, a, an, and, in, ...)
        tokens = [token for token in tokens if token not in stop_words]     # Remove stop words from the list of tokens 
        
        return tokens    
            
    @staticmethod
    def __fetch__(url:str) -> str:
        headers = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'              
        }
        
        try: 
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(e)
            return f"ERROR: RequestException in Crawler.__fetch__() for URL \"{url}\"."
        except Exception as e:
            print(e)
            return f"ERROR: Unknown exception in Crawler.__fetch__() for URL \"{url}\"."
    
    
    def index_url(self, url:str):

        # Since this function is recursive, check if we've seen this URL before and simply return if we have
        if self.url_index.check_url_exists(url): return 
        
        # Keep track of the number of original URLs so we know how many new ones we visited 
        original_num_urls = len(self.url_index.urls)
            
        try:
            # Fetch the content of the base URL
            content:str = Crawler.__fetch__(url)
            soup = BeautifulSoup(content, 'html.parser')    # Parse the HTML
            
            # Find links in the content
            hyperlinks = [f"{'/'.join(url.split('/')[:-1])}/{link.get('href')}" for link in soup.find_all('a')]
            
            # Tokenize the content 
            tokens:list[str] = Crawler.__process_text__(soup.text)
            
            # Add the new URL to the url_index
            if not self.url_index.new_url(url, len(tokens), tokens, hyperlinks): 
                print(f"new_url({url}) == False")
                return
            
            # Use the teleportation factor to determine if we're going to follow the hyperlinks or not 
            teleport:bool = (rand.randint(0,1) <= self.tele_factor)
            if teleport: 
                # Jump to a random page from hyperlinks (with equal probability)
                link_index:int = rand.randint(0, len(hyperlinks)-1)
                next_link:str = hyperlinks[link_index]
                hyperlinks.remove(next_link)
                            
                # Use recursion to visit the next link 
                self.index_url(next_link)
            
            # NOTE: run this WITHOUT "else" condition so that we hit all hyperlinks on the page eventually
            # Visit the next hyperlink in the list of hyperlinks (assuming we haven't visited it yet)
            while hyperlinks:
                next_link:str = hyperlinks[0]
                hyperlinks.remove(next_link)                
                self.index_url(next_link)
            
            # Calculate the difference between the original number of urls and the current number of urls to calc
            # how many urls we visited in total
            return len(self.url_index.urls) - original_num_urls
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the content for {url}: {e}")
            return len(self.url_index.urls) - original_num_urls
        except Exception as e:
            print(f"Error: {e}")
            return len(self.url_index.urls) - original_num_urls
        