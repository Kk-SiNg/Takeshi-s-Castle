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

# ============================================
# UDP Setup
# ============================================
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)

# ============================================
# Pygame Setup
# ============================================
pygame.init()
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ESP8266 RC Car Controller")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 48)
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

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
    screen.fill(DARK_GRAY)
    
    # Title
    title = title_font.render("RC CAR CONTROL", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Connection status
    status_color = GREEN if connection_status == "CONNECTED" else RED
    status_text = small_font.render(f"Status: {connection_status}", True, status_color)
    screen.blit(status_text, (20, 70))
    
    # Target info
    target_text = small_font.render(f"Target: {ESP_IP}:{ESP_PORT}", True, WHITE)
    screen.blit(target_text, (20, 95))
    
    # Packets sent
    packets_text = small_font.render(f"Packets: {packets_sent}", True, WHITE)
    screen.blit(packets_text, (WIDTH - 150, 70))
    
    # Current command display
    cmd_bg = pygame.Rect(WIDTH//2 - 150, 130, 300, 60)
    pygame.draw.rect(screen, BLACK, cmd_bg, border_radius=10)
    pygame.draw.rect(screen, GREEN, cmd_bg, 3, border_radius=10)
    
    cmd_text = font.render(f"CMD: {current_command}", True, GREEN)
    screen.blit(cmd_text, (WIDTH//2 - cmd_text.get_width()//2, 145))
    
    # Speed display
    speed_text = small_font.render(f"Speed: {current_speed}/1023", True, WHITE)
    screen.blit(speed_text, (WIDTH//2 - speed_text.get_width()//2, 200))
    
    # Speed bar
    bar_width = 300
    bar_height = 20
    bar_x = WIDTH//2 - bar_width//2
    bar_y = 230
    
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
    filled_width = int((current_speed / 1023) * bar_width)
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, filled_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Draw directional arrows
    center_x = WIDTH // 2
    center_y = 340
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
    guide_y = 450
    guide_texts = [
        "W/↑: Forward  |  S/↓: Backward  |  A/←: Left  |  D/→: Right  |  +: Speed↑  |  -: Speed↓  |  ESC: Quit"
    ]
    
    guide = small_font.render(guide_texts[0], True, GRAY)
    screen.blit(guide, (WIDTH//2 - guide.get_width()//2, guide_y))

# ============================================
# Main Loop
# ============================================
def main():
    global current_command, current_speed
    
    running = True
    last_command = None
    
    print("=" * 60)
    print("ESP8266 RC Car Controller (Pygame)")
    print("=" * 60)
    print(f"Target: {ESP_IP}:{ESP_PORT}")
    print("Controls:")
    print("  W/↑  - Forward")
    print("  S/↓  - Backward")
    print("  A/←  - Left")
    print("  D/→  - Right")
    print("  +/=  - Increase Speed")
    print("  -/_  - Decrease Speed")
    print("  ESC  - Quit")
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
        command = None
        command_name = "STOPPED"
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            command = "F"
            command_name = "FORWARD"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            command = "B"
            command_name = "BACKWARD"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            command = "L"
            command_name = "LEFT"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            command = "R"
            command_name = "RIGHT"
        else:
            command = "S"
            command_name = "STOPPED"
        
        # Send command only if it changed (reduce spam)
        if command != last_command:
            if send_command(command):
                current_command = command_name
                log_command(command, command_name)
                print(f"→ {command_name}")
            last_command = command
        
        # Draw UI
        draw_ui()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate (30 FPS = ~33ms between commands)
        clock.tick(30)
    
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