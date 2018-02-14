from cartesian_tree import CartesianTree
from lca import LCA


class RMQ:
    def __init__(self, data):
        if not data:
            raise ValueError('data must not be empty')
        tree = CartesianTree()
        self.indices = tree.update(data)
        self.lca = LCA(tree.root)

    def __getitem__(self, indices):
        if isinstance(indices, slice):
            if indices.step is not None:
                raise NotImplementedError('rmq supports only continues sequences')
            i = indices.start
            j = indices.stop
            i = 0 if i is None else i
            j = len(self) - 1 if j is None else j
            if not (0 <= i, j < len(self)):
                raise IndexError('index out of range')
            return self.lca.get_lca(self.indices[i], self.indices[j])

    def __len__(self):
        return len(self.indices)
