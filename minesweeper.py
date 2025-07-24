import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count > 0:
            return self.cells.copy()
        return set()
        
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1  # FIXED: was missing 'self.'
            self.cells.remove(cell)
        

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Step 1: Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Step 2: Mark the cell as safe
        self.mark_safe(cell)

        # Step 3: Add a new sentence to the knowledge base
        neighbours = set()
        i, j = cell

        for vi in [-1, 0, 1]:
            for vj in [-1, 0, 1]:
                if vi == 0 and vj == 0:
                    continue
                ni, nj = i + vi, j + vj
                # FIXED: Check bounds before adding neighbors
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbours.add((ni, nj))

        new_sentence_cells = set()
        new_sentence_count = count

        for neighbour in neighbours:
            if neighbour in self.mines:
                new_sentence_count -= 1
            elif neighbour not in self.safes:  # FIXED: Don't include known safe cells
                new_sentence_cells.add(neighbour)

        # Only add sentence if it has cells
        if new_sentence_cells:
            new_sentence = Sentence(new_sentence_cells, new_sentence_count)
            self.knowledge.append(new_sentence)
        
        # Step 4: Update knowledge based on current sentences
        self._update_knowledge()
        
        # Step 5: Add new sentences that can be inferred from existing knowledge
        self._infer_new_sentences()

    def _update_knowledge(self):
        """
        Helper method to update knowledge by marking cells as safe or mines
        based on current sentences.
        """
        knowledge_changed = True
        while knowledge_changed:
            knowledge_changed = False
            
            # Check each sentence for definitive conclusions
            for sentence in self.knowledge[:]:  # Use slice to avoid modification during iteration
                # Find cells that are definitely mines
                mines_found = sentence.known_mines()
                for mine in mines_found:
                    if mine not in self.mines:
                        self.mark_mine(mine)
                        knowledge_changed = True
                
                # Find cells that are definitely safe
                safes_found = sentence.known_safes()
                for safe in safes_found:
                    if safe not in self.safes:
                        self.mark_safe(safe)
                        knowledge_changed = True
            
            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

    def _infer_new_sentences(self):
        """
        Helper method to infer new sentences from existing knowledge.
        Uses the subset method: if sentence A is a subset of sentence B,
        we can create a new sentence C = B - A.
        """
        new_sentences = []
        
        # Compare each pair of sentences
        for i in range(len(self.knowledge)):
            for j in range(i + 1, len(self.knowledge)):
                sentence1 = self.knowledge[i]
                sentence2 = self.knowledge[j]
                
                # Check if sentence1 is a subset of sentence2
                if sentence1.cells.issubset(sentence2.cells) and sentence1.cells != sentence2.cells:
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    if new_count >= 0:  # FIXED: Ensure count is not negative
                        new_sentence = Sentence(new_cells, new_count)
                        
                        # Add the new sentence if it's not already in our knowledge
                        if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                            new_sentences.append(new_sentence)
                
                # Check if sentence2 is a subset of sentence1
                elif sentence2.cells.issubset(sentence1.cells) and sentence2.cells != sentence1.cells:
                    new_cells = sentence1.cells - sentence2.cells
                    new_count = sentence1.count - sentence2.count
                    if new_count >= 0:  # FIXED: Ensure count is not negative
                        new_sentence = Sentence(new_cells, new_count)
                        
                        # Add the new sentence if it's not already in our knowledge
                        if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                            new_sentences.append(new_sentence)
        
        # Add all new sentences to knowledge
        self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    possible_moves.append(cell)
        
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return None