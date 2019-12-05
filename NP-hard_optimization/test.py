from mip.model import *
import mip
import copy

m = Model()
V = range(4)
pairs = [(1,2), (1,3), (3,1), (2,3)]
M = [[0 for j in V] for i in V]
x = copy.deepcopy(M)
D = copy.deepcopy(M)
x[1][2] = m.add_var(name='x[{}][{}]'.format(1, 2), var_type=INTEGER)
x[1][3] = m.add_var(name='x[{}][{}]'.format(1, 3), var_type=INTEGER)
x[3][1] = m.add_var(name='x[{}][{}]'.format(3, 1), var_type=INTEGER)
x[2][3] = m.add_var(name='x[{}][{}]'.format(2, 3), var_type=INTEGER)

D[1][2] = m.add_var(name='D[{}][{}]'.format(1, 2), var_type=INTEGER)
D[1][3] = m.add_var(name='D[{}][{}]'.format(1, 3), var_type=INTEGER)
D[3][1] = m.add_var(name='D[{}][{}]'.format(3, 1), var_type=INTEGER)
D[2][3] = m.add_var(name='D[{}][{}]'.format(2, 3), var_type=INTEGER)

m += x[1][2] + x[3][1] >= 2 * x[1][3] + x[2][3]
m += D[1][2] + x[3][1] >= 2 * D[1][3] + 100 * x[2][3]
m += D[1][2] + D[2][3] + D[3][1] + D[1][3] >= x[1][2] + x[2][3] + x[3][1] + x[1][3]
m += D[1][2] >= 10

m.objective = minimize(3 * D[1][2] + 2 * D[1][3] + D[3][1] + D[2][3] * 4.5 + x[1][2] + 8 * x[1][3] + 8 * x[3][1] + 0.8 * x[2][3])
A = [[1,1,1,1],[1,1,1,1],[1,1,1,1], [1,1,1,1]]
B = [[1,1,1,1],[1,1,1,1],[1,1,1,1], [1,1,1,1]]
m.start = [(D[1][2], -100)]
m.validate_mip_start()
m.optimize(max_seconds=20)