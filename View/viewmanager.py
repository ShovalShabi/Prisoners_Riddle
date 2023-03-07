import math
from pygame import KEYDOWN, K_BACKSPACE
import sys
from box_view import *
from prisoner_view import *


class ViewManager:
    def __init__(self,listener) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Prisoners")
        self.font = pygame.font.SysFont('monospace', FONT_SIZE, bold=True)
        self.clock = pygame.time.Clock()
        self.state = 'start'
        self.running = True
        self.num_of_boxes_view = 0
        self.num_of_prisoners = 0
        self.size = (screen_width, screen_height)
        self.screen = pygame.display.set_mode(self.size)
        self.image = IMG_BACKGROUND
        self.background_image = pygame.transform.scale(self.image, (screen_width, screen_height))
        self.text_input_n = ""
        self.text_input_k = ""
        self.status = 'Prisoner'
        self.p_color = RED
        self.r_color = BLACK
        self.actual_num_of_boxes = 0
        self.num_of_rounds=0
        self.start_rect = pygame.Rect(50, 800, button_width, button_height)
        self.start_hover_rect = pygame.Rect(50, 800, button_width, button_height)
        self.text_surface_start = self.font.render("START", True, BLACK)
        self.reset_rect = pygame.Rect(200, 800, button_width, button_height)
        self.reset_hover_rect = pygame.Rect(200, 800, button_width, button_height)
        self.text_surface_reset = self.font.render("RESET", True, BLACK)
        self.boxes = {}
        self.prisoners = {}
        self.listener=listener

    def run(self):
        while self.running:
            # draw board
            self.start_events()
            self.start_draw()
            self.button_events()

            # start pressed
            if self.state == 'begin':
                self.create_boxes()  # create boxes with number and locations
                self.create_prisoner()  # create prisoner with number and locations
                print(self.prisoners)
                #here there is a need to sent data to model
            pygame.display.update()
        pygame.quit()
        sys.exit()

    def button_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        self.draw_button(mouse_click, mouse_pos, self.start_rect, self.start_hover_rect, self.text_surface_start, GREEN)
        self.draw_button(mouse_click, mouse_pos, self.reset_rect, self.reset_hover_rect, self.text_surface_reset, RED)

    def draw_button(self, mouse_click, mouse_pos, rect, hover, text_surface, color):
        # Check if the mouse is over the button
        if rect.collidepoint(mouse_pos):
            # Draw the hover state
            pygame.draw.rect(self.screen, color, hover)
            if mouse_click[0] == 1:
                self.state = 'begin'
                print("Button clicked!")
        else:
            # Draw the normal state
            pygame.draw.rect(self.screen, WHITE, rect)
        self.screen.blit(text_surface, (rect.x + 23, rect.y + 17))

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == KEYDOWN and self.state != 'begin':
                if event.key == pygame.K_LEFT:
                    self.status = 'Prisoner'
                    self.p_color = RED
                    self.r_color = BLACK
                if event.key == pygame.K_RIGHT:
                    self.status = 'Round'
                    self.p_color = BLACK
                    self.r_color = RED

                if self.status == 'Round':  # rounds
                    self.text_input_k = self.handle_input(event, self.text_input_k)
                    #0self.num_of_rounds = int(str(self.text_input_k))
                if self.status == 'Prisoner':  # prisoner
                    self.text_input_n = self.handle_input(event, self.text_input_n)
                    self.convert_input_to_num()

    def start_draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.draw_menu()
        self.draw_boxes()
        # self.draw_prisoners()

    def draw_menu(self):
        # Draw the input text
        self.draw_label(self.p_color, 350, 800, 'Number of prisoners:')
        self.draw_label(RED, 350, 820, self.text_input_n)
        self.draw_label(self.r_color, 600, 800, 'Number of rounds:')
        self.draw_label(RED, 600, 820, self.text_input_k)

    def draw_label(self, color, x, y, text):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_boxes(self):

        if self.num_of_boxes_view <= MAX_BOX_WIDTH:
            for box_index in range(self.num_of_boxes_view):
                box = BoxV(self.screen, box_index + 1)
                box.location = box.draw_box(box_index, 0, self.font)

        else:
            rows = int(math.floor(self.num_of_boxes_view / MAX_BOX_WIDTH))
            remainder = self.num_of_boxes_view - rows * MAX_BOX_WIDTH
            for row in range(rows):
                for box_index in range(MAX_BOX_WIDTH):
                    box = BoxV(self.screen, box_index + 1)
                    box.location = box.draw_box(box_index, row, self.font)

            for rem in range(remainder):
                box = BoxV(self.screen, rem + 1)
                box.location = box.draw_box(rem, rows, self.font)

    def convert_input_to_num(self):
        if self.text_input_n != "":
            num = int(str(self.text_input_n))
            if num <= MAX_NO_PRISONER_BOX:
                self.num_of_boxes_view = num
            else:
                self.num_of_boxes_view = MAX_NO_PRISONER_BOX
            self.actual_num_of_boxes = num
            self.num_of_prisoners = num
        else:
            self.num_of_boxes_view = 0
            self.num_of_prisoners = 0

    def handle_input(self, event_input, text):
        if event_input.key == K_BACKSPACE:
            if len(text) > 0:
                text = text[:-1]
        else:
            text += event_input.unicode
        return text

    def create_boxes(self):
        if self.num_of_boxes_view <= MAX_BOX_WIDTH:
            for box_index in range(self.num_of_boxes_view):
                box = BoxV(self.screen, box_index + 1)
                self.boxes[box.num] = self.get_box_location(box.num, 0)
        else:
            rows = int(math.floor(self.num_of_boxes_view / MAX_BOX_WIDTH))
            remainder = self.num_of_boxes_view - rows * MAX_BOX_WIDTH
            for row in range(rows):
                for box_index in range(MAX_BOX_WIDTH):
                    box = BoxV(self.screen, box_index + 1 + row * MAX_BOX_WIDTH)
                    self.boxes[box.num] = self.get_box_location(box.num, row)
            for rem in range(remainder):
                box = BoxV(self.screen, rows * MAX_BOX_WIDTH + rem + 1)
                self.boxes[box.num] = self.get_box_location(box.num, rows)

    def get_box_location(self, box_index, inc):
        x = 150 + box_index * CELL_SIZE
        y = 80 + inc * CELL_SIZE
        return x, y

    def create_prisoner(self):
        for p in range(self.num_of_prisoners):
            prisoner = PrisonerV(DOOR_WAY, p + 1, self.screen)
            self.prisoners[prisoner.num] = prisoner.location
