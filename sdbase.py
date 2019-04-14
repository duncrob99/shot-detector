import pygame
import numpy
import pygame.camera
import serial
import serial.tools.list_ports
import time
import thread
import math
import base_graphics as bg

pygame.init()
pygame.camera.init()

pygame.display.set_caption('Shot Detector')
clock = pygame.time.Clock()


class Detector:
    recent_shot_magnitudes = []
    recent_shot_coords = []
    shots = []
    translated_shots = []
    fired = 0
    calibration = (0, 20)
    threshold_pic = 0
    shot_coords = (0, 0)
    serial_data = ''
    calibrating = False
    window_transformation = [[0, 0, 1], [0, 0, 0]] # [[x, y, *z],[x, y, z]]
    trans_amnt = 2 # Amount to translate when transforming window
    scale_amnt = 0.005 # Amount to scale by
    rot_amnt = 0.01 # Degrees to rotate by

    def __init__(self, dims, num_saved_shots=20, cam="/dev/video0", serial_port="/dev/ttyACM0", mag_size=20,
                 num_mags=1, weapon_active=True):
        self.dims = dims
        for i in range(num_saved_shots):
            self.recent_shot_magnitudes.append(0)
            self.recent_shot_coords.append((0, 0))
        self.cam = pygame.camera.Camera(cam)
        self.cam.start()
        self.threshold_pic = self.take_frame()
        self.num_saved_shots = num_saved_shots
        self.raw_image = self.take_frame()
        self.thresholded_image = pygame.Surface(self.raw_image.get_size(), 0)
        pygame.transform.threshold(self.thresholded_image, self.raw_image,
        (0, 0, 0), (255, 255, 255), (255, 255, 255), 2)
        self.weapon_active = weapon_active
        self.serial_port = serial_port
        self.mag_size = mag_size
        self.num_mags = num_mags
        if weapon_active:
            self.serial_connection = serial.Serial(serial_port, 9600, timeout=0.045)
            self.wait_till_ready()
            self.serial_connection.write("magSize: " + str(mag_size) + ";")
            self.wait_till_ready()
            self.serial_connection.write("numMags: " + str(num_mags) + ";")
            self.wait_till_ready()
            self.serial_connection.write("start;")
        else:
            print "weapon inactive"

    def take_frame(self):
        return self.cam.get_image()

    def take_threshold(self):
        self.threshold_pic = self.take_frame()

    def calibrate(self):
        if self.weapon_active:
            self.serial_connection.write(b'calibrate;')
        self.calibrating = True

    def stop_calibration(self):
        if self.weapon_active:
            self.serial_connection.write(b'end calibration;')
        self.calibrating = False
    
    def reset(self):
        self.shots = []
        self.translated_shots = []
        self.shot_coords = (0, 0)
        if self.weapon_active:
                self.serial_connection = serial.Serial(self.serial_port, 9600, timeout=0.045)
                self.wait_till_ready()
                self.serial_connection.write("magSize: " + str(self.mag_size) + ";")
                self.wait_till_ready()
                self.serial_connection.write("numMags: " + str(self.num_mags) + ";")
                self.wait_till_ready()
                self.serial_connection.write("start;")


    def get_serial_threaded(self):
        if self.weapon_active:
            if self.serial_data == '':
                while True:
                    try:
                        self.serial_data = self.serial_connection.readline().decode("ascii")
                        break
                    except serial.serialutil.SerialException as exception:
                        print exception
                        quit()

    def tick(self, events, window_corners):
        if self.weapon_active:
            thread.start_new_thread(self.get_serial_threaded, ())
        # Get base image
        self.raw_image = self.take_frame()
        self.thresholded_image = pygame.Surface(self.raw_image.get_size(), 0)
        pygame.transform.threshold(self.thresholded_image, self.raw_image,
        (0, 0, 0), (255, 255, 255), (255, 255, 255), 2)

        thresholded_array = pygame.surfarray.pixels3d(self.thresholded_image)
#       self.shot_coords = numpy.unravel_index(numpy.argmax(thresholded_array), thresholded_array.shape)
        ## EXPERIMENTAL AVERAGE POSITION!
        max_indices = numpy.where(thresholded_array == thresholded_array.max())
        self.shot_coords = (numpy.mean(max_indices[0]), numpy.mean(max_indices[1]), numpy.mean(max_indices[2]))
