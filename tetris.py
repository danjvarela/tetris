#!/usr/bin/env python3

import pygame as pg
import random
pg.init()

# Global variables
MINO_WIDTH = 25
COL = 10
ROW = 20
GRID_WIDTH = 250
GRID_HEIGHT = SCREEN_HEIGHT = 500
SCREEN_WIDTH = 500
# BLACK = pg.Color(40, 44, 52)
BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(171, 178, 191)
LIGHT_YELLOW = pg.Color(229, 192, 123)
GUTTER_GRAY = pg.Color(76, 82, 99)


TETRAMINO_SHAPES = {"I": [(0, 0), (-1, 0), (1, 0), (2, 0)],
                    "J": [(0, 0), (-1, 0), (-1, -1), (1, 0)],
                    "L": [(0, 0), (-1, 0), (1, 0), (1, -1)],
                    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
                    "S": [(0, 0), (-1, 0), (0, -1), (1, -1)],
                    "T": [(0, 0), (-1, 0), (1, 0), (0, -1)],
                    "Z": [(0, 0), (0, -1), (-1, -1), (1, 0)]}


TETRAMINO_COLORS = {"I": pg.Color(224, 108, 117),
                    "J": pg.Color(152, 195, 121),
                    "O": pg.Color(229, 192, 123),
                    "L": pg.Color(97, 175, 239),
                    "S": pg.Color(198, 120, 221),
                    "T": pg.Color(86, 182, 194),
                    "Z": pg.Color(190, 80, 70)}

LOCKED_MINOES = []

