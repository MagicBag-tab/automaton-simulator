import pygame
import sys

class TreeVisualizer:
    def __init__(self, tree, expression_text=""):
        self.tree = tree
        self.expression_text = expression_text
        self.node_positions = {}
        self.rank = 0
        self.width = 600
        self.height = 400
        self.vertical_spacing = 70
        self.horizontal_spacing = 45
        self.radius = 20
        self.font = None
        self.title_font = None
        
    def _calculate_positions(self, node, depth=0):
        if node is None:
            return
        
        self._calculate_positions(node.left, depth + 1)
        
        self.rank += 1
        x = self.rank * self.horizontal_spacing
        y = 100 + depth * self.vertical_spacing
        self.node_positions[id(node)] = (x, y)
        
        self.width = max(self.width, x + 100)
        self.height = max(self.height, y + 100)
        
        self._calculate_positions(node.right, depth + 1)

    def draw(self):
        if not self.tree or not self.tree.root:
            print("El árbol está vacío.")
            return

        pygame.init()
        self.font = pygame.font.SysFont('arial', 20)
        self.title_font = pygame.font.SysFont('arial', 24, bold=True)
        
        # Calculate screen size based on the tree depth and width
        self.rank = 0
        self.node_positions.clear()
        self._calculate_positions(self.tree.root)
        
        # Ensure a minimum width for the window title
        self.width = max(self.width, 600)
        
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"Syntax Tree: {self.expression_text}")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        running = False
            
            screen.fill((250, 250, 250))
            
            # Title
            title_surface = self.title_font.render(f"RegEx: {self.expression_text}", True, (50, 50, 50))
            screen.blit(title_surface, (20, 20))
            
            info_surface = self.font.render("Presiona Enter o Esc para ver la siguiente expresión.", True, (100, 100, 100))
            screen.blit(info_surface, (20, 50))
            
            self._draw_lines(screen, self.tree.root)
            self._draw_nodes(screen, self.tree.root)
            
            pygame.display.flip()
            pygame.time.Clock().tick(30)
            
        pygame.quit()
        
    def _draw_lines(self, screen, node):
        if node is None:
            return
        
        pos1 = self.node_positions[id(node)]
        
        if node.left:
            pos2 = self.node_positions[id(node.left)]
            pygame.draw.line(screen, (100, 100, 100), pos1, pos2, 2)
            self._draw_lines(screen, node.left)
            
        if node.right:
            pos2 = self.node_positions[id(node.right)]
            pygame.draw.line(screen, (100, 100, 100), pos1, pos2, 2)
            self._draw_lines(screen, node.right)
            
    def _draw_nodes(self, screen, node):
        if node is None:
            return
            
        x, y = self.node_positions[id(node)]
        
        pygame.draw.circle(screen, (220, 235, 255), (x, y), self.radius)
        pygame.draw.circle(screen, (50, 100, 200), (x, y), self.radius, 2)
        
        text_surface = self.font.render(str(node.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
        
        self._draw_nodes(screen, node.left)
        self._draw_nodes(screen, node.right)
