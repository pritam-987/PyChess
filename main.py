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
                    player_clicked.append(sq_selected)
                if len(player_clicked) == 2:
                    move = engine.Move(player_clicked[0], player_clicked[1], gs.board)
                    if move in valid_moves:
                        gs.makeMove(move)
                        move_made = True
                    sq_selected = ()
                    player_clicked = []

            # undo move
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_gameState(window, gs)
        clock.tick(fps)
        p.display.update()


"""Graphics Rendering"""


def draw_gameState(display, gs):
    draw_board(display)
    draw_pieces(display, gs.board)


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
