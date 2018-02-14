import math


class IntervalTreeNode:
    def __init__(self, data, left=None, right=None, parent=None, interval=None):
        self.__data = data
        self.__left = left
        self.__right = right
        self.__parent = parent
        self.__interval = interval

    def set(self, data):
        self.__data = data

    def get_interval(self):
        return self.__interval

    def set_parent(self, parent):
        self.__parent = parent

    def data(self):
        return self.__data

    def left(self):
        return self.__left

    def right(self):
        return self.__right

    def parent(self):
        return self.__parent

    def __contains__(self, interval):
        """
        check if interval contained in self interval
        """
        return self.__interval[0] <= interval[0] and self.__interval[1] >= interval[1]

    def __repr__(self):
        return '<{} : {}>'.format(self.__interval, self.__data)


class IntervalsTree:
    def __init__(self, data, associative_op, default):
        self.__default = default
        self.leaves = [IntervalTreeNode(d, interval=(i, i)) for i, d in enumerate(data)]
        self.high_bound = len(self.leaves)
        pad_len = 2 ** int(math.ceil(math.log2(len(self.leaves)))) - len(self.leaves)
        pad = [IntervalTreeNode(self.__default, interval=(i, i)) for i in
               range(len(self.leaves), len(self.leaves) + pad_len)]
        self.leaves.extend(pad)
        self.op = associative_op
        self.root = self.__build_tree(self.leaves, 1)

    def __setitem__(self, index, value):
        if not (0 <= index < self.high_bound):
            raise IndexError('index out of range')
        leaf = self.leaves[index]
        leaf.set(value)
        p = leaf.parent()
        while p is not None:
            new_val = self.op(p.left().data(), p.right().data())
            p.set(new_val)
            p = p.parent()

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step is not None:
                raise NotImplementedError('intervals tree supports only continues sequences')
            i, j = index.start, index.stop
            i = 0 if i is None else i
            j = self.high_bound - 1 if j is None else j
            if not (0 <= i <= j < self.high_bound):
                raise IndexError('index out of range')
            if i == j:
                return self.leaves[i].data()
            return self.get_interval(i, j)
        else:
            if not (0 <= index < self.high_bound):
                raise IndexError('index out of range')
            return self.leaves[index].data()

    def __build_tree(self, leaves, height, start=0):
        if len(leaves) <= 1:
            return leaves[0]
        i = 0
        interval_len = (2 ** height) - 1
        low = start
        high = low + interval_len
        new_leaves = []
        while i < len(leaves):
            l1 = leaves[i]
            i += 1
            l2 = leaves[i]
            # create parents for the two nodes
            p = IntervalTreeNode(self.op(l1.data(), l2.data()), left=l1, right=l2,
                                 interval=(low, high))
            l1.set_parent(p)
            l2.set_parent(p)
            new_leaves.append(p)
            # move to the next pair
            i += 1
            low = high + 1
            high = low + interval_len
        return self.__build_tree(new_leaves, height + 1, start)

    def get_interval(self, i, j):
        if (i, j) not in self.root:
            raise IndexError('index out of range')
        root = self.root
        interval = (i, j)
        while interval in root:
            if interval in root.left():
                root = root.left()
            elif interval in root.right():
                root = root.right()
            else:
                break
        res = self.__default
        left = self.__suffix_calc(i, root.left(), res)
        right = self.__prefix_calc(j, root.right(), res)
        res = self.op(left, right)
        return res

    def __suffix_calc(self, i, root, val):
        if not root:
            return self.__default
        if root.get_interval()[0] == i:
            return self.op(val, root.data())
        elif i <= root.left().get_interval()[1]:
            val = self.op(val, root.right().data())
            root = root.left()
        else:
            root = root.right()
        return self.__suffix_calc(i, root, val)

    def __prefix_calc(self, j, root, val):
        if not root:
            return self.__default
        if root.get_interval()[1] == j:
            return self.op(val, root.data())
        elif j >= root.right().get_interval()[0]:
            val = self.op(val, root.left().data())
            root = root.right()
        else:
            root = root.left()
        return self.__prefix_calc(j, root, val)

    def __len__(self):
        return self.high_bound

    def append(self, value):
        if self.high_bound == len(self.leaves):
            pad_len = len(self.leaves)
            pad = [IntervalTreeNode(self.__default, interval=(i, i)) for i in
                   range(len(self.leaves), len(self.leaves) + pad_len)]
            new_right = self.__build_tree(pad, 1, start=len(self.leaves))
            self.leaves.extend(pad)
            self.root = IntervalTreeNode(self.op(self.root.data(), new_right.data()),
                                         left=self.root, right=new_right,
                                         interval=(0, len(self.leaves)))
            self.root.left().set_parent(self.root)
            self.root.right().set_parent(self.root)
        self.high_bound += 1
        self.__setitem__(self.high_bound - 1, value)

    def pop(self):
        if self.high_bound == 0:
            raise IndexError('pop from empty list')
        self[self.high_bound - 1] = self.__default
        self.high_bound -= 1

    def __contains__(self, item):
        return item in map(IntervalTreeNode.data, self.leaves[:self.high_bound])

    def __repr__(self):
        return str(list(map(IntervalTreeNode.data, self.leaves[:self.high_bound])))
