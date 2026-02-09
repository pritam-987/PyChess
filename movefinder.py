import random


def random_move(valid_moves):
    if not valid_moves:
        return None
    return random.choice(valid_moves)


def safe_get_moves(gs):
    old_checkmate = gs.checkmate
    old_stalemate = gs.stalemate
    old_in_check = gs.in_check

    moves = gs.get_valid_moves()

    gs.checkmate = old_checkmate
    gs.stalemate = old_stalemate
    gs.in_check = old_in_check

    return moves


"""Depth 2 minimax"""
piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}


def utility(gs):
    moves = safe_get_moves(gs)
    if len(moves) == 0:
        if gs.in_check:
            return -10000
        else:
            return 0

    score = 0
    for row in range(8):
        for col in range(8):
            sq = gs.board[row][col]
            if sq == "--":
                continue
            value = piece_score[sq[1]]

            if sq[1] in ("p", "N", "B"):
                if 2 <= row <= 5 and 2 <= col <= 5:
                    value += 0.2

            score += value if sq[0] == "w" else -value

    return score


def ordered_moves(gs):
    moves = safe_get_moves(gs)

    def score(m):
        if m.piece_cap == "--":
            return 0
        return 10 * piece_score[m.piece_cap[1]] - piece_score[m.piece_moved[1]]

    moves.sort(key=score, reverse=True)
    return moves[:12]


def terminal(gs):
    moves = safe_get_moves(gs)
    if len(moves) == 0:
        return True
    return False


def minimax(gs, depth):
    alpha = float("-inf")
    beta = float("inf")

    valid_moves = ordered_moves(gs)
    best_move = None

    if gs.white_to_move:
        best_value = float("-inf")

        for move in valid_moves:
            gs.makeMove(move)
            value = min_value(gs, depth - 1, alpha, beta)
            gs.undo_move()

            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)

    else:
        best_value = float("inf")

        for move in valid_moves:
            gs.makeMove(move)
            value = max_value(gs, depth - 1, alpha, beta)
            gs.undo_move()

            if value < best_value:
                best_value = value
                best_move = move
            beta = min(beta, best_value)

    return best_move


def min_value(gs, depth, alpha, beta):
    if terminal(gs) or depth == 0:
        return utility(gs)

    v = float("inf")
    for move in ordered_moves(gs):
        gs.makeMove(move)
        v = min(v, max_value(gs, depth - 1, alpha, beta))
        gs.undo_move()

        beta = min(beta, v)
        if beta <= alpha:
            break  # prune
    return v


def max_value(gs, depth, alpha, beta):
    if terminal(gs) or depth == 0:
        return quiescence(gs, alpha, beta)

    v = float("-inf")
    for move in ordered_moves(gs):
        gs.makeMove(move)
        v = max(v, min_value(gs, depth - 1, alpha, beta))
        gs.undo_move()

        alpha = max(alpha, v)
        if alpha >= beta:
            break  # prune
    return v


def negamax(gs, depth, alpha, beta, color):
    if depth == 0 or terminal(gs):
        return utility(gs)

    max_eval = float("-inf")

    for move in ordered_moves(gs):
        gs.makeMove(move)

        eval = -negamax(gs, depth - 1, -beta, -alpha, -color)
        gs.undo_move()

        max_eval = max(max_eval, eval)
        alpha = max(alpha, eval)
        if alpha >= beta:
            break
    return max_eval


def find_best_move(gs, depth):
    best_move = None
    alpha = float("-inf")
    beta = float("inf")

    color = 1 if gs.white_to_move else -1
    max_eval = float("-inf")

    for move in ordered_moves(gs):
        gs.makeMove(move)
        eval = -negamax(gs, depth - 1, -beta, -alpha, -color)
        gs.undo_move()
        if eval > max_eval:
            max_eval = eval
            best_move = move
        alpha = max(alpha, eval)

    return best_move


def quiescence(gs, alpha, beta):
    stand_pat = utility(gs)

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in ordered_moves(gs):
        if move.piece_cap == "--":
            continue
        gs.makeMove(move)
        score = -quiescence(gs, -beta, -alpha)
        gs.undo_move()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha
