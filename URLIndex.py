
class URLIndex: 
    
    ''' index:dict[str, dict[int,int]] - Index of the terms and their frequencies (key:val == term:[{url_id,frequency}])
        Ex: {
            "auto": {
                      1:1, 
                      5:2, 
                      10:21
                    },
            "games": { 
                      3:4,
                      38:4,
                      24: 12
                    },
            ... : { ... }
    '''
    index:dict[str, list[dict[int,int]]] 
    
    ''' url_num_terms:dict[int, int] - Number of terms in each URL to calc page rank (key:val == url_id,num_terms)
        Ex: {
              0 : 496,
              1 : 156,
              2 : 52, 
              3 : 845, 
              ... : ... 
              len(self.urls) - 1 : num_terms
            }
    '''
    url_num_terms:dict[int, int]        
    
    ''' url_hyperlinks:dict[int, list[str]] - Hyperlinks seen in each URL (key:val == url_id:[hyperlinks])
        Ex: { 
              0: ["https://google.com", 
                  "https://facebook.com" 
                 ],
              1: ["https://reddit.com",
                  "https://cs.wpi.edu/cs2192"
                 ],
              2: [],
              ... : ... 
              len(self.urls) - 1: ["https://link1.net/endpoint1/endpoint2",
                                   "https://link2.edu" 
                                  ]    
            }
    ''' 
    url_hyperlinks:dict[int, list[str]] 
    
    ''' urls:list[str] - List of all seen URLs 
        Ex: ["https://google.com", 
            "https://facebook.com", 
            "https://reddit.com/web-crawling",
            ... 
            ]
    '''
    urls:list[str]  
    
    def __init__(self): 
        
        # Check if the given base URL is a valid URL
        # NOTE: use regex, throw error if not
        # DO SOMETHING ... 
        
        self.index = {}     
        self.url_num_terms = {}
        self.url_hyperlinks = {}
        self.urls = []  

    ''' check_url_exists(url) - check if the URL exists in the index
        
        PARAMETERS: 
            url (str) - URL to check if exists
            
        RETURNS: 
            True if the URL DOES exist, False if the URL DOES NOT exist
    '''
    def check_url_exists(self, url:str) -> bool: 
        return url in self.urls
    
    ''' new_url(url) - add a new URL to the index, return FALSE if the url exists already
        
        PARAMETERS: 
            url (str) - new URL to add
            
        RETURNS: 
            True if added successfully, false if the url exists already        
    '''
    def new_url(self, url:str, num_terms:int, tokenized_content:list[str], hyperlinks:list[str]) -> bool:
        
        # Check if we've seen this URL yet, return False if we have
        if self.check_url_exists(url): 
            print(f"check_url_exists({url}) == True") 
            return False
        
        # Get the will-be ID for this URL 
        # NOTE: called before appending b/c self.urls is 0-indexed, so the id is len(self.urls) - 1 AFTER new url is added,
        #       thus is just the length BEFORE new url is added
        this_id:int = len(self.urls) 
        
        # Adding the data from the new URL
        self.urls.append(url)                       # Add the url to self.urls
        self.url_num_terms[this_id] = num_terms     # Save the number of terms 
        self.url_hyperlinks[this_id] = hyperlinks   # Save the hyperlinks
        
        # Add the tokenized content for this url to self.index
        for t in tokenized_content: 
            # If the token does not already exist in the index, create a new key with a dictionary containing only this url_id and "1" for the term freq
            if not t in self.index: self.index[t] = {this_id: 1} 
                
            # If the token DOES already exist in the index 
            else: 
                curr_val = self.index[t]  # Get the current value (url_ids and term freq) for this token in self.index
                
                # Check if this url_id already exists in the dict for this token
                if this_id in curr_val: curr_val[this_id] += 1  # If this url_id DOES exist already, add 1 to the term frequency
                else: curr_val[this_id] = 1                     # If this url_id does NOT exist already, then add it with "1" as the term frequency           
                
                # Replace this value in self.index with the updated value
                self.index[t] = curr_val    
        
        return True
        