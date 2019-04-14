import pygame
import pygame.camera
import sdbase
import base_graphics as bg
from pygame.locals import *
import time
import sys
import getopt
import math

weapon_active = True


def calibrate_window(detector, objects=None):
    global window_corners
    exiting = False
    transformations = ((0, 0, 0), (0, 0, 0))
    update_blocks = [[0, 0, display_width, display_height]]
    available_cams = pygame.camera.list_cameras()
    # Deal with object manipulator
    if type(detector) == tuple:
        objects = detector[1]
        detector = detector[0]
    if objects is None:
        objects = bg.ObjectController()
    else:
        objects.del_all()
    objects.del_object("bottom_bar")
    objects.update()
    objects.add_object("bottom bar",
                       bg.SplitBar(display, display_height - bottom_bar_height, bottom_bar_height,
                                   ["Finish Calibration"], main_loop, [(detector, objects, window_corners)]))
#    objects.add_object("top left dot",
#                       bg.DraggableDot(display, window_corners[0][0], window_corners[0][1], 10,
#                                       bg.green, bg.bright_green,
#                                       bg.bright_blue))
#    objects.add_object("top right dot",
#                       bg.DraggableDot(display, window_corners[1][0], window_corners[1][1], 10,
#                                       bg.green, bg.bright_green,
#                                       bg.bright_blue))
#    objects.add_object("bottom right dot",
#                       bg.DraggableDot(display, window_corners[2][0], window_corners[2][1], 10,
#                                       bg.green, bg.bright_green,
#                                       bg.bright_blue))
#    objects.add_object("bottom left dot",
#                       bg.DraggableDot(display, window_corners[3][0], window_corners[3][1], 10,
#                                       bg.green, bg.bright_green,
#                                       bg.bright_blue))
    objects.add_object("camera_bar",
                       bg.SplitBar(display, 0, 20, available_cams, detector.change_cam, available_cams))

    # Arrows
    objects.add_object("up_arrow", bg.Arrow(display, display_width - 75, display_height - 100, 25, 25, 0, detector.transform_window, 3))
    objects.add_object("down_arrow", bg.Arrow(display, display_width - 75, display_height - 50, 25, 25, 180, detector.transform_window, 1))
    objects.add_object("right_arrow", bg.Arrow(display, display_width - 50, display_height - 75, 25, 25, 270, detector.transform_window, 0))
    objects.add_object("left_arrow", bg.Arrow(display, display_width - 100, display_height - 75, 25, 25, 90, detector.transform_window, 2))
    objects.add_object("bwd_arrow", bg.Arrow(display, display_width - 75, display_height - 135, 25, 25, 180, detector.transform_window, 4))
    objects.add_object("fwd_arrow", bg.Arrow(display, display_width - 75, display_height - 170, 25, 25, 0, detector.transform_window, 5)) 
    objects.add_object("+xrot_arrow", bg.Arrow(display, 50, display_height - 100, 25, 25, 0, detector.transform_window, 6))
    objects.add_object("-xrot_arrow", bg.Arrow(display, 50, display_height - 50, 25, 25, 180, detector.transform_window, 7))
    objects.add_object("+yrot_arrow", bg.Arrow(display, 75, display_height - 75, 25, 25, 270, detector.transform_window, 8))
    objects.add_object("-yrot_arrow", bg.Arrow(display, 25, display_height - 75, 25, 25, 90, detector.transform_window, 9))
    objects.add_object("+zrot_arrow", bg.Arrow(display, 75, display_height - 150, 25, 25, 270, detector.transform_window, 10))
    objects.add_object("-zrot_arrow", bg.Arrow(display, 25, display_height - 150, 25, 25, 90, detector.transform_window, 11))
    while not exiting:
