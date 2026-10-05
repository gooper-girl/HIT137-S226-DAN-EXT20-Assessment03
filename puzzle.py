import tkinter as tk
from tkinter import filedialog
import cv2
import random
import numpy as np
from PIL import Image, ImageTk

def main():
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()

class PuzzleGUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Puzzle Game")
        self.window.geometry("800x600")
        self.selected_tile = None
        self.game_over = False

        self.build_setup_screen()

    def build_setup_screen(self):
        self.setup_frame = tk.Frame(self.window)
        self.setup_frame.pack(fill="both", expand=True)

        self.grid_var = tk.IntVar()

        tk.Label(
            self.setup_frame,
            text="Puzzle Set Up",
            font=("Arial", 24)
        ).pack(pady=30)

        tk.Label(
            self.setup_frame,
            text="Accepted formats: PNG, JPG, JPEG, BMP",
            font=("Arial", 12),
            fg="gray"
        ).pack()

        browse_row = tk.Frame(self.setup_frame)
        browse_row.pack(pady=10)

        self.browse_button = tk.Button(
            browse_row,
            text="Browse",
            font=("Arial", 14),
            width=10,
            command=self.select_image_path
        )
        self.browse_button.pack(side="left")
        self.browse_button.config(state="normal")

        self.path_entry = tk.Entry(
            browse_row,
            width=40,
            font=("Arial", 14)
        )
        self.path_entry.pack(side="left", padx=10)

        tk.Label(
            self.setup_frame,
            text="Choose puzzle size:",
            font=("Arial", 16)
            ).pack(pady=(20, 5))

        size_row = tk.Frame(self.setup_frame)
        size_row.pack()

        tk.Radiobutton(size_row, text="3 x 3", value=3, variable=self.grid_var, font=("Arial", 14)).pack(side="left", padx=10)
        tk.Radiobutton(size_row, text="4 x 4", value=4, variable=self.grid_var, font=("Arial", 14)).pack(side="left", padx=10)
        tk.Radiobutton(size_row, text="5 x 5", value=5, variable=self.grid_var, font=("Arial", 14)).pack(side="left", padx=10)

        tk.Button(
            self.setup_frame,
            text="Start Game",
            font=("Arial", 20),
            command=self.start_game
        ).pack(pady=30)

    def select_image_path(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
        )

        if self.image_path:
            self.path_entry.config(state="normal")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.image_path)
            self.path_entry.config(state="readonly")

    def start_game(self):

        if not hasattr(self, "image_path") or not self.image_path:
            tk.messagebox.showerror("Error", "Please select an image before starting the game.")
            return

        valid_ext = (".png", ".jpg", ".jpeg", ".bmp")
        if not self.image_path.lower().endswith(valid_ext):
            tk.messagebox.showerror("Error", "Invalid file format.\nPlease select a PNG, JPG, JPEG, or BMP image.")
            return

        grid_size = self.grid_var.get()
        if grid_size == 0:
            tk.messagebox.showerror("Error", "Please select a puzzle size before starting the game.")
            return

        processor = ImageProcessor()

        self.cv_img = processor.load_image(self.image_path)
        prepared = processor.prepare_image(self.cv_img, grid_size)
        prepared = cv2.cvtColor(prepared, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(prepared)
        self.prepared_image = ImageTk.PhotoImage(pil_img)

        self.setup_frame.destroy()
        self.build_game_screen()
        self.draw_board()

    def on_left_click(self, event):
        if self.game_over:
            return

        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return

        item_id = clicked[0]
        tags = self.canvas.gettags(item_id)
        if not tags:
            return

        tag = tags[0]
        if not tag.startswith("tile_"):
            return

        index = int(tag.split("_")[1])

        if self.selected_tile is None:
            self.selected_tile = index
            self.draw_board()
            return

        if self.selected_tile == index:
            self.selected_tile = None
            self.draw_board()
            return

        transformation = Swap(self.selected_tile, index)

        if self.board.player_move(transformation):
            self.selected_tile = None
            self.draw_board()
            self.update_move_label()

        if self.board.is_solved():
            self.show_solved_popup()

    def on_shift_left_click(self, event):
        if self.game_over:
            return

        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return

        item_id = clicked[0]
        tags = self.canvas.gettags(item_id)
        if not tags:
            return

        tag = tags[0]
        if not tag.startswith("tile_"):
            return

        index = int(tag.split("_")[1])

        transformation = Flip(index, "horizontal")
        if self.board.player_move(transformation):
            self.selected_tile = None 
            self.draw_board()
            self.update_move_label()

        if self.board.is_solved():
            self.show_solved_popup()

    def on_right_click(self, event):
        if self.game_over:
            return

        clicked = self.canvas.find_closest(event.x, event.y)
        if not clicked:
            return

        item_id = clicked[0]
        tags = self.canvas.gettags(item_id)
        if not tags:
            return

        tag = tags[0]
        if not tag.startswith("tile_"):
            return

        index = int(tag.split("_")[1])

        transformation = Rotate(index, 1)
        if self.board.player_move(transformation):
            self.draw_board()
            self.update_move_label()

        if self.board.is_solved():
            self.show_solved_popup()

    def update_move_label(self):
        self.move_label.config(text=f"Moves: {self.board.get_moves()}")

    def use_hint(self):
        hint = self.board.use_hint()
        if hint is None:
            return

        if self.board.get_hints_left() == 0:
            self.hint_button.config(state="disabled")

        self.draw_board()

    def solve_puzzle(self):
        self.board.solve()
        self.selected_tile = None
        self.draw_board()
        self.update_move_label()

        self.hint_button.config(state="disabled")
        self.solve_button.config(state="disabled")

        self.show_solved_popup()

    def build_game_screen(self):
        self.game_frame = tk.Frame(self.window)
        self.game_frame.pack(fill="both", expand=True)

        self.top_bar = tk.Frame(self.game_frame, bg="#dddddd", pady=5)
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.move_label = tk.Label(self.top_bar, text="Moves: 0")
        self.move_label.pack(side="left", padx=10)

        self.correct_label = tk.Label(self.top_bar, text="Correct: 0/0")
        self.correct_label.pack(side="left", padx=10)

        self.hint_button = tk.Button(self.top_bar, text="Hint", command=self.use_hint)
        self.hint_button.pack(side="left", padx=10)

        self.solve_button = tk.Button(self.top_bar, text="Solve", command=self.solve_puzzle)
        self.solve_button.pack(side="left", padx=10)

        self.game_frame.columnconfigure(0, weight=1)
        self.game_frame.columnconfigure(1, weight=1)

        self.game_frame.rowconfigure(0, weight=0)

        self.game_frame.rowconfigure(1, weight=1)

        self.board = Board(self.cv_img, self.grid_var.get())

        self.left_container = tk.Frame(self.game_frame)
        self.left_container.grid(row=1, column=0, sticky="nsew")

        self.left_container.rowconfigure(0, weight=1)
        self.left_container.columnconfigure(0, weight=1)

        self.left_canvas = tk.Canvas(self.left_container)
        self.left_canvas.grid(row=0, column=0, sticky="nsew")

        self.left_canvas.create_image(0, 0, image=self.prepared_image, anchor="nw")
        self.left_canvas.image = self.prepared_image

        self.right_frame = tk.Frame(self.game_frame)
        self.right_frame.grid(row=1, column=1, sticky="nsew")

        self.canvas = tk.Canvas(self.right_frame)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Shift-Button-1>", self.on_shift_left_click)

        self.game_frame.rowconfigure(1, weight=1)
        self.game_frame.columnconfigure(0, weight=1)
        self.game_frame.columnconfigure(1, weight=1)

        bottom_bar = tk.Frame(self.game_frame, pady=10)
        bottom_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.bottom_browse_button = tk.Button(
            bottom_bar,
            text="Browse",
            font=("Arial", 12),
            width=10,
            command=self.bottom_image_path
        )
        self.bottom_browse_button.pack(side="left", padx=10)

        self.bottom_path_entry = tk.Entry(bottom_bar, width=40, font=("Arial", 12))
        self.bottom_path_entry.pack(side="left", padx=10)

        self.load_new_button = tk.Button(
            bottom_bar,
            text="Load Image",
            font=("Arial", 12),
            command=self.load_new_image
        )
        self.load_new_button.pack(side="left", padx=10)


    def draw_board(self):
        grid_size = self.board.get_grid_size()
        tile_size = self.prepared_image.width() // grid_size

        self.left_canvas.delete("all")
        self.left_canvas.create_image(0, 0, image=self.prepared_image, anchor="nw")
        self.left_canvas.image = self.prepared_image

        self.canvas.delete("all")
        self.tk_tiles = []

        for i, tile in enumerate(self.board._Board__tiles):
            np_img = tile.get_image()
            np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(np_img)
            tk_img = ImageTk.PhotoImage(pil_img)
            self.tk_tiles.append(tk_img)

            row = i // grid_size
            col = i % grid_size

            self.canvas.create_image(
                col * tile_size,
                row * tile_size,
                image=tk_img,
                anchor="nw",
                tags=(f"tile_{i}")
            )

            if self.board.is_tile_correct(i):
                self.canvas.create_text(
                    col * tile_size + 5,
                    row * tile_size + 5,
                    text="✓",
                    fill="lightgreen",
                    anchor="nw",
                    font=("Arial", 16, "bold")
                )

            if i == self.selected_tile:
                self.canvas.create_rectangle(
                    col * tile_size,
                    row * tile_size,
                    (col + 1) * tile_size,
                    (row + 1) * tile_size,
                    outline="red",
                    width=3
    )

        hint = self.board.get_hint()
        if hint is not None:
            wrong_pos, home_pos = hint

            wrong_row = wrong_pos // grid_size
            wrong_col = wrong_pos % grid_size

            self.canvas.create_oval(
                wrong_col * tile_size + 10,
                wrong_row * tile_size + 10,
                wrong_col * tile_size + tile_size - 10,
                wrong_row * tile_size + tile_size - 10,
                outline="blue",
                width=3
            )

            home_row = home_pos // grid_size
            home_col = home_pos % grid_size

            self.left_canvas.create_oval(
                home_col * tile_size + 10,
                home_row * tile_size + 10,
                home_col * tile_size + tile_size - 10,
                home_row * tile_size + tile_size - 10,
                outline="blue",
                width=3
            )

        for col in range(grid_size + 1):
            x = col * tile_size
            self.canvas.create_line(x, 0, x, self.prepared_image.height(), fill="black")

        for row in range(grid_size + 1):
            y = row * tile_size
            self.canvas.create_line(0, y, self.prepared_image.width(), y, fill="black")

        total = self.board.get_grid_size() ** 2
        incorrect = self.board.count_incorrect()
        correct = total - incorrect

        self.correct_label.config(text=f"Correct: {correct}/{total}")

    def show_solved_popup(self):
        self.game_over = True

        popup = tk.Toplevel(self.window)
        popup.title("Puzzle Solved!")
        popup.geometry("300x180")
        popup.resizable(False, False)

        tk.Label(
            popup,
            text="Congratulations!\nYou solved the puzzle!",
            font=("Arial", 16),
            pady=20
        ).pack()

        button_row = tk.Frame(popup)
        button_row.pack(pady=10)

        tk.Button(
            button_row,
            text="Return to Setup",
            font=("Arial", 14),
            command=lambda: self.return_to_setup(popup)
        ).pack(side="left", padx=10)

        tk.Button(
            button_row,
            text="Exit Game",
            font=("Arial", 14),
            command=self.window.destroy
        ).pack(side="left", padx=10)

    def return_to_setup(self, popup):
        popup.destroy()
        self.game_over = False
        self.game_frame.destroy()

        self.window.update_idletasks()

        if hasattr(self, "browse_button"):
            del self.browse_button

        self.image_path = None
        self.new_image_path = None

        self.build_setup_screen()

    def bottom_image_path(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )

        if path:
            self.new_image_path = path
            self.bottom_path_entry.config(state="normal")
            self.bottom_path_entry.delete(0, tk.END)
            self.bottom_path_entry.insert(0, path)
            self.bottom_path_entry.config(state="readonly")

    def load_new_image(self):

        if not hasattr(self, "new_image_path") or not self.new_image_path:
            tk.messagebox.showerror("Error", "Please select an image to load.")
            return

        valid_ext = (".png", ".jpg", ".jpeg", ".bmp")
        if not self.new_image_path.lower().endswith(valid_ext):
            tk.messagebox.showerror("Error", "Invalid file format.\nPlease select a PNG, JPG, JPEG, or BMP image.")
            return

        processor = ImageProcessor()
        self.cv_img = processor.load_image(self.new_image_path)

        grid_size = self.grid_var.get()

        prepared = processor.prepare_image(self.cv_img, grid_size)
        prepared = cv2.cvtColor(prepared, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(prepared)
        self.prepared_image = ImageTk.PhotoImage(pil_img)

        self.board = Board(self.cv_img, grid_size)
        self.selected_tile = None
        self.game_over = False

        self.draw_board()
        self.update_move_label()

        self.hint_button.config(state="normal")
        self.solve_button.config(state="normal")

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

main()