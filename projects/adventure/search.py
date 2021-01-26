from queue import Queue, LifoQueue
import random
import logging



logging.basicConfig(filename='log.txt', level=logging.INFO)

log = logging.getLogger(__name__)

log.info('Search Initialized')


directions = ['n', 'e', 's', 'w']

decision_points = {}



class Branch():
    def __init__(self, start, path=None, unexplored=None, explored=None, id=None):
        self.id = id
        self.start = start 
        self.path = Path(
            start=start,
        )
        self.explored = []
        self.unexplored = unexplored

    def __repr__(self):
        return f'Branch ID: {self.id} - Path: {self.path}'
    
    def __len__(self):
        return len(self.path)

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


    def resolve_forks(self, first=True, network=None):
        def _get_fork_loc(path):
            forks = []
            for i, v in enumerate(path):
                if type(v) not in (int, str):
                    forks.append((i, v))
            return forks

        def _run_forks(forks):
            paths = []
            for fork in forks:
                h = fork[1]
                h.search_branches(backtrack=True)
                ## CONTROL FORK BEHAVOR WITH h.get* ##
                paths.append((fork[0], h.get_random(resolve=False).path))
                # paths.append((fork[0], h.get_shortest(resolve=False).path))
            return paths
        

        def _build_connection(start, destination, network):
            if start != destination:
                openings = detect_openings(get_room_from_id(start, network))
                ids = [openings[d].id for d in openings]
                log.debug(f'Checking for connection: {ids}')
                if destination in ids:
                    return start
                else:
                    return BFS(start=start, destination=destination, network=network)


        def _insert_paths(paths, network):
            for p in paths:
                i = p[0]
                fpath = p[1]
                lft = self.path[0:i]
                con = _build_connection(start=fpath[-1], destination=lft[-1], network=network)
                if con is not None:
                    fpath.add(con)
                self.path.insert(path=fpath, idx=i)
        
        forks = _get_fork_loc(self.path)
        if len(forks) < 1:
            return
        if first:
            forks = [forks[0]]
        if len(forks) > 0:
            paths = _run_forks(forks)
            log.debug(f'Paths to Insert: {forks}')
            _insert_paths(paths, network)








class BranchHandler():

    def __init__(self, room, world, branches=None, ignore=None, last_direction=None):
        self.openings = detect_openings(room, last_direction)
        self.start = room
        self.world = world
        if branches is None:
            self.branches = []
            self.create_branches(ignore)
        else:
            self.branches = branches


    def create_branches(self, ignore=None):
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


    def run_branch(self, branch, backtrack=False):
        log.debug(f'Diagnostics for {branch.id}')
        run = True
        while run:
            run = self._check_stop(branch)
            direction = branch.get_dir()
            trav = DFT(
                start = branch.start,
                direction = direction,
                network = self.world,
                visited=[]
            )
            leg = trav()
            
            branch.path.stack(leg)
            log.debug(f'Path (td: {direction}): {branch.path}')
            if  (len(leg) < 3) or (not self._check_circular(branch)):
                run = self._check_stop(branch)
                if run:
                    self._back_track(leg=leg, branch=branch)
            else:
                log.debug(f'Loop found at: {leg}')
                branch.path.add(self.start.id)
                self._trim_loop(branch, leg)
                run = self._check_stop(branch)
        if backtrack:
            self._back_track(leg=leg, branch=branch)
            log.debug(f'Backtracked path: {branch.path}')


    def _check_stop(self, branch):
        # Check world completion
        log.debug(f'stop check branch len: {len(branch.path.visited)}  world_len: {len(self.world.rooms)}')
        if len(branch.path.visited) == len(self.world.rooms):
            return False
        # Check branch completion
        else:
            log.debug(f'Unexplored openings: {len(branch.unexplored) > 0}')
            return len(branch.unexplored) > 0


    def _check_circular(self, branch):
        ngbs = [self.openings[key].id for key in self.openings]
        log.debug(f'Checking circular: path_end {branch.path[-1]} ngbs {ngbs}')
        return branch.path[-1] in ngbs


    def _trim_loop(self, branch, leg):
        loop_ends = [leg[1], leg[-1]]
        loop_dirs = [key for key in self.openings if self.openings[key].id in loop_ends]
        log.debug(f'Trimming loop_ends: {loop_ends}, loop_dirs: {loop_dirs}')
        for d in loop_dirs: branch.trim_dir(d)


    def _back_track(self, leg, branch):
        backpath =  leg.reverse()
        backpath.steps.pop(0)
        log.debug(f'Backtrack Requested. Path: {backpath}')
        if len(backpath) == 1:
            branch.path.add(backpath.steps[0])
        else:
            branch.path.stack(backpath)
        return backpath


    def search_branches(self, backtrack=False):
        for branch in self.branches:
            self.run_branch(branch, backtrack)


    def _resolve_one_level(self):
        for b in self.branches:
            b.resolve_forks(first=True, network=self.world)

    def get_shortest(self, resolve=True, trim=False):      
        spath = None
        slen = None

        if resolve:
            self._resolve_one_level()

        for b in self.branches:
            if spath is None:
                sbranch = b
                spath = b.path 
                slen = len(b.path)
            elif len(b.path) < slen:
                sbranch = b
                spath = b.path 
                slen = len(b.path)

        
        
        if trim:
            update_decisions(trim_path(sbranch))
            return store_return_decision(sbranch)
        return store_return_decision(sbranch)
        


    def get_random(self, resolve=True):
        # print([branch.id for branch in self.branches])
        if resolve:
            self._resolve_one_level()
        return store_return_decision(random.choice(self.branches))


    @property 
    def paths(self):
        return [branch.path for branch in self.branches if branch is not None]
    


