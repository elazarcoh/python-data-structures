import math


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
            line.append(data[i])
            for j in range(i + 1, n):
                line.append(min(line[j - 1], data[j]))
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
        p = n.bit_length() - 2  # -1 for the first row, -1 for get the log2(n)-1
        self.box = [([data[i]] + [None] * p) for i in range(n)]

        for i in range(n):
            self.box[i][p] = self.__cell(i, p)

    def __cell(self, i, p):
        if i >= len(self.box):
            return math.inf
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
            j = len(self)-1 if j is None else j
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


if __name__ == '__main__':
    data = [0, 5, 7, 4, 1, 19, 6, 9, 6, 0]
    rmq = RMQ4(data)
    a = rmq[5:9]
    print(a)
