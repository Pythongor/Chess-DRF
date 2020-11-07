from django.db import models


class Figure(models.Model):
    is_white = models.BooleanField()
    role = models.CharField(max_length=10)
    status = models.CharField(max_length=2)
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    def __str__(self):
        color = 'white' if self.is_white else 'black'
        return f'{color} {self.role} ({self.height}, {self.width})'

    def move_check(self, height, width):
        if self.is_valid_pos(height, width):
            functions = {
                'king': self.king_move_possibility,
                'rook': self.rook_move_possibility,
                'bishop': self.bishop_move_possibility,
                'queen': self.queen_move_possibility,
                'knight': self.knight_move_possibility,
                'pawn': self.pawn_move_possibility
            }
            return functions[getattr(self, 'role')](height, width)
        return ValueError

    def pos_difference(self, height, width):
        return height - self.height, width - self.width

    def abs_pos_difference(self, height, width):
        return abs(height - self.height), abs(width - self.width)

    @staticmethod
    def is_valid_pos(height, width):
        return 0 <= height <= 7 and 0 <= width <= 7

    def query(self, height, width):
        aheight, awidth = self.abs_pos_difference(height, width)
        if not (aheight or awidth) or ((aheight and awidth) and aheight != awidth):
            raise ValueError
        else:
            query = [(self.height, self.width)]
            height, width = self.pos_difference(height, width)
            length = max(aheight, awidth)
            hindex = {height < 0: -1, height == 0: 0, height > 0: 1}[True]
            windex = {width < 0: -1, width == 0: 0, width > 0: 1}[True]
            for i in range(length):
                new = (query[-1][0] + hindex, query[-1][1] + windex)
                query.append(new)
            return query[1:]

    def king_move_possibility(self, height, width):
        dif_0, dif_1 = self.abs_pos_difference(height, width)
        if (dif_0 < 2 and dif_1 < 2) and (dif_0 | dif_1):
            return 'MAS' if self.status == 'S' else 'MA'
        elif self.status == 'S' and width in (2, 6) and height == {True: 0, False: 7}[getattr(self, 'is_white')]:
            rook_width = {2: 0, 6: 7}[width]
            rook_pos = (height, rook_width)
            return f'QC {self.query(height, width)} R {rook_pos}'
        return 'I'

    def rook_move_possibility(self, height, width):
        dif_0, dif_1 = self.abs_pos_difference(height, width)
        if bool(dif_0) != bool(dif_1):
            if self.status == 'S':
                return f'QMAS {self.query(height, width)}'
            return f'QMA {self.query(height, width)}'
        return 'I'

    def bishop_move_possibility(self, height, width):
        dif_0, dif_1 = self.abs_pos_difference(height, width)
        if dif_0 and dif_1 and dif_0 == dif_1:
            return f'QMA {self.query(height, width)}'
        return 'I'

    def queen_move_possibility(self, height, width):
        if self.rook_move_possibility(height, width) != 'I':
            return self.rook_move_possibility(height, width).replace('S', '')
        return self.bishop_move_possibility(height, width)

    def knight_move_possibility(self, height, width):
        diffs = self.abs_pos_difference(height, width)
        return 'MA' if tuple(sorted(diffs)) == (1, 2) else 'I'

    def pawn_move_possibility(self, height, width):
        dif_0, dif_1 = self.pos_difference(height, width)
        is_white = getattr(self, 'is_white')
        one_step = {0: -1, 1: 1}[is_white]
        if dif_0 == one_step:
            if not dif_1:
                last_line = {0: 0, 1: 7}[is_white]
                if height == last_line:
                    return 'MS'
                return 'MS' if self.status == 'S' else 'M'
            elif abs(dif_1) > 1:
                return 'I'
            elif abs(dif_0) == 1:
                last_line = {0: 0, 1: 7}[is_white]
                en_passant_line = {0: 2, 1: 5}[is_white]
                if height == last_line:
                    return 'AS'
                elif height == en_passant_line:
                    return f'AE P ({height - one_step}, {width}), ({height}, {width})'
                return 'AS' if self.status == 'S' else 'A'
            return 'I'
        elif self.status == 'S' and dif_0 == one_step * 2 and not dif_1:
            return f'QMS {self.query(height, width)}'
        return 'I'
