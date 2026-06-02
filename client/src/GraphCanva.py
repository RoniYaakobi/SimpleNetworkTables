__author__ = "RONI YAAKOBI"
import pygame
from threading import Lock

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WINDOW_SIZE = (WINDOW_WIDTH,WINDOW_HEIGHT)

GRAPH_OFFSET = 50

WHITE = (255,255,255)

_graphs = []

__running = False
_screen = None

def initialize():
    """ Initialize the module """
    global _screen, __running, CLOCK, _graphs
    _graphs = []
    pygame.init()
    _screen = pygame.display.set_mode(WINDOW_SIZE)
    CLOCK = pygame.time.Clock()
    __running = True

def quit():
    """ Quit pygame """
    global _screen, __running, CLOCK
    __running = False
    pygame.quit()


def run():
    """ Run the main loop """
    global _screen, __running, CLOCK, _graphs
    while __running:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                quit()
                return
            
        for graph in _graphs:
            graph.draw()
        pygame.display.flip()
        CLOCK.tick(60)

class TextLabel:
    def __init__(self, text: str, font: pygame.font.Font, color: tuple[int,int,int] = WHITE):
        self.font = font
        self.color = color
        self.text = text

        self.surface = None
        self.rect = None
        self._render()

    def _render(self):
        """Render text surface and update rect."""
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()

    def set_text(self, text: str):
        """
        Args:
            text (str): new text
        """
        self.text = text
        self._render()

    def set_color(self, color: tuple[int, int, int]):
        """
        Args:
            color (tuple[int, int, int]): the new text color
        """
        self.color = color
        self._render()

    def draw_midtop(self, surface: pygame.surface.Surface, x: int, y: int):
        """ Draw with the midtop of the text at a set of coords

        Args:
            surface (pygame.surface.Surface): the surface to draw on
            x (int): x coordinate on the screen
            y (int): y coordinate on the screen
        """
        self.rect = self.surface.get_rect()
        self.rect.midtop = (x, y + 10)
        surface.blit(self.surface, self.rect)

    def draw_midright(self, surface: pygame.surface.Surface, x: int, y: int):
        """Draw with the midright of the text at a set of coords

        Args:
            surface (pygame.surface.Surface): the surface to draw on
            x (int): x coordinate on the screen
            y (int): y coordinate on the screen
        """
        self.rect = self.surface.get_rect()
        self.rect.midright = (x - 5, y + 5)
        surface.blit(self.surface, self.rect)


class Graph:
    TICK_SIZE = 30
    def __init__(self,title: str, 
                    data_points : list[tuple[float, float | int]],
                    data_lock: Lock,
                    size_x : int = WINDOW_WIDTH - 4*GRAPH_OFFSET,
                    size_y: int = WINDOW_HEIGHT - 2*GRAPH_OFFSET, 
                    tick_interval: int = 10):
        """Build a graph

        Args:
            data_points (list[tuple[float, float | int]]): The sorted buffer which holds the data points to draw
            size_x (int): the graph width
            size_y (int): the graph height
        """

        self.SIZE_X = size_x
        self.SIZE_Y = size_y
        self.tick_amount = tick_interval

        self.SIZE_DRAW_X = self.SIZE_X - Graph.TICK_SIZE
        self.SIZE_DRAW_Y = self.SIZE_Y

        self.x_tick_length = self.SIZE_DRAW_X / self.tick_amount
        self.y_tick_length = self.SIZE_DRAW_Y / self.tick_amount

        self.display = pygame.surface.Surface((self.SIZE_X + 2*Graph.TICK_SIZE, self.SIZE_Y + 1.5*Graph.TICK_SIZE))
        self.title = TextLabel(title, pygame.font.Font(None, 40))

        self.data_points = data_points
        self.data_points_lock = data_lock

        self.CLOSED_DRAW = False

        _graphs.append(self)


    def fit_x_to_graph(self, x: float) -> float:
        """ Translate the x coordinate to the graph

        Args:
            x (float): the x coordinate

        Returns:
            float: the translated x coordinate
        """
        return x + 2*Graph.TICK_SIZE
    
    def fit_y_to_graph(self, y: float):
        return self.SIZE_DRAW_Y - y
    
    def fit_point_to_graph(self, point: tuple[float]):
        return (self.fit_x_to_graph(point[0]), self.fit_y_to_graph(point[1]))
    
    def scale_point(self, point):
        return (point[0] - self.x_min) * self.x_scale, (point[1] - self.y_min) * self.y_scale

    def draw_lines(self):
        with self.data_points_lock:
            scaled_points = [self.scale_point(point) for point in self.data_points]

        points_fitted = [self.fit_point_to_graph(point) for point in scaled_points]

        pygame.draw.lines(self.display, WHITE, self.CLOSED_DRAW, points_fitted, 3)

    def draw_axis(self):
        self.x_min = self.data_points[0][0]
        x_max = self.data_points[-1][0]

        self.y_min = y_max = self.data_points[-1][1]
        for _, value in self.data_points:
            y_max = max(y_max, value)
            self.y_min = min(self.y_min, value)

        x_len = x_max - self.x_min
        y_len = y_max - self.y_min

        self.x_scale = self.SIZE_DRAW_X / x_len
        self.y_scale = self.SIZE_DRAW_Y / y_len

        ticks_x = [x * self.x_tick_length for x in range(self.tick_amount + 1)]
        ticks_y = [self.fit_y_to_graph(y * self.y_tick_length) for y in range(self.tick_amount + 1)]

        pygame.draw.lines(self.display, WHITE, self.CLOSED_DRAW, [(2*Graph.TICK_SIZE, 0),(2*Graph.TICK_SIZE, self.SIZE_Y), (self.SIZE_DRAW_X + 2*Graph.TICK_SIZE, self.SIZE_Y)], 2)

        for tick_num, tick in enumerate(ticks_x):
            tick_val = self.x_min + tick_num * x_len / self.tick_amount

            pygame.draw.line(self.display, WHITE, self.fit_point_to_graph((tick, -Graph.TICK_SIZE / 2)), 
                             self.fit_point_to_graph((tick, Graph.TICK_SIZE / 2)), 2)
            
            TextLabel(f"{tick_val}", pygame.font.Font(None, 14)).draw_midtop(self.display, *self.fit_point_to_graph((tick, -0.5*Graph.TICK_SIZE)))
            
        for tick_num, tick in enumerate(ticks_y):
            tick_val = self.y_min + tick_num * y_len / self.tick_amount

            pygame.draw.line(self.display, WHITE, (1.5*Graph.TICK_SIZE, tick), 
                             (2.5*Graph.TICK_SIZE, tick), 2)
            
            TextLabel(f"{tick_val:.2e}", pygame.font.Font(None, 14)).draw_midright(self.display, 2*Graph.TICK_SIZE, tick)

    def draw(self):
        self.display.fill("black")
        try:
            self.draw_axis()
        except ZeroDivisionError:
            print("Two points needed for a graph")
            return
        
        self.draw_lines()
        self.title.draw_midtop(_screen, WINDOW_WIDTH // 2, 0)
        _screen.blit(self.display, (GRAPH_OFFSET, GRAPH_OFFSET))