# Offset data for rotation
# See https://harddrop.com/wiki/SRS for reference
JLSTZ_OFFSET = [[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
                [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
                [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]]

I_OFFSET = [[(0, 0), (-1, 0), (2, 0), (-1, 0), (2, 0)],
            [(-1, 0), (0, 0), (0, 0), (0, 1), (0, -2)],
            [(-1, 1), (1, 1), (-2, 1), (1, 0), (-2, 0)],
            [(0, 1), (0, 1), (0, 1), (0, -1), (0, 2)]]

O_OFFSET = [(0, 0), (0, -1), (-1, -1), (-1, 0)]


# Mino is the building block of a Tetramino
class Mino:
  def __init__(self, position, color):
    self.position = position
    self.color = color

  def draw(self, screen):
    pg.draw.rect(screen, self.color, pg.Rect(
        self.position[0] * MINO_WIDTH, self.position[1] * MINO_WIDTH, MINO_WIDTH - 1, MINO_WIDTH - 1))


# Tetra means 4 so... Tetramino is 4 Minoes?
class Tetramino:
  def __init__(self, position=None, shape=None):
    self.rotation = 0
    self.shape = random.choice(list(TETRAMINO_SHAPES.keys())) if shape is None else shape
    self.color = TETRAMINO_COLORS[self.shape]
    self.minoes = []
    # default position is the center of the grid
    self.position = (4, -2) if position is None else position

    # initialize the minoes' positions
    self.minoes = [Mino((pos[0] + self.position[0], pos[1] + self.position[1]), self.color)
                   for pos in TETRAMINO_SHAPES[self.shape]]

  # Checks if a Tetramino can be translated by x cells horizontally and y cells vertically
  # Used before translating or rotating a tetramino
  def is_possible_offset(self, positions, offset):
    for position in positions:
      if position[0] + offset[0] < 0 or position[0] + offset[0] >= COL or position[1] + offset[1] >= ROW:
        return False
      if (position[0] + offset[0], position[1] + offset[1]) in [mino.position for mino in LOCKED_MINOES]:
        return False
    return True

  # Translates the Tetramino
  # x cells horizontally and y cells vertically
  def translate(self, x, y):
    positions = [mino.position for mino in self.minoes]

    if self.is_possible_offset(positions, (x, y)):
      for mino in self.minoes:
        mino.position = (mino.position[0] + x, mino.position[1] + y)

      self.position = (self.position[0] + x, self.position[1] + y)
      # print([mino.position for mino in self.minoes])
      return True
    return False

  # Rotates the Tetramino clockwise
  def rotate(self):
    # rotation index to rotate to
    rotate_to = (self.rotation + 1) % 4
    possible_offsets = []

    # choose the offset based on the shape
    if self.shape in ["J", "L", "S", "T", "Z"]:
      for i in range(5):
        x = JLSTZ_OFFSET[self.rotation][i][0] - JLSTZ_OFFSET[rotate_to][i][0]
        y = JLSTZ_OFFSET[self.rotation][i][1] - JLSTZ_OFFSET[rotate_to][i][1]
        possible_offsets.append((x, y))
    elif self.shape == "I":
      for i in range(5):
        x = I_OFFSET[self.rotation][i][0] - I_OFFSET[rotate_to][i][0]
        y = I_OFFSET[self.rotation][i][1] - I_OFFSET[rotate_to][i][1]
        possible_offsets.append((x, y))
    elif self.shape == "O":
      possible_offsets = O_OFFSET

    # get the positions of each mino without the offset from self.position
    mino_positions = [(mino.position[0] - self.position[0], mino.position[1] - self.position[1])
                      for mino in self.minoes]
    rotated_mino_positions = [(-y, x) for x, y in mino_positions]

    # check if the rotation is possible
    for offset in possible_offsets:
      if self.is_possible_offset(rotated_mino_positions, (offset[0] + self.position[0], offset[1] + self.position[1])):
        self.minoes = [Mino((x + self.position[0] + offset[0], y + self.position[1] + offset[1]), self.color)
                       for x, y in rotated_mino_positions]
        # update rotation and position of the tetramino
        self.rotation = rotate_to
        self.position = (self.position[0] + offset[0], self.position[1] + offset[1])
        return True
    return False

  # Drop the tetramino to the lowest possible position
  def drop(self):
    while self.translate(0, 1):
      pass

  # Determine if the tetramino is at the bottom of the grid or cannot move down further
  def is_dropped(self):
    if self.is_possible_offset([mino.position for mino in self.minoes], (0, 1)):
      return False
    return True

  # Draws the Tetramino
  def draw(self, screen):
    for mino in self.minoes:
      mino.draw(screen)

# Renders a text on a given surface
def render_text(screen, text, position, font, color):
  text = font.render(text, True, color)
  text_rect = text.get_rect()
  text_rect.center = position
  screen.blit(text, text_rect)

# draws the next tetramino
def render_next_tetromino(screen, tetramino):
  t = Tetramino((14, 9), tetramino.shape)
  t.draw(screen)

# draws the area outside the grid which contains the Score and the Next Tetramino
def draw_side_screen(screen):
  # background
  ui_rect = pg.Rect(GRID_WIDTH, 0, SCREEN_WIDTH - GRID_WIDTH, SCREEN_HEIGHT)
  pg.draw.rect(screen, GUTTER_GRAY, ui_rect)

  tetris_font = pg.font.Font('PressStart2P-Regular.ttf', 32)

  render_text(screen, "SCORE", (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 70), tetris_font, WHITE)
  render_text(screen, "NEXT", (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 170), tetris_font, WHITE)
  tetris_font = pg.font.Font('PressStart2P-Regular.ttf', 12)
  render_text(screen, '← → move left/right', (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 350), tetris_font, WHITE)
  render_text(screen, '↑ rotate right', (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 380), tetris_font, WHITE)
  render_text(screen, '<space> drop block', (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 410), tetris_font, WHITE)
  render_text(screen, '<esc> pause', (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 440), tetris_font, WHITE)


# Updates score displayed on the side screen
def render_score(score, screen):
  # update the side screen first
  draw_side_screen(screen)

  # update the score
  scoreFont = pg.font.Font('PressStart2P-Regular.ttf', 25)
  render_text(screen, str(score), (GRID_WIDTH + (SCREEN_WIDTH - GRID_WIDTH) // 2, 110), scoreFont, LIGHT_YELLOW)

# Draws the grid
def draw_grid(screen):
  grid_rect = pg.Rect(0, 0, GRID_WIDTH, GRID_HEIGHT)
  pg.draw.rect(screen, BLACK, grid_rect)

# draws locked minoes
def draw_locked_minoes(screen):
  for mino in LOCKED_MINOES:
    mino.draw(screen)

# Remove minoes that complete a row
# returns the number of rows cleared
def clear_complete_rows():
  row_cleared = 0
  for row in range(ROW):
    row_blocks = [mino for mino in LOCKED_MINOES if mino.position[1] == row]
    if len(row_blocks) == COL:
      row_cleared += 1
      # remove the minoes in the row
      for mino in row_blocks:
        LOCKED_MINOES.remove(mino)
      # move the minoes above the row down
      for mino in LOCKED_MINOES:
        if mino.position[1] < row:
          mino.position = (mino.position[0], mino.position[1] + 1)
  return row_cleared

# Calculate the next score based on current score, cleared rows and level
def calculate_score(score, level, cleared_rows):
  coefficients = [0, 40, 100, 300, 1200]
  score += coefficients[cleared_rows] * (level + 1)
  return score


def intro(screen):
  while True:
    screen.fill(BLACK)
    font = pg.font.Font('PressStart2P-Regular.ttf', 60)
    render_text(screen, "TETRIS", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25), font, WHITE)
    font = pg.font.Font('PressStart2P-Regular.ttf', 20)
    render_text(screen, "Press Enter to Play", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25), font, LIGHT_YELLOW)
    for event in pg.event.get():
      if event.type == pg.QUIT:
        quit()
      if event.type == pg.KEYDOWN:
        if event.key == pg.K_RETURN:
          return
    pg.display.flip()

# game over screen
def game_over_screen(screen):
  while True:
    screen.fill(BLACK)
    font = pg.font.Font('PressStart2P-Regular.ttf',50)
    render_text(screen, "GAME OVER", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25), font, WHITE)
    font = pg.font.Font('PressStart2P-Regular.ttf',15)
    render_text(screen, "Press Enter to Play Again", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25), font, LIGHT_YELLOW)
    for event in pg.event.get():
      if event.type == pg.QUIT:
        quit()
      if event.type == pg.KEYDOWN:
        if event.key == pg.K_RETURN:
          return
    pg.display.flip()

