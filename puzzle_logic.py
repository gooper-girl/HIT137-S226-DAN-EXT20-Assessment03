import random
import cv2
import numpy as np


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