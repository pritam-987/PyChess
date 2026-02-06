import random


def random_move(valid_moves):
    if not valid_moves:
        return None
    return random.choice(valid_moves)


"""Depth 2 minimax"""
piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}


def utility(gs):
    if gs.checkmate:
        return -10000 if gs.white_to_move else 10000
    if gs.stalemate:
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
    moves = gs.get_valid_moves()
    moves.sort(key=lambda m: m.piece_cap != "--", reverse=True)
    return moves


def terminal(gs):
    return gs.checkmate or gs.stalemate


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
        return utility(gs)

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
        return color * utility(gs)

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
