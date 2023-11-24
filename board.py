import pygame



#image for background -> podemos escolher outra para adaptar na interface
#change path to image
BACKGROUND = '/Users/larasousa/Desktop/uni/labiacd/trabalho2/GO_GAME'

BOARD_SIZE = (820, 820)

# Colors here
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')

#-------------------------------------------------------------------------

#-> TIRAR FORA <-
def get_rbg(color):
    if color == 'WHITE':
        return 255, 255, 255
    elif color == 'BLACK':
        return 0, 0, 0
    else:
        return 0, 133, 211


#Return the coordinate of a stone on board
#(pixel coordinates for a stone on the board, given its point in terms of grid coordinates)
def stone_coords(point):
    return 5 + point[0] * 40, 5 + point[1] * 40


#calculates the top-left corner of a square on the board, given its point in terms of grid coordinates
def leftup_corner(point):
    return -15 + point[0] * 40, -15 + point[1] * 40

#-------------------------------------------------------------------------


class Interface:

    def __init__(self):
        self.outline = pygame.Rect(45, 45, 720, 720)    #board's rectangle
        self.screen = None      #display surface
        self.background = None   #background image



    #Call this method to initialize the board
    # sets up the Pygame environment
    def initialize(self):
        pygame.init()
        pygame.display.set_caption('Go Game')
        self.screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)    #window dimensions
        self.background = pygame.image.load(BACKGROUND).convert()   #loads the background image
        pygame.draw.rect(self.background, BLACK, self.outline, 3)   #draws the board's rectangle


        #This can be useful later for detecting mouse clicks within a larger area around the actual game board
        self.outline.inflate_ip(20, 20)

        #create a grid -> change dimensions -> 9x9 or 7x7
        for i in range(9):
            for j in range(9):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(self.background, BLACK, rect, 1)

        #Drawing the Star Points (Hoshi)
        for i in range(3):
            for j in range(3):
                coords = (165 + (240 * i), 165 + (240 * j))
                pygame.draw.circle(self.background, BLACK, coords, 5, 0)

        self.screen.blit(self.background, (0, 0))

        pygame.display.update()



   # Draw a stone on board
    def draw_stone(self, point, color, size=20):
        color = pygame.Color(color)
        pygame.draw.circle(self.screen, color, stone_coords(point), size, 0)
        pygame.display.update()

   #remove a stone from the board (when a stone or group of stones is captured)
    def remove(self, point):
        blit_coords = leftup_corner(point)  #the top-left corner of the square on the board where the stone to be removed is located
        area_rect = pygame.Rect(blit_coords, (40, 40))  # the area of the screen from which the stone will be removed
        self.screen.blit(self.background, blit_coords, area_rect)
        pygame.display.update()

    #allows the current state of the game board to be saved as an image file.
    def save_as_image(self, path_to_save):
        pygame.image.save(self.screen, path_to_save)
