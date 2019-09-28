class State:
    def __init__(self, name):
        self.name = name
        self.action = None
        self.answer = None
        self.event = None
        self.edges = {} # event:state

    def set_action(self, action):
        self.action = action

    def set_answer(self, answer):
        self.answer = answer

    def add_edge(self, event, state):
        self.edges[event] = state

    def has_event(self, event):
        return any([event == key for key in self.edges])

    def set_event(self, event):
        self.event = event

    def next_state(self, event):
        if event in self.edges:
            return self.edges[event]
        else:
            return None
