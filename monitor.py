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
from winotify import Notification, audio
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton
import sys
import random
import time

def print_line(message):
    print(time.strftime(f"%Y-%m-%d %H:%M:%S :: {message}"))

def stop_music():
    """Stop the alert sound"""
    pygame.mixer.music.stop()

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / 'config.ini'

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    config.read(config_path)
    return config

def capture_screen():
    """Capture the entire screen and convert to CV2 format"""
    screenshot = ImageGrab.grab()
    opencv_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return opencv_img

def show_pop_up():
    app = QApplication.instance() or QApplication(sys.argv)

    msg = QMessageBox()
    msg.setWindowTitle("Desktop Monitor")
    msg.setText("Target image not found! Do you want to continue monitoring?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    # Show Stop Music only if Music is playing
    if pygame.mixer.music.get_busy():
        msg.addButton("Stop Music", QMessageBox.ButtonRole.ActionRole)
    result = msg.exec()
    if pygame.mixer.music.get_busy():
        stop_music()
    if result == QMessageBox.StandardButton.No or result == QMessageBox.StandardButton.Yes:
        return result
    return show_pop_up()

def show_app_mode_pop_up():
    app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setWindowTitle("Desktop Monitor")
    msg.setText("Please select application mode!")
    standardModeButton = msg.addButton("Standard", QMessageBox.ButtonRole.ActionRole)
    aggressiveModeButton = msg.addButton("Agressive", QMessageBox.ButtonRole.ActionRole)
    # msg.setStandardButtons(standardModeButton | aggressiveModeButton)
    result = msg.exec()
    if (msg.clickedButton() == standardModeButton):
        return 'standard'
    return 'aggressive'


def show_toast_notification(message):
    toast = Notification(
        app_id="Auto Refresh",
        title="Auto Refresh",
        msg=message
    )
    toast.set_audio(audio.Reminder, loop=False)
    toast.show()


class DesktopMonitor:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Load configuration
        self.config = load_config()
        
        # Set up paths
        self.project_dir = Path(__file__).parent
        self.target_image_path = self.project_dir / self.config['Files']['image_name']
        self.button_image_path = self.project_dir / self.config['Files']['button_image_name']
        self.alert_sound_path = self.project_dir / self.config['Files']['mp3_name']
        
        # Load the reference image
        self.reference_image = cv2.imread(str(self.target_image_path))
        if self.reference_image is None:
            raise FileNotFoundError(f"Reference image not found at {self.target_image_path}")
        self.button_image_path = cv2.imread(str(self.button_image_path))
        if self.button_image_path is None:
            raise FileNotFoundError(f"Button image not found at {self.button_image_path}")
            
        # Load the alert sound
        if not self.alert_sound_path.exists():
            raise FileNotFoundError(f"Alert sound not found at {self.alert_sound_path}")
            
        # Initialize Tesseract
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def find_image(self, screen_img):
        """Try to find the reference image in the screenshot"""
        # Use template matching to find the image
        result = cv2.matchTemplate(screen_img, self.reference_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Get threshold from config
        threshold = float(self.config['Settings']['match_threshold'])
        print_line(f"Image matched '{max_val}' percent on screen for threshold {threshold}")
        return max_val > threshold
    
    def find_location_of_button(self, screen_img):
        try:
            result = cv2.matchTemplate(screen_img, self.button_image_path, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            threshold = float(self.config['Settings']['match_threshold'])
            if max_val >= threshold:
                location = max_loc
            else:
                raise ValueError("Button image not found on screen")
            return location
        except Exception as e:
            print_line(f"Error finding location of button: {e}")
            return None
    
    def click_button(self, screen_img):
        """Get Location of button"""
        location = self.find_location_of_button(screen_img)
        """Click the button on the screen"""
        if location is not None:
            x, y = location
            x += 50 # Move to the center of the button
            y += 20 # Move to the center of the button
            pyautogui.moveTo(x, y, duration=0.7, tween=pyautogui.easeInOutQuad)
            pyautogui.click(x, y)
            print_line(f"Clicked button at location {x}, {y}")
        else:
            print_line("Button location not found")
        
    def play_music(self):
        """Play the alert sound"""
        pygame.mixer.music.load(str(self.alert_sound_path))
        pygame.mixer.music.play()
        
    def random_wait(self):
        average_wait_seconds = int(self.config['Settings']['check_interval'])
        min_value = int(average_wait_seconds * 0.7)
        max_value = int(average_wait_seconds * 1.3)
        interval = random.randint(min_value, max_value)  # Random interval between checks
        print_line(f"Waiting for {interval} seconds")
        time.sleep(interval)
    
    def refresh_screen(self):
        pyautogui.press('f5')  # Press F5 to refresh
        time.sleep(10)

    def monitor(self):
        """Main monitoring loop"""
        print_line("Choose application mode")
        appMode = show_app_mode_pop_up()
        print_line(f"Selected application mode: {appMode}")
        print_line(f"Starting desktop monitoring. Looking for image: {self.target_image_path}")
        
        # Notify user and wait for 30 seconds before starting
        show_toast_notification("Will start monitoring in 30 seconds")

        while True:
            try:
                self.random_wait()
                self.refresh_screen()  # Press F5 to refresh
                screen_img = capture_screen()
                image_found = self.find_image(screen_img)

                if not image_found:
                    print_line("Target image not found! Playing alert...")
                    self.play_music()
                    # Click on button if in aggressive mode
                    if(appMode == 'aggressive'):
                       self.click_button(screen_img)

                    # Present a popup asking if the user wants to continue
                    result = show_pop_up()
                    if result == QMessageBox.StandardButton.Yes:  # User clicked "Yes"
                        print_line("User chose to continue monitoring.")
                        # Notify user and wait for 30 seconds before starting
                        show_toast_notification("Will start monitoring again in 30 seconds")
                        time.sleep(30)
                    if result == QMessageBox.StandardButton.No:  # User clicked "No"
                        print_line("User chose to stop monitoring.")
                        break

                else:
                    print_line("Target image found on screen, refreshing")
                    if self.config.getboolean('Settings', 'notify_on_refresh'):
                        show_toast_notification("Refreshed the screen.")

            except KeyboardInterrupt:
                print_line("\nMonitoring stopped by user")
                break
            except Exception as exception:
                print_line(f"An error occurred: {exception}")
                raise exception

if __name__ == "__main__":
    try:
        monitor = DesktopMonitor()
        monitor.monitor()
    except Exception as e:
        print_line(f"Failed to start monitoring: {e}")