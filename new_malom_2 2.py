import pygame
import sys
import time
import re
import random

# Játékos időzítők
white_time = 0
black_time = 0
last_time = time.time()  # Kezdési idő

pygame.init()


# Színek
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)
BG_COLOR = (245, 245, 220)  # Világos háttérszín
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Képernyő méretek
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Betűtípusok
font = pygame.font.Font(None, 36)

# Tábla paraméterek
board_color = BLACK
board_thickness = 10
node_radius = 15
highlight_thickness = 5

# Játékos korongok száma
player_white_pieces = 9
player_black_pieces = 9
current_player = "fehér"
selected_piece = None  # A kiválasztott korong, amelyet mozgatunk
game_phase = "placing"  # Fázis: 'placing' vagy 'moving'
remove_phase = False  # Ha igaz, a játékos levehet egy ellenfél korongot

# Tábla pozíciói
positions = [
    # Külső négyzet
    (100, 100), (400, 100), (700, 100),
    (100, 400), (700, 400),
    (100, 700), (400, 700), (700, 700),
    # Középső négyzet
    (200, 200), (400, 200), (600, 200),
    (200, 400), (600, 400),
    (200, 600), (400, 600), (600, 600),
    # Belső négyzet
    (300, 300), (400, 300), (500, 300),
    (300, 400), (500, 400),
    (300, 500), (400, 500), (500, 500)
]

# Lehelyezett korongok
white_pieces = []
black_pieces = []
occupied_positions = []  # List of positions already occupied by any piece

# Szomszédsági szabályok (melyik csomópontok szomszédosak)
neighbors = {
    (100, 100): [(400, 100), (100, 400)],
    (400, 100): [(100, 100), (700, 100), (400, 200)],
    (700, 100): [(400, 100), (700, 400)],
    (100, 400): [(100, 100), (100, 700), (200, 400)],
    (700, 400): [(700, 100), (700, 700), (600, 400)],
    (100, 700): [(100, 400), (400, 700)],
    (400, 700): [(100, 700), (700, 700), (400, 600)],
    (700, 700): [(400, 700), (700, 400)],
    (200, 200): [(400, 200), (200, 400)],
    (400, 200): [(400, 100), (200, 200), (600, 200), (400, 300)],
    (600, 200): [(400, 200), (600, 400)],
    (200, 400): [(200, 200), (100, 400), (200, 600), (300, 400)],
    (600, 400): [(600, 200), (600, 600), (700, 400), (500, 400)],
    (200, 600): [(200, 400), (400, 600)],
    (400, 600): [(200, 600), (400, 700), (600, 600), (400, 500)],
    (600, 600): [(400, 600), (600, 400)],
    (300, 300): [(400, 300), (300, 400)],
    (400, 300): [(300, 300), (500, 300), (400, 200)],
    (500, 300): [(400, 300), (500, 400)],
    (300, 400): [(300, 300), (300, 500), (200, 400)],
    (500, 400): [(500, 300), (500, 500), (600, 400)],
    (300, 500): [(300, 400), (400, 500)],
    (400, 500): [(300, 500), (500, 500), (400, 600)],
    (500, 500): [(400, 500), (500, 400)]
}

# Malmok meghatározása (előre definiált malom kombinációk)
mills = [
    [(100, 100), (400, 100), (700, 100)],
    [(100, 400), (200, 400), (300, 400)],
    [(100, 700), (400, 700), (700, 700)],
    [(100, 100), (100, 400), (100, 700)],
    [(400, 100), (400, 200), (400, 300)],
    [(700, 100), (700, 400), (700, 700)],
    [(200, 200), (400, 200), (600, 200)],
    [(200, 600), (400, 600), (600, 600)],
    [(200, 200), (200, 400), (200, 600)],
    [(600, 200), (600, 400), (600, 600)],
    [(300, 300), (400, 300), (500, 300)],
    [(300, 500), (400, 500), (500, 500)],
    [(300, 300), (300, 400), (300, 500)],
    [(500, 400), (600, 400), (700, 400)],
    [(400, 500), (400, 600), (400, 700)],
    [(500, 300), (500, 400), (500, 500)]

]
# Szöveg mező a játékos neve számára
input_box = pygame.Rect(300, 200, 200, 50)
player_name = ''
active = False
name_valid = False
input_color = WHITE  # Alapértelmezett háttérszín

