import os
import sys
import threading

import pygame as p

import engine
import movefinder

size = WIDTH, HEIGHT = 700, 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
fps = 60
IMAGES = {}
play_again = p.Rect(620, 420, 160, 50)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def mouse_debug(pos):
    x, y = pos
    if 0 <= x < 8 * SQ_SIZE and 0 <= y < 8 * SQ_SIZE:
        return y // SQ_SIZE, x // SQ_SIZE
    return None


def load_images():
    """Load Images only once in the main"""
    pieces = ["wp", "bp", "wB", "bB", "wK", "bK", "wN", "bN", "wQ", "bQ", "wR", "bR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(resource_path(f"images/{piece}.png")), (SQ_SIZE, SQ_SIZE)
        )


def draw_menu(screen):
    screen.fill(p.Color("White"))
    font = p.font.SysFont("arial", 40, bold=True)
    small_font = p.font.SysFont("arial", 24)

    title = font.render("Chess Game", True, p.Color("Black"))
    pvp = small_font.render("Player Vs Player", True, p.Color("Black"))
    pvai = small_font.render("Player Vs Ai", True, p.Color("Black"))

    title_rect = title.get_rect(center=(WIDTH // 2, 100))

    pvp_rect = p.Rect(WIDTH // 2 - 150, 220, 300, 60)
    pvai_rect = p.Rect(WIDTH // 2 - 150, 320, 300, 60)

    p.draw.rect(screen, p.Color("Lightgray"), pvp_rect, border_radius=10)
    p.draw.rect(screen, p.Color("Lightgray"), pvai_rect, border_radius=10)

    screen.blit(title, title_rect)
    screen.blit(pvp, pvp.get_rect(center=pvp_rect.center))
    screen.blit(pvai, pvai.get_rect(center=pvai_rect.center))

    return pvp_rect, pvai_rect


def draw_color_menu(screen):
    screen.fill(p.Color("White"))
    font = p.font.SysFont("arial", 36, bold=True)
    small_font = p.font.SysFont("arial", 24)

    title = font.render("Choose Your Color", True, p.Color("Black"))
    title_rect = title.get_rect(center=(WIDTH // 2, 100))

    white_rect = p.Rect(WIDTH // 2 - 150, 220, 300, 60)
    black_rect = p.Rect(WIDTH // 2 - 150, 320, 300, 60)

    p.draw.rect(screen, p.Color("Lightgray"), white_rect, border_radius=10)
    p.draw.rect(screen, p.Color("Lightgray"), black_rect, border_radius=10)

    white_text = small_font.render("Play as White", True, p.Color("Black"))
    black_text = small_font.render("Play as Black", True, p.Color("Black"))

    screen.blit(title, title_rect)
    screen.blit(white_text, white_text.get_rect(center=white_rect.center))
    screen.blit(black_text, black_text.get_rect(center=black_rect.center))

    return white_rect, black_rect


def endgame(screen, text):
    font = p.font.SysFont("arial", 40, bold=True)
    label = font.render(text, True, p.Color("Black"))
    rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(label, rect)


def draw_timer(screen, white_time, black_time):
    font = p.font.SysFont("arial", 36, bold=True)

    def format_time(time):
        minutes = int(time) // 60
        seconds = int(time) % 60
        return f"{minutes:02}:{seconds:02}"

    white_text = font.render(format_time(white_time), True, p.Color("Black"))
    black_text = font.render(format_time(black_time), True, p.Color("Black"))

    screen.blit(black_text, (WIDTH + 20, 40))
    screen.blit(white_text, (WIDTH + 20, HEIGHT - 60))


def draw_move_log(screen, gs):
    y = 0
    log_rect = p.Rect(WIDTH - 120, 10, 220, HEIGHT - 20)

    font = p.font.SysFont("arial", 18)

    for i in range(0, len(gs.san_log), 2):
        text = f"{i // 2 + 1}. {gs.san_log[i]}"
        if i + 1 < len(gs.san_log):
            text += f"  {gs.san_log[i + 1]}"
        text_obj = font.render(text, True, p.Color("Black"))
        screen.blit(text_obj, (log_rect.x, log_rect.y + y))

        y += 20


def draw_play_again(screen):
    font = p.font.SysFont("arial", 24)

    p.draw.rect(screen, (40, 40, 40), play_again)
    p.draw.rect(screen, (255, 255, 255), play_again, 2)

    text = font.render("Play Again", True, (255, 255, 255))
    screen.blit(text, (play_again.x + 20, play_again.y + 12))


def ai_worker(gs_copy, result):
    result["move"] = movefinder.find_best_move(gs_copy, depth=5)


def main():
    p.init()
    window = p.display.set_mode((size))
    p.display.set_caption("PyChess")
    clock = p.time.Clock()
    # images loaded only once before the game loop
    load_images()
    ai_thinking = False
    ai_move_result = None
    ai_thread = None

    while True:
        gs = engine.GameState()
        active_color = "w"
        black_time = white_time = 10 * 60
        last_tick = p.time.get_ticks()
        valid_moves = gs.get_valid_moves()
        move_made = False
        run = True
        sq_selected = ()
        player_clicked = []
        in_menu = True
        player_white = True
        player_black = True
        choose_color = False
        pvp_rect = pvai_rect = None
        white_rect = black_rect = None
        while in_menu:
            if not choose_color:
                pvp_rect, pvai_rect = draw_menu(window)
            else:
                white_rect, black_rect = draw_color_menu(window)

            for event in p.event.get():
                if event.type == p.QUIT:
                    return

                if event.type == p.MOUSEBUTTONDOWN:
                    if not choose_color:
                        if pvp_rect.collidepoint(event.pos):
                            player_white = True
                            player_black = True
                            in_menu = False

                        elif pvai_rect.collidepoint(event.pos):
                            choose_color = True
                    else:
                        if white_rect.collidepoint(event.pos):
                            player_white = True
                            player_black = False
                            in_menu = False

                        elif black_rect.collidepoint(event.pos):
                            player_white = False
                            player_black = True
                            in_menu = False

            p.display.update()

        while run:
            dt = clock.tick(fps) / 1000
            human_turn = (gs.white_to_move and player_white) or (
                not gs.white_to_move and player_black
            )

            if not gs.checkmate and not gs.stalemate:
                if active_color == "w":
                    white_time -= dt
                else:
                    black_time -= dt

            white_time = max(0, white_time)
            black_time = max(0, black_time)
            for event in p.event.get():
                if event.type == p.QUIT:
                    return

                if event.type == p.MOUSEBUTTONDOWN and (gs.checkmate or gs.stalemate):
                    if play_again.collidepoint(event.pos):
                        run = False
                        break

                elif event.type == p.MOUSEBUTTONDOWN and human_turn:
                    square = mouse_debug(event.pos)
                    if square is None:
                        continue
                    row, col = square

                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicked = []
                    else:
                        sq_selected = (row, col)
                        player_clicked.append(sq_selected)

                    if len(player_clicked) == 2:
                        chosen_move = None

                        for move in valid_moves:
                            if (move.start_row, move.start_col) == player_clicked[
                                0
                            ] and (
                                move.end_row,
                                move.end_col,
                            ) == player_clicked[1]:
                                move_made = True
                                chosen_move = move
                                break
                        if chosen_move:
                            san = chosen_move.getSAN(gs)
                            gs.makeMove(chosen_move)
                            gs.san_log.append(san)
                            active_color = "b" if active_color == "w" else "w"
                            move_made = True
                        sq_selected = ()
                        player_clicked = []

            window.fill(p.Color("White"))

            if not human_turn and not gs.checkmate and not gs.stalemate:
                if not ai_thinking:
                    ai_thinking = True
                    ai_move_result = {"move": None}
                    gs_copy = gs.copy()
                    ai_thread = threading.Thread(
                        target=ai_worker, args=(gs_copy, ai_move_result), daemon=True
                    )
                    ai_thread.start()
                elif ai_move_result is not None and ai_move_result["move"] is not None:
                    ai_move = ai_move_result["move"]
                    san = ai_move.getSAN(gs)
                    gs.makeMove(ai_move)
                    gs.san_log.append(san)
                    active_color = "b" if active_color == "w" else "w"
                    valid_moves = gs.get_valid_moves()
                    ai_thinking = False

            if move_made:
                valid_moves = gs.get_valid_moves()
                move_made = False

            draw_gameState(window, gs, valid_moves, sq_selected)
            draw_move_log(window, gs)
            draw_timer(window, white_time, black_time)
            if gs.checkmate:
                if gs.white_to_move:
                    endgame(window, "Black won by checkmate")
                    draw_play_again(window)
                else:
                    endgame(window, "White won by checkmate")
                    draw_play_again(window)

            elif gs.stalemate:
                endgame(window, "Stalemate")
                draw_play_again(window)

            if white_time <= 0:
                gs.checkmate = True
                endgame(window, "Black won by timeout")
            elif black_time <= 0:
                gs.checkmate = True
                endgame(window, "White won by timeout")
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
