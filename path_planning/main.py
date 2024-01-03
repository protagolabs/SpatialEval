from grid import Grid, Grid3D
from dijkstra import dijkstra
from astar import a_star
from obstacles_utils import generate_3d_obstacles, generate_2d_obstacles


def verify_path(g, path, obstacles):
    """验证路径是否合法.

    Args:
        path (list[tuple]): 节点组成的路径
        obstacles (_type_): 障碍物的坐标

    Returns:
        bool: 如果路径合法, 返回True, 否则返回False
    """""
    for node in path:
        if node in obstacles:
            return False

    for idx in range(1, len(path)):
        if path[idx] not in g.get_adjacent(path[idx-1]):
            return False

    return True

def test_2d_grid():
    # 随机生成障碍物
    maze, obstacles = generate_2d_obstacles(n=7, n_obstacles=10)

    g = Grid(7, 7, obstacles = obstacles)
    src = (0, 0)
    dest = (6, 6)

    print("Grid visualization: ")
    print(g)

    print("\nLegend:\n\tS = Start\n\tE = End\n\tX = Obstacle\n\t_ = Empty space")

    print("\nPath by Dijkstra's algorithm:")
    shortest_path = dijkstra(g, src, dest)
    print(g.plot_path(shortest_path))

    # dijkstra 给出的路径是正确的
    # 1. 可以根据 gpt给出的路径长度, 和 dijkstra 给出的路径长度, 判断 gpt 的路径长度是否是最短的
    print (f"Shortest Path: {len(shortest_path)}")

    # 2. 检查路径的合法性, 可以检查gpt给出的每一步的路径, 是否走上了障碍物, 是否是走到相邻节点
    print ("Verified: ", verify_path(g, shortest_path, obstacles))
    
    # 3. 评估路径是否到达了终点
    print ("Reached destination: ", shortest_path[-1] == dest)

def test_3d_grid():
    # n 网格的尺寸, k为障碍物的数量
    maze, obstacles = generate_3d_obstacles(n=3, n_obstacles=5)

    print (obstacles)

    g = Grid3D(i=3, j=3, k=3, obstacles=obstacles)
    src = (0, 0, 0)
    dest = (2, 2, 2)

    shortest_path = dijkstra(g, src, dest)

    # dijkstra 给出的路径是正确的
    # 1. 可以根据 gpt给出的路径长度, 和 dijkstra 给出的路径长度, 判断 gpt 的路径长度是否是最短的
    print (f"Shortest Path: {len(shortest_path)}")

    # 2. 检查路径的合法性, 可以检查gpt给出的每一步的路径, 是否走上了障碍物, 是否是走到相邻节点
    print ("Verified: ", verify_path(g, shortest_path, obstacles))

    # 3. 评估路径是否到达了终点
    print ("Reached destination: ", shortest_path[-1] == dest)

if __name__ == "__main__":
    # main()
    test_3d_grid()
    # test_2d_grid()
