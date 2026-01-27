import socket
import pygame
import sys

# ============================================
# CONFIGURATION - CHANGE THIS!
# ============================================
ESP_IP = "10.67.214.228"  # ← PUT YOUR ESP8266 IP HERE
ESP_PORT = 4210

# ============================================
# Colors
# ============================================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

# ============================================
# UDP Setup
# ============================================
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)

# ============================================
# Pygame Setup
# ============================================
pygame.init()
WIDTH, HEIGHT = 600, 550  # Increased height for team logo
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ESP8266 RC Car Controller - TAKESHI'S TROOPS")
clock = pygame.time.Clock()

# Fonts
team_font = pygame.font.Font(None, 56)  # Large font for team name
title_font = pygame.font.Font(None, 48)
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Load team logo as full background
try:
    team_logo = pygame.image.load("takeshi_castle.png")  # Save your image as takeshi_castle.png
    # Scale logo to fill entire window
    team_logo = pygame.transform.scale(team_logo, (WIDTH, HEIGHT))
    # Set transparency (0-255, where 255 is opaque, 128 is 50% transparent)
    team_logo.set_alpha(100)  # Adjust this value for more/less transparency (lower = more transparent)
    logo_loaded = True
except:
    logo_loaded = False
    print("Warning: Could not load team logo. Place 'takeshi_castle.png' in the same folder.")

# ============================================
# State Variables
# ============================================
current_command = "STOPPED"
current_speed = 512
command_history = []
max_history = 10
packets_sent = 0
connection_status = "CONNECTING..."

# ============================================
# Functions
# ============================================
def send_command(command):
    """Send UDP command to ESP8266"""
    global packets_sent, connection_status
    try:
        sock.sendto(command.encode(), (ESP_IP, ESP_PORT))
        packets_sent += 1
        connection_status = "CONNECTED"
        return True
    except Exception as e:
        connection_status = f"ERROR: {e}"
        return False

def log_command(cmd, description):
    """Add command to history"""
    global command_history
    command_history.append(f"{description}")
    if len(command_history) > max_history:
        command_history.pop(0)

def draw_button(text, x, y, width, height, active=False):
    """Draw a button on screen"""
    color = GREEN if active else GRAY
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 3, border_radius=10)
    
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surf, text_rect)

def draw_arrow(direction, x, y, size, active=False):
    """Draw directional arrow"""
    color = YELLOW if active else BLUE
    
    if direction == "UP":
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
    elif direction == "DOWN":
        points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
    elif direction == "LEFT":
        points = [(x - size, y), (x + size, y - size), (x + size, y + size)]
    elif direction == "RIGHT":
        points = [(x + size, y), (x - size, y - size), (x - size, y + size)]
    
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, WHITE, points, 3)

