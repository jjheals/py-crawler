
class InvalidOperator(Exception): 
    def __init__(self, message="Given operator is not supported.", op=''):
        if op: self.message=f"Given operator \"{op}\" is not supported."
        else: self.message=message
        super.__init__(self.message)
        