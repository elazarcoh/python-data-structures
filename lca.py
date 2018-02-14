from cartesian_tree import CartesianTree
from rrmq import RestrictedRMQ


class LCA:
    def __init__(self, root):
        self.root = root
        self.E = self.__euler_cycle()
        levels = self.__calc_levels()
        L = [levels[e] for e in self.E]
        self.H = {}
        for i, v in enumerate(self.E):
            if v not in self.H:
                self.H[v] = i
        self.rmq = RestrictedRMQ(L)

    def get_lca(self, u, v):
        i = self.H[u]
        j = self.H[v]
        if i > j:
            i, j = j, i
        res = self.rmq[i:j][1]  # 1 is the index of the minimum
        return self.E[res]

    def __calc_levels(self):
        levels = {}

        def __helper(level, node):
            if not node:
                return
            levels[node] = level
            __helper(level + 1, node.left())
            __helper(level + 1, node.right())

        __helper(0, self.root)
        return levels

    def __euler_cycle(self):

        def __helper(node):
            res = []
            if not node:
                return res
            if node.is_leaf():
                return [node]
            if node.left():
                res += [node] + __helper(node.left())
            if node.right():
                res += [node] + __helper(node.right())
            return res + [node]

        return __helper(self.root)


if __name__ == '__main__':
    d = [4, 1, 6, 2, 8, 0]
    tree = CartesianTree()
    tree.update(d)
    lca = LCA(tree.root)
    u = tree.root.left().right().right()
    v = tree.root.left().right()
    a = lca.get_lca(u, v)
    print(a)
