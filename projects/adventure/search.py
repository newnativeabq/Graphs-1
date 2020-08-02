from queue import Queue, LifoQueue



directions = ['n', 'e', 's', 'w']


class Path():
    def __init__(self, start=None, ext=None):
        self.start = start 
        self.ext = ext
        self.steps = []

    def add(self, node):
        self.steps.append(node)

    def stack(self, path):
        if self.steps[-1] == path.steps[0]:
            self.steps.extend(path.steps[1:])
        else:
            self.steps.extend(path.steps)



class BFS():
    def __init__(self, start, direction:str, visited, network):
        self.start = start
        self.direction = direction
        self.network = network
        self.visited = visited

    def run(self):
        pass



class DFT():
    def __init__(self, start, direction, network, visited):
        self.start = start
        self.network = network
        self.visited = set(visited)
        self.direction = direction

    def run(self):
        pass


    def get_neighbors(self, room):

        def _detect_openings(room=room):
            direction = self.direction
            openings = {}
            for direction in directions:
                s = check_dir(room, direction)
                if s is not None:
                    openings[direction] = s
            return openings

        def _find_left(direction=self.direction):
            lefts = {
                'n': 'w',
                'w': 's',
                's': 'e',
                'e': 'n',
            }
            return lefts[direction]

        def _find_right(direction=self.direction):
            rights = {
                'n': 'e',
                'e': 's',
                's': 'w',
                'w': 'n',
            }
            return rights[direction]

        def _turn(openings):
            current_direction = self.direction
            ldir = _find_left(current_direction)
            if ldir in openings:
                return ldir
            rdir = _find_right(current_direction)
            if rdir in openings:
                return rdir
            return current_direction

        openings = _detect_openings(room)
        self.direction = _turn(openings)

        return [check_dir(room, self.direction)]


    def traverse(self, starting_vertex=None):

        if starting_vertex == None:
            starting_vertex = self.start.id

        q = LifoQueue()
        q.put(starting_vertex)

        visited = set()
        path = []

        while not q.empty():
            c = q.get()
            if c not in visited:
                visited.add(c)
                path.append(c)
                [q.put(n.id) for n in self.get_neighbors(self.network.rooms[c])]
        
        return path



class Branch():
    def __init__(self, node, path):
        self.node = node 
        self.path = path 

    def run(self):
        pass
        


def check_dir(room, direction):
    return room.get_room_in_direction(direction)