#        window_corners = (objects.objects["top left dot"].coords, objects.objects["top right dot"].coords,
#                          objects.objects["bottom right dot"].coords, objects.objects["bottom left dot"].coords)
        events = pygame.event.get()
        window_corners = (detector.translate_pixel(base_window_corners[0], (display_width, display_height)), detector.translate_pixel(base_window_corners[1], (display_width, display_height)), detector.translate_pixel(base_window_corners[2], (display_width, display_height)), detector.translate_pixel(base_window_corners[3], (display_width, display_height)))
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        display.fill(bg.grey)

        detector.tick(events, window_corners)

	# Blit camera image
	image_width = detector.raw_image.get_width()
	image_height = detector.raw_image.get_height()
	height_ratio = (display_height - top_bar_height - bottom_bar_height) / float(image_height)
	width_ratio = display_width / float(image_width)
	scale_factor = min(height_ratio, width_ratio)
	scaled_image = pygame.transform.scale(detector.raw_image, (int(image_width * scale_factor), int(image_height * scale_factor)))

	if height_ratio < width_ratio:
		display.blit(scaled_image, ((display_width - scaled_image.get_width())/2, top_bar_height))
	else:
		display.blit(scaled_image, (0, top_bar_height + (display_height - top_bar_height - bottom_bar_height - scaled_image.get_height())/2))

	update_blocks.append((0, top_bar_height, display_width, display_height - bottom_bar_height))

        # Window Lines
        update_blocks.append(pygame.draw.polygon(display, bg.green, window_corners, 2))
        
        # Arrow Labels
        text_surface, rect = bg.text_objects("Translation", bg.small_text, bg.red)
        display.blit(text_surface, (display_width - 5 - text_surface.get_width(), display_height - 200))
        text_surface, rect = bg.text_objects("Rotation", bg.small_text, bg.red)
        display.blit(text_surface, (62 - text_surface.get_width()/2, display_height - 200))


        # Update all objects
        update_blocks.extend(objects.update(events))

        pygame.display.update(update_blocks)
        update_blocks = []


def view_shots(detector, objects=None):
    global window_corners
    if type(detector) == tuple:
        objects = detector[1]
        detector = detector[0]
    exiting = False
    update_blocks = [[0, 0, display_width, display_height]]
    objects.del_all()
    objects.add_object("bottom bar viewing shots",
                       bg.SplitBar(display, display_height - bottom_bar_height, bottom_bar_height,
                                   ["Finish"], main_loop, (detector, objects)))
    while not exiting:
        events = pygame.event.get()
        for event in events:  # Event management
            if event.type == QUIT:
                pygame.quit()
                detector.cam.stop()
                quit()
        display.fill(bg.grey)
        update_blocks.extend(objects.update(events))
        for i in detector.translated_shots:
            update_blocks.extend(bg.cross(display, i[0], i[1], 50, 50, 2, bg.red))
        update_blocks.extend(pygame.draw.polygon(display, bg.green, base_window_corners, 1))
        pygame.display.update()
        update_blocks = []


def end_pos_calibration(detector, objects=None):
    if type(detector) == tuple:
        objects = detector[1]
        detector = detector[0]
    detector.stop_calibration()
    main_loop(detector, objects)


