from queue import Queue, LifoQueue


directions = ['n', 'e', 's', 'w']



class Branch():
    def __init__(self, start, path=None, unexplored=None, explored=None):
        self.start = start 
        self.path = Path(
            start=start,
        )
        self.explored = []
        self.unexplored = unexplored

    def get_dir(self):
        temp = self.unexplored.pop()
        if temp is not None:
            self.explored.append(temp)
        return temp

    def __call__(self):
        pass



class BranchHandler():

    def __init__(self, room, world, branches=None):
        self.openings = detect_openings(room)
        self.start = room
        self.world = world
        if branches is None:
            self.branches = []
            self.create_branches()
        else:
            self.branches = branches


    def create_branches(self):
        dirs = list(self.openings.keys())
        for i in range(len(self.openings)):
            exploration_order = dirs[i:] + dirs[:i]
            self.branches.append(
                Branch(
                    start = self.start,
                    unexplored = exploration_order,
                )
            )


    def run_branch(self, branch):
        while len(branch.unexplored) > 0:
            trav = DFT(
                start = branch.start,
                direction = branch.get_dir(),
                network = self.world,
                visited=[]
            )
            
            leg = trav()
            branch.path.stack(leg)
            if  not self._check_circular(branch):
                branch.path.stack(self._back_track(leg))
            else:
                branch.path.add(self.start.id)


    def _check_circular(self, branch):
        ngbs = [self.openings[key].id for key in self.openings]
        return branch.path[-1] in ngbs


    def _back_track(self, leg):
        backpath =  leg.reverse()
        backpath.steps.pop(0)
        return backpath


    def search_branches(self):
        for branch in self.branches:
            self.run_branch(branch)


    def get_optim(self):
        ## TODO sort through final branch path for shortest path
        pass


    @property 
    def paths(self):
        return [branch.path for branch in self.branches if branch is not None]
    





class Path():
    def __init__(self, start=None, exit=None, steps=None):
        self.start = start 
        self.exit = exit
        if steps is None:
            self.steps = []
        else:
            self.steps = steps

    def __repr__(self):
        return f'{self.steps}'

    def __len__(self):
        return len(self.steps)

    def add(self, node):
        self.steps.append(node)

    def stack(self, path):
        if path is None:
            return
        # print('stacking ', path.steps, 'to', self.steps)
        # print('checking ', self.start.id, 'against ', path[0])
        if self.start.id == path[0]:
            self.steps.extend(path.steps[1:])
        else:
            self.steps.extend(path.steps)

    def reverse(self):
        rpath = Path(steps = self.steps[::-1]) 
        return rpath

    def __getitem__(self, idx):
        return self.steps[idx]



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

    def __call__(self):
        return self.traverse()


    def get_neighbors(self, room):

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

        openings = detect_openings(room)
        self.direction = _turn(openings)

        return [check_dir(room, self.direction)]


    def traverse(self, starting_vertex=None):

        if starting_vertex == None:
            starting_vertex = self.start.id

        q = LifoQueue()
        q.put(starting_vertex)

        visited = set()
        path = Path()

        while not q.empty():
            c = q.get()
            if c not in visited:
                visited.add(c)
                path.add(c)
                [q.put(n.id) for n in self.get_neighbors(self.network.rooms[c]) if n is not None]
        
        return path



########################
### Helper Functions ###
########################


def check_dir(room, direction):
    return room.get_room_in_direction(direction)


def detect_openings(room, last_direction=None):
    openings = {}
    for direction in directions:
        s = check_dir(room, direction)
        if s is not None:
            openings[direction] = s

    if last_direction is not None:
        del openings[last_direction]
    return openings

