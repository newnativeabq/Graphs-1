"""
Simple graph implementation
"""
from queue import Queue, LifoQueue
import numpy as np

class Graph():

    """Represent a graph as a dictionary of vertices mapping labels to edges."""
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex_id):
        """
        Add a vertex to the graph.
        """
        self.vertices[vertex_id] = set()

    def add_edge(self, v1, v2):
        """
        Add a directed edge to the graph.
        """
        self.vertices[v1].add(v2)

    def get_neighbors(self, vertex_id):
        """
        Get all neighbors (edges) of a vertex.
        """
        return self.vertices[vertex_id]

    def bft(self, starting_vertex=1, step=False):
        q = Queue()
        q.put(starting_vertex)

        visited = set()

        # if step == False:
        while not q.empty():
            c = q.get()
            if c not in visited:
                print(c)
                visited.add(c)
                ngb = self.get_neighbors(c)
                [q.put(n) for n in ngb]


    def dft(self, starting_vertex):
        q = LifoQueue()
        q.put(starting_vertex)

        visited = set()

        # if step == False:
        while not q.empty():
            c = q.get()
            if c not in visited:
                print(c)
                visited.add(c)
                [q.put(n) for n in self.get_neighbors(c)]


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


    def dft_y(self, starting_vertex):
        q = LifoQueue()
        q.put(starting_vertex)

        visited = set()

        while not q.empty():
            c = q.get()
            if c not in visited:
                visited.add(c)
                yield c
                [q.put(n) for n in self.get_neighbors(c)]


    def dft_recursive(self,vertex: int= None, q: LifoQueue = None, visited: set = None, ):
        """
        Print each vertex in depth-first order
        beginning from starting_vertex.

        This should be done using recursion.
        """
        if q is None:
            visited=set()
            q = LifoQueue()
            q.put(vertex)

        
        if not q.empty():
            c = q.get()
            if c not in visited:
                print(c)
                visited.add(c)
                [q.put(n) for n in self.get_neighbors(c)]
                self.dft_recursive(q=q, visited=visited)


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
        

    def dfs(self, starting_vertex, destination_vertex):
        """
        Return a list containing a path from
        starting_vertex to destination_vertex in
        depth-first order.
        """
        path = []

        for v in self.dft_y(starting_vertex):
            path.append(v)
            if v == destination_vertex:
                return path


    def dfs_recursive(self, starting_vertex, destination_vertex):
        """
        Return a list containing a path from
        starting_vertex to destination_vertex in
        depth-first order.

        This should be done using recursion.
        """
        path = []

        for v in self.dft_y(starting_vertex):
            path.append(v)
            if v == destination_vertex:
                return path


if __name__ == '__main__':
    graph = Graph()  # Instantiate your graph
    # https://github.com/LambdaSchool/Graphs/blob/master/objectives/breadth-first-search/img/bfs-visit-order.png
    graph.add_vertex(1)
    graph.add_vertex(2)
    graph.add_vertex(3)
    graph.add_vertex(4)
    graph.add_vertex(5)
    graph.add_vertex(6)
    graph.add_vertex(7)
    graph.add_edge(5, 3)
    graph.add_edge(6, 3)
    graph.add_edge(7, 1)
    graph.add_edge(4, 7)
    graph.add_edge(1, 2)
    graph.add_edge(7, 6)
    graph.add_edge(2, 4)
    graph.add_edge(3, 5)
    graph.add_edge(2, 3)
    graph.add_edge(4, 6)

    '''
    Should print:
        {1: {2}, 2: {3, 4}, 3: {5}, 4: {6, 7}, 5: {3}, 6: {3}, 7: {1, 6}}
    '''
    print(graph.vertices)

    '''
    Valid BFT paths:
        1, 2, 3, 4, 5, 6, 7
        1, 2, 3, 4, 5, 7, 6
        1, 2, 3, 4, 6, 7, 5
        1, 2, 3, 4, 6, 5, 7
        1, 2, 3, 4, 7, 6, 5
        1, 2, 3, 4, 7, 5, 6
        1, 2, 4, 3, 5, 6, 7
        1, 2, 4, 3, 5, 7, 6
        1, 2, 4, 3, 6, 7, 5
        1, 2, 4, 3, 6, 5, 7
        1, 2, 4, 3, 7, 6, 5
        1, 2, 4, 3, 7, 5, 6
    '''
    print('\nBFT_YIELD')
    for vert in graph.bft_y():
        print(vert)


    '''
    Valid DFT paths:
        1, 2, 3, 5, 4, 6, 7
        1, 2, 3, 5, 4, 7, 6
        1, 2, 4, 7, 6, 3, 5
        1, 2, 4, 6, 3, 5, 7
    '''
    print('\nDFT_YIELD')
    for vert in graph.dft_y(1):
        print(vert)

    print('\nDFT_RECURSIVE')
    graph.dft_recursive(1)

    '''
    Valid BFS path:
        [1, 2, 4, 6]
    '''
    print(graph.bfs(1, 6))

    '''
    Valid DFS paths:
        [1, 2, 4, 6]
        [1, 2, 4, 7, 6]
    '''
    print(graph.dfs(1, 6))
    print(graph.dfs_recursive(1, 6))
