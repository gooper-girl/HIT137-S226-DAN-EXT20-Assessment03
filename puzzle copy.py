import tkinter as tk
from tkinter import filedialog
import cv2
import random
import numpy as np
from PIL import Image, ImageTk

# will have to refactor eventually to meet the polymorphism requirement

def main():
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()

class PuzzleGUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Puzzle Game")
        self.window.geometry("800x600")

        self.build_setup_screen()

    def build_setup_screen(self):
        self.setup_frame = tk.Frame(self.window)
        self.setup_frame.pack(fill="both", expand=True)
        self.grid_var = tk.IntVar()

        tk.Label(self.setup_frame, text="Puzzle Set Up", font=("Arial", 20)).pack(pady=20)

        tk.Button(self.setup_frame, text="Browse Image", font=("Arial", 20), command=self.image_path).pack(pady=10)

        tk.Radiobutton(self.setup_frame, text="3 x 3", value=3, variable=self.grid_var).pack()
        tk.Radiobutton(self.setup_frame, text="4 x 4", value=4, variable=self.grid_var).pack()
        tk.Radiobutton(self.setup_frame, text="5 x 5", value=5, variable=self.grid_var).pack()

        tk.Button(self.setup_frame, text="Start Game", font=("Arial", 20), command=self.start_game).pack(pady=10)

    def image_path(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
        )

    def start_game(self):
        # add a check that makes sure an image is loaded
        grid_size = self.grid_var.get()

        self.board = Board(self.cv_img, self.grid_var.get())

        pil_img = self.board.get_original_image()
        self.prepared_image = ImageTk.PhotoImage(pil_img)

        self.setup_frame.destroy()
        self.build_game_screen()

    def on_tile_click(self, transformation):
        if self.board.player_move(transformation):
            self.update_move_label()

    def update_move_label(self):
        self.move_label.config(text=f"Moves: {self.board.get_moves()}")


    def build_game_screen(self):
        self.game_frame = tk.Frame(self.window)
        self.game_frame.pack(fill="both", expand=True)

        self.move_label = tk.Label(self.game_frame, text="Moves: 0").pack()

        self.left_frame = tk.Label(self.game_frame, image=self.prepared_image)
        self.left_frame.pack(side="left", expand=True)

        self.right_frame = tk.Frame(self.game_frame)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.right_frame, width=500, height=500)
        self.canvas.pack()

# ----------------------------------------------------------------------------------------------------------------------------------

class ImageProcessor:
    def __init__(self, size=400):
        self.__size = size
        
    def load_image(self, path):
        image = cv2.imread(path)

        if image is None:
            raise ValueError("Could not load image")
        return image        
    
    def prepare_image(self, image, grid_size):
        height = image.shape[0]
        width = image.shape[1]
        side = min(height, width)
        top = (height - side) // 2
        left = (width - side) // 2
        square = image[top:top + side, left:left + side]
        
        tile_size = self.__size // grid_size
        new_size = tile_size * grid_size
        return cv2.resize(square, (new_size, new_size))
    
    def split_image(self, image, grid_size):
        tile_size = image.shape[0] // grid_size
        pieces = []
        for row in range(grid_size):
            for col in range(grid_size):
                y = row * tile_size
                x = col * tile_size
                pieces.append(image[y:y + tile_size, x:x + tile_size])
        return pieces

    def join_tiles(self, pieces, grid_size):
        rows = []
        for row in range(grid_size):
            start = row * grid_size
            rows.append(np.hstack(pieces[start:start + grid_size]))
        return np.vstack(rows)

# ----------------------------------------------------------------------------------------------------------------------------------
    
class Tile:
    def __init__(self, home, image):
        self.__home = home
        self.__original = image
        self.__current = image.copy()
        
    def get_home(self):
        return self.__home
    
    def get_image(self):
        return self.__current
    
    def rotate(self):
        self.__current = cv2.rotate(self.__current, cv2.ROTATE_90_CLOCKWISE)
        
    def flip_horizontal(self):
        self.__current = cv2.flip(self.__current, 1)
        
    def flip_vertical(self):
        self.__current = cv2.flip(self.__current, 0)
        
    def is_right_way_up(self):
        return np.array_equal(self.__current, self.__original)
    
    def reset(self):
        self.__current = self.__original.copy()
        
# ----------------------------------------------------------------------------------------------------------------------------------      

class Transformation:
    def apply(self, board):
        raise NotImplementedError
    