#        print str(max_indices) + " = " + str(self.shot_coords_orig) + " => " + str(self.shot_coords)
        self.shot_coords_orig = (max_indices[0].max(), max_indices[1].max(), max_indices[2].max())
        ## END OF EXPERIMENTAL SECTION
        #self.shot_coords = (self.shot_coords[0] + self.calibration[0], self.shot_coords[1] + self.calibration[1])
        shot_magnitude = numpy.amax(thresholded_array)
        if not self.calibrating:
            # before_time = time.time()
            # serial_data = self.serial_connection.read(32).decode("ascii")
            # print(time.time() - before_time)
            if len(self.serial_data) > 0:
                if self.serial_data[:5] == "fired":
                    if self.fired == 0:
                        self.fired = 1
            self.serial_data = ''

            if self.fired > 0:
                self.fired += 1
            if self.fired == self.num_saved_shots / 2:
                best_shot = self.recent_shot_coords[numpy.argmax(self.recent_shot_magnitudes)]
                self.shots.append(best_shot)
                self.translated_shots.append(self.untranslate_pixel(best_shot, window_corners[0], window_corners[1]))
                self.fired = 0
                print "fired"

            self.recent_shot_magnitudes.insert(0, shot_magnitude)
            self.recent_shot_magnitudes.pop()
            self.recent_shot_coords.insert(0, self.shot_coords)
            self.recent_shot_coords.pop()
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.pos[1]:
                        self.calibrating = False
                        self.calibration = (self.calibration[0] + event.pos[0] - self.shot_coords[0],
                                            self.calibration[1] + event.pos[1] - self.shot_coords[1])
                        self.stop_calibration()

    def change_cam(self, new_cam):
        self.cam.stop()
        self.cam = pygame.camera.Camera(new_cam)
        self.cam.start()
        print self.cam.get_controls()

    def change_rifle_settings(self, mag_size, num_mags):
        if self.weapon_active:
            self.serial_connection.write("magSize: " + str(mag_size) + ";")
            self.serial_connection.write("numMags: " + str(num_mags) + ";")

    def wait_till_ready(self):
        if self.weapon_active:
            ready = False
            while not ready:
                self.serial_connection.write("ready?;")
                serial_data = self.serial_connection.read(32)
                if len(serial_data) > 0:
                    if serial_data == "ready":
                        ready = True


    def translate_pixel(self, coords, (display_width, display_height), final_size=(1, 1)):
        x, y = (0, 0)
        trans = self.window_transformation
        # Centre
        x = coords[0] - display_width/2
        y = coords[1] - display_height/2
        # Z-rotate
        x2 = x*math.cos(trans[1][2]) - y*math.sin(trans[1][2])
        y2 = x*math.sin(trans[1][2]) + y*math.cos(trans[1][2])
        x, y = x2, y2
        # X-rotate
        y = y*math.cos(trans[1][0]) - trans[0][2]*math.sin(trans[1][0])
        # Y-rotate
        x = x*math.cos(trans[1][1]) + trans[0][2]*math.sin(trans[1][1])
        # Z-translate
        x = (x * trans[0][2])
        y = (y * trans[0][2])
        # De-centre
        x = x + display_width/2
        y = y + display_height/2
        # X/Y-translate
        x = x+trans[0][0]
        y = y+trans[0][1]
        return (x, y)

    def untranslate_pixel(self, coords, (display_width, display_height), final_size=(1, 1)):
        x, y = (0, 0)
        trans = self.window_transformation
        # X/Y-translate
        x = coords[0] - trans[0][0]
        y = coords[1] - trans[0][1]
        # Centre
        x = x - display_width/2
        y = y - display_height/2
        # Z-translate
        x = x / trans[0][2]
        y = y / trans[0][2]
        # Y-rotate
        x = x*math.cos(-trans[1][1]) + trans[0][2]*math.sin(-trans[1][1])
        # X-rotate
        y = y*math.cos(-trans[1][0]) - trans[0][2]*math.sin(-trans[1][0])
        # Z-rotate
        x2 = x*math.cos(-trans[1][2]) - y*math.sin(-trans[1][2])
        y2 = x*math.sin(-trans[1][2]) + y*math.cos(-trans[1][2])
        x, y = x2, y2
        # De-centre
        x = x + display_width/2
        y = y + display_height/2
        return (x, y)


    def transform_window(self, direction):
        if pygame.key.get_pressed()[pygame.K_LCTRL]:
            trans = 1
            rot = self.rot_amnt/10
            scale = self.scale_amnt/10
        else:
            trans = self.trans_amnt
            rot = self.rot_amnt
            scale = self.scale_amnt
        if direction == 0:
            self.window_transformation[0][0] += trans
        elif direction == 1:
            self.window_transformation[0][1] += trans
        elif direction == 2:
            self.window_transformation[0][0] -= trans
        elif direction == 3:
            self.window_transformation[0][1] -= trans
        elif direction == 4:
            self.window_transformation[0][2] += scale
        elif direction == 5:
            self.window_transformation[0][2] -= scale
        elif direction == 6:
            self.window_transformation[1][0] += rot
        elif direction == 7:
            self.window_transformation[1][0] -= rot
        elif direction == 8:
            self.window_transformation[1][1] += rot
        elif direction == 9:
            self.window_transformation[1][1] -= rot
        elif direction == 10:
            self.window_transformation[1][2] += rot
        elif direction == 11:
            self.window_transformation[1][2] -= rot
        else:
            print("ERROR: Incorrect direction: " + str(direction))
            quit()

    def change_trans_amnt(self, amnt):
        self.trans_amnt += amnt

    def change_scale_amnt(self, amnt):
        self.trans_amnt += amnt