def draw_ui():
    """Draw the user interface"""
    # Fill background with dark color
    screen.fill(DARK_GRAY)
    
    # Draw full background logo (translucent)
    if logo_loaded:
        screen.blit(team_logo, (0, 0))
    
    # Semi-transparent overlay for better text readability
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)  # Adjust for darker/lighter overlay
    overlay.fill(DARK_GRAY)
    screen.blit(overlay, (0, 0))
    
    # Team Name Banner
    banner_height = 80
    banner_surface = pygame.Surface((WIDTH, banner_height))
    banner_surface.set_alpha(200)  # Semi-transparent banner
    banner_surface.fill((20, 20, 20))
    screen.blit(banner_surface, (0, 0))
    pygame.draw.rect(screen, GOLD, (0, banner_height - 3, WIDTH, 3))  # Gold underline
    
    # Team Name
    team_name = team_font.render("TAKESHI'S TROOPS", True, GOLD)
    team_name_rect = team_name.get_rect(center=(WIDTH//2, 40))
    
    # Add shadow effect for team name
    shadow = team_font.render("TAKESHI'S TROOPS", True, BLACK)
    screen.blit(shadow, (team_name_rect.x + 3, team_name_rect.y + 3))
    screen.blit(team_name, team_name_rect)
    
    # Title
    title = title_font.render("RC CAR CONTROL", True, WHITE)
    title_shadow = title_font.render("RC CAR CONTROL", True, BLACK)
    screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 2, 102))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    # Connection status
    status_color = GREEN if connection_status == "CONNECTED" else RED
    status_text = small_font.render(f"Status: {connection_status}", True, status_color)
    screen.blit(status_text, (20, 160))
    
    # Target info
    target_text = small_font.render(f"Target: {ESP_IP}:{ESP_PORT}", True, WHITE)
    screen.blit(target_text, (20, 185))
    
    # Packets sent
    packets_text = small_font.render(f"Packets: {packets_sent}", True, WHITE)
    screen.blit(packets_text, (WIDTH - 150, 160))
    
    # Current command display
    cmd_bg = pygame.Rect(WIDTH//2 - 150, 220, 300, 60)
    pygame.draw.rect(screen, BLACK, cmd_bg, border_radius=10)
    pygame.draw.rect(screen, GREEN, cmd_bg, 3, border_radius=10)
    
    cmd_text = font.render(f"CMD: {current_command}", True, GREEN)
    screen.blit(cmd_text, (WIDTH//2 - cmd_text.get_width()//2, 235))
    
    # Speed display
    speed_text = small_font.render(f"Speed: {current_speed}/1023", True, WHITE)
    screen.blit(speed_text, (WIDTH//2 - speed_text.get_width()//2, 290))
    
    # Speed bar
    bar_width = 300
    bar_height = 20
    bar_x = WIDTH//2 - bar_width//2
    bar_y = 320
    
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
    filled_width = int((current_speed / 1023) * bar_width)
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, filled_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Draw directional arrows
    center_x = WIDTH // 2
    center_y = 430
    spacing = 80
    
    # Get key states
    keys = pygame.key.get_pressed()
    
    # Up arrow
    draw_arrow("UP", center_x, center_y - spacing, 20, 
               keys[pygame.K_UP] or keys[pygame.K_w])
    
    # Down arrow
    draw_arrow("DOWN", center_x, center_y + spacing, 20, 
               keys[pygame.K_DOWN] or keys[pygame.K_s])
    
    # Left arrow
    draw_arrow("LEFT", center_x - spacing, center_y, 20, 
               keys[pygame.K_LEFT] or keys[pygame.K_a])
    
    # Right arrow
    draw_arrow("RIGHT", center_x + spacing, center_y, 20, 
               keys[pygame.K_RIGHT] or keys[pygame.K_d])
    
    # Controls guide
    guide_y = 520
    guide_texts = [
        "W/↑: Forward  |  S/↓: Backward  |  A/←: Left  |  D/→: Right  |  +: Speed↑  |  -: Speed↓  |  ESC: Quit"
    ]
    
    guide = small_font.render(guide_texts[0], True, WHITE)
    screen.blit(guide, (WIDTH//2 - guide.get_width()//2, guide_y))

# ============================================
# Main Loop
# ============================================
def main():
    global current_command, current_speed
    
    running = True
    last_command = None
    
    print("=" * 60)
    print("ESP8266 RC Car Controller - TAKESHI'S TROOPS")
    print("=" * 60)
    print(f"Target: {ESP_IP}:{ESP_PORT}")
    print("=" * 60)
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Speed control on key press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    current_speed = min(1023, current_speed + 100)
                    send_command("+")
                    log_command("+", f"Speed increased to {current_speed}")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    current_speed = max(200, current_speed - 100)
                    send_command("-")
                    log_command("-", f"Speed decreased to {current_speed}")
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get current key states
        keys = pygame.key.get_pressed()
        
        # Determine command based on keys
        command = "S"  # Default to stop
        command_name = "STOPPED"


        if keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            command = "R"
            command_name = "UPPER_LEFT"
        elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            command = "Y"
            command_name = "UPPER_RIGHT"
        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            command = "C"
            command_name = "DOWN_LEFT"
        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            command = "B"
            command_name = "DOWN_RIGHT"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            command = "F"
            command_name = "FORWARD"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            command = "K"
            command_name = "BACKWARD"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            command = "L"
            command_name = "LEFT"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            command = "E"
            command_name = "RIGHT"
        
        
        # Always send command (removed change check for better responsiveness)
        if send_command(command):
            current_command = command_name
            # Only log and print when command changes to reduce console spam
            if command != last_command:
                log_command(command, command_name)
                print(f"→ {command_name}")
            last_command = command
        
        # Draw UI
        draw_ui()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate (20 FPS = 50ms between commands)
        clock.tick(20)
    
    # Cleanup
    send_command("S")  # Stop car before exiting
    pygame.quit()
    sock.close()
    print("\n✓ Controller stopped.")

# ============================================
# Run Program
# ============================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        pygame.quit()
        sock.close()
        sys.exit(0)