class Swap(Transformation):
    def __init__(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2
        
    def apply(self, board):
        board.swap_tiles(self.pos1, self.pos2)
        
class Rotate(Transformation):
    def __init__(self, pos, turns):
        self.pos = pos
        self.turns = turns
        
    def apply(self, board):
        for i in range(self.turns):
            board.get_tile(self.pos).rotate()
            
class Flip(Transformation):
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        
    def apply(self, board):
        if self.direction == "horizontal":
            board.get_tile(self.pos).flip_horizontal()
        else:
            board.get_tile(self.pos).flip_vertical()
            
# ----------------------------------------------------------------------------------------------------------------------------------

class Board:
    def __init__(self, image, grid_size=3):
        self.__grid_size = grid_size
        self.__processor = ImageProcessor()
        self.__original = self.__processor.prepare_image(image, grid_size)
        self.__tile_size = self.__original.shape[0] // grid_size
        
        self.__tiles = []
        pieces = self.__processor.split_image(self.__original, grid_size)
        for i in range(len(pieces)):
            self.__tiles.append(Tile(i, pieces[i]))
            
        self.__moves = 0
        self.__hints_used = 0
        self.__hint = None
        
        self.scramble()
        
    def get_grid_size(self):
        return self.__grid_size
    
    def get_tile_size(self):
        return self.__tile_size
    
    def get_original_image(self):
        return self.__original
    
    def get_moves(self):
        return self.__moves
    
    def get_hints_left(self):
        return 3 - self.__hints_used
    
    def get_hint(self):
        return self.__hint
    
    def get_tile(self, pos):
        return self.__tiles[pos]
    
    def get_puzzle_image(self):
        pieces = []
        for tile in self.__tiles:
            pieces.append(tile.get_image())
        return self.__processor.join_tiles(pieces, self.__grid_size)
    
    def is_tile_correct(self, pos):
        tile = self.__tiles[pos]
        return tile.get_home() == pos and tile.is_right_way_up()
    
    def count_incorrect(self):
        count = 0
        for pos in range(len(self.__tiles)):
            if not self.is_tile_correct(pos):
                count += 1
        return count
        
    def is_solved(self):
        return self.count_incorrect() == 0
    
    def click_to_position(self, x, y):
        col = x // self.__tile_size
        row = y // self.__tile_size
        if row < 0 or row >= self.__grid_size or col < 0 or col >= self.__grid_size:
            return None
        return row * self.__grid_size + col
    
    def swap_tiles(self, pos1, pos2):
        self.__tiles[pos1], self.__tiles[pos2] = self.__tiles[pos2], self.__tiles[pos1]
        
    def scramble(self):
        amounts = {3: 6, 4: 12, 5: 20}
        count = amounts[self.__grid_size]
        total_tiles = len(self.__tiles)
        
        types = ["swap", "rotate", "flip"]
        while len(types) < count:
            types.append(random.choice(["swap", "rotate", "flip"]))
            
        transformations = []
        for t in types:
            if t == "swap":
                pos1, pos2 = random.sample(range(total_tiles), 2)
                transformations.append(Swap(pos1, pos2))
            elif t == "rotate":
                pos = random.randrange(total_tiles)
                transformations.append(Rotate(pos, random.choice([1, 2, 3])))
            else:
                pos = random.randrange(total_tiles)
                transformations.append(Flip(pos, random.choice(["horizontal", "vertical"])))
                
        for t in transformations:
            t.apply(self)
            
        if self.is_solved():
            self.scramble()
        
        
    def player_move(self, transformation):
        if self.is_solved():
            return False
        transformation.apply(self)
        self.__moves += 1
        self.__hint = None
        return True
    
    def player_swap(self, pos1, pos2):
        return self.player_move(Swap(pos1, pos2))
    
    def player_rotate(self, pos):
        return self.player_move(Rotate(pos, 1))
    
    def player_flip(self, pos):
        return self.player_move(Flip(pos, "horizontal"))
    
    
    def use_hint(self):
        if self.__hints_used >= 3 or self.is_solved():
            return None
        wrong = []
        for pos in range (len(self.__tiles)):
            if not self.is_tile_correct(pos):
                wrong.append(pos)
        pos = random.choice(wrong)
        home = self.__tiles[pos].get_home()
        self.__hint = (pos, home)
        self.__hints_used += 1
        return self.__hint
    
    def solve(self):
        solved = [None] * len(self.__tiles)
        for tile in self.__tiles:
            tile.reset()
            solved[tile.get_home()] = tile
        self.__tiles = solved
        self.__moves = 0
        self.__hint = None

# ----------------------------------------------------------------------------------------------------------------------------------

main()