# Nehézségi szintek
difficulty_levels = ["Könnyű", "Közepes", "Nehéz"]
selected_difficulty = "Könnyű"
radio_buttons = {
    "Könnyű": pygame.Rect(300, 300, 20, 20),
    "Közepes": pygame.Rect(300, 330, 20, 20),
    "Nehéz": pygame.Rect(300, 360, 20, 20)
}

# Kezdés gomb
start_button = pygame.Rect(300, 400, 200, 50)
start_button_active = False

def draw_text(text, rect, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, rect)

def check_name_validity(name):
    # Csak alfanumerikus karakterek megengedettek
    if re.match("^[A-Za-z0-9]+$", name):
        return True
    return False

def draw_radio_buttons():
    for level in difficulty_levels:
        color = BLACK if selected_difficulty == level else GRAY
        pygame.draw.circle(screen, color, (radio_buttons[level].x + 10, radio_buttons[level].y + 10), 10, 2)
        if selected_difficulty == level:
            pygame.draw.circle(screen, color, (radio_buttons[level].x + 10, radio_buttons[level].y + 10), 5)
        draw_text(level, (radio_buttons[level].x + 30, radio_buttons[level].y), BLACK)
def start_game():
    global active, player_name, input_color, name_valid, selected_difficulty, start_button_active
    while True:
        screen.fill(BG_COLOR)
        clock = pygame.time.Clock()
        # Játékos név beírása
        draw_text("Játékos neve:", (input_box.x - 160, input_box.y + 10), BLACK)
        pygame.draw.rect(screen, input_color, input_box)
        draw_text(player_name, (input_box.x + 10, input_box.y + 10), BLACK)

        # Nehézségi szint rádiógombok
        draw_text("Robot nehézségi szintje:", (radio_buttons["Könnyű"].x - 300, radio_buttons["Könnyű"].y+30), BLACK)
        draw_radio_buttons()

        # Kezdés gomb
        button_color = WHITE if start_button_active else GRAY
        pygame.draw.rect(screen, button_color, start_button)
        draw_text("Kezdés", (start_button.x + 50, start_button.y + 10), BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Szövegmező aktiválása
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False

                # Rádiógomb kiválasztás
                for level, rect in radio_buttons.items():
                    if rect.collidepoint(event.pos):
                        selected_difficulty = level

                # Kezdés gomb aktiválása
                if start_button.collidepoint(event.pos) and start_button_active:
                    print(f"Játékos neve: {player_name}, Nehézségi szint: {selected_difficulty}")
                    main()

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

                # Ellenőrizzük, hogy a név érvényes-e
                name_valid = check_name_validity(player_name)
                if name_valid:
                    input_color = GREEN
                    start_button_active = True
                else:
                    input_color = RED
                    start_button_active = False
        pygame.display.flip()
        clock.tick(30)

# Rajzolja a tábla négyzeteit és vonalait
def draw_board():
    screen.fill(BG_COLOR)
    for pos in positions:
        pygame.draw.circle(screen, LIGHT_GRAY, pos, node_radius)
    # Rajzoljuk meg a tábla vonalait
    for line in neighbors:
        for n in neighbors[line]:
            pygame.draw.line(screen, board_color, line, n, board_thickness)

# Korongok kirajzolása
def draw_pieces():
    for piece in white_pieces:
        pygame.draw.circle(screen, WHITE, piece, node_radius)
    for piece in black_pieces:
        pygame.draw.circle(screen, BLACK, piece, node_radius)

    # Kijelölt korong kiemelése
    if selected_piece:
        pygame.draw.circle(screen, BLUE, selected_piece, node_radius + highlight_thickness, highlight_thickness)

# Ellenőrizzük, hogy létrejött-e malom
def check_for_mill(piece_color, pieces, position):
    """
    Ellenőrzi, hogy a megadott pozícióval létrejött-e malom.
    Csak az adott pozícióhoz kapcsolódó malomkombinációkat vizsgálja.
    """
    for mill in mills:
        # Csak azokat a malomkombinációkat vizsgáljuk, amelyek tartalmazzák a megadott pozíciót.
        if position in mill:
            # Ellenőrizzük, hogy a malom minden pozíciója benne van-e a játékos aktuális korongjaiban.
            if all(pos in pieces for pos in mill):
                print(f"{piece_color} malmot alakított ki: {mill}")
                return True
    return False
def is_in_mill(position, pieces):
    """
    Ellenőrzi, hogy a megadott pozíció malomban van-e.
    """
    return any(all(pos in pieces for pos in mill) for mill in mills if position in mill)
def draw_surrender_button():
    # "Feladom" gomb létrehozása
    surrender_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 120, 40)
    pygame.draw.rect(screen, LIGHT_GRAY, surrender_button)
    surrender_text = font.render("Feladom", True, BLACK)
    screen.blit(surrender_text, (surrender_button.x + 10, surrender_button.y + 10))
    return surrender_button

