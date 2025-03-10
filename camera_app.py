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
        self.exposure_time = 0
        self.iso = 100
        self.brightness = 50
        self.contrast = 0
        
        # Create buttons
        self.buttons = {
            "snapshot": pygame.Rect(10, 400, 150, 50),
            "toggle_agc": pygame.Rect(170, 400, 150, 50)
        }
        
        # Create sliders
        self.sliders = {
            "gain": [pygame.Rect(330, 400, 150, 10), 1.0, 16.0],
            "exposure": [pygame.Rect(330, 420, 150, 10), 0, 800],
            "iso": [pygame.Rect(330, 440, 150, 10), 100, 800],
            "brightness": [pygame.Rect(330, 460, 150, 10), 0, 100],
            "contrast": [pygame.Rect(330, 480, 150, 10), -100, 100]
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
                        self.handle_slider_adjust(event.pos)
            
            self.update_camera_view()
            self.draw_buttons()
            self.draw_sliders()
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
    
    def draw_sliders(self):
        colors = (200, 200, 200)
        
        for label, (rect, min_val, max_val) in self.sliders.items():
            pygame.draw.rect(self.screen, colors, rect)
            slider_x = int(rect.x + (getattr(self, label) - min_val) / (max_val - min_val) * rect.width)
            pygame.draw.circle(self.screen, (0, 0, 255), (slider_x, rect.y + 5), 5)
    
    def handle_button_click(self, position):
        if self.buttons["snapshot"].collidepoint(position):
            self.take_snapshot()
        elif self.buttons["toggle_agc"].collidepoint(position):
            self.toggle_agc()
    
    def handle_slider_adjust(self, position):
        for label, (rect, min_val, max_val) in self.sliders.items():
            if rect.collidepoint(position):
                value = min_val + (position[0] - rect.x) / rect.width * (max_val - min_val)
                setattr(self, label, round(value))
                self.apply_camera_settings()
                print(label.title() + " Set: " + str(getattr(self, label)))
    
    def apply_camera_settings(self):
        if not self.agc_enabled:
            self.camera.iso = self.iso
            self.camera.shutter_speed = self.exposure_time * 1000
        self.camera.brightness = self.brightness
        self.camera.contrast = self.contrast
    
    def take_snapshot(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "snapshot_" + timestamp + ".jpg"
        self.camera.capture(filename)
        print("Saved: " + filename)
    
    def toggle_agc(self):
        self.agc_enabled = not self.agc_enabled
        self.camera.exposure_mode = 'auto' if self.agc_enabled else 'off'
        print("AGC " + ("Enabled" if self.agc_enabled else "Disabled"))

if __name__ == "__main__":
    CameraApp()
