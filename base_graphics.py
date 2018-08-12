import pygame
from pygame.locals import *
import math

pygame.init()
black = (0, 0, 0)
white = (255, 255, 255)
grey = (255/2, 255/2, 255/2)
red = (200, 0, 0)
green = (0, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
blue = (0, 0, 200)
bright_blue = (0, 0, 255)
small_text = pygame.font.Font("freesansbold.ttf", 20)


def text_objects(text, font, colour):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def button(surface, msg, x, y, w, h, ic, ac, action=None, param=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(surface, ac, (x, y, w, h))
        if click[0] == 1 and action:
            if param is not None:
                action(param)
            else:
                action()
    else:
        pygame.draw.rect(surface, ic, (x, y, w, h))

    text_surf, text_rect = text_objects(msg, small_text, black)
    text_rect.center = ((x+(w/2)), (y+(h/2)))
    surface.blit(text_surf, text_rect)
    return pygame.Rect(x, y, w, h)


def rotate(x, y, rot, centre_x=0, centre_y=0):
    rel_x = x-centre_x
    rel_y = y-centre_y
    return (rel_x*math.cos(rot)-rel_y*math.sin(rot)+x, rel_x*math.sin(rot)+rel_y*math.cos(rot)+y)


def cross(surface, x, y, w, h, thickness=0, colour=green):
    rect1 = pygame.draw.line(surface, colour, (x - w/2, y), (x + w/2, y), thickness)
    rect2 = pygame.draw.line(surface, colour, (x, y - h/2), (x, y + h/2), thickness)
    return rect1, rect2


def split_bar(surface, y, h, texts, functions=None, params=None):
    rects = []
    for index, i in enumerate(texts):
        text = i
        x = index * surface.get_width() / len(texts)
        w = surface.get_width() / len(texts)
        if (index % 2) == 0:
            ic = green
            ac = bright_green
        else:
            ic = red
            ac = bright_red
        if isinstance(functions, list) and isinstance(params, list):
            rects.append(button(surface, text, x, y, w, h, ic, ac, functions[index], params[index]))
        elif not isinstance(functions, list) and isinstance(params, list):
            rects.append(button(surface, text, x, y, w, h, ic, ac, functions, params[index]))
        elif isinstance(functions, list) and not isinstance(params, list):
            rects.append(button(surface, text, x, y, w, h, ic, ac, functions[index], params))
        else:
            rects.append(button(surface, text, x, y, w, h, ic, ac, functions, params))
    return rects


class Arrow:
    exists = True
    hover = False
    click = False

    def __init__(self, surface, x, y, w, h, rot, functions=None, params=None):
        self.surface = surface
        self.y = y
        self.x = x
        self.w = w
        self.h = h
        self.rot = rot
        self.function = functions
        self.param = params
        self.orig_img = pygame.image.load('arrow_up.png')
        self.orig_img = pygame.transform.scale(self.orig_img, (w, h))
        self.orig_img = pygame.transform.rotate(self.orig_img, rot)
        self.orig_img.convert_alpha()

    def update(self, event, mouse_pos):
        if self.exists:
            # Event management
            if event == None:
                pass
            elif event.type == MOUSEMOTION:
                if self.orig_img.get_rect().left <= mouse_pos[0] - self.x <= self.orig_img.get_rect().right and self.orig_img.get_rect().top <= mouse_pos[1] - self.y <= self.orig_img.get_rect().bottom:
                    self.hover = True
                else:
                    self.hover = False
            elif event.type == MOUSEBUTTONDOWN:
                if self.hover:
                    self.click = True
                else:
                    self.click = False
            elif event.type == MOUSEBUTTONUP:
                # if self.hover and self.click:
                #     if self.function is not None:
                #         if self.param is not None:
                #             self.function(self.param)
                #         else:
                #             self.function()
                #     else:
                #         print "No function for button press!"
                self.click = False

            if self.hover and self.click:
                if self.function is not None:
                    if self.param is not None:
                        self.function(self.param)
                    else:
                        self.function()
                else:
                    print "No function for button press!"
            # Blitting correct image onto surface
            img = self.orig_img.copy()
            if self.click:
                colour_surface(self.orig_img, red)
            elif self.hover:
                colour_surface(self.orig_img, green)
            else:
                colour_surface(self.orig_img, blue)
            rect = self.surface.blit(self.orig_img, (self.x, self.y))

        else:
            rect = (0, 0, 0, 0)
        return rect

    def apoptose(self):
        self.exists = False
        return (self.x, self.y, self.w, self.h)


def colourise(image, newColor):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()

    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    return image


def colour_surface(surface, (red, green, blue)):
    arr = pygame.surfarray.pixels3d(surface)
    arr[:,:,0] = red
    arr[:,:,1] = green
    arr[:,:,2] = blue


class SplitBar:
    buttons = []
    exists = True

    def __init__(self, surface, y, h, texts, functions=None, params=None):
        self.surface = surface
        self.y = y
        self.height = h
        self.texts = texts
        self.functions = functions
        self.params = params
        for index, text in enumerate(texts):
            x = index * self.surface.get_width() / len(texts)
            w = self.surface.get_width() / len(texts)
            if (index % 2) == 0:
                inactive_colour = green
                active_colour = bright_green
            else:
                inactive_colour = red
                active_colour = bright_red
            clicked_colour = bright_blue

            if isinstance(functions, list) and isinstance(params, list):
                self.buttons.append(
                    Button(surface, text, x, y, w, h, inactive_colour, active_colour, clicked_colour, functions[index],
                           params[index]))
            elif not isinstance(functions, list) and isinstance(params, list):
                self.buttons.append(
                    Button(surface, text, x, y, w, h, inactive_colour, active_colour, clicked_colour, functions,
                           params[index]))
            elif isinstance(functions, list) and not isinstance(params, list):
                self.buttons.append(
                    Button(surface, text, x, y, w, h, inactive_colour, active_colour, clicked_colour, functions[index],
                           params))
            else:
                self.buttons.append(
                    Button(surface, text, x, y, w, h, inactive_colour, active_colour, clicked_colour, functions,
                           params))

    def update(self, event, mouse_pos):
        if self.exists:
            rects = []
            for butt in self.buttons:
                rects.append(butt.update(event, mouse_pos))
            return rects

    def apoptose(self):
        self.exists = False
        rects = []
        for btn in self.buttons:
            rects.append(btn.apoptose())
        return rects


class DraggableDot:
    def __init__(self, surface, x, y, r, inactive_colour, active_colour, clicked_colour):
        self.surface = surface
        self.x = x
        self.y = y
        self.r = r
        self.hover = False
        self.click = False
        self.inactive_colour = inactive_colour
        self.active_colour = active_colour
        self.clicked_colour = clicked_colour
        self.exists = True
        self.coords = (self.x, self.y)

    def update(self, event, mouse_pos):
        self.coords = (self.x, self.y)
        if self.exists:
            if event is None:
                pass
            elif event.type == MOUSEMOTION:
                if math.sqrt(math.pow(mouse_pos[0] - self.x, 2) + math.pow(mouse_pos[1] - self.y, 2)) <= self.r:
                    self.hover = True
                else:
                    self.hover = False
                if self.click:
                    self.x, self.y = mouse_pos
            elif event.type == MOUSEBUTTONDOWN:
                if self.hover:
                    self.click = True
            elif event.type == MOUSEBUTTONUP:
                if self.click and self.hover:
                    self.click = False

            if self.click:
                pygame.draw.circle(self.surface, self.clicked_colour, (self.x, self.y), self.r)
            elif self.hover:
                pygame.draw.circle(self.surface, self.active_colour, (self.x, self.y), self.r)
            else:
                pygame.draw.circle(self.surface, self.inactive_colour, (self.x, self.y), self.r)

            return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
        else:
            return pygame.Rect(0, 0, 0, 0)

    def apoptose(self):
        pygame.draw.circle(self.surface, grey, (self.x, self.y), self.r)
        self.exists = False
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)


class Button:
    hover = False
    click = False
    exists = True

    def __init__(self, surface, msg, x, y, width, height, inactive_colour, active_colour, clicked_colour, action=None,
                 param=None):
        self.surface = surface
        self.msg = msg
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inactive_colour = inactive_colour
        self.active_colour = active_colour
        self.clicked_colour = clicked_colour
        self.action = action
        self.param = param

    def update(self, event, mouse_pos):
        if self.exists:
            if event is None:
                pass
            elif event.type == MOUSEMOTION:
                if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
                    self.hover = True
                else:
                    self.hover = False
            elif event.type == MOUSEBUTTONDOWN:
                if self.hover:
                    self.click = True
            elif event.type == MOUSEBUTTONUP:
                if self.hover and self.click:
                    # try:
                    #    self.action(self.param)
                    # except TypeError:
                    #    self.action()
                    if self.param is not None:
                        self.action(self.param)
                    else:
                        self.action()
                self.click = False

            if self.click:
                pygame.draw.rect(self.surface, self.clicked_colour, (self.x, self.y, self.width, self.height))
            elif self.hover:
                pygame.draw.rect(self.surface, self.active_colour, (self.x, self.y, self.width, self.height))
            else:
                pygame.draw.rect(self.surface, self.inactive_colour, (self.x, self.y, self.width, self.height))

            text_surf, text_rect = text_objects(self.msg, small_text, black)
            text_rect.center = ((self.x + (self.width / 2)), (self.y + (self.height / 2)))
            self.surface.blit(text_surf, text_rect)

            return pygame.Rect(self.x, self.y, self.width, self.height)
        else:
            return pygame.Rect(0, 0, 0, 0)

    def apoptose(self):
        pygame.draw.rect(self.surface, grey, (self.x, self.y, self.width, self.height))
        self.exists = False
        return pygame.Rect(self.x, self.y, self.width, self.height)


class ObjectController:
    objects = {}
    to_delete = []

    def __init__(self):
        pass

    def update(self, events=[]):
        rects = []
        mouse_pos = (0, 0)
        for key in self.to_delete:                                                               # Delete marked objects
            try:
                rect = self.objects[key].apoptose()
                if type(rect) == list:
                    rects.extend(rect)
                else:
                    rects.append(rect)
                self.objects.pop(key)
            except KeyError:
                print "Object " + key + " couldn't be deleted because it doesn't exist"
        self.to_delete = []
        if events != []:
            for event in events:
                if event.type == MOUSEMOTION:
                    mouse_pos = event.pos
                for obj in self.objects:
                    rect = self.objects[obj].update(event, mouse_pos)
                    if type(rect) == list:
                        rects.extend(rect)
                    else:
                        rects.append(rect)
        else:
            for obj in self.objects:
                rect = self.objects[obj].update(None, mouse_pos)
                if type(rect) == list:
                    rects.extend(rect)
                else:
                    rects.append(rect)
        return rects

    def add_object(self, key, obj):
        self.objects[key] = obj

    def del_object(self, key):
        self.to_delete.append(key)

    def del_all(self):
        keys = []
        for key in self.objects:
            keys.append(key)
        for key in keys:
            self.objects[key].apoptose()
            self.objects.pop(key)
        # for key in self.objects:
        #    self.to_delete.append(key)
        #    print "delete: " + str(key)
