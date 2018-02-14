import math

from rmq import RMQ4, RMQ2


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
            curr_min = math.inf
            j = 0
            while j < L and i < len(data):
                curr_min = min(curr_min, data[i])
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
                canon_data.append(data[i] - d)
                i += 1
                j += 1
            canon_data = tuple(canon_data)
            if canon_data not in self.canonicals_rmq2:
                self.canonicals_rmq2[canon_data] = RMQ2(canon_data)
            self.rmq2.append((d, canon_data))

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
                res = self.canonicals_rmq2[canon][rel_i:rel_j] + d
                return res
            else:
                interval_len = j - i + 1
                d_i, canon_i = self.rmq2[i_block]
                d_j, canon_j = self.rmq2[j_block]
                rel_i = i % L
                rel_j = j % L
                left_min = self.canonicals_rmq2[canon_i][rel_i:] + d_i
                right_min = self.canonicals_rmq2[canon_j][:rel_j] + d_j
                inner_blocks_num = (interval_len - (L - rel_i) - rel_j) // 3
                if inner_blocks_num != 0:
                    inner_min = self.rmq4[i_block + 1: j_block - 1]
                else:
                    inner_min = math.inf
                res = min(left_min, inner_min, right_min)
                return res

    def __len__(self):
        return self.length
