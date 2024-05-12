import pygame
from sys import exit
import math

pygame.init()

S_HEIGHT = 720
HALF_OF_GAME_AREA_WIDTH = S_HEIGHT // 2
BG_COLOR, PANEL_COLOR, TEXT_COLOR = (0, 0, 0), (63, 63, 63), (95, 95, 95)
BUTTON_COLOR_1, BUTTON_COLOR_2 = (47, 47, 47), (31, 31, 31)
SLIDER_BAR_COLOR, SLIDER_CONTROLLER_COLOR = (47, 47, 47), (31, 31, 31)
COLOR_1, COLOR_2, COLOR_3 = (255, 255, 0), (0, 0, 255), (255, 255, 255)
RADIUS_SIZE_1, RADIUS_SIZE_2, RADIUS_SIZE_3 = S_HEIGHT // 20, S_HEIGHT // 40, S_HEIGHT // 80

screen = pygame.display.set_mode((4 * S_HEIGHT // 3, S_HEIGHT))
pygame.display.set_caption("Three Planet Simulation")

clock = pygame.time.Clock()

gui_font = pygame.font.Font(None, S_HEIGHT // 24)
gui_font_large = pygame.font.Font(None, S_HEIGHT // 18)

panel_rect = pygame.rect.Rect((S_HEIGHT, 0), (S_HEIGHT // 3, S_HEIGHT))

distance_2_text_body_rect = pygame.rect.Rect(89 * S_HEIGHT // 72, S_HEIGHT // 9, S_HEIGHT // 18, S_HEIGHT // 18)
distance_3_text_body_rect = pygame.rect.Rect(89 * S_HEIGHT // 72, 2 * S_HEIGHT // 9, S_HEIGHT // 18, S_HEIGHT // 18)

speed_text_body_rect_1 = pygame.rect.Rect(89 * S_HEIGHT // 72, 11 * S_HEIGHT // 18, S_HEIGHT // 18, S_HEIGHT // 18)
speed_text_body_rect_2 = pygame.rect.Rect(89 * S_HEIGHT // 72, 13 * S_HEIGHT // 18, S_HEIGHT // 18, S_HEIGHT // 18)
speed_text_body_rect_3 = pygame.rect.Rect(89 * S_HEIGHT // 72, 5 * S_HEIGHT // 6, S_HEIGHT // 18, S_HEIGHT // 18)


class Button:

    def __init__(self, surface, text, font, x, y, width, height,
                 button_color_1, button_color_2, text_color, border_radius):
        self.surface = surface
        self.font = font
        self.button_color_1 = button_color_1
        self.button_color_2 = button_color_2
        self.color = button_color_1
        self.text_color = text_color
        self.border_radius = border_radius
        self.body_rect = pygame.rect.Rect(x, y, width, height)
        self.text = text
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        self.press_allowed = True
        self.pressed = False

    def is_clicked(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            if mouse_pressed:
                self.pressed = True
            elif self.pressed and self.press_allowed:
                self.pressed = False
                return True
        else:
            self.pressed = False
            if mouse_pressed:
                self.press_allowed = False
            else:
                self.press_allowed = True
        return False

    def draw(self, text):
        if text != self.text:
            self.text = text
            self.text_surf = self.font.render(text, True, self.text_color)
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.button_color_2
        else:
            self.color = self.button_color_1
        pygame.draw.rect(self.surface, self.color, self.body_rect, border_radius=self.border_radius)
        self.surface.blit(self.text_surf, self.text_rect)


button_start_stop = Button(screen, "Start", gui_font, 13 * S_HEIGHT // 12, 13 * S_HEIGHT // 36,
                           S_HEIGHT // 6, S_HEIGHT // 18, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR, S_HEIGHT // 72)
button_reset = Button(screen, "Reset", gui_font, 13 * S_HEIGHT // 12, 17 * S_HEIGHT // 36,
                      S_HEIGHT // 6, S_HEIGHT // 18, BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR, S_HEIGHT // 72)


class Slider:

    def __init__(self, surface, min_value, max_value, left_x, middle_y, width, bar_color, controller_color):
        self.surface = surface
        self.bar_color = bar_color
        self.controller_color = controller_color
        self.border_radius = width // 24
        self.circle_radius = self.border_radius * 2
        self.min_x, self.max_x = left_x + width // 12, left_x + 11 * width // 12
        self.slide_length = self.max_x - self.min_x
        self.controller_x = left_x + width // 12
        self.controller_y = middle_y
        self.min_value, self.max_value = min_value, max_value
        self.value_gap = self.max_value - self.min_value
        self.bar_rect = pygame.rect.Rect(left_x, middle_y - width // 24, width, width // 12)
        self.holding = False

    def mouse_collides_controller(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance = ((mouse_x - self.controller_x) ** 2 + (mouse_y - self.controller_y) ** 2) ** .5
        if distance < self.circle_radius:
            return True
        return False

    def movement(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if self.mouse_collides_controller():
                self.holding = True
            if self.holding:
                self.controller_x = mouse_pos[0]
            elif self.bar_rect.collidepoint(mouse_pos):
                self.controller_x = mouse_pos[0]
            if self.controller_x < self.min_x:
                self.controller_x = self.min_x
            elif self.controller_x > self.max_x:
                self.controller_x = self.max_x
        else:
            self.holding = False

    def calculate_value(self):
        return round(self.min_value + self.value_gap * (self.controller_x - self.min_x) / self.slide_length, 1)

    def set_controller_pos_from_value(self, value):
        self.controller_x = self.min_x + self.slide_length * (value - self.min_value) / self.value_gap
        if self.controller_x < self.min_x:
            self.controller_x = self.min_x
        elif self.controller_x > self.max_x:
            self.controller_x = self.max_x

    def draw(self):
        pygame.draw.rect(self.surface, self.bar_color, self.bar_rect, border_radius=self.border_radius)
        pygame.draw.circle(self.surface, self.controller_color,
                           (self.controller_x, self.controller_y), self.circle_radius)


slider_distance_2 = Slider(screen, S_HEIGHT // 20, S_HEIGHT // 5, 25 * S_HEIGHT // 24, 5 * S_HEIGHT // 36,
                           S_HEIGHT // 6, SLIDER_BAR_COLOR, SLIDER_CONTROLLER_COLOR)
slider_distance_3 = Slider(screen, S_HEIGHT // 20, S_HEIGHT // 5, 25 * S_HEIGHT // 24, S_HEIGHT // 4,
                           S_HEIGHT // 6, SLIDER_BAR_COLOR, SLIDER_CONTROLLER_COLOR)

slider_distance_2.set_controller_pos_from_value(S_HEIGHT // 10)
slider_distance_3.set_controller_pos_from_value(S_HEIGHT // 10)

slider_speed_1 = Slider(screen, 0, 4, 25 * S_HEIGHT // 24, 23 * S_HEIGHT // 36,
                        S_HEIGHT // 6, SLIDER_BAR_COLOR, SLIDER_CONTROLLER_COLOR)
slider_speed_2 = Slider(screen, 0, 4, 25 * S_HEIGHT // 24, 3 * S_HEIGHT // 4,
                        S_HEIGHT // 6, SLIDER_BAR_COLOR, SLIDER_CONTROLLER_COLOR)
slider_speed_3 = Slider(screen, 0, 4, 25 * S_HEIGHT // 24, 31 * S_HEIGHT // 36,
                        S_HEIGHT // 6, SLIDER_BAR_COLOR, SLIDER_CONTROLLER_COLOR)

slider_speed_1.set_controller_pos_from_value(1)
slider_speed_2.set_controller_pos_from_value(2)
slider_speed_3.set_controller_pos_from_value(4)


def convert_into_screen_coordinates(x, y):
    new_x = x + HALF_OF_GAME_AREA_WIDTH
    new_y = y + HALF_OF_GAME_AREA_WIDTH
    return new_x, new_y


alpha_1, alpha_2, alpha_3 = 90, 90, 90
coefficient_1, coefficient_2, coefficient_3 = 1, 1, 1

animate_on = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # # # # # # #

    if button_reset.is_clicked():
        alpha_1, alpha_2, alpha_3 = 90, 90, 90
        coefficient_1, coefficient_2, coefficient_3 = 1, 1, 1
        animate_on = False
    if button_start_stop.is_clicked():
        if animate_on:
            animate_on = False
        else:
            animate_on = True

    # distance #

    slider_distance_2.movement()
    slider_distance_3.movement()

    distance_2 = round(slider_distance_2.calculate_value())
    distance_3 = round(slider_distance_3.calculate_value())

    distance_2_text_surf = gui_font_large.render(str(distance_2), True, TEXT_COLOR)
    distance_2_text_rect = distance_2_text_surf.get_rect(center=distance_2_text_body_rect.center)
    distance_3_text_surf = gui_font_large.render(str(distance_3), True, TEXT_COLOR)
    distance_3_text_rect = distance_3_text_surf.get_rect(center=distance_3_text_body_rect.center)

    # speed #

    slider_speed_1.movement()
    slider_speed_2.movement()
    slider_speed_3.movement()

    speed_1 = slider_speed_1.calculate_value()
    speed_2 = slider_speed_2.calculate_value()
    speed_3 = slider_speed_3.calculate_value()

    speed_1_text_surf = gui_font_large.render(str(speed_1), True, TEXT_COLOR)
    speed_1_text_rect = speed_1_text_surf.get_rect(center=speed_text_body_rect_1.center)
    speed_2_text_surf = gui_font_large.render(str(speed_2), True, TEXT_COLOR)
    speed_2_text_rect = speed_2_text_surf.get_rect(center=speed_text_body_rect_2.center)
    speed_3_text_surf = gui_font_large.render(str(speed_3), True, TEXT_COLOR)
    speed_3_text_rect = speed_3_text_surf.get_rect(center=speed_text_body_rect_3.center)

    # # # # # # #

    if animate_on:

        alpha_1 -= speed_1
        if alpha_1 <= -90:
            alpha_1 = 90 + alpha_1 % -90
            if coefficient_1 == 1:
                coefficient_1 = -1
            else:
                coefficient_1 = 1

        alpha_2 -= speed_2
        if alpha_2 <= -90:
            alpha_2 = 90 + alpha_2 % -90
            if coefficient_2 == 1:
                coefficient_2 = -1
            else:
                coefficient_2 = 1

        alpha_3 -= speed_3
        if alpha_3 <= -90:
            alpha_3 = 90 + alpha_3 % -90
            if coefficient_3 == 1:
                coefficient_3 = -1
            else:
                coefficient_3 = 1

    t_1 = math.tan(alpha_1 * math.pi / 180)
    t_2 = math.tan(alpha_2 * math.pi / 180)
    t_3 = math.tan(alpha_3 * math.pi / 180)

    a_1 = int((distance_2 + distance_3) / (t_1 ** 2 + 1) ** .5) * coefficient_1
    a_2 = int(distance_2 / (t_2 ** 2 + 1) ** .5) * coefficient_2
    a_3 = int(distance_3 / (t_3 ** 2 + 1) ** .5) * coefficient_3

    b_1 = int(((distance_2 + distance_3) / (t_1 ** 2 + 1) ** .5) * t_1) * coefficient_1
    b_2 = int((distance_2 / (t_2 ** 2 + 1) ** .5) * t_2) * coefficient_2
    b_3 = int((distance_3 / (t_3 ** 2 + 1) ** .5) * t_3) * coefficient_3

    old_a_3, old_b_3 = a_3, b_3
    a_3 += a_2
    b_3 += b_2
    a_2 += a_1
    b_2 += b_1
    a_1 += old_a_3
    b_1 += old_b_3

    a_1, b_1 = convert_into_screen_coordinates(a_1, b_1)
    a_2, b_2 = convert_into_screen_coordinates(a_2, b_2)
    a_3, b_3 = convert_into_screen_coordinates(a_3, b_3)

    # # # # # # #

    screen.fill(BG_COLOR)

    pygame.draw.circle(screen, COLOR_1, (a_1, b_1), RADIUS_SIZE_1)
    pygame.draw.circle(screen, COLOR_2, (a_2, b_2), RADIUS_SIZE_2)
    pygame.draw.circle(screen, COLOR_3, (a_3, b_3), RADIUS_SIZE_3)

    pygame.draw.rect(screen, PANEL_COLOR, panel_rect)

    if animate_on:
        button_start_stop.draw("Stop")
    else:
        button_start_stop.draw("Start")
    button_reset.draw("Reset")

    slider_distance_2.draw()
    slider_distance_3.draw()
    screen.blit(distance_2_text_surf, distance_2_text_rect)
    screen.blit(distance_3_text_surf, distance_3_text_rect)

    slider_speed_1.draw()
    slider_speed_2.draw()
    slider_speed_3.draw()
    screen.blit(speed_1_text_surf, speed_1_text_rect)
    screen.blit(speed_2_text_surf, speed_2_text_rect)
    screen.blit(speed_3_text_surf, speed_3_text_rect)

    clock.tick(60)
    pygame.display.update()