def calibrate_pos(detector, objects=None):
    global window_corners
    if type(detector) == tuple:  # Ensure correct paramaters
        objects = detector[1]
        detector = detector[0]
    detector.calibrate()  # Begin Calibration
    available_cams = pygame.camera.list_cameras()
    exiting = False
    update_blocks = [[0, 0, display_width, display_height]]
    if objects is None:
        objects = bg.ObjectController()
    else:  # Remove extraneous objects
        objects.del_object("bottom_bar")
        objects.del_object("bottom bar")
        objects.update()
    objects.add_object("bottom bar",
                       bg.SplitBar(display, display_height - bottom_bar_height, bottom_bar_height,
                                   ["End calibration"], end_pos_calibration, (detector, objects)))
    objects.add_object("camera_bar",
                       bg.SplitBar(display, 0, 20, available_cams, detector.change_cam, available_cams))
    while not exiting:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                quit()
        display.fill(bg.grey)

        # Update detector
        detector.tick(events, window_corners)

	# Blit camera image
	image_width = detector.raw_image.get_width()
	image_height = detector.raw_image.get_height()
	height_ratio = (display_height - top_bar_height - bottom_bar_height) / float(image_height)
	width_ratio = display_width / float(image_width)
	scale_factor = min(height_ratio, width_ratio)
	scaled_image = pygame.transform.scale(detector.raw_image, (int(image_width * scale_factor), int(image_height * scale_factor)))

	if height_ratio < width_ratio:
		display.blit(scaled_image, ((display_width - scaled_image.get_width())/2, top_bar_height))
	else:
		display.blit(scaled_image, (0, top_bar_height + (display_height - top_bar_height - bottom_bar_height - scaled_image.get_height())/2))

	update_blocks.append((0, top_bar_height, display_width, display_height - bottom_bar_height))

        # Window lines
        for i in range(0, 4):
            update_blocks.append(
                pygame.draw.line(display, bg.green, window_corners[i], window_corners[(i + 1) % 4]))

        # Update
        update_blocks.extend(objects.update(events))
        update_blocks.extend(bg.cross(display, detector.shot_coords[0], detector.shot_coords[1], 10, 10, 1, bg.green))
        update_blocks.extend(bg.cross(display, detector.shot_coords[0], detector.shot_coords[1] + top_bar_height, 10, 10, 1, bg.blue))
        pygame.display.update(update_blocks)
        update_blocks = []


def main_loop(detector=None, objects=None):
    global window_corners
    winner = False
    if type(detector) == tuple:
        objects = detector[1]
        detector = detector[0]
    exiting = False
    update_blocks = [[0, 0, display_width, display_height]]
    available_cams = pygame.camera.list_cameras()
    if detector is None:
        detector = sdbase.Detector((display_width, display_height - top_bar_height - bottom_bar_height),
                                   serial_port="/dev/ttyACM0", weapon_active=weapon_active)
    if objects is None:
        objects = bg.ObjectController()
    else:
        objects.del_all()
    objects.add_object("bottom_bar", bg.SplitBar(display, display_height - bottom_bar_height, 20,
                                                 ["Take Threshold", "Calibrate position", "Calibrate window",
                                                  "View modified shots", "Reset"],
                                                 [detector.take_threshold, calibrate_pos,
                                                  calibrate_window, view_shots, detector.reset],
                                                 [None, (detector, objects), (detector, objects, window_corners),
                                                  (detector, objects), None]))
    objects.add_object("camera_bar",
                       bg.SplitBar(display, 0, 20, available_cams, detector.change_cam, available_cams))
    while not exiting:  # Main loop
        start_time = time.time()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                detector.cam.stop()
                quit()
            elif event.type == MOUSEBUTTONUP and not weapon_active:
                if top_bar_height <= event.pos[1] <= display_height - bottom_bar_height:
                    detector.shots.append(
                        (event.pos[0] + detector.calibration[0], event.pos[1] + detector.calibration[1]))
                    detector.translated_shots.append(detector.untranslate_pixel(
                        [event.pos[0] + detector.calibration[0], event.pos[1] + detector.calibration[1]],
                        (display_width, display_height)))
        display.fill(bg.grey)

        detector.tick(events, window_corners)

        # Check for test completion
        if len(detector.shots) >= 20:
            ave_dists = []
            for i in range(4):
                total_x = 0
                total_y = 0
                for j in range(5):
                    total_x += detector.translated_shots[4*i+j][0]
                    total_y += detector.translated_shots[4*i+j][1]
                ave_x = total_x/5
                ave_y = total_y/5
                total_dx = 0
                total_dy = 0
                for j in range(5):
                    total_dx += math.fabs(((detector.translated_shots[4*i+j][0]-ave_x)/factor)*sim_dist/dist)
                    total_dy += math.fabs(((detector.translated_shots[4*i+j][1]-ave_y)/factor)*sim_dist/dist)
                ave_dx = total_dx/5
                ave_dy = total_dy/5
                ave_dists.append(math.sqrt(ave_dx**2 + ave_dy**2))
            tot_ave_dists = 0
            for i in ave_dists:
                tot_ave_dists += i
            ave_ave_dists = tot_ave_dists/4
            mm_groupings = []
            for i in ave_dists:
                mm_groupings.append(i*1000)
            if ave_ave_dists <= 0:
                print "WINNER!!!"
                img = pygame.image.load('win_img.png')
                img = pygame.transform.scale(img, (display_width, display_height))
                img.convert_alpha()
                winner = True
                display.blit(img, (0, 0))
            print "groupings: " + str(mm_groupings)
            print "average grouping: " + str(ave_ave_dists * 1000)

        # Blit Video, figuring out max resolution first
	image_width = detector.raw_image.get_width()
	image_height = detector.raw_image.get_height()
	height_ratio = (display_height - top_bar_height - bottom_bar_height) / float(image_height)
	width_ratio = display_width / float(image_width)
	scale_factor = min(height_ratio, width_ratio)
	scaled_image = pygame.transform.scale(detector.raw_image, (int(image_width * scale_factor), int(image_height * scale_factor)))

	if height_ratio < width_ratio:
		display.blit(scaled_image, ((display_width - scaled_image.get_width())/2, top_bar_height))
	else:
		display.blit(scaled_image, (0, top_bar_height + (display_height - top_bar_height - bottom_bar_height - scaled_image.get_height())/2))

        update_blocks.append((0, top_bar_height, display_width, display_height - bottom_bar_height))

        # Crosshairs
        for i in detector.shots:
            update_blocks.extend(bg.cross(display, i[0], i[1], 50, 50, 2, bg.red))

        # Window lines
        for i in range(0, 4):
            update_blocks.append(
                pygame.draw.line(display, bg.green, window_corners[i], window_corners[(i + 1) % 4]))

        if winner:
            display.blit(img, (0, 0))
            update_blocks.append([0, 0, display_width, display_height])
        # Update
        update_blocks.extend(objects.update(events))
        pygame.display.update(update_blocks)
        update_blocks = []
        FPS = str(1 / (float(time.time()) - float(start_time)))


