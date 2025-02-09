import pygame
from colors import Colors


def show_start_screen(screen):
    """Display the intro screen with an image and prompt to start the game."""
    # Initialize font module
    pygame.font.init()
    
    # Load the intro screen image from the sprites folder
    start_image = pygame.image.load('sprites/IntroScreen.png').convert()
    
    # Scale the image to 90% of the screen height
    scaled_height = int(screen.get_height() * 0.9)
    start_image = pygame.transform.scale(start_image, (screen.get_width(), scaled_height))
    
    # Setup font and render the prompt text
    font = pygame.font.SysFont(None, 48)
    text = font.render("Press any key to start", True, Colors.WHITE)
    
    # Create a rectangle for the text background covering the bottom 10% of the screen
    text_bg_rect = pygame.Rect(0, scaled_height, screen.get_width(), screen.get_height() - scaled_height)
    
    # Calculate text position centered in the bottom area
    text_rect = text.get_rect(center=(screen.get_width() // 2, scaled_height + (screen.get_height() - scaled_height) // 2))
    
    # Loop until user presses any key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        # Blit the intro image in the top 90% of the screen
        screen.blit(start_image, (0, 0))
        
        # Fill the bottom area with a black rectangle for better text visibility
        pygame.draw.rect(screen, Colors.BLACK, text_bg_rect)
        
        # Blit the prompt text on top of the black rectangle
        screen.blit(text, text_rect)
        
        pygame.display.flip()
