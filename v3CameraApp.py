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
        pygame.display.set_caption("Raspberry Pi Camera Controls")
        
        self.camera = PiCamera()
        self.camera.resolution = (800, 480)
        self.camera.framerate = 30
        
        self.running = True
        
        # Adjustable settings with [current_value, min_value, max_value]
        self.adjustments = {
            "brightness": [50, 0, 100],
            "contrast": [0, -100, 100],
            "exposure_time": [0, 0, 800],
            "iso": [100, 100, 800],
            "adjust_red": [1.0, 0.5, 2.0],
            "adjust_blue": [1.0, 0.5, 2.0]
        }
        
        # Create buttons for adjustments
        self.adjustment_buttons = {}
        x_offset = 620  # Move buttons to the right side of the screen
        y_offset = 50  # Adjust vertical positioning slightly higher
        for label in self.adjustments.keys():
            self.adjustment_buttons[label] = {
                "minus": pygame.Rect(x_offset, y_offset, 40, 25),
                "plus": pygame.Rect(x_offset + 120, y_offset, 40, 25),
                "display": pygame.Rect(x_offset + 50, y_offset, 60, 25)
            }
            y_offset += 40
        
        self.buttons = {
            "snapshot": pygame.Rect(620, y_offset, 150, 40)
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
                        self.handle_adjustment_buttons(event.pos)
            
            self.update_camera_view()
            self.draw_buttons()
            self.draw_adjustment_buttons()
            pygame.display.flip()
        
        pygame.quit()
    
    def update_camera_view(self):
        if not hasattr(self, 'frame_buffer'):
            self.frame_buffer = np.empty((480, 800, 3), dtype=np.uint8)  # Create once
        
        self.camera.capture(self.frame_buffer, format='rgb', use_video_port=True)
        frame = np.rot90(self.frame_buffer)
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
    
    def draw_adjustment_buttons(self):
        font = pygame.font.Font(None, 24)
        colors = (200, 200, 200)
        
        for label, buttons in self.adjustment_buttons.items():
            pygame.draw.rect(self.screen, colors, buttons["minus"])
            pygame.draw.rect(self.screen, colors, buttons["plus"])
            pygame.draw.rect(self.screen, (100, 100, 100), buttons["display"])
            
            minus_text = font.render("-", True, (0, 0, 0))
            plus_text = font.render("+", True, (0, 0, 0))
            value_text = font.render(str(self.adjustments[label][0]), True, (255, 255, 255))
            label_text = font.render(label.replace('_', ' ').title(), True, (255, 255, 255))
            
            self.screen.blit(minus_text, (buttons["minus"].x + 20, buttons["minus"].y + 5))
            self.screen.blit(plus_text, (buttons["plus"].x + 20, buttons["plus"].y + 5))
            self.screen.blit(value_text, (buttons["display"].x + 15, buttons["display"].y + 5))
            self.screen.blit(label_text, (buttons["minus"].x - 120, buttons["minus"].y + 5))
    
    def handle_button_click(self, position):
        if self.buttons["snapshot"].collidepoint(position):
            self.take_snapshot()
    
    def handle_adjustment_buttons(self, position):
        for label, buttons in self.adjustment_buttons.items():
            if buttons["minus"].collidepoint(position):
                self.adjustments[label][0] = max(self.adjustments[label][0] - 1, self.adjustments[label][1])
            elif buttons["plus"].collidepoint(position):
                self.adjustments[label][0] = min(self.adjustments[label][0] + 1, self.adjustments[label][2])
            self.apply_camera_settings()
            print(label.title() + " Set: " + str(self.adjustments[label][0]))
    
    def apply_camera_settings(self):
        self.camera.brightness = self.adjustments["brightness"][0]
        self.camera.contrast = self.adjustments["contrast"][0]
        self.camera.iso = self.adjustments["iso"][0]
        self.camera.awb_gains = (self.adjustments["adjust_red"][0], self.adjustments["adjust_blue"][0])
        self.camera.shutter_speed = int(self.adjustments["exposure_time"][0] * 1000)
    
    def take_snapshot(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "snapshot_" + timestamp + ".jpg"
        self.camera.capture(filename)
        print("Saved: " + filename)

if __name__ == "__main__":
    CameraApp()
