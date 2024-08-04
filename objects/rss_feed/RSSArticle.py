

class RSSArticle: 
    
    # STATIC ATTRIBUTES
    dict_title:str = "article_title"            # article_title key when converted to/from dict
    dict_link:str = "article_link"              # article_link key when converted to/from dict
    dict_pub_date:str = "article_pub_date"      # pub_date key when converted to/from dict
    dict_num_terms:str = "article_num_terms"    # num_terms key when converted to/from dict
    dict_outlinks:str = "article_outlinks"      # out_links key when converted to/from dict
    
    # DYNAMIC ATTRIBUTES
    article_link:str            # Link to the article
    article_title:str           # Title of the article
    article_pub_date:str        # Published date of the article (if available)
    num_terms:int               # Number of terms (tokens) in the article 
    outlinks:list[str]          # The outbound links in the article
    
    
    def __init__(self, title:str, link:str, pub_date:str, out_links:list[str], num_terms:int=0): 
        self.article_title = title
        self.article_link = link
        self.article_pub_date = pub_date
        self.num_terms = num_terms
        self.outlinks = outlinks
    
    
    def to_dict(self) -> dict: 
        """Return this RSSArticle as a dictionary.""" 
        return {
            RSS_Article.dict_title: self.article_title,
            RSS_Article.dict_link: self.article_link,
            RSS_Article.dict_pub_date: self.article_pub_date,
            RSS_Article.dict_num_terms: self.num_terms,
            RSS_Article.dict_outlinks: self.outlinks
        }
        
        
    def to_string(self) -> str:
        """Return the attributes of this RSSArticle as a meaningful string."""
        return f"ARTICLE: \"{self.article_title}\"\n\tLink: {self.article_link}\n\tNum Terms: {self.num_terms}\n\tNum Outlinks: {len(self.outlinks)}"
    
    
    @staticmethod
    def from_dict(d:dict) -> 'RSSArticle': 
        """Create an RSSArticle from the given dictionary."""
        
        return RSSArticle(
            d.get([RSSArticle.dict_title], None), 
            d.get([RSSArticle.dict_link], None), 
            d.get([RSSArticle.dict_pub_date], None), 
            d.get([RSSArticle.outlinks], None),
            num_terms=d.get([RSSArticle.dict_num_terms], None)
        )
        
        
        