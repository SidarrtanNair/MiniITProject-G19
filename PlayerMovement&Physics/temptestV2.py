import pygame
import sys
import os
from PlayerV4 import Player, gender_selection_screen, load_base_animations, load_action_animations, SCREEN_WIDTH, SCREEN_HEIGHT, BG, FPS, clock, script_dir
from Enemy import Enemy
from spritesheet import SpriteSheet

pygame.init()

# Game constants
PLAYER_MAX_HEALTH = 100
ENEMY_MAX_HEALTH = 100
ENEMY_DAMAGE = 10  # 10% of player health
PLAYER_DAMAGE = 50  # 50% of enemy health

def main():
    # Gender selection
    gender = gender_selection_screen()
    
    # Load player sprites based on gender
    if gender == 'male':
        base_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_spriteV8_flipped.png')).convert_alpha()
        attack_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_sprite_attack.png')).convert_alpha()
        mine_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/male_sprite_mine.png')).convert_alpha()
        action_sprite_width, action_sprite_height = 273, 182
        action_scale_factor = 0.3
    else:
        base_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_spriteV1_flipped.png')).convert_alpha()
        attack_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_sprite_attack.png')).convert_alpha()
        mine_sprite_image = pygame.image.load(os.path.join(script_dir,'Sprite_Img/female_sprite_mine.png')).convert_alpha()
        action_sprite_width, action_sprite_height = 232, 182
        action_scale_factor = 0.3

    # Load animations
    base_animation_list = load_base_animations(base_sprite_image)
    action_animation_list = load_action_animations(attack_sprite_image, mine_sprite_image, 
                                                 action_sprite_width, action_sprite_height, action_scale_factor)
    
    # Create player with fixed health
    player = Player(base_animation_list, action_animation_list, gender)
    player.current_health = PLAYER_MAX_HEALTH
    player.maximum_health = PLAYER_MAX_HEALTH
    player.health_ratio = player.maximum_health / player.health_bar_length
    
    # Load enemy sprite sheet
    try:
        enemy_sheet_img = pygame.image.load(os.path.join(script_dir,'Sprite_Img/enemy_sprite.png')).convert_alpha()
    except pygame.error:
        # Create a placeholder sprite sheet if file doesn't exist
        enemy_sheet_img = pygame.Surface((256, 32)).convert_alpha()
        enemy_sheet_img.fill((255, 0, 0))  # Red placeholder
        
    enemy_sheet = SpriteSheet(enemy_sheet_img)
    
    # Create sprite groups
    enemy_group = pygame.sprite.Group()
    
    # Game variables
    scroll = 0
    enemy_spawn_timer = 0
    enemy_spawn_cooldown = 180  # Spawn enemy every 3 seconds (60 FPS * 3)
    player_attack_pressed = False
    enemy_damage_cooldown = {}  # Track damage cooldown for each enemy
    
    # Game state
    game_over = False
    victory = False
    
    # Fonts for UI
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    
    run = True
    while run:
        clock.tick(FPS)
        
        if not game_over and not victory:
            # Handle input
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT]
            right = keys[pygame.K_RIGHT]
            jump = keys[pygame.K_SPACE]
            attack = keys[pygame.K_1]
            mine = keys[pygame.K_2]
            
            # Track attack key press (only trigger once per press)
            if attack and not player_attack_pressed:
                player_attack_pressed = True
            elif not attack:
                player_attack_pressed = False
            
            # Test health bar keys (for debugging)
            if keys[pygame.K_UP]:
                player.get_health(10)
            if keys[pygame.K_DOWN]:
                player.get_damage(10)
            
            # Move and update player
            player.move(left, right, jump, attack, mine)
            player.update()
            
            # Spawn enemies
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_cooldown:
                if len(enemy_group) < 3:  # Limit number of enemies on screen
                    enemy = Enemy(SCREEN_WIDTH, SCREEN_HEIGHT - 150, enemy_sheet, 2)
                    # Set enemy health
                    enemy.current_health = ENEMY_MAX_HEALTH
                    enemy.maximum_health = ENEMY_MAX_HEALTH
                    enemy_group.add(enemy)
                enemy_spawn_timer = 0
            
            # Update enemies
            enemy_group.update(scroll, SCREEN_WIDTH)
            
            # Collision detection between player and enemies
            for enemy in enemy_group:
                # Check collision
                if player.rect.colliderect(enemy.rect):
                    # Enemy deals damage to player on collision (with cooldown)
                    current_time = pygame.time.get_ticks()
                    enemy_id = id(enemy)
                    
                    if enemy_id not in enemy_damage_cooldown or current_time - enemy_damage_cooldown[enemy_id] > 1000:  # 1 second cooldown
                        player.get_damage(ENEMY_DAMAGE)
                        enemy_damage_cooldown[enemy_id] = current_time
                        print(f"Player takes {ENEMY_DAMAGE} damage! Health: {player.current_health}")
                
                # Player deals damage when attacking (key 1 pressed)
                if player_attack_pressed and player.action == 3:  # ATTACK state
                    # Check if player is close enough and facing the enemy
                    attack_range = 80  # Attack range in pixels
                    if abs(player.rect.centerx - enemy.rect.centerx) <= attack_range:
                        enemy.current_health -= PLAYER_DAMAGE
                        print(f"Enemy takes {PLAYER_DAMAGE} damage! Health: {enemy.current_health}")
                        
                        # Remove enemy if health <= 0
                        if enemy.current_health <= 0:
                            enemy.kill()
                            # Remove from damage cooldown dict
                            enemy_id = id(enemy)
                            if enemy_id in enemy_damage_cooldown:
                                del enemy_damage_cooldown[enemy_id]
                            print("Enemy defeated!")
            
            # Clean up damage cooldown for removed enemies
            active_enemy_ids = [id(enemy) for enemy in enemy_group]
            enemy_damage_cooldown = {k: v for k, v in enemy_damage_cooldown.items() if k in active_enemy_ids}
            
            # Check game over conditions
            if player.current_health <= 0:
                game_over = True
            elif len([enemy for enemy in enemy_group if hasattr(enemy, 'current_health')]) == 0:
                # All enemies defeated (this is just a simple win condition)
                pass
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_r and (game_over or victory):
                    # Restart game
                    main()
                    return
        
        # Draw everything
        screen = pygame.display.get_surface()
        screen.fill(BG)
        
        if not game_over and not victory:
            # Draw player
            player.draw(screen)
            
            # Draw enemies with health bars
            for enemy in enemy_group:
                screen.blit(enemy.image, enemy.rect)
                
                # Draw enemy health bar if it has health attribute
                if hasattr(enemy, 'current_health'):
                    health_bar_width = 60
                    health_ratio = enemy.current_health / enemy.maximum_health
                    bar_x = enemy.rect.centerx - health_bar_width // 2
                    bar_y = enemy.rect.top - 10
                    
                    # Background
                    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, health_bar_width, 6))
                    # Health
                    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_bar_width * health_ratio, 6))
                    # Border
                    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, health_bar_width, 6), 1)
            
            # Draw UI information
            ui_y = 10
            health_text = small_font.render(f"Player Health: {player.current_health}/{PLAYER_MAX_HEALTH}", True, (255, 255, 255))
            screen.blit(health_text, (10, ui_y))
            
            enemies_count = len(enemy_group)
            enemy_text = small_font.render(f"Enemies: {enemies_count}", True, (255, 255, 255))
            screen.blit(enemy_text, (10, ui_y + 30))
        
        elif game_over:
            # Game over screen
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            restart_text = small_font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        elif victory:
            # Victory screen
            victory_text = font.render("VICTORY!", True, (0, 255, 0))
            restart_text = small_font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
            
            screen.blit(victory_text, (SCREEN_WIDTH//2 - victory_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()