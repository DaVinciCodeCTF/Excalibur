class Form:

    def __init__(self, url, method, parameters):
        self.url = url
        if method is None:
            method = "POST"
        self.method = method
        self.parameters = parameters
