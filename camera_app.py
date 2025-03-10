import cv2
import time
import numpy as np
from picamera import PiCamera
import pygame
import os

class CameraApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Raspberry Pi Camera Viewer")
        
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 30
        
        self.running = True
        self.agc_enabled = True
        self.manual_gain = 1.0
        
        self.main_loop()
    
    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # Take Screenshot
                        self.take_snapshot()
                    elif event.key == pygame.K_g:  # Toggle AGC
                        self.toggle_agc()
                    elif event.key == pygame.K_UP:  # Increase Gain
                        self.set_manual_gain(self.manual_gain + 0.5)
                    elif event.key == pygame.K_DOWN:  # Decrease Gain
                        self.set_manual_gain(self.manual_gain - 0.5)
            
            self.update_camera_view()
            pygame.display.flip()
        
        pygame.quit()
    
    def update_camera_view(self):
        frame = np.empty((480, 640, 3), dtype=np.uint8)
        self.camera.capture(frame, format='rgb', use_video_port=True)
        frame = np.rot90(frame)
        frame = np.flipud(frame)
        frame = pygame.surfarray.make_surface(frame)
        self.screen.blit(frame, (0, 0))
    
    def take_snapshot(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"snapshot_{timestamp}.jpg"
        self.camera.capture(filename)
        print(f"Saved: {filename}")
    
    def toggle_agc(self):
        self.agc_enabled = not self.agc_enabled
        self.camera.exposure_mode = 'auto' if self.agc_enabled else 'off'
        print(f"AGC {'Enabled' if self.agc_enabled else 'Disabled'}")
    
    def set_manual_gain(self, value):
        if not self.agc_enabled:
            self.manual_gain = max(1.0, min(value, 16.0))  # Clamp gain between 1 and 16
            self.camera.iso = int(self.manual_gain * 100)
            print(f"Manual Gain Set: {self.manual_gain}")

if __name__ == "__main__":
    CameraApp()
