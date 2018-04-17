from collections import namedtuple

Event = namedtuple('Event', 'name src dst')


class TransitionError(Exception):
    pass


class SimpleFSM:
    def __init__(self, events, initial=None):
        self.state = initial
        self.graph = dict()
        for e in (Event(*i) for i in events):
            trans = self.graph.setdefault(e.name, dict())
            trans[e.src] = e.dst
        import pprint
        pprint.pprint(self.graph)

    def __call__(self, event):
        src = self.state
        graph = self.graph
        try:
            self.state = ((src in graph[event] and graph[event][src]) or
                          ('*' in graph[event] and graph[event]['*']) or
                          (graph['ThisIsMostCertainlyNotHandled!1']))
        except KeyError:
            try:
                self.state = graph['*'][src]
            except KeyError:
                raise TransitionError(event, self.state)
            else:
                return
