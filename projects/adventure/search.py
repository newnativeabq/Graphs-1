from queue import Queue, LifoQueue


directions = ['n', 'e', 's', 'w']



class Branch():
    def __init__(self, start, path=None, unexplored=None, explored=None, id=None):
        self.id = id
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


    def trim_dir(self, direction):
        def _get_loc(direction):
            for i, d in enumerate(self.unexplored):
                if d == direction:
                    return i
        idx = _get_loc(direction)
        if idx is not None:
            self.explored.append(self.unexplored.pop(idx))


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
                    id = f'{self.start.id}-{exploration_order[0]}'
                )
            )


    def run_branch(self, branch):
        print(f'Diagnostics for {branch.id}')
        run = self._check_stop(branch)
        while run: #len(branch.unexplored) > 0:
            direction = branch.get_dir()
            trav = DFT(
                start = branch.start,
                direction = direction,
                network = self.world,
                visited=[]
            )
            leg = trav()
            
            branch.path.stack(leg)
            print(f'Path (td: {direction}): {branch.path}')
            if  not self._check_circular(branch):
                run = self._check_stop(branch)
                if run:
                    branch.path.stack(self._back_track(leg))
            else:
                branch.path.add(self.start.id)
                self._trim_loop(branch, leg)
            


    def _check_stop(self, branch):
        # Check world completion
        # print(f'stop check branch len: {len(branch.path.visited)}  world_len: {len(self.world.rooms)}')
        if len(branch.path.visited) == len(self.world.rooms):
            return False
        # Check branch completion
        else:
            return len(branch.unexplored) > 0


    def _check_circular(self, branch):
        ngbs = [self.openings[key].id for key in self.openings]
        return branch.path[-1] in ngbs


    def _trim_loop(self, branch, leg):
        loop_ends = [leg[1], leg[-1]]
        loop_dirs = [key for key in self.openings if self.openings[key].id in loop_ends]
        for d in loop_dirs: branch.trim_dir(d)


    def _back_track(self, leg):
        backpath =  leg.reverse()
        backpath.steps.pop(0)
        return backpath


    def search_branches(self):
        for branch in self.branches:
            self.run_branch(branch)


    def get_shortest(self):
        spath = None
        slen = None

        for b in self.branches:
            if spath is None:
                spath = b.path 
                slen = len(b.path)
            elif len(b.path) < slen:
                spath = b.path 
                slen = len(b.path)

        return spath




    @property 
    def paths(self):
        return [branch.path for branch in self.branches if branch is not None]
    


class Path():
    def __init__(self, start=None, exit=None, steps=None):
        self.start = start 
        self.exit = exit
        self.visited = set()
        if steps is None:
            self.steps = []
        else:
            self.steps = steps

    def __repr__(self):
        return f'{self.steps}'

    def __len__(self):
        return len(self.steps)

    def add(self, room_id):
        self.steps.append(room_id)
        self.visited.add(room_id)

    def stack(self, path):
        if path is None:
            return
        # print('stacking ', path.steps, 'to', self.steps)
        # print('checking ', self.start.id, 'against ', path[0])
        if self.start.id == path[0]:
            self.steps.extend(path.steps[1:])
        else:
            self.steps.extend(path.steps)
        self.visited.update(path.steps)

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

        def _turn(openings, room):
            current_direction = self.direction
            if room.id == self.start.id:
                return current_direction
            ldir = _find_left(current_direction)
            if ldir in openings:
                return ldir
            rdir = _find_right(current_direction)
            if rdir in openings:
                return rdir
            return current_direction

        openings = detect_openings(room)
        self.direction = _turn(openings, room)

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
                croom = get_room_from_id(c, self.network)
                if detect_fork(room=croom, last_direction=_flip_dir(self.direction), ignore=self.start):
                    # bh = BranchHandler(
                    #     room = croom,
                    # )
                    
                    print('Fork Detected at ', c)
                else:
                    [q.put(n.id) for n in self.get_neighbors(self.network.rooms[c]) if n is not None]
        
        return path



########################
### Helper Functions ###
########################

def get_room_from_id(id, world):
    return world.rooms[id]


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


def detect_fork(room, last_direction, ignore):
    if room.id == ignore.id:
        return False

    openings = detect_openings(room, last_direction)
    if len(openings) > 1:
        return True 
    return False


def _find_left(direction):
    lefts = {
        'n': 'w',
        'w': 's',
        's': 'e',
        'e': 'n',
    }
    return lefts[direction]

def _find_right(direction):
    rights = {
        'n': 'e',
        'e': 's',
        's': 'w',
        'w': 'n',
    }
    return rights[direction]


def _flip_dir(direction):
    opposites = {
        'n': 's',
        'e': 'w',
        's': 'n',
        'w': 'e',
    }
    return opposites[direction]