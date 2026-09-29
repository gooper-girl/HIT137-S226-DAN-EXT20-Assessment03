import tkinter as tk
from tkinter import filedialog
import cv2

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

        tk.Label(self.setup_frame, text="Puzzle Set Up", font=("Arial", 20)).pack(pady=20)

        tk.Button(self.setup_frame, text="Browse Image", font=("Arial", 20), command=self.load_image).pack(pady=10)

        tk.Button(self.setup_frame, text="Start Game", font=("Arial", 20), command=self.start_game).pack(pady=10)

    def load_image(self):
        path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
        )
        if path:
            self.image_path = path
            print("Loaded:", path)

    def process_image(self): # might make own class
        img = cv2.imread(self.image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (400, 400))

        self.cv_image = img

        if img is None:
            raise ValueError("Could not load image")

    def start_game(self):
        # add a check that makes sure an image is loaded
        
        self.setup_frame.destroy()
        self.build_game_screen()

    def build_game_screen(self):
        self.game_frame = tk.Frame(self.window)
        self.game_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.game_frame, width=200, height=200, bg="lightgray")
        self.left_frame.pack(side="left", expand=True)

        self.right_frame = tk.Frame(self.game_frame, width=200, height=200, bg="white")
        self.right_frame.pack(side="right", expand=True)

main()