class GameState:
    def __init__(self):
        # the board is a 2d 8x8 list where '--' is a space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_func = {
            "p": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves,
        }
        self.movelog = []
        self.white_to_move = True
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.en_passant_possible = ()
        self.san_log = []

        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            CastleRights(
                self.current_castle_rights.wks,
                self.current_castle_rights.bks,
                self.current_castle_rights.wqs,
                self.current_castle_rights.bqs,
            )
        ]

    def makeMove(self, move):
        move.en_passant_possible = self.en_passant_possible
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king = (move.end_row, move.end_col)
        if move.piece_moved == "bK":
            self.black_king = (move.end_row, move.end_col)
        if move.is_pawn_promoted:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"
        if move.en_passant:
            cap_row = move.start_row
            cap_col = move.end_col
            self.board[cap_row][cap_col] = "--"
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = (
                (move.start_row + move.end_row) // 2,
                move.start_col,
            )
        else:
            self.en_passant_possible = ()

        self.update_castle_rights(move)
        self.castle_rights_log.append(
            CastleRights(
                self.current_castle_rights.wks,
                self.current_castle_rights.bks,
                self.current_castle_rights.wqs,
                self.current_castle_rights.bqs,
            )
        )
        if move.can_castle:
            if move.end_col - move.start_col == 2:
                rook_start_col = 7
                rook_end_col = move.end_col - 1
            else:
                rook_start_col = 0
                rook_end_col = move.end_col + 1

            self.board[move.end_row][rook_end_col] = self.board[move.end_row][
                rook_start_col
            ]
            self.board[move.end_row][rook_start_col] = "--"

    """Undo last move"""

    def undo_move(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.white_to_move = not self.white_to_move
            if move.piece_moved == "wK":
                self.white_king = (move.start_row, move.start_col)
            if move.piece_moved == "bK":
                self.black_king = (move.start_row, move.start_col)

            if move.en_passant:
                self.board[move.start_row][move.start_col] = move.piece_moved
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_cap

            else:
                self.board[move.start_row][move.start_col] = move.piece_moved
                self.board[move.end_row][move.end_col] = move.piece_cap

            self.en_passant_possible = move.en_passant_possible

            self.castle_rights_log.pop()
            self.current_castle_rights = self.castle_rights_log[-1]

            if move.can_castle:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][7] = self.board[move.end_row][5]
                    self.board[move.end_row][5] = "--"
                else:
                    self.board[move.end_row][0] = self.board[move.end_row][3]
                    self.board[move.end_row][3] = "--"

    """Check if a piece is pinned"""

    def check_for_pins(self):
        pins = []
        checks = []
        in_check = False

        if self.white_to_move:
            enemy_colour = "b"
            ally_colour = "w"
            start_row, start_col = self.white_king
        else:
            enemy_colour = "w"
            ally_colour = "b"
            start_row, start_col = self.black_king

        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j, d in enumerate(directions):
            poss_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    piece = self.board[end_row][end_col]
                    if piece[0] == ally_colour:
                        if poss_pin == ():
                            poss_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif piece[0] == enemy_colour:
                        p_type = piece[1]

                        if (
                            (0 <= j <= 3 and p_type == "R")
                            or (4 <= j <= 7 and p_type == "B")
                            or (p_type == "Q")
                            or (i == 1 and p_type == "K")
                            or (
                                i == 1
                                and p_type == "p"
                                and (
                                    (enemy_colour == "w" and 6 <= j <= 7)
                                    or (enemy_colour == "b" and 4 <= j <= 5)
                                )
                            )
                        ):
                            if poss_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else:
                                pins.append(poss_pin)
                            break

                        else:
                            break
                else:
                    break
        return in_check, pins, checks

    """Generate valid moves with checks"""

    def get_valid_moves(self):
        move = []
        self.in_check, self.pins, self.checks = self.check_for_pins()
        temp_castle_rights = CastleRights(
            self.current_castle_rights.wks,
            self.current_castle_rights.bks,
            self.current_castle_rights.wqs,
            self.current_castle_rights.bqs,
        )

        if self.white_to_move:
            king_row, king_col = self.white_king
        else:
            king_row, king_col = self.black_king

        if self.in_check:
            if len(self.checks) == 1:
                move = self.get_pos_moves()
                check = self.checks[0]
                check_row, check_col, d_row, d_col = check
                valid_sq = [(check_row, check_col)]

                for i in range(1, 8):
                    sq = (king_row + d_row * i, king_col + d_col * i)
                    valid_sq.append(sq)
                    if sq == (check_row, check_col):
                        break

                move = [
                    m
                    for m in move
                    if m.piece_moved[1] == "K" or (m.end_row, m.end_col) in valid_sq
                ]
            else:
                move = []
                self.get_king_moves(king_row, king_col, move)

        else:
            move = self.get_pos_moves()
            self.get_castle_moves(king_row, king_col, move)

        if len(move) == 0:
            self.checkmate = self.in_check
            self.stalemate = not self.in_check

        self.current_castle_rights = temp_castle_rights
        return move

    """Check if the king is in check"""

    def check_if_in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king[0], self.white_king[1])
        else:
            return self.square_under_attack(self.black_king[0], self.black_king[1])

    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move
        temp_castle_rights = self.current_castle_rights
        self.current_castle_rights = CastleRights(False, False, False, False)
        op_move = self.get_pos_moves(ignore_king=True)
        self.current_castle_rights = temp_castle_rights
        self.white_to_move = not self.white_to_move
        for move in op_move:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    """Generate moves without checks"""

    def get_pos_moves(self, ignore_king=False):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece_str = self.board[row][col]
                if piece_str != "--":
                    turn = piece_str[0]
                    if (turn == "w" and self.white_to_move) or (
                        turn == "b" and not self.white_to_move
                    ):
                        if ignore_king and piece_str[1] == "K":
                            continue
                        piece = piece_str[1]
                        self.move_func[piece](row, col, moves)

        return moves

    """Get the pawn moves with row, col and add them to the move list"""

    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_dir = ()

        for pin in self.pins:
            if pin[0] == row and pin[1] == col:
                piece_pinned = True
                pin_dir = (pin[2], pin[3])

        if self.white_to_move:
            if piece_pinned and pin_dir != (-1, 0) and pin_dir != (1, 0):
                return
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))

            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))

            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
            if row == 3:
                if col - 1 >= 0 and (row - 1, col - 1) == self.en_passant_possible:
                    moves.append(
                        Move(
                            (row, col),
                            (row - 1, col - 1),
                            self.board,
                            self.en_passant_possible,
                            en_passant=True,
                        )
                    )
                if col + 1 <= 7 and (row - 1, col + 1) == self.en_passant_possible:
                    moves.append(
                        Move(
                            (row, col),
                            (row - 1, col + 1),
                            self.board,
                            self.en_passant_possible,
                            en_passant=True,
                        )
                    )

        else:
            if piece_pinned and pin_dir != (-1, 0) and pin_dir != (1, 0):
                return
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))

            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))

            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
            if row == 4:
                if col - 1 >= 0 and (row + 1, col - 1) == self.en_passant_possible:
                    moves.append(
                        Move(
                            (row, col),
                            (row + 1, col - 1),
                            self.board,
                            self.en_passant_possible,
                            en_passant=True,
                        )
                    )
                if col + 1 <= 7 and (row + 1, col + 1) == self.en_passant_possible:
                    moves.append(
                        Move(
                            (row, col),
                            (row + 1, col + 1),
                            self.board,
                            self.en_passant_possible,
                            en_passant=True,
                        )
                    )

    """Get the piece moves with row, col and add them to the move list"""

    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_dir = ()

        for pin in self.pins:
            if pin[0] == row and pin[1] == col:
                piece_pinned = True
                pin_dir = (pin[2], pin[3])

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        if self.white_to_move:
            enemy_colour = "b"
            ally_colour = "w"
        else:
            enemy_colour = "w"
            ally_colour = "b"

        for dr, dc in directions:
            if piece_pinned and (dr, dc) != pin_dir and (-dr, -dc) != pin_dir:
                continue
            for i in range(1, 8):
                end_row = row + dr * i
                end_col = col + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_colour:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break

    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        pin_dir = ()

        for pin in self.pins:
            if pin[0] == row and pin[1] == col:
                piece_pinned = True
                pin_dir = (pin[2], pin[3])
        directions = (
            (-2, -1),
            (-2, 1),  # Up 2, left/right 1
            (-1, -2),
            (-1, 2),  # Up 1, left/right 2
            (1, -2),
            (1, 2),  # Down 1, left/right 2
            (2, -1),
            (2, 1),
        )

        if self.white_to_move:
            ally_colour = "w"
        else:
            ally_colour = "b"

        for dr, dc in directions:
            if piece_pinned and (dr, dc) != pin_dir and (-dr, -dc) != pin_dir:
                continue
            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_colour:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_dir = ()

        for pin in self.pins:
            if pin[0] == row and pin[1] == col:
                piece_pinned = True
                pin_dir = (pin[2], pin[3])
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        if self.white_to_move:
            enemy_colour = "b"
            ally_colour = "w"
        else:
            enemy_colour = "w"
            ally_colour = "b"

        for dr, dc in directions:
            if piece_pinned and (dr, dc) != pin_dir and (-dr, -dc) != pin_dir:
                continue
            for i in range(1, 8):
                end_row = row + dr * i
                end_col = col + dc * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_colour:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break

    def get_queen_moves(self, row, col, moves):
        # the bishop and rook methods cover 8 directions for the queen to move
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        piece_pinned = False
        pin_dir = ()

        for pin in self.pins:
            if pin[0] == row and pin[1] == col:
                piece_pinned = True
                pin_dir = (pin[2], pin[3])
        directions = (
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
        )
        if self.white_to_move:
            ally_colour = "w"
            enemy_colour = "b"
        else:
            ally_colour = "b"
            enemy_colour = "w"
        for dr, dc in directions:
            if piece_pinned and (dr, dc) != pin_dir and (-dr, -dc) != pin_dir:
                continue
            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] == enemy_colour:
                    original_piece = self.board[end_row][end_col]
                    original_pos = (
                        self.white_king if ally_colour == "w" else self.black_king
                    )
                    self.board[row][col] = "--"
                    self.board[end_row][end_col] = ally_colour + "K"

                    if ally_colour == "w":
                        self.white_king = (end_row, end_col)
                    else:
                        self.black_king = (end_row, end_col)

                    in_check = self.square_under_attack(end_row, end_col)
                    self.board[row][col] = ally_colour + "K"
                    self.board[end_row][end_col] = original_piece

                    if ally_colour == "w":
                        self.white_king = original_pos
                    else:
                        self.black_king = original_pos

                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    """Get moves for castle"""

    def get_castle_moves(self, row, col, move):
        if self.square_under_attack(row, col):
            return
        if (self.white_to_move and self.current_castle_rights.wks) or (
            not self.white_to_move and self.current_castle_rights.bks
        ):
            self.king_side_castle(row, col, move)
        if (self.white_to_move and self.current_castle_rights.wqs) or (
            not self.white_to_move and self.current_castle_rights.bqs
        ):
            self.queen_side_castle(row, col, move)

    def king_side_castle(self, row, col, move):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.square_under_attack(
                row, col + 1
            ) and not self.square_under_attack(row, col + 2):
                move.append(
                    Move((row, col), (row, col + 2), self.board, can_castle=True)
                )

    def queen_side_castle(self, row, col, move):
        if (
            self.board[row][col - 1] == "--"
            and self.board[row][col - 2] == "--"
            and self.board[row][col - 3] == "--"
        ):
            if not self.square_under_attack(
                row,
                col - 1,
            ) and not self.square_under_attack(row, col - 2):
                move.append(
                    Move((row, col), (row, col - 2), self.board, can_castle=True)
                )

    """Update castle rights when needed"""

    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.current_castle_rights.wks = False  # pyright: ignore
            self.current_castle_rights.wqs = False  # pyright: ignore
        elif move.piece_moved == "bK":
            self.current_castle_rights.bks = False  # pyright: ignore
            self.current_castle_rights.bqs = False  # pyright: ignore

        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castle_rights.wqs = False  # pyright: ignore
                elif move.start_col == 7:
                    self.current_castle_rights.wks = False  # pyright: ignore

        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.bks = False


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(
        self,
        started_sq,
        end_sq,
        board,
        en_passant_possible=(),
        en_passant=False,
        can_castle=False,
    ):
        self.start_row = started_sq[0]
        self.start_col = started_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        if en_passant:
            self.piece_cap = "bp" if self.piece_moved[0] == "w" else "wp"

        else:
            self.piece_cap = board[self.end_row][self.end_col]
        self.move_id = (
            self.start_row * 1000
            + self.start_col * 100
            + self.end_row * 10
            + self.end_col
        )
        self.is_pawn_promoted = (self.piece_moved == "wp" and self.end_row == 0) or (
            self.piece_moved == "bp" and self.end_row == 7
        )
        self.en_passant = en_passant
        self.en_passant_possible = en_passant_possible
        self.can_castle = can_castle

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def getChessNotation(self):
        return self.getRankFile(self.start_row, self.start_col) + self.getRankFile(
            self.end_row, self.end_col
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def getSAN(self, gs):
        if self.can_castle:
            return "O-O" if self.end_col == 6 else "O-O-O"

        piece = self.piece_moved[1]
        dest = self.getRankFile(self.end_row, self.end_col)

        if piece == "p":
            san = ""
            if self.piece_cap != "--":
                san += self.colsToFiles[self.start_col] + "x"
            san += dest
            if self.is_pawn_promoted:
                san += "=Q"

        else:
            san = piece
            if self.piece_cap != "--":
                san += "x"
            san += dest

        gs.makeMove(self)
        if gs.checkmate:
            san += "#"
        elif gs.in_check:
            san += "+"
        gs.undo_move()

        return san


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


def perft(gs, depth):
    if depth == 0:
        return 1

    moves = gs.get_valid_moves()
    nodes = 0

    for move in moves:
        gs.makeMove(move)
        nodes += perft(gs, depth - 1)
        gs.undo_move()

    return nodes


def perft_divide(gs, depth):
    moves = gs.get_valid_moves()
    total = 0

    for move in moves:
        gs.makeMove(move)
        nodes = perft(gs, depth - 1)
        gs.undo_move()

        print(move.getChessNotation(), nodes)
        total += nodes

    print("Total:", total)
