def printMatrix(matrix):
    for row in matrix[0]:
        s = ''

        for num in row:
            if num != -1:
                s += str(int(num))
            else:
                s += ' '
            
            s += ' '
        print(s)
    print()

def copyMatrix(obs):
    matrix = []

    for l in obs:
        level = []

        for r in l:
            row = []

            for e in r:
                row.append(e)
                
            level.append(row)

        matrix.append(level)

    return matrix


def island(obs):
    matrix = copyMatrix(obs)
    #print('Entering ShouldBuild')
    
    N = len(matrix[0])

    start_i = start_j = N // 2

    if N % 2 == 0:
        start_j -= 1

    block_queue = [(start_i, start_j)]
    #printMatrix(matrix)

    while len(block_queue) > 0:
        
        I, J = block_queue.pop(0)
        #print(f'matrix[0][I][J]: {matrix[0][I][J]}, {type(matrix[0][I][J])}')

        if logFound(matrix, I, J):
            return False

        #print(f'matrix[0][I][J] in (2, 4): {matrix[0][I][J] in {2, 4}}')

        if matrix[0][I][J] in {2, 4}:
            #print(f'matrix[0][I][J] in {2, 4}')
            matrix[0][I][J] = -1


            # check all adjacent blocks of a valid block
            for block in {(I+1, J), (I-1, J), (I, J-1), (I, J+1)}:
                if withinBounds(block[0], block[1], N):
                    block_queue.append(block)
        #printMatrix(matrix)

    #print(f'RETURN: {matrix[0][target_i][target_j] == 2}')

    #printMatrix(matrix)



    return matrix


def withinBounds(i, j, N):
    return (0 <= i < N) and (0 <= j < N)

def logFound(matrix, i, j):
    #print('entering logFound')
    for level in range(len(matrix)):
        if matrix[level][i][j] == 1:
            #print(f'FOUND LOG AT LEVEL {level}')
            #printMatrix([matrix[level]])
            #print(f'i: {i}, j: {j}')

            return True

    return False

'''
class Island:
    def __init__(self, matrix):
        self.matrix = matrix

        self.N = len(self.matrix[0])

    def visit(self, i, j):
        self.matrix[0][i][j] = -1

    

        while self.withinBounds():

            block_queue
 
            if self.logFound():
                return False

            if self.adjacentUnvisited():
                self.changeDirection()

            self.move()

        return True

    def withinBounds(self):
        return (0 <= self.i <= self.N) and (0 <= self.j <= self.N)

    def logFound(i, j):
        for level in range(len(self.matrix)):
            if self.matrix[level][i][j] == 1:
                return True

        self.matrix[0][self.i][self.j] = -1
        return False

    def adjacentUnvisited(self):
        i, j = self.i, self.j

        if self.direction == 'right':
            i += 1
        elif self.direction == 'down':
            j -= 1
        elif self.direction == 'left':
            i -= 1
        if self.direction == 'up':
            j += 1

        return (self.matrix[0][i][j] != -1)

    def changeDirection(self):
        if self.direction == 'right':
            self.direction = 'down'

        elif self.direction == 'down':
            self.direction = 'left'

        elif self.direction == 'left':
            self.direction = 'up'

        elif self.direction == 'up':
            self.direction = 'right'

    def move(self):
        if self.direction == 'right':
            self.j += 1

        elif self.direction == 'down':
            self.i += 1

        elif self.direction == 'left':
            self.j -= 1

        if self.direction == 'up':
            self.i -= 1
'''
    
if __name__ == '__main__':
    tree = [[[2, 2, 2, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1],
          [0, 0, 0, 0, 1, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1],
          [0, 0, 0, 0, 1, 2]]]

    bridge = [[[2, 2, 2, 2, 0, 0],
          [0, 0, 4, 0, 0, 0],
          [0, 0, 4, 0, 0, 0],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]]]

    tree_and_bridge = [[[2, 2, 2, 2, 0, 0],
          [0, 0, 4, 0, 0, 0],
          [0, 0, 4, 0, 0, 0],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1],
          [0, 0, 0, 0, 1, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 1],
          [0, 0, 0, 0, 1, 2]]]

    no_tree_no_bridge = [[[2, 2, 2, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2],
          [0, 0, 2, 2, 2, 2]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
         [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]]]

    user_input = input('\nenter: no bridge or tree\n1: tree\n2: bridge\n3:bridge and tree\n')

    while user_input not in {'1', '2', '3', ''}:
        user_input = input('\nenter: no bridge or tree\n1: tree\n2: bridge\n3:bridge and tree\n')

    if user_input == '1':
        m = tree
    elif user_input == '2':
        m = bridge
    elif user_input == '3':
        m = tree_and_bridge
    else:
        m = no_tree_no_bridge

    shouldBuild(m, 0, 2)

    
    