from crawler.Crawler import Crawler
from config.Paths import Paths 
from rss_feed.RSS import *
from crawler.crawler_exceptions import *

class Indexer: 
    
    # STATIC ATTRIBUTES
    # Operators for querying the index
    AND_OP:str = "AND"      
    OR_OP:str = "OR"
    NOR_OP:str = "NOR" 
    XOR_OP:str = "XOR"
    
    OPERATORS:list[str] = [
        AND_OP,
        OR_OP,
        NOR_OP,
        XOR_OP
    ]
    
    # DYNAMIC ATTRIBUTES 
    index:dict
    all_articles:list[RSS_Article]
    
    def __init__(self): 
        self.index = json.load(open(Paths.INDEX_JSON, "r"))
        self.all_articles = json.load(open(Paths.ARTICLES_JSON, "r"))
        print(f"Init Indexer: \n\tNum terms: {len(self.index)}\n\tNum articles: {len(self.all_articles)}")
        
    
    ''' search_index(query)
    
        PURPOSE: 
            Search the index for the given query 
        
        PARAMETERS: 
            search_terms (str) - search terms as a single string containing an arbitrary number of values
            op (str) - (optional) a valid operator string, i.e. contained in Indexer.OPERATORS; default = "AND"
        
        RETURNS: 
            (dict[int,dict]) An ordered dictionary with key:val pairs => rel_tf:article_as_dict, where rel_tf is the avg relative term
            frequency match across all given terms and article_as_dict is a dictionary representation of an RSS_Article
            object.
            
        RAISES: 
            Custom exception "InvalidOperator" if given an operator that is not supported. 
            Supported operators are contained in Indexer.OPERATORS
    '''
    def search_index(self, query:str, op:str=AND_OP) -> dict[float,dict]: 
        print(f"AND QUERY: \"{query}\"")
        
        # Base cases 
        if not query: return []                                             # Not given any search terms
        if not op or not op in Indexer.OPERATORS: raise InvalidOperator(op) # Given an invalid operator
        
        # Tokenize and stem the query 
        query_toks:list[str] = Crawler.tokenize(query)
        print(query_toks)
        
        # Call the appropriate helper according to the given operator
        matched_ids:dict[int,int] = []
        match(op): 
            case Indexer.AND_OP: matched_ids = self.and_search(query_toks)
            #case Indexer.OR_OP: matched_ids = Indexer.or_search(query_toks)
            #case Indexer.NOR_OP: matched_ids = Indexer.nor_search(search_terms)
            #case Indexer.XOR_OP: matched_ids = Indexer.xor_search(search_terms)
        
        matched_articles = {} 
        
        for a,tf in matched_ids.items(): 
            this_article:dict = self.all_articles[a]
            rel_tf:float = tf / this_article['article_num_terms']
            
            matched_articles[rel_tf] = this_article

        return dict(sorted(matched_articles.items(), reverse=True))
    
    
    ''' and_search(search_terms) - 
    
        PURPOSE: 
            Helper to conduct a search of the index for the given terms using the AND operator
        
        PARAMETERS: 
            search_terms (list[str]) - list of terms to search for
        
        RETURNS: 
            A dictionary (dict[int,int]) of key:val => article_id:ctf, where ctf is the cumulative term frequency across all terms
            in the query for that article, i.e. the sum of the number of times each search term appears in that article, and 
            article_id corresponds to indices in the index
    '''
    def and_search(self, search_terms:list[str]) -> dict[int,int]:
        
        # Query the index to get a list of dictionaries containing the article ids and term frequencies for each search term 
        matched_terms:dict[str,dict] = {}
        for t in search_terms: 
            try: matched_terms[t] = self.index[t]   # Get this term in the index
            except KeyError: continue               # Skip if term does not exist in the index
        
        # Convert the list of dictionaries into a single dictionary with key:val => article_id:cumulative_term_freq 
        # and remove any IDs that don't appear in ALL terms
        # NOTE: Since this is an AND query, we don't care about individual frequencies for each term, so we can combine 
        #       the term frequencies for each article id to be the sum of the frequencies across all search terms
        
        # Get all the values from matched_terms (i.e a list of dictionaries with key:val => article_id:term_freq)
        # NOTE: at this point we don't care what the actual term strings are
        lod:list[dict] = list(matched_terms.values())              
        
        # Take the intersection of the keys to eliminate any that don't match ALL terms                     
        intersect_ids:set = set.intersection(*[set(d.keys()) for d in lod])
        
        # Convert this to a dictionary in the format we want to return, i.e. article_id:cumulative_tf
        result_dict:dict[int,int] = {int(key): sum([d[key] for d in lod]) for key in intersect_ids}
        return result_dict
    
    ''' or_search(search_terms) - 
    
        PURPOSE: 
            Helper to conduct a search of the index for the given terms using the OR operator
        
        PARAMETERS: 
            search_terms (list[str]) - list of terms to search for
        
        RETURNS: 
            A list of int containing the indices (IDs) of the matched articles in Indexer.urls_path json file
    '''
    def or_search(self, search_terms:list[str]) -> dict[int,int]:
        pass
        
        