import time
import pytesseract
from PIL import ImageGrab
import cv2
import numpy as np
import pygame
from pathlib import Path
import os
import configparser
import pyautogui
import win10toast
import ctypes
import tkinter as tk
from tkinter import messagebox
import random

class DesktopMonitor:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Load configuration
        self.config = self.load_config()
        
        # Set up paths
        self.project_dir = Path(__file__).parent
        self.target_image_path = self.project_dir / self.config['Files']['image_name']
        self.alert_sound_path = self.project_dir / self.config['Files']['mp3_name']
        
        # Load the reference image
        self.reference_image = cv2.imread(str(self.target_image_path))
        if self.reference_image is None:
            raise FileNotFoundError(f"Reference image not found at {self.target_image_path}")
            
        # Load the alert sound
        if not self.alert_sound_path.exists():
            raise FileNotFoundError(f"Alert sound not found at {self.alert_sound_path}")
            
        # Initialize Tesseract
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def load_config(self):
        """Load configuration from config.ini"""
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        
        config.read(config_path)
        return config
    
    def capture_screen(self):
        """Capture the entire screen and convert to CV2 format"""
        screenshot = ImageGrab.grab()
        opencv_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return opencv_img
    
    def find_image(self, screen_img):
        """Try to find the reference image in the screenshot"""
        # Use template matching to find the image
        result = cv2.matchTemplate(screen_img, self.reference_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Get threshold from config
        threshold = float(self.config['Settings']['match_threshold'])
        return max_val > threshold
    
    def play_alert(self):
        """Play the alert sound"""
        pygame.mixer.music.load(str(self.alert_sound_path))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        
    def monitor(self):
        """Main monitoring loop"""
        interval = int(self.config['Settings']['check_interval'])
        print(f"Starting desktop monitoring. Looking for image: {self.target_image_path}")
        print(f"Will check every {interval} seconds")
        
        # Notify user and wait for 30 seconds before starting
        toaster = win10toast.ToastNotifier()
        toaster.show_toast("Desktop Monitor", "Will start monitoring in 30 seconds", duration=10)
        time.sleep(30)
        toaster.show_toast("Desktop Monitor", "Started monitoring", duration=10)

        while True:
            try:
                screen_img = self.capture_screen()
                image_found = self.find_image(screen_img)
                
                if not image_found:
                    print("Target image not found! Playing alert...")
                    self.play_alert()
                    
                    # Present a popup asking if the user wants to continue
                    result = self.show_alert()
                    if result:  # User clicked "Yes"
                        print("User chose to continue monitoring.")
                        continue
                    else:  # User clicked "No"
                        print("User chose to stop monitoring.")
                        break
                else:
                    print("Target image found on screen, refreshing")
                    pyautogui.press('f5')  # Press F5 to refresh
                
                interval = random.randint(10, 20)
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(30)

    def show_alert(self):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        result = messagebox.askyesno("Desktop Monitor", "Target image not found! Do you want to continue monitoring?")
        root.destroy()
        return result

if __name__ == "__main__":
    try:
        monitor = DesktopMonitor()
        monitor.monitor()
    except Exception as e:
        print(f"Failed to start monitoring: {e}")