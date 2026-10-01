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