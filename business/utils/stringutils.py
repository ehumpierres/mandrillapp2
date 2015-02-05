

class StringUtils():
    
    def __init__(self):
        pass
    
    # clear line breaks
    @staticmethod
    def clear_line_breaks(self, text):
        return text.replace('\n', ' ').replace('\r', '')