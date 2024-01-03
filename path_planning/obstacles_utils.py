import random

def generate_3d_obstacles(n, n_obstacles):
    # 创建一个n x n x n的三维数组表示迷宫
    maze = [[[False] * n for _ in range(n)] for _ in range(n)]
    
    obstacle_coordinates = []
    
    # 随机放置n_obstacles个障碍物
    for _ in range(n_obstacles):
        x, y, z = random.randint(0, n-1), random.randint(0, n-1), random.randint(0, n-1)
        maze[x][y][z] = True
        obstacle_coordinates.append((x, y, z))
    
    # 用DFS检查是否至少存在一条路径.
    def dfs(x, y, z):
        if x < 0 or x >= n or y < 0 or y >= n or z < 0 or z >= n or maze[x][y][z]:
            return False
        if x == y == z == n-1:
            return True
        
        maze[x][y][z] = True
        directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        random.shuffle(directions)
        
        for dx, dy, dz in directions:
            if dfs(x+dx, y+dy, z+dz):
                return True
        
        return False

    # 检查是否存在路径
    if dfs(0, 0, 0):
        # 如果存在路径，返回迷宫和障碍物坐标
        return maze, obstacle_coordinates
    else:
        # 如果不存在路径，重新生成迷宫
        return generate_3d_obstacles(n, n_obstacles)

def generate_2d_obstacles(n, n_obstacles):
    # 创建一个n x n的二维数组表示迷宫
    maze = [[False] * n for _ in range(n)]
    
    # 存储障碍物坐标的列表
    obstacle_coordinates = []
    
    # 随机放置n_obstacles个障碍物
    for _ in range(n_obstacles):
        x, y = random.randint(0, n-1), random.randint(0, n-1)
        maze[x][y] = True
        obstacle_coordinates.append((x, y))
    
    # 用DFS检查是否至少存在一条路径
    def dfs(x, y):
        if x < 0 or x >= n or y < 0 or y >= n or maze[x][y]:
            return False
        if x == y == n-1:
            return True
        
        maze[x][y] = True
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            if dfs(x+dx, y+dy):
                return True
        
        return False

    # 检查是否存在路径
    if dfs(0, 0):
        # 如果存在路径，返回迷宫和障碍物坐标
        return maze, obstacle_coordinates
    else:
        # 如果不存在路径，重新生成迷宫
        return generate_2d_obstacles(n, n_obstacles)
