import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load music
main_music = 'music1.mp3'
minigame_music = 'music2.mp3'

# Function to start background music for the main game
def start_main_game_music():
    pygame.mixer.music.load(main_music)
    pygame.mixer.music.play(-1)  # Looping indefinitely

# Function to start background music for mini-games
def start_minigame_music():
    pygame.mixer.music.load(minigame_music)
    pygame.mixer.music.play(-1)  # Looping indefinitely

# Remember to stop the music when exiting
# pygame.mixer.music.stop()  # Call this at the appropriate exit point