def move_piece(new_position):
    global selected_piece, current_player, remove_phase, game_phase, last_time, white_time, black_time
    # Mozgatjuk a kijelölt korongot az új pozícióra
    if current_player == "fehér":
        white_pieces.remove(selected_piece)
        white_pieces.append(new_position)
        if check_for_mill("fehér", white_pieces, new_position):
            remove_phase = True
        else:
            current_player = "fekete"
            if len(black_pieces) == 3:
                game_phase = "jumping"
                print(game_phase)
            else:
                game_phase = "moving"
                print(game_phase)
            white_time += time.time() - last_time  # Fehér játékos idő frissítése
            last_time = time.time()  # Új játékos idejének indítása
    else:
        black_pieces.remove(selected_piece)
        black_pieces.append(new_position)
        if check_for_mill("fekete", black_pieces, new_position):
            remove_phase = True
        else:
            black_time += time.time() - last_time  # Fekete játékos idő frissítése
            current_player = "fehér"
            last_time = time.time()  # Új játékos idejének indítása
            if len(white_pieces) == 3:
                game_phase = "jumping"
                print(game_phase)
            else:
                game_phase = "moving"
                print(game_phase)

    occupied_positions.remove(selected_piece)
    occupied_positions.append(new_position)
    selected_piece = None  # Kijelölés megszüntetése.
    # Ellenőrizzük, hogy az ugrálási fázisra kell-e váltani

def can_form_mill(position, pieces):
    """
    Ellenőrzi, hogy az adott pozícióval malom alakítható-e ki.
    """
    for mill in mills:
        if position in mill:
            # Ha a malom többi pozíciója már elfoglalt a játékos korongjaival, malom kialakítható
            if all(pos in pieces or pos == position for pos in mill):
                return True
    return False

def evaluate_move(piece, new_position, color):
    """
    Értékeli a lépést: minél magasabb a pontszám, annál előnyösebb a lépés.
    """
    score = 0
    player_pieces = black_pieces if color == "fekete" else white_pieces
    opponent_pieces = white_pieces if color == "fekete" else black_pieces

    # Malom létrehozása
    if can_form_mill(new_position, player_pieces):
        score += 15  # Kiemelt prioritás a malom létrehozására

    # Kulcsfontosságú pozíciók (középső négyzetek)
    if new_position in [(400, 400), (400, 200), (400, 600), (200, 400), (600, 400)]:
        score += 5

    # Ellenfél malmának megelőzése
    for mill in mills:
        if new_position in mill and all(pos in opponent_pieces or pos == new_position for pos in mill):
            score += 10  # Ellenséges malom megelőzése

    return score

#########################################################################################################################
#            |                                                                                                          #
#            |             AZ AI FUNKCIÓI                                                                               #
#            V                                                                                                          #
#########################################################################################################################

def bot_make_move():
    """
    Fejlett AI lépési logika.
    Az AI a legjobb lépést választja ki, amely a legtöbb stratégiai előnnyel jár.
    """
    global player_black_pieces, occupied_positions, game_phase, current_player, remove_phase, last_time, black_time

    if game_phase == "placing" and player_black_pieces > 0:
        free_positions = [pos for pos in positions if pos not in occupied_positions]
        if free_positions:
            # Minden szabad hely értékelése
            best_move = max(free_positions, key=lambda pos: evaluate_move(None, pos, "fekete"))
            black_pieces.append(best_move)
            occupied_positions.append(best_move)
            player_black_pieces -= 1
            if check_for_mill("fekete", black_pieces, best_move):
                remove_phase = True
            else:
                current_player = "fehér"
                black_time += time.time() - last_time
                last_time = time.time()
            if player_white_pieces == 0 and player_black_pieces == 0:
                game_phase = "moving"

    elif game_phase == "moving" and len(black_pieces) > 3:
        movable_pieces = [piece for piece in black_pieces if any(
            neighbor not in occupied_positions for neighbor in neighbors[piece]
        )]
        if movable_pieces:
            best_move = None
            best_score = -float("inf")
            for piece in movable_pieces:
                for neighbor in neighbors[piece]:
                    if neighbor not in occupied_positions:
                        score = evaluate_move(piece, neighbor, "fekete")
                        if score > best_score:
                            best_score = score
                            best_move = (piece, neighbor)
            if best_move:
                move_piece_bot(*best_move)

    elif game_phase == "jumping" and len(black_pieces) == 3:
        free_positions = [pos for pos in positions if pos not in occupied_positions]
        if free_positions:
            best_move = None
            best_score = -float("inf")
            for piece in black_pieces:
                for pos in free_positions:
                    score = evaluate_move(piece, pos, "fekete")
                    if score > best_score:
                        best_score = score
                        best_move = (piece, pos)
            if best_move:
                move_piece_bot(*best_move)

