import collections
import math
import operator


def value_in_template(template, value):
    if not isinstance(template, collections.Iterable):
        return value
    else:
        return tuple((value_in_template(y, value) for y in template))


class RMQ2:
    def __init__(self, data):
        if not data:
            raise ValueError('data must not be empty')
        n = len(data)
        self.box = []
        for i in range(n):
            line = []
            for j in range(i):
                line.append(None)
            line.append((data[i], i))
            for j in range(i + 1, n):
                line.append(min(line[j - 1], (data[j], j)))
            self.box.append(line)

    def __getitem__(self, indices):
        if isinstance(indices, slice):
            if indices.step is not None:
                raise NotImplementedError('rmq supports only continues sequences')
            i = indices.start
            j = indices.stop
            i = 0 if i is None else i
            j = len(self) - 1 if j is None else j
            if not (0 <= i <= j < len(self.box)):
                raise IndexError('index out of range')
            return self.box[i][j]

    def __len__(self):
        return len(self.box)


class RMQ4:
    def __init__(self, data):
        if not data:
            raise ValueError('data must not be empty')
        n = len(data)
        # p = log2(n)
        p = n.bit_length() - 1  # -1 for the first row
        self.box = [([(data[i], i)] + [None] * p) for i in range(n)]

        for i in range(n):
            self.box[i][p] = self.__cell(i, p)

    def __cell(self, i, p):
        if i >= len(self.box):
            return value_in_template(self.box[0][0], math.inf)
        if self.box[i][p] is None:
            self.box[i][p] = min(self.__cell(i, p - 1), self.__cell(i + 2 ** (p - 1), p - 1))
        return self.box[i][p]

    def __getitem__(self, indices):
        if isinstance(indices, slice):
            if indices.step is not None:
                raise NotImplementedError('rmq supports only continues sequences')
            i = indices.start
            j = indices.stop
            i = 0 if i is None else i
            j = len(self) - 1 if j is None else j
            if not (0 <= i <= j < len(self.box)):
                raise IndexError('index out of range')
            interval_len = j - i
            if interval_len == 0:
                return self.box[i][0]
            p = interval_len.bit_length() - 1
            step = 2 ** p
            j = j - step + 1
            return min(self.box[i][p], self.box[j][p])

    def __len__(self):
        return len(self.box)


class RestrictedRMQ:
    def __init__(self, data):
        if not data:
            raise ValueError('data must not be empty')
        n = len(data)
        self.length = n
        L = int(math.ceil(0.5 * n.bit_length()))
        self.block_size = L
        # build RMQ4 Data Structure
        rmq4_base = []
        i = 0
        while i < len(data):
            curr_min = value_in_template((data[0], 0), math.inf)
            j = 0
            while j < L and i < len(data):
                curr_min = min(curr_min, (data[i], i))
                j += 1
                i += 1
            rmq4_base.append(curr_min)
        self.rmq4 = RMQ4(rmq4_base)
        # build RMQ2
        i = 0
        self.canonicals_rmq2 = {}
        self.rmq2 = []
        for d in rmq4_base:
            canon_data = []
            j = 0
            while j < L and i < len(data):
                canon_data.append(data[i] - d[0])
                i += 1
                j += 1
            canon_data = tuple(canon_data)
            if canon_data not in self.canonicals_rmq2:
                self.canonicals_rmq2[canon_data] = RMQ2(canon_data)
            self.rmq2.append((d[0], canon_data))

    def __getitem__(self, indices):
        if isinstance(indices, slice):
            if indices.step is not None:
                raise NotImplementedError('rmq supports only continues sequences')
            i = indices.start
            j = indices.stop
            i = 0 if i is None else i
            j = len(self) - 1 if j is None else j
            if not (0 <= i <= j < self.length):
                raise IndexError('index out of range')
            L = self.block_size
            i_block = i // L
            j_block = j // L
            if i_block == j_block:
                d, canon = self.rmq2[i_block]
                rel_i = i % L
                rel_j = j % L
                res = tuple(
                    map(operator.add, self.canonicals_rmq2[canon][rel_i:rel_j], (d, i - rel_i)))
                return res
            else:
                interval_len = j - i + 1
                d_i, canon_i = self.rmq2[i_block]
                d_j, canon_j = self.rmq2[j_block]
                rel_i = i % L
                rel_j = j % L
                left_min = tuple(
                    map(operator.add, self.canonicals_rmq2[canon_i][rel_i:], (d_i, i - rel_i)))
                right_min = tuple(
                    map(operator.add, self.canonicals_rmq2[canon_j][:rel_j], (d_j, j - rel_j)))
                inner_blocks_num = (interval_len - (L - rel_i) - rel_j) // 3
                if inner_blocks_num != 0:
                    inner_min = self.rmq4[i_block + 1: j_block - 1][0]
                else:
                    inner_min = value_in_template(left_min, math.inf)
                res = min(left_min, inner_min, right_min)
                return res

    def __len__(self):
        return self.length


if __name__ == '__main__':
    d = [2, 1, 2, 1, 2, 0, 4, 5, 6, 5, 6, 5, 4, 3, 1, 2, 3, 4, 5, 6, 7, 6, 5, 6]
    rmq = RestrictedRMQ(d)
    a = rmq[2:5]
    print(a)
