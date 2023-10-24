import requests 
from bs4 import BeautifulSoup
import nltk
import random as rand
import numpy as np
from re import sub, compile, match

from URLIndex import URLIndex

class Crawler: 
    
    # STATIC ATTRIBUTES 
    url_regex_pattern:str = r'https?://[^\s/$.?#].[^\s]*'   # Regex pattern that a valid URL must match 
    headers:dict[str,str] = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'              
            }
    tele_factor:int = 0.1
    
    # DYNAMIC ATTRIBUTES 
    index:dict[str,list[int]]   # Index of terms 
    page_rank_matrix:np.array   # Page rank matrix
    page_ranks:list[float]      # Precomputed page ranks for each URL where indices correspond to self.urls
    urls:list[str]              # List of URLs
    
    def __init__(self):
        self.index = {}             
        self.page_rank_matrix = []   
        self.page_ranks = []        
        self.urls = []              
        
        
    ''' index_url(url)

        PURPOSE: 
            Visit the index url and then all frontiers off it. DO NOT visit links off frontiers.
            
        PARAMETERS: 
            url (str) - base (index) url

        RETURNS: 
            The number of pages indexed (int)    
    '''
    def index_url(self, url, tag:str='link') -> int:
         
        outbound_links:dict[int, list[str]] = {}  # Dict keeping track of the outbound links off the index AND off each frontier to construct matrix later

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
        
        outbound_links[0] = frontiers.copy()
        
        # Visit all the hyperlinks off this page and get their links
        while frontiers: 
            frontier_info = self.parse_url_content(frontiers.pop())
            
            # Check if we got a valid response - we've seen the frontier before if not
            if frontier_info[0] >= 0: outbound_links[frontier_info[0]] = frontier_info[1]
        
        print("OUTBOUND_LINKS: ")
        for k,v in outbound_links.items(): print(f"{k} | {v}")
        
        # ---- Calculate the page ranks matrix (self.pageRanks) using the outbound_links dict ---- # 
        
        # Initialize self.pageRanks to have all the proper number of rows and columns
        n:int = len(outbound_links)                     # x == number of URLs we're indexing (including the index) 
        self.page_rank_matrix = np.zeros((n,n))         # Create a square n * n matrix to avoid index out of bounds errors when adding rows
        
        # Formatting the tele matrix
        tele_matrix = np.ones((n,n))                        # Tele matrix to sum with page rank matrix 
        tele_matrix = tele_matrix * (self.tele_factor/n)    # Dividnig by the sum (n) and multiplying by the scaler alpha (tele factor)

        # Traverse through outbound_links and convert each key:val into a row in self.pageRanks 
        # NOTE: v == list[str] of the outbound links for url_id k[int]
        #   > Normalize each entry at the same time by adding each cell as 1/(num outlinks for this row)
        #   > Multiply the tele factor (alpha) at the same time, instead of distributing it after 
        for k,v in outbound_links.items(): 
            these_outlinks:list[int] = [self.urls.index(out_link) for out_link in v] # Convert the list of outbound links (as strings) to the correspondnig URL indices 
            this_row:list[int] = list(np.zeros(len(self.urls)))                      # Start with an array of 0s representing NO outlinks
            
            # Traverse these_outlinks and set the indices corresponding to the outlinks in these_outlinks to 1/(num outlinks)
            for i in these_outlinks: this_row[i] = round((1-self.tele_factor)*(1/len(these_outlinks)), 2)            
            self.page_rank_matrix[k, :] = this_row                                 
        
        self.page_rank_matrix = self.page_rank_matrix + tele_matrix             # Sum the page rank matrix with the tele matrix 
        self.page_rank_matrix = np.round(self.page_rank_matrix, decimals=3)     # Round the values 
        
        # Compute the page ranks for each page and store in self.page_ranks by summing the columns of the matrix
        self.calc_page_ranks()
        
        # Return the length of outbound links, since that is the number of urls we visited
        return len(outbound_links)
    
    ''' calc_page_ranks() 
        
        PURPOSE: 
            Calculate the page ranks for each page and stores in self.page_ranks

        RETURNS: 
            None
    '''
    def calc_page_ranks(self) -> None: 
        x0 = np.zeros(len(self.urls))
        x0[0] = 1
        X = [x0]
        
        for i in range(1, len(self.urls)): X.append(np.round(np.dot(X[i-1], self.page_rank_matrix), 3))
        self.page_ranks = X[len(X)-1]
        
    
    ''' parse_url_content(url) 
        
        PURPOSE: 
            Add the content from the URL to self.index and get the links off the page

        PARAMETERS: 
            url (str) - url 
        
        RETURNS: 
            tuple(frontier's url id, list of frontiers off this url)
    '''
    def parse_url_content(self, url) -> (int, list[str]): 
        
        # Check if we've seen this URL before - return if we have
        if url in self.urls: return (-1, [])
        
        # Define the regex pattern for valid URLs
        pattern = re.compile(Crawler.url_regex_pattern)
        
        try: 
            response = requests.get(url, headers=Crawler.headers) # Fetch the HTML content
            response.raise_for_status()                           # Check if the request was successful
            soup = BeautifulSoup(response.text, 'html.parser')    # Parse the HTML
            self.urls.append(url)                                 # Append the URL to self.documents 
            url_id:int = len(self.urls) - 1                       # Save this URL id
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the content for {url}: {e}")
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []
        
        # Find links in the content
        frontiers = [f"{link.get('href')}" for link in soup.find_all('a') if pattern.match(str(link.get('href')))]
        
        # Remove duplicates in the frontiers list by casting to a set and back to list
        frontiers = list(set(frontiers))           
        
        # Tokenize the content and add tokens to self.index
        tokens:list[str] = self.tokenize(soup.text)      
        for t in tokens: 
            try: self.index[t].append(url_id) 
            except KeyError: self.index[t] = [url_id] 
            
        return url_id, frontiers
    
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
        pattern:str = r'[^a-zA-Z0-9\s]'     # Pattern of plaintext characters (a-z, A-Z, 0-9, no special chars)
        text = sub(pattern, ' ', text)      # Substitute all matches with spaces  
        text = sub(r'html\r\n', '', text) 
        
        # Split the text on spaces, convert to lower, and strip whitespace from each token 
        tokens = [s.lower().strip() for s in text.split(' ') if not s.isspace() and s]
        
        return tokens
    
