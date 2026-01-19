class GameState:
    def __init__(self):
        # the board is a 2d 8x8 list where '--' is a space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "bp", "--", "--", "--", "--"],
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

    def makeMove(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move)
        self.white_to_move = not self.white_to_move

    """Undo last move"""

    def undo_move(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_cap
            self.white_to_move = not self.white_to_move

    """Generate valid moves with checks"""

    def get_valid_moves(self):
        return self.get_pos_moves()

    """Generate moves without checks"""

    def get_pos_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (
                    turn == "b" and not self.white_to_move
                ):
                    piece = self.board[row][col][1]
                    self.move_func[piece](row, col, moves)

        return moves

    """Get the pawn moves with row, col and add them to the move list"""

    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:
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

        else:
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

    """Get the piece moves with row, col and add them to the move list"""

    def get_rook_moves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        if self.board[row][col][0] == "w":
            enemy_colour = "b"
        else:
            enemy_colour = "w"

        for dr, dc in directions:
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

        if self.board[row][col][0] == "w":
            enemy_colour = "b"
        else:
            enemy_colour = "w"

        for dr, dc in directions:
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

    def get_bishop_moves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        if self.board[row][col][0] == "w":
            enemy_colour = "b"
        else:
            enemy_colour = "w"

        for dr, dc in directions:
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
        if self.board[row][col][0] == "w":
            enemy_colour = "b"
        else:
            enemy_colour = "w"

        for dr, dc in directions:
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


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, started_sq, end_sq, board):
        self.start_row = started_sq[0]
        self.start_col = started_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_cap = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_col

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
