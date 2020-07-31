import numpy as np
from queue import Queue, LifoQueue

class User:
    def __init__(self, name):
        self.name = name



class SocialGraph:
    def __init__(self):
        self.last_id = 0
        self.users = {}
        self.friendships = {}


    def add_friendship(self, user_id, friend_id):
        """
        Creates a bi-directional friendship
        """
        if user_id == friend_id:
            print("WARNING: You cannot be friends with yourself")
        elif friend_id in self.friendships[user_id] or user_id in self.friendships[friend_id]:
            print("WARNING: Friendship already exists")
        else:
            self.friendships[user_id].add(friend_id)
            self.friendships[friend_id].add(user_id)


    def add_user(self, name):
        """
        Create a new user with a sequential integer ID
        """
        self.last_id += 1  # automatically increment the ID to assign the new user
        self.users[self.last_id] = User(name)
        self.friendships[self.last_id] = set()


    def populate_graph(self, num_users, avg_friendships):
        """
        Takes a number of users and an average number of friendships
        as arguments

        Creates that number of users and a randomly distributed friendships
        between those users.

        The number of users must be greater than the average number of friendships.
        """
        # Reset graph
        self.last_id = 0
        self.friendships = {}

        # Create distribution
        u = np.arange(num_users)
        s = [abs(int(f)) for f in np.random.normal(avg_friendships, 2, num_users)]

        # Initialize Friendships
        for val in u:
            self.friendships[val] = set()

        for i in range(num_users // 2):
            friends = np.random.choice([su for su in u if su != i], s[i], replace=False)
            self.friendships[i].update(friends)
            for f in friends:
                if f in self.friendships:
                    self.friendships[f].add(i)


    def get_all_social_paths(self, user_id):
        """
        Takes a user's user_id as an argument

        Returns a dictionary containing every user in that user's
        extended network with the shortest friendship path between them.

        The key is the friend's ID and the value is the path.
        """
        visited = {}  # Note that this is a dictionary, not a set
        
        # Get all nodes in user network
        unet = self.bft(user_id)
        
        # Run BFS to each node in user network
        for f in unet:
            visited.update({f: self.bfs(user_id, f)})
        
        return visited


    def get_neighbors(self, vertex_id):
        """
        Get all neighbors (edges) of a vertex.
        """
        return self.friendships[vertex_id]


    def bft(self, starting_vertex=1, step=False):
        q = Queue()
        q.put(starting_vertex)

        visited = set()

        # if step == False:
        while not q.empty():
            c = q.get()
            if c not in visited:
                visited.add(c)
                ngb = self.get_neighbors(c)
                [q.put(n) for n in ngb]

        visited.remove(starting_vertex)
        return visited


    def bft_y(self, starting_vertex=1):
        q = Queue()
        q.put(starting_vertex)

        visited = set()

        while not q.empty():
            c = q.get()
            if c not in visited:
                visited.add(c)
                yield c
                [q.put(n) for n in self.get_neighbors(c)]


    def bfs(self, starting_vertex, destination_vertex):
        """
        Return a list containing the shortest path from
        starting_vertex to destination_vertex in
        breath-first order.
        """
        def _run_line(vertex, destination):
            t = []
            for v in self.bft_y(vertex):
                t.append(v)
                if v == destination:
                    return t

        def _find_shortest(iterable):
            mini = iterable[0]
            for i in iterable:
                if len(i) < len(mini):
                    mini = i
            return mini

        paths = []
        rpath = []
        visited = set()
        
        for v in self.bft_y(starting_vertex):
            rpath.append(v)
            if (v not in visited):
                npath = [_run_line(n, destination_vertex) for n in self.get_neighbors(v)]
                if len(npath) == 0:
                    break
                full_paths = [rpath + p for p in npath if p is not None]
                if len(full_paths) > 0:
                    paths.append(_find_shortest(full_paths))
                
        
        # return _find_shortest(paths)
        return _find_shortest(paths)




if __name__ == '__main__':
    sg = SocialGraph()
    sg.populate_graph(10, 2)
    print(sg.friendships)
    connections = sg.get_all_social_paths(1)
    print(connections)
