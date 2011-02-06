# Written by Sudharshan 'Sup3rkiddo' S
# released under WTFPL

# I know a simple mirror would suffice. But screw mirrors.
# The sound file taken from http://www.freesound.org/samplesViewSingle.php?id=72557

import datetime
from datetime import datetime
from optparse import OptionParser


NOTIFICATIONS = True
try:
    import pynotify
    pynotify.init("Boss Alert")
except:
    print "Pynotify not installed. Notifications will be disabled"
    NOTIFICATIONS = False
    

import pygame
import pygame.camera
import pygame.font
import pygame.mixer

from pygame.locals import *


class BossAlert(object):

    def __init__(self, soundpath=None):
        self.reference_color = None
        size = (640,480)        
        pygame.camera.init()
            
        self.display = pygame.display.set_mode(size, 0)
        cams = pygame.camera.list_cameras()
        assert cams, "No Cameras detected. Get a mirror instead"

        self.notify = None
        if NOTIFICATIONS:
            self.notify = pynotify.Notification("BossAlert", "Your Boss just walked down the hallway. Back to work")
            self.notify.set_urgency(pynotify.URGENCY_CRITICAL)
            self.notify.set_timeout(5)
        
        self.cam = pygame.camera.Camera(cams[0], size, "RGB24")
        self.cam.start()
        print "Initializing Camera"
        
        self.surface = pygame.surface.Surface(size, 0, self.display)
        self.font = pygame.font.SysFont("Courier New", 30, bold=True)

        self.sound = None
        if soundpath:
            print "Init pygame mixer"
            pygame.mixer.init()
            self.sound = pygame.mixer.Sound(soundpath)
        self.refresh()

        
    def check_movement(self, rect, threshold=30):
        """Really dumb way to check for movement.
        Find out the average color within the rectangular area. If it differs from
        the reference colour by a certain threshold, we have movement.
        Simple but effective in cases where the background colour is uniform.
        """
        color = pygame.transform.average_color(self.surface, rect)
        diff = [a - b for a,b in zip(color, self.reference_color)]
        for d in diff:
            if abs(d) > threshold:
                return True
        return False


    def get_image(self, surface):
        success = self.cam.query_image()
        if success:
            return self.cam.get_image(surface)
        return None

    
    def refresh(self):
        snapshot = self.get_image(self.surface)

        # Change the position of the rectangular window here. Or position your webcam accordingly
        rect = pygame.draw.rect(snapshot, (255, 0, 0), (10, 40, 100, 100), 2)
        
        if not self.reference_color:
            self.reference_color = pygame.transform.average_color(snapshot, rect)
        if snapshot:
            # Play a sound and pop up a desktop notification if any motion is detected within the rect window
            if self.check_movement(rect):
                print "Movement detected at ", datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                if not pygame.mixer.get_busy() and self.sound:
                    self.sound.play(loops=-1)
                if NOTIFICATIONS:
                    self.notify.show()
                snapshot.fill((255, 0, 0), rect)
                ren = self.font.render("Boss Alert", 30, (255, 0, 0))
                snapshot.blit(ren, (400, 200))
            else:
                if self.sound:
                    self.sound.fadeout(500) 
        self.display.blit(snapshot, (0,0))
        self.surface = snapshot
        pygame.display.flip()

        
    def startloop(self):
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT:
                    self.cam.stop()
                    exit()
            self.refresh()


if __name__ == '__main__':
    pygame.init()
    oparser = OptionParser()
    oparser.add_option("-s", "--sound", dest="soundpath",
                       help="Path to the Sound file to be played when movement is detected", metavar="FILE")
    oparser.add_option("-x", "--disable-notifications", dest="no_notify", action="store_true", default=False,
                       help="Disable desktop notifications (Need pynotify to be installed)")
    (options, args) = oparser.parse_args()
    NOTIFICATIONS = not options.no_notify
    alert = BossAlert(soundpath=options.soundpath)
    alert.startloop()
