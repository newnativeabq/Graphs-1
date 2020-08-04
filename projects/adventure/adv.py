from room import Room
from player import Player
from world import World

import random
from ast import literal_eval

from search import Path, BFS, DFT, Branch, BranchHandler, decision_points, trim_path

import sys 

# sys.setrecursionlimit(3000)



# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()


player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []

bhandler = BranchHandler(
    room = world.starting_room,
    world = world,
)
bhandler.search_branches()


sbranch = bhandler.get_shortest(resolve=True, trim=False)
print('Shortest branch: ', sbranch, len(sbranch))


def iterate_traverse(branch_handler):
    # print('running iteration')
    def _needs_resolution(branch):
        # print('Checking resolution: ', branch)
        return len([s for s in branch.path.steps.copy() if type(s)!=int]) > 0

    def _is_complete(branch):
        # print('Checking complete: ', branch)
        valid_path = [s for s in branch.path.steps.copy() if type(s)==int]
        return len(valid_path) >= len(world)

    if _needs_resolution(sbranch):
        bhandler.get_shortest(resolve=True, trim=False)
    elif _is_complete(sbranch):
        return bhandler.get_shortest(resolve=False, trim=True)

    return False



run = True
for i in range(100):
    try:
        result = iterate_traverse(bhandler)
        if result:
            print('FOUND! Shortest branch: ', sbranch, len(sbranch))
            run = False
            break
        else:
            pass
            # print('iteration ', i)
    except Exception as e:
        print(f'Error {e}')
        break

tb = trim_path(sbranch)
print('\nCurrent shortest branch:\n ', tb, len(tb))
print('\nCurrent shortest untrimmedbranch: \n', sbranch, len(sbranch))

print('\nDecisionPoints\n', decision_points)


# print('All Paths: ', bhandler.paths)

# # TRAVERSAL TEST
# visited_rooms = set()
# player.current_room = world.starting_room
# visited_rooms.add(player.current_room)

# for move in traversal_path:
#     player.travel(move)
#     visited_rooms.add(player.current_room)

# if len(visited_rooms) == len(room_graph):
#     print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
# else:
#     print("TESTS FAILED: INCOMPLETE TRAVERSAL")
#     print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
