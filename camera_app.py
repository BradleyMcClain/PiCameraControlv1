import cv2
import time
import numpy as np
from picamera import PiCamera
import pygame
import os

class CameraApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 480))
        pygame.display.set_caption("Raspberry Pi Camera Viewer")
        
        self.camera = PiCamera()
        self.camera.resolution = (800, 480)
        self.camera.framerate = 30
        
        self.running = True
        self.agc_enabled = True
        self.manual_gain = 1.0
        
        # Create buttons
        self.buttons = {
            "snapshot": pygame.Rect(10, 400, 150, 50),
            "toggle_agc": pygame.Rect(170, 400, 150, 50),
            "increase_gain": pygame.Rect(330, 400, 150, 50),
            "decrease_gain": pygame.Rect(490, 400, 150, 50)
        }
        
        self.main_loop()
    
    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.handle_button_click(event.pos)
            
            self.update_camera_view()
            self.draw_buttons()
            pygame.display.flip()
        
        pygame.quit()
    
    def update_camera_view(self):
        frame = np.empty((480, 800, 3), dtype=np.uint8)
        self.camera.capture(frame, format='rgb', use_video_port=True)
        frame = np.rot90(frame)
        frame = np.flipud(frame)
        frame = pygame.surfarray.make_surface(frame)
        self.screen.blit(frame, (0, 0))
    
    def draw_buttons(self):
        font = pygame.font.Font(None, 30)
        colors = (200, 200, 200)
        
        for label, rect in self.buttons.items():
            pygame.draw.rect(self.screen, colors, rect)
            text = font.render(label.replace('_', ' ').title(), True, (0, 0, 0))
            self.screen.blit(text, (rect.x + 10, rect.y + 15))
    
    def handle_button_click(self, position):
        if self.buttons["snapshot"].collidepoint(position):
            self.take_snapshot()
        elif self.buttons["toggle_agc"].collidepoint(position):
            self.toggle_agc()
        elif self.buttons["increase_gain"].collidepoint(position):
            self.set_manual_gain(self.manual_gain + 0.5)
        elif self.buttons["decrease_gain"].collidepoint(position):
            self.set_manual_gain(self.manual_gain - 0.5)
    
    def take_snapshot(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "snapshot_" + timestamp + ".jpg"
        self.camera.capture(filename)
        print("Saved: " + filename)
    
    def toggle_agc(self):
        self.agc_enabled = not self.agc_enabled
        self.camera.exposure_mode = 'auto' if self.agc_enabled else 'off'
        print("AGC " + ("Enabled" if self.agc_enabled else "Disabled"))
    
    def set_manual_gain(self, value):
        if not self.agc_enabled:
            self.manual_gain = max(1.0, min(value, 16.0))  # Clamp gain between 1 and 16
            self.camera.iso = int(self.manual_gain * 100)
            print("Manual Gain Set: " + str(self.manual_gain))

if __name__ == "__main__":
    CameraApp()
