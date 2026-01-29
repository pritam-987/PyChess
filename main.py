import pygame as p

import engine

size = WIDTH, HEIGHT = 512, 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
fps = 60
IMAGES = {}


def load_images():
    """Load Images only once in the main"""
    pieces = ["wp", "bp", "wB", "bB", "wK", "bK", "wN", "bN", "wQ", "bQ", "wR", "bR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )


def main():
    p.init()
    window = p.display.set_mode((size))
    clock = p.time.Clock()
    window.fill("White")
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    # images loaded only once before the game loop
    load_images()
    run = True
    sq_selected = ()
    player_clicked = []

    while run:
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False

            # mouse input
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicked = []
                else:
                    sq_selected = (row, col)
                    player_clicked.append(sq_selected)  # pyright: ignore
                if len(player_clicked) == 2:
                    move_made_flag = False
                    for valid_move in valid_moves:
                        if (
                            valid_move.start_row == player_clicked[0][0]
                            and valid_move.start_col == player_clicked[0][1]
                            and valid_move.end_row == player_clicked[1][0]
                            and valid_move.end_col == player_clicked[1][1]
                        ):
                            gs.makeMove(valid_move)
                            move_made = True
                            sq_selected = ()
                            player_clicked = []
                            move_made_flag = True
                            break
                    if not move_made_flag:
                        player_clicked = [sq_selected]

            # undo move
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_gameState(window, gs, valid_moves, sq_selected)
        clock.tick(fps)
        p.display.update()


"""Graphics Rendering"""


def draw_gameState(display, gs, valid_moves, sq_selected):
    draw_board(display)
    draw_pieces(display, gs.board)
    highlight_sq(display, gs, valid_moves, sq_selected)
    highlight_last_sq(display, gs)
    highlight_check(display, gs)


def highlight_sq(display, gs, valid_moves, sq_selected):
    if sq_selected == ():
        return
    row, col = sq_selected

    if gs.board[row][col] == "--":
        return
    if (gs.board[row][col][0] == "w" and not gs.white_to_move) or (
        gs.board[row][col][0] == "b" and gs.white_to_move
    ):
        return

    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(120)

    s.fill(p.Color("blue"))
    display.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

    s.fill(p.Color("green"))

    for move in valid_moves:
        if move.start_row == row and move.start_col == col:
            end_r, end_c = move.end_row, move.end_col
            if gs.board[end_r][end_c] == "--":
                p.draw.circle(
                    display,
                    p.Color("green"),
                    (
                        end_c * SQ_SIZE + SQ_SIZE // 2,
                        end_r * SQ_SIZE + SQ_SIZE // 2,
                    ),
                    SQ_SIZE // 6,
                )
            else:
                p.draw.circle(
                    display,
                    p.Color("red"),
                    (
                        end_c * SQ_SIZE + SQ_SIZE // 2,
                        end_r * SQ_SIZE + SQ_SIZE // 2,
                    ),
                    SQ_SIZE // 2 - 5,
                    4,
                )


def highlight_last_sq(display, gs):
    if len(gs.movelog) == 0:
        return

    move = gs.movelog[-1]
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(120)
    s.fill(p.Color("yellow"))

    display.blit(s, (move.start_col * SQ_SIZE, move.start_row * SQ_SIZE))
    display.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def highlight_check(display, gs):
    if not gs.in_check:
        return
    row, col = gs.white_king if gs.white_to_move else gs.black_king
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(140)
    s.fill(p.Color("red"))
    display.blit(s, (col * SQ_SIZE, row * SQ_SIZE))


def draw_board(display):
    colors = [p.Color("White"), p.Color("Light Grey")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(
                display, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


def draw_pieces(display, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            if board[row][col] != "--":
                display.blit(
                    IMAGES[board[row][col]],
                    p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                )


if __name__ == "__main__":
    main()
    gs = engine.GameState()
    print(engine.perft(gs, 1))
    print(engine.perft(gs, 2))
    print(engine.perft(gs, 3))
    moves = gs.get_valid_moves()
    for m in moves:
        print(m.getChessNotation())
