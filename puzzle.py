import tkinter as tk
from tkinter import filedialog

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

    def start_game(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return

        self.setup_frame.destroy()
        self.build_game_screen()

    def build_game_screen(self):
        pass

main()