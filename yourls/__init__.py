
class YourlsError(Exception):
    '''Base exception for all Yourls exceptions'''
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class YourlsOperationError(YourlsError):
    '''Error during URL shortening or expansion'''
    def __init__(self, url, message):
        self.url = url
        self.message = message
    def __str__(self):
        return repr('Error with url \'%s\' - %s' % (self.url, self.message))