def move_piece_bot(selected_piece, new_position):
    """
    AI által mozgatott korong frissítése az új pozícióra.
    """
    global current_player, remove_phase, game_phase, last_time, black_time

    black_pieces.remove(selected_piece)
    black_pieces.append(new_position)
    occupied_positions.remove(selected_piece)
    occupied_positions.append(new_position)
    if check_for_mill("fekete", black_pieces, new_position):
        remove_phase = True
    else:
        black_time += time.time() - last_time  # Fekete játékos idő frissítése
        current_player = "fehér"
        last_time = time.time()
        if len(white_pieces) == 3:
            game_phase = "jumping"
        else:
            game_phase = "moving"


#########################################################################################################################
#            A                                                                                                          #
#            |             AZ AI FUNKCIÓI                                                                               #
#            |                                                                                                          #
#########################################################################################################################

def handle_player_move():
    """
    A fehér játékos lépéseinek kezelése:
    - Korong lerakása ('placing' fázisban).
    - Korong mozgatása ('moving' fázisban).
    - Ugrás bármely szabad helyre ('jumping' fázisban).
    """
    global current_player, selected_piece, game_phase, remove_phase, player_white_pieces, last_time, white_time

    pos = pygame.mouse.get_pos()

    if remove_phase:
        # Eltávolítási fázis
        opponent_pieces = black_pieces
        non_mill_pieces = [p for p in opponent_pieces if not is_in_mill(p, opponent_pieces)]
        for position in (non_mill_pieces if non_mill_pieces else black_pieces):
            if pygame.Rect(position[0] - 20, position[1] - 20, 40, 40).collidepoint(pos):
                black_pieces.remove(position)
                occupied_positions.remove(position)
                remove_phase = False
                current_player = "fekete"
                white_time += time.time() - last_time
                last_time = time.time()

                if game_phase == "placing":
                    game_phase = "placing"
                elif len(black_pieces) == 3:
                    game_phase = "jumping"
                elif len(black_pieces) < 3:
                    show_winner(player_name + " nyert!")
                elif game_phase == "moving":
                    game_phase = "moving"
                break

    elif game_phase == "placing":
        # 'Placing' fázis: korong lerakása
        for position in positions:
            if pygame.Rect(position[0] - 20, position[1] - 20, 40, 40).collidepoint(pos):
                if position not in occupied_positions:
                    white_pieces.append(position)
                    occupied_positions.append(position)
                    player_white_pieces -= 1
                    if check_for_mill("fehér", white_pieces, position):
                        remove_phase = True
                    else:
                        current_player = "fekete"
                        white_time += time.time() - last_time
                        last_time = time.time()
                    if player_white_pieces == 0 and player_black_pieces == 0:
                        game_phase = "moving"
                break

    elif game_phase == "moving":
        # 'Moving' fázis: korong mozgatása
        if selected_piece is None:
            for position in positions:
                if pygame.Rect(position[0] - 20, position[1] - 20, 40, 40).collidepoint(pos):
                    if position in white_pieces:
                        selected_piece = position
                        break
        else:
            for neighbor in neighbors[selected_piece]:
                if pygame.Rect(neighbor[0] - 20, neighbor[1] - 20, 40, 40).collidepoint(pos) and neighbor not in occupied_positions:
                    move_piece(neighbor)
                    break
            if pygame.Rect(selected_piece[0] - 20, selected_piece[1] - 20, 40, 40).collidepoint(pos):
                selected_piece = None

    elif game_phase == "jumping":
        # 'Jumping' fázis: korong ugrása bármely szabad helyre
        if selected_piece is None:
            for position in positions:
                if pygame.Rect(position[0] - 20, position[1] - 20, 40, 40).collidepoint(pos):
                    if position in white_pieces:
                        selected_piece = position
                        break
        else:
            for position in positions:
                if pygame.Rect(position[0] - 20, position[1] - 20, 40, 40).collidepoint(pos) and position not in occupied_positions:
                    move_piece(position)
                    break
            if pygame.Rect(selected_piece[0] - 20, selected_piece[1] - 20, 40, 40).collidepoint(pos):
                selected_piece = None


