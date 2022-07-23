class State:
    def __init__(self):
        self.dic = {}

    def set(self, id, state):
        self.dic[str(id)] = state

    def clear(self, id):
        self.dic[str(id)] = 'Default'

    def get(self, id):
        if self.dic.get(str(id)) is None:
            return 'Default'
        else:
            return self.dic.get(str(id))
