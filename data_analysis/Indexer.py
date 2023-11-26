from crawler.Crawler import Crawler
from Paths import Paths 
from rss_feed.RSS import *
from crawler.crawler_exceptions import *

class Indexer: 
    
    # STATIC ATTRIBUTES
    # Operators for querying the index
    AND_OP:str = "AND"      
    OR_OP:str = "OR"
    NOR_OP:str = "NOR" 
    XOR_OP:str = "XOR"
    
    # List of all valid operators 
    OPERATORS:list[str] = [
        Indexer.AND_OP,
        Indexer.OR_OP, 
        Indexer.NOR_OP,
        Indexer.XOR_OP
    ]
    
    def __init__(self): 
        pass
    
    
    ''' search_index(query)
    
        PURPOSE: 
            Search the index for the given query 
        
        PARAMETERS: 
            search_terms (list[str]) - search terms as a list containing an arbitrary number of values
            op (str) - (optional) a valid operator string, i.e. contained in Indexer.OPERATORS; default = "AND"
        
        RETURNS: 
            An ordered list of matched articles as RSS_Article objects in order of relevancy, where relevancy is calculated by the relative
            term frequency for each article and the query 
            
        RAISES: 
            Custom exception "InvalidOperator" if given an operator that is not supported. 
            Supported operators are contained in Indexer.OPERATORS
    '''
    def search_index(self, search_terms:str, op:str=Indexer.AND_OP) -> list[RSS_Article]: 
        
        # Base cases 
        if not search_terms: return []                                          # Not given any search terms
        if not op or not op in Indexer.OPERATORS: raise InvalidOperator(op)     # Given an invalid operator
        
        # Stem the given search terms 
        # DO SOMETHING ... 
        
        # Call the appropriate helper according to the given operator
        matched_ids:list[int] = []
        match(op): 
            case Indexer.AND_OP: matched_ids = Indexer.and_search(search_terms)
            case Indexer.OR_OP: matched_ids = Indexer.or_search(search_terms)
            #case Indexer.NOR_OP: matched_ids = Indexer.nor_search(search_terms)
            #case Indexer.XOR_OP: matched_ids = Indexer.xor_search(search_terms)

        # Convert the matched ids to RSS_Article objects 
        all_articles = json.loads(open(Indexer.articles_path, "r"))
        matched_articles = [RSS_Article.article_from_dict(all_articles[a]) for a in matched_ids]
        
        
        pass
    
    
    ''' and_search(search_terms) - 
    
        PURPOSE: 
            Helper to conduct a search of the index for the given terms using the AND operator
        
        PARAMETERS: 
            search_terms (list[str]) - list of terms to search for
        
        RETURNS: 
            A list of int containing the indices (IDs) of the matched articles in Indexer.urls_path json file
    '''
    @staticmethod
    def and_search(search_terms:list[str]) -> list[int]:
        pass
    
    ''' or_search(search_terms) - 
    
        PURPOSE: 
            Helper to conduct a search of the index for the given terms using the OR operator
        
        PARAMETERS: 
            search_terms (list[str]) - list of terms to search for
        
        RETURNS: 
            A list of int containing the indices (IDs) of the matched articles in Indexer.urls_path json file
    '''
    @staticmethod
    def and_search(search_terms:list[str]) -> list[int]:
        pass
        
        