if __name__ == '__main__':
    args = sys.argv
    # python 20-Shot.py <width> <height> <real distance> <simulated distance>
    # All in metres
    try:
        width = float(args[1])
        height = float(args[2])
        dist = float(args[3])
        sim_dist = float(args[4])
	display_width = int(args[5])
	display_height = int(args[6])
    except IndexError:
        print "Using default arguments"
        width = 0.297
        height = 0.210
        dist = 5
        sim_dist = 200
	
	# Get current screen resolution
	screenInfo = pygame.display.Info()
	screenResolution = (screenInfo.current_w, screenInfo.current_h)
	
	display_width = screenResolution[0]
	display_height = screenResolution[1]
    except ValueError:
        if args[1] == "help" or args[1] == "h":
            print "python 20-Shot.py <width=0.297> <height=0.210> <real distance=5> <simulated distance=200> <display width=957> <display height = 758>"
            quit()

    # Window initialisation stuff
    factor = min((display_width)/width, (display_height-50)/height)
    true_height = height * factor
    true_width = width * factor
    top = (display_height - true_height) / 2
    bottom = (display_height + true_height) / 2
    left = (display_width - true_width) / 2
    right = (display_width + true_width) / 2
    base_window_corners = [[left, top], [right, top], [right, bottom], [left, bottom]]

    pygame.init()
    pygame.camera.init()

    top_bar_height = 20
    bottom_bar_height = 20

    display = pygame.display.set_mode((display_width, display_height),)
    pygame.display.set_caption('20 Shot Test')
    clock = pygame.time.Clock()

    window_corners = [[0, 0], [display_width, 0],
		      [display_width,display_height], [0, display_height]]
    base_window_corners = [[0, 0], [display_width, 0],
    		      [display_width,display_height], [0, display_height]]

    window_corners = [[left, top], [right, top], [right, bottom], [left, bottom]]

    main_loop()

