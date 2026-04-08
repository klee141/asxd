import random
import sys

import pygame


# Grid settings
CELL_SIZE = 30
COLS = 10
ROWS = 20
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
PANEL_WIDTH = 180
SCREEN_WIDTH = GRID_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT

# Timing
FPS = 60
FALL_INTERVAL_MS = 500
SOFT_DROP_INTERVAL_MS = 50

# Colors
BLACK = (20, 20, 20)
WHITE = (240, 240, 240)
GRAY = (55, 55, 55)
BG = (15, 15, 25)

COLORS = {
    "I": (0, 230, 230),
    "O": (240, 240, 0),
    "T": (170, 0, 240),
    "S": (0, 220, 0),
    "Z": (230, 0, 0),
    "J": (0, 100, 230),
    "L": (240, 140, 0),
}

# Tetromino definitions (relative coordinates around pivot)
SHAPES = {
    "I": [(-2, 0), (-1, 0), (0, 0), (1, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
    "S": [(-1, 1), (0, 1), (0, 0), (1, 0)],
    "Z": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "J": [(-1, 0), (0, 0), (1, 0), (1, 1)],
    "L": [(-1, 1), (-1, 0), (0, 0), (1, 0)],
}

LINE_SCORES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.color = COLORS[kind]
        self.blocks = list(SHAPES[kind])
        self.x = COLS // 2
        self.y = 1

    def cells(self):
        return [(self.x + bx, self.y + by) for bx, by in self.blocks]

    def rotated(self):
        # O-piece is rotationally symmetric.
        if self.kind == "O":
            return list(self.blocks)
        # Rotate 90 degrees clockwise around (0, 0): (x, y) -> (y, -x)
        return [(by, -bx) for bx, by in self.blocks]


class Tetris:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simple Tetris")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.game_over = False

        self.current = self.new_piece()
        self.next_piece = self.new_piece()

        self.last_fall_ms = pygame.time.get_ticks()
        self.last_soft_drop_ms = pygame.time.get_ticks()
        self.soft_drop = False

    def new_piece(self):
        return Piece(random.choice(list(SHAPES.keys())))

    def valid(self, cells):
        for x, y in cells:
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def try_move(self, dx, dy):
        test_cells = [(x + dx, y + dy) for x, y in self.current.cells()]
        if self.valid(test_cells):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def try_rotate(self):
        rotated_blocks = self.current.rotated()
        test_cells = [(self.current.x + bx, self.current.y + by) for bx, by in rotated_blocks]
        if self.valid(test_cells):
            self.current.blocks = rotated_blocks
            return

        # Basic wall-kick attempts for playability
        for kick_x in (-1, 1, -2, 2):
            kicked_cells = [
                (self.current.x + bx + kick_x, self.current.y + by) for bx, by in rotated_blocks
            ]
            if self.valid(kicked_cells):
                self.current.x += kick_x
                self.current.blocks = rotated_blocks
                return

    def lock_piece(self):
        for x, y in self.current.cells():
            if y < 0:
                self.game_over = True
                return
            self.grid[y][x] = self.current.color
        self.clear_lines()
        self.current = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid(self.current.cells()):
            self.game_over = True

    def clear_lines(self):
        full_rows = [r for r in range(ROWS) if all(self.grid[r][c] is not None for c in range(COLS))]
        if not full_rows:
            return

        for row in full_rows:
            del self.grid[row]
            self.grid.insert(0, [None for _ in range(COLS)])

        lines_cleared = len(full_rows)
        self.lines += lines_cleared
        self.score += LINE_SCORES[lines_cleared]

    def hard_drop(self):
        while self.try_move(0, 1):
            pass
        self.lock_piece()

    def update(self):
        now = pygame.time.get_ticks()
        interval = SOFT_DROP_INTERVAL_MS if self.soft_drop else FALL_INTERVAL_MS
        last = self.last_soft_drop_ms if self.soft_drop else self.last_fall_ms

        if now - last >= interval:
            if not self.try_move(0, 1):
                self.lock_piece()
            if self.soft_drop:
                self.last_soft_drop_ms = now
            else:
                self.last_fall_ms = now

    def draw_grid(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, GRID_WIDTH, GRID_HEIGHT))
        for row in range(ROWS):
            for col in range(COLS):
                color = self.grid[row][col]
                if color:
                    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        for x, y in self.current.cells():
            if y >= 0:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, self.current.color, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Grid lines
        for c in range(COLS + 1):
            pygame.draw.line(
                self.screen,
                (40, 40, 50),
                (c * CELL_SIZE, 0),
                (c * CELL_SIZE, GRID_HEIGHT),
                1,
            )
        for r in range(ROWS + 1):
            pygame.draw.line(
                self.screen,
                (40, 40, 50),
                (0, r * CELL_SIZE),
                (GRID_WIDTH, r * CELL_SIZE),
                1,
            )

    def draw_side_panel(self):
        panel_x = GRID_WIDTH
        pygame.draw.rect(self.screen, BG, (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines}", True, WHITE)
        self.screen.blit(score_text, (panel_x + 12, 20))
        self.screen.blit(lines_text, (panel_x + 12, 56))

        next_text = self.small_font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (panel_x + 12, 110))

        preview_origin_x = panel_x + 55
        preview_origin_y = 160
        for bx, by in SHAPES[self.next_piece.kind]:
            px = preview_origin_x + bx * 20
            py = preview_origin_y + by * 20
            rect = pygame.Rect(px, py, 20, 20)
            pygame.draw.rect(self.screen, self.next_piece.color, rect)
            pygame.draw.rect(self.screen, GRAY, rect, 1)

        controls = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft drop",
            "Space: Hard drop",
            "R: Restart",
            "Esc: Quit",
        ]
        y = 270
        for line in controls:
            txt = self.small_font.render(line, True, WHITE)
            self.screen.blit(txt, (panel_x + 12, y))
            y += 24

    def draw_game_over(self):
        overlay = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        msg1 = self.font.render("Game Over", True, WHITE)
        msg2 = self.small_font.render("Press R to restart", True, WHITE)
        self.screen.blit(msg1, (GRID_WIDTH // 2 - msg1.get_width() // 2, GRID_HEIGHT // 2 - 28))
        self.screen.blit(msg2, (GRID_WIDTH // 2 - msg2.get_width() // 2, GRID_HEIGHT // 2 + 8))

    def restart(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.current = self.new_piece()
        self.next_piece = self.new_piece()
        now = pygame.time.get_ticks()
        self.last_fall_ms = now
        self.last_soft_drop_ms = now
        self.soft_drop = False

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
                    if event.key == pygame.K_r:
                        self.restart()
                    if self.game_over:
                        continue
                    if event.key == pygame.K_LEFT:
                        self.try_move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.try_move(1, 0)
                    elif event.key == pygame.K_UP:
                        self.try_rotate()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_DOWN:
                        self.soft_drop = True

                if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                    self.soft_drop = False

            if not self.game_over:
                self.update()

            self.screen.fill(BG)
            self.draw_grid()
            self.draw_side_panel()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Tetris().run()
