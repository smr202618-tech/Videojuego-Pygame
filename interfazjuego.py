import pygame
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer

# Load music files
pygame.mixer.music.load('./assets/audio/music1.mp3')
pygame.mixer.music.load('./assets/audio/music2.mp3')

# Function to start main game music
def start_main_game_music():
    pygame.mixer.music.play(-1)  # Loop the main music indefinitely

# Function to start minigame music
def start_minigame_music():
    pygame.mixer.music.play(-1)  # Loop the minigame music indefinitely

# Rest of your code

# Main function
if __name__ == '__main__':
    start_main_game_music() 
    main()  # Assuming you have a main game loop defined
