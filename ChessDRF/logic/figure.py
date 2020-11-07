from colorama import Fore


class Figure:
    COLORS = [Fore.CYAN, Fore.BLACK]
    _symbols = {'king': '@', 'queen': 'Q', 'rook': 'R', 'bishop': 'B', 'knight': 'K', 'pawn': 'P'}

    def __init__(self, is_white: bool, kind: str, status: str, pos: tuple):
        self.is_white = is_white
        self.kind = kind
        self.status = status
        self.pos = pos
        self.symbol = self._symbols[kind]

    def __repr__(self):
        return ''.join((self.COLORS[self.is_white], '\033[1m', self.symbol))

    def move_check(self, pos):
        if self.is_valid_pos(pos):
            functions = {
                'king': self.king_move_possibility,
                'rook': self.rook_move_possibility,
                'bishop': self.bishop_move_possibility,
                'queen': self.queen_move_possibility,
                'knight': self.knight_move_possibility,
                'pawn': self.pawn_move_possibility
            }
            return functions[self.kind](pos)
        return ValueError

    def pos_difference(self, pos):
        return pos[0] - self.pos[0], pos[1] - self.pos[1]

    def abs_pos_difference(self, pos):
        return abs(self.pos[0] - pos[0]), abs(self.pos[1] - pos[1])

    @staticmethod
    def is_valid_pos(pos):
        return 0 <= pos[0] <= 7 and 0 <= pos[1] <= 7

    def query(self, pos):
        aheight, awidth = self.abs_pos_difference(pos)
        if not (aheight or awidth) or ((aheight and awidth) and aheight != awidth):
            raise ValueError
        else:
            query = [self.pos]
            height, width = self.pos_difference(pos)
            length = max(aheight, awidth)
            hindex = {height < 0: -1, height == 0: 0, height > 0: 1}[True]
            windex = {width < 0: -1, width == 0: 0, width > 0: 1}[True]
            for i in range(length):
                new = (query[-1][0] + hindex, query[-1][1] + windex)
                query.append(new)
            return query[1:]

    def king_move_possibility(self, pos):
        dif_0, dif_1 = self.abs_pos_difference(pos)
        if (dif_0 < 2 and dif_1 < 2) and (dif_0 | dif_1):
            return 'MAS' if self.status == 'S' else 'MA'
        elif self.status == 'S' and pos[1] in (2, 6) and pos[0] == {True: 0, False: 7}[self.is_white]:
            rook_width = {2: 0, 6: 7}[pos[1]]
            rook_pos = (pos[0], rook_width)
            return f'QC {self.query(pos)} R {rook_pos}'
        return 'I'

    def rook_move_possibility(self, pos):
        dif_0, dif_1 = self.abs_pos_difference(pos)
        if bool(dif_0) != bool(dif_1):
            if self.status == 'S':
                return f'QMAS {self.query(pos)}'
            return f'QMA {self.query(pos)}'
        return 'I'

    def bishop_move_possibility(self, pos):
        dif_0, dif_1 = self.abs_pos_difference(pos)
        if dif_0 and dif_1 and dif_0 == dif_1:
            return f'QMA {self.query(pos)}'
        return 'I'

    def queen_move_possibility(self, pos):
        if self.rook_move_possibility(pos) != 'I':
            return self.rook_move_possibility(pos).replace('S', '')
        return self.bishop_move_possibility(pos)

    def knight_move_possibility(self, pos):
        diffs = self.abs_pos_difference(pos)
        return 'MA' if tuple(sorted(diffs)) == (1, 2) else 'I'

    def pawn_move_possibility(self, pos):
        dif_0, dif_1 = self.pos_difference(pos)
        one_step = {0: -1, 1: 1}[self.is_white]
        if dif_0 == one_step:
            if not dif_1:
                last_line = {0: 0, 1: 7}[self.is_white]
                if pos[0] == last_line:
                    return 'MS'
                return 'MS' if self.status == 'S' else 'M'
            elif abs(dif_0) == 1:
                last_line = {0: 0, 1: 7}[self.is_white]
                en_passant_line = {0: 2, 1: 5}[self.is_white]
                if pos[0] == last_line:
                    return 'AS'
                elif pos[0] == en_passant_line:
                    return f'AE P ({pos[0] - one_step}, {pos[1]})'
                return 'AS' if self.status == 'S' else 'A'
            return 'I'
        elif self.status == 'S' and dif_0 == one_step * 2 and not dif_1:
            return f'QMS {self.query(pos)}'
        return 'I'