class Path():
    def __init__(self, start=None, steps=None, fork=False, debug=False):
        self.start = start 
        self.visited = set()
        self.fork = fork
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
        if type(room_id) == int:
            self.visited.add(room_id)

    def stack(self, path):
        if path is None:
            return
        log.debug(f'stacking {path.steps} to {self.steps}')
        log.debug(f'checking {self.start.id} against {path[0]}')
        if self.start.id == path[0]:
            self.steps.extend(path.steps[1:])
        else:
            self.steps.extend(path.steps)
        self.visited.update(path.steps)

    def reverse(self):
        rpath = Path(steps = self.steps[::-1]) 
        return rpath

    def insert(self, path, idx):
        lft = self.steps[0:idx]
        rgt = self.steps[idx+1:]

        npath = lft + path.steps + rgt

        log.debug(f'Inserting at {idx} of len {len(path)}: {path}')
        log.debug(f'path before insert: {self.steps}')
        
        self.steps = npath
        log.debug(f'path after insert: {self.steps}')

    def copy(self):
        return Path(
            steps=self.steps.copy()
        )

    def pop(self, idx=None):
        if idx is not None:
            self.steps.pop(idx)
        else:
            self.steps.pop()

    def __getitem__(self, idx):
        return self.steps[idx]



class BFS():
    def __init__(self, start, destination, network):
        self.start = start
        self.destination = destination
        self.network = network

    def __repr__(self):
        return f'<search.BFS: {self.start}->{self.destination}>'

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
                    bh = BranchHandler(
                        room = croom,
                        world = self.network,
                        last_direction = _flip_dir(self.direction),
                    )
                    # Annotate forked path for lazy eval
                    log.debug(f'Creating forked path at room {bh.start.id}')
                    path.fork = True
                    path.add(bh)
                    log.debug(f'Forke found along: {path}')

                    # Solve fork inline
                    # bh.search_branches(backtrack=True)
                    # log.info(f'Fork Detected at {c}')
                    # log.info(f'Fork path > {bh.get_shortest()}')
                    # fork_path = bh.get_shortest()
                    # [path.add(n) for n in fork_path.steps]

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
        openings.pop(last_direction)
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


def store_return_decision(branch):
    decision_points[branch.start.id] = {
        'selected': branch.id, 
        'outcome': len(branch)}
    return branch

def update_decisions(branch):
    for key in decision_points:
        decision_points[key]['outcome'] = len(branch)


def trim_path(branch):
    test_path = [s for s in branch.path.steps.copy() if type(s)==int]
    visited = set(test_path.copy())

    while len(visited.difference(set(test_path))) == 0:
        last_rec = test_path.pop()
    test_path.append(last_rec)
    branch.path.steps = test_path
    return branch