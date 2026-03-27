import itertools
import random

# -------------------------------
# Minesweeper Game
# -------------------------------

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()
        self.board = [[False for _ in range(width)] for _ in range(height)]

        # Place mines randomly
        while len(self.mines) < mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # Track mines found by player
        self.mines_found = set()

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines in adjacent cells
        """
        count = 0
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if (i,j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self):
        """
        Check if all safe cells have been revealed
        """
        return len(self.mines_found) == len(self.mines)

# -------------------------------
# Sentence Class
# -------------------------------

class Sentence():
    """
    Logical statement about Minesweeper
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count and self.count != 0:
            return set(self.cells)
        return set()

    def known_safes(self):
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

# -------------------------------
# Minesweeper AI
# -------------------------------

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = set()
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if 0 <= i < self.height and 0 <= j < self.width and (i,j) != cell:
                    if (i,j) not in self.safes and (i,j) not in self.mines:
                        neighbors.add((i,j))
                    elif (i,j) in self.mines:
                        count -= 1

        new_sentence = Sentence(neighbors, count)
        if new_sentence not in self.knowledge and neighbors:
            self.knowledge.append(new_sentence)

        self.update_knowledge()

    def update_knowledge(self):
        updated = True
        while updated:
            updated = False
            safes = set()
            mines = set()

            for sentence in self.knowledge:
                safes |= sentence.known_safes()
                mines |= sentence.known_mines()

            for safe in safes:
                if safe not in self.safes:
                    self.mark_safe(safe)
                    updated = True
            for mine in mines:
                if mine not in self.mines:
                    self.mark_mine(mine)
                    updated = True

            self.knowledge = [s for s in self.knowledge if s.cells]

            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 != s2 and s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        new_sentence = Sentence(diff_cells, diff_count)
                        if new_sentence not in self.knowledge and new_sentence.cells:
                            self.knowledge.append(new_sentence)
                            updated = True

    def make_safe_move(self):
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        choices = [
            (i,j)
            for i in range(self.height)
            for j in range(self.width)
            if (i,j) not in self.moves_made and (i,j) not in self.mines
        ]
        if choices:
            return random.choice(choices)
        return None

# -------------------------------
# Optional: Run AI Automatically
# -------------------------------

if __name__ == "__main__":
    height = 8
    width = 8
    mines = 8

    game = Minesweeper(height, width, mines)
    ai = MinesweeperAI(height, width)

    while not game.won():
        move = ai.make_safe_move()
        if move is None:
            move = ai.make_random_move()
        if move is None:
            break  # No moves left

        count = game.nearby_mines(move)
        ai.add_knowledge(move, count)

        # Optional: stop if AI hits a mine
        if game.is_mine(move):
            break