def main():
  screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  pg.display.set_caption("Tetris")
  clock = pg.time.Clock()
  tetramino = Tetramino()
  next_tetramino = Tetramino()
  score = level = counter = 0
  framesPerGrid = 48
  paused = game_over = False

  draw_side_screen(screen)
  # delay so we can still move a tetramino at the last second before it locks position
  lock_delay = 0

  # intro screen
  intro(screen)

  # main game loop
  while True:
    global LOCKED_MINOES
    counter += 1
    for event in pg.event.get():
      if event.type == pg.QUIT:
        quit()
      elif event.type == pg.KEYDOWN:
        # prevent other key presses if paused
        if not paused:
          if event.key == pg.K_LEFT:
            tetramino.translate(-1, 0)
          elif event.key == pg.K_RIGHT:
            tetramino.translate(1, 0)
          elif event.key == pg.K_DOWN:
            tetramino.translate(0, 1)
          elif event.key == pg.K_UP:
            tetramino.rotate()
          elif event.key == pg.K_SPACE:
            tetramino.drop()
          if event.key == pg.K_ESCAPE:
            paused = True
        # only allow the enter key to be pressed to resume
        else:
          if event.key == pg.K_RETURN:
            paused = False

    if paused:
      screen.fill(BLACK)
      font = pg.font.Font('PressStart2P-Regular.ttf', 45)
      render_text(screen, "GAME PAUSED", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25), font, WHITE)
      font = pg.font.Font('PressStart2P-Regular.ttf', 15)
      render_text(screen, "Press Enter to Resume", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25), font, LIGHT_YELLOW)
    else:
      if counter >= framesPerGrid:
        tetramino.translate(0, 1)
        if tetramino.is_dropped():
          lock_delay += 1
          if tetramino.position[1] == -2:
            game_over = True
          if lock_delay > 1:
            LOCKED_MINOES.extend(tetramino.minoes)
            tetramino = next_tetramino
            next_tetramino = Tetramino()
            lock_delay = 0
        counter = 0

      # acts as a buffer
      draw_grid(screen)
      # draws the tetraminoes
      tetramino.draw(screen)
      draw_locked_minoes(screen)
      # clear completed rows
      cleared_rows = clear_complete_rows()
      # update score
      score = calculate_score(score, level, cleared_rows)
      # level advancement logic
      if cleared_rows >= max(100, level * 10 - 50):
        level += 1
        if level in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
          framesPerGrid = 48 - level * 5
        elif level in [10, 11, 12]:
          framesPerGrid = 5
        elif level in [13, 14, 15]:
          framesPerGrid = 4
        elif level in [16, 17, 18]:
          framesPerGrid = 3
        elif level in range(19, 29):
          framesPerGrid = 2
        elif level > 29:
          framesPerGrid = 1
      render_score(score, screen)
      render_next_tetromino(screen, next_tetramino)

    if game_over:
      game_over_screen(screen)
      game_over = False
      LOCKED_MINOES = []
      main()

    pg.display.flip()
    clock.tick()


main()