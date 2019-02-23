# definition of U and V
class Direction(object):

    def __init__(self, direction):

        self.direction = direction

U = Direction('u')
V = Direction('v')

# definition of U0, U1, V0, V1 as the edges of surfaces
class Edge(object):

    def __init__(self, direction, value):

        self.direction = direction
        self.value = value

U0 = Edge(U, 0)
U1 = Edge(U, 1)
V0 = Edge(V, 0)
V1 = Edge(V, 1)
