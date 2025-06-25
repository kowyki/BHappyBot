class Chat_ID:
    def __init__(self, data):
        self.data = data
        if type(self.data) is str: 
            self.string = data
            self.integer = int(self.data.replace('minus', '-'))
        elif type(self.data) is int: 
            self.integer = data
            self.string = str(self.data).replace('-', 'minus')
