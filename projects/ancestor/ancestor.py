from graph import Graph
from copy import copy

class AGraph(Graph):
    def __init__(self):
        super().__init__()


    def run_all_verts(self, starting_node):
        test_verts = [v for v in self.vertices if v != starting_node]

        ancestors = []
        for v in test_verts:
            path = self.dfs(starting_node, v)
            if path is not None:
                ancestors.append(path)

        # print(ancestors)  # DEBUG
        return ancestors



def _flip(x1, x2):
    return x2, x1


def _flip_items(x):
    for i in range(len(x)):
        x[i] = _flip(*x[i])
    return x


def _get_all_nums(data):
    nums = set()
    for conn in data:
        for n in conn:
            nums.add(n)
    return nums


def load_graph(g, data):
    vertices = _get_all_nums(data)
    [g.add_vertex(v) for v in vertices]
    [g.add_edge(*d) for d in data]
    return g


def _find_longest(iterable):
    lengths = []
    idx = {len(i):[] for i in iterable}
    
    for j, i in enumerate(iterable):
        lengths.append(len(i))
        idx[len(i)].append(j)

    maxl = max(lengths)

    return [iterable[i] for i in idx[maxl]]


def earliest_ancestor(pairs, starting_node, rev=True):
    g = AGraph()
    ancestors = copy(pairs)
    if rev:
        ancestors = _flip_items(ancestors)
    load_graph(g, ancestors)

    sngb = g.get_neighbors(starting_node)
    print(f'start ngb {starting_node}: ', sngb)
    print('vertices: ', g.vertices)
    if (sngb is None) or (len(sngb) == 0):
        return -1

    longest_paths = _find_longest(g.run_all_verts(starting_node))
    ancestor = min([p[-1] for p in longest_paths])

    return ancestor

if __name__ == "__main__":
    anc = [(0,2), (1, 2), (2, 3), (3, 4)]
    a = earliest_ancestor(anc, 1, rev=False)
    print(a)