def main():
    global player_white_pieces, player_black_pieces, current_player, selected_piece, game_phase, remove_phase, last_time, white_time, black_time
    clock = pygame.time.Clock()
    while True:
        screen.fill(BG_COLOR)
        draw_board()
        draw_pieces()
        # Játékosok idő megjelenítése
        draw_text(f"{player_name} idő: {int(white_time)} mp", (50, 720), BLACK)
        draw_text(f"Fekete idő: {int(black_time)} mp", (450, 720), BLACK)
        surrender_button = draw_surrender_button()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if surrender_button.collidepoint(event.pos):
                    if current_player == "fehér":
                        show_winner("Fekete nyert!")
                    else:
                        show_winner(player_name + " nyert!")
                else:
                    pos = pygame.mouse.get_pos()

        # Ha a fekete játékos jön, a bot lép
        if current_player == "fekete":
            bot_make_move()
        else:
            # Fehér játékos lépéseit az eredeti logika kezeli
            handle_player_move()

        draw_text(f"{player_name} játékos korongjai: {player_white_pieces}", (50, 750), BLACK)
        draw_text(f"Fekete játékos korongjai: {player_black_pieces}", (450, 750), BLACK)
        if current_player == "fehér":
            draw_text(f"Jelenlegi játékos: {player_name}", (300, 50), BLACK)
        else:
            draw_text(f"Jelenlegi játékos: Fekete (Bot)", (300, 50), BLACK)

        pygame.display.flip()
        clock.tick(30)


def draw_text(text, rect, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, rect)
def reset_game():
    global player_white_pieces, player_black_pieces, current_player, selected_piece, game_phase, remove_phase
    global white_pieces, black_pieces, occupied_positions, white_time, black_time,last_time
    # Kezdő értékek visszaállítása
    player_white_pieces = 9
    player_black_pieces = 9
    current_player = "fehér"
    selected_piece = None
    game_phase = "placing"
    remove_phase = False
    white_pieces = []
    black_pieces = []
    occupied_positions = []
    white_time=0
    black_time=0
    main()


def show_winner(winner_text):
    # Háttér
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(150)  # Átlátszóság, hogy a játék háttér látható legyen
    screen.blit(overlay, (0, 0))

    # Győzelmi üzenet ablak
    box_width, box_height = 400, 250
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = (SCREEN_HEIGHT - box_height) // 2
    pygame.draw.rect(screen, BG_COLOR, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 5)  # Keret

    # Nyertes üzenet
    winner_message = font.render(winner_text, True, BLACK)
    screen.blit(winner_message, (box_x + (box_width - winner_message.get_width()) // 2, box_y + 40))

    # Összesített játékidő
    total_time = int(white_time + black_time)
    time_text = font.render(f"Összesített idő: {total_time} mp", True, BLACK)
    screen.blit(time_text, (box_x + (box_width - time_text.get_width()) // 2, box_y + 80))

    # Kilépés gomb
    exit_button = pygame.Rect(box_x + 30, box_y + 150, 110, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, exit_button)
    exit_text = font.render("Kilépés", True, BLACK)
    screen.blit(exit_text, (exit_button.x + 15, exit_button.y + 10))

    # Visszavágó gomb
    rematch_button = pygame.Rect(box_x + box_width -180, box_y + 150, 140, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, rematch_button)
    rematch_text = font.render("Visszavágó", True, BLACK)
    screen.blit(rematch_text, (rematch_button.x + 5, rematch_button.y + 10))

    pygame.display.flip()

    # Várakozási ciklus a gombokra való kattintásra
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif rematch_button.collidepoint(event.pos):
                    reset_game()  # Újraindítjuk a játékot
                    waiting = False






if __name__ == "__main__":
    start_game()

