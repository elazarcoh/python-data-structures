class TreeNode:
    def __init__(self, data, left=None, right=None):
        self.__data = data
        self.__left = left
        self.__right = right
        self.__parent = None
        if self.__left:
            self.__left.__parent = self
        if self.__right:
            self.__right.__parent = self

    def is_leaf(self):
        return not (self.__right or self.__left)

    def set_left(self, node):
        self.__left = node
        if node:
            node.__parent = self

    def set_right(self, node):
        self.__right = node
        if node:
            node.__parent = self

    def left(self):
        return self.__left

    def right(self):
        return self.__right

    def parent(self):
        return self.__parent

    def data(self):
        return self.__data

    def __repr__(self):
        return str(self.__data)


class CartesianTree:
    def __init__(self):
        self.root = None
        self.last_node = None

    def add_node(self, value):
        if not self.root:
            new_node = TreeNode(value)
            self.root = new_node
        else:
            node = self.last_node
            while node.parent() and node.data() > value:
                node = node.parent()
            if not node.parent() and node.data() > value:  # its the root
                new_node = TreeNode(value, left=node)
                self.root = new_node
            else:
                new_node = TreeNode(value, left=node.right())
                node.set_right(new_node)
        self.last_node = new_node
        return new_node

    def update(self, iterable):
        nodes = []
        for v in iterable:
            nodes.append(self.add_node(v))
        return nodes

    def in_order(self):
        res = []

        def __helper(node):
            if node:
                __helper(node.left())
                res.append(node.data())
                __helper(node.right())

        __helper(self.root)
        return res


if __name__ == '__main__':
    d = [4, 1, 6, 2, 8, 0]
    tree = CartesianTree()
    tree.update(d)
    print(tree.in_order())
