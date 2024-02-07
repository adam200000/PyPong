import pygame
import math
from ball_and_paddle import Ball, Paddle

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

class PongGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("My Pong Game")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.ball = Ball(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 10, (0, 255, 0))
        self.paddle1 = Paddle(20, WINDOW_HEIGHT // 2, 10, 60, (255, 255, 255))
        self.paddle2 = Paddle(WINDOW_WIDTH - 20 - 10, WINDOW_HEIGHT // 2, 10, 60, (255, 255, 255))
        self.running = True
        self.is_single_player = True
        self.player1_score = 0
        self.player2_score = 0

    def run(self):
        while self.running:
            delta_t = self.clock.tick(60)
            self.handle_input(delta_t)
            self.update_game_state(delta_t)
            self.render()
            pygame.display.flip()
        pygame.quit()

    def handle_input(self, delta_t):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

        self.is_single_player = self.handle_player_input(delta_t)
    
    def handle_player_input(self, delta_t):
        speed_per_second = 350
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.paddle1.move(-speed_per_second, delta_t)
        if keys[pygame.K_s]:
            self.paddle1.move(speed_per_second, delta_t)

        if self.is_single_player:
            if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                self.is_single_player = False

        if not self.is_single_player:
            if keys[pygame.K_UP]:
                self.paddle2.move(-speed_per_second, delta_t)
            if keys[pygame.K_DOWN]:
                self.paddle2.move(speed_per_second, delta_t)
        
        return self.is_single_player
    
    def handle_ai_movement(self, delta_t):
        ai_max_speed = 400
        distance_threshold = 5
        engage_distance_threshold = 30
        ball_center = self.ball.get_position()[1]
        paddle_center = self.paddle2.get_position()[1] + self.paddle2.height / 2
        distance = ball_center - paddle_center

        if abs(distance) > engage_distance_threshold:
            direction = 1 if distance > 0 else -1
            speed = ai_max_speed * direction if abs(distance) > distance_threshold else 0
            self.paddle2.move(speed, delta_t)
        else:
            self.paddle2.move(0, delta_t)

    def update_game_state(self, delta_t):
        self.ball.move(delta_t)
        if self.is_single_player:
            self.handle_ai_movement(delta_t)

        # Handle collisions
        self.handle_collision(self.ball, self.paddle1, delta_t)
        self.handle_collision(self.ball, self.paddle2, delta_t)

        # Reset ball and update scores
        if self.ball.x < 0:  # Ball went off the left side, player 2 scores
            self.player2_score += 1
            self.ball.reset_position(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 'left')  # Toward player 2
        elif self.ball.x > WINDOW_WIDTH:  # Ball went off the right side, player 1 scores
            self.player1_score += 1
            self.ball.reset_position(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 'right')  # Toward player 1
    
    def check_collision(self, ball, paddle):
        if self.ball.rect.colliderect(paddle.rect):
            dx = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
            dy = (ball.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
            return dx, dy
        else:
            return 0, 0
    
    def handle_collision(self, ball, paddle, delta_t):
        dx, dy = self.check_collision(ball, paddle)
        if dx or dy:
            # Side collision condition
            if (ball.rect.left <= paddle.rect.right and ball.rect.right >= paddle.rect.left) or \
            (ball.rect.right >= paddle.rect.left and ball.rect.left <= paddle.rect.right):
                # Reverse horizontal direction and increase speed slightly
                speed_increase_factor = 1.1
                ball.speed[0] = -ball.speed[0] * speed_increase_factor
                
                # Ensure horizontal speed stays within min and max bounds
                max_horizontal_speed = 1000
                min_horizontal_speed = 200
                ball.speed[0] = max(min_horizontal_speed, min(abs(ball.speed[0]), max_horizontal_speed)) * \
                                (-1 if ball.speed[0] < 0 else 1)

                # Vertical speed adjustment based on hit position
                hit_pos = (ball.rect.centery - paddle.rect.y) / paddle.rect.height
                center_offset = (hit_pos - 0.5) * 2  # -1 (top edge) to +1 (bottom edge), 0 (center)
                deflection_factor = 0.5  # Adjust this value as needed
                ball.speed[1] += center_offset * deflection_factor * max_horizontal_speed
                
                # Cap the vertical speed
                max_vertical_speed = 500
                ball.speed[1] = max(-max_vertical_speed, min(ball.speed[1], max_vertical_speed))

            # Top or bottom edge collision condition
            elif (ball.rect.bottom <= paddle.rect.top and dy < 0) or \
                (ball.rect.top >= paddle.rect.bottom and dy > 0):
                # Reverse vertical direction
                ball.speed[1] = -ball.speed[1]

            # Apply paddle speed to ball's vertical movement
            ball.speed[1] += paddle.speed * (delta_t / 1000.0)
            
            # Adjust paddle hit impact (steeper angles for edge hits) - only occurs on side collisions
            if dx and not dy:
                max_angle = 75  # Degrees for maximum deflection angle
                base_speed = 300  # Speed to calculate deflection
                if hit_pos < 0.2 or hit_pos > 0.8:  # Edge hits
                    angle = max_angle
                else:  # Center hits
                    angle = max_angle * abs(center_offset)  # Smaller angle for closer to center

                # Calculate the new vertical speed based on the angle
                ball.speed[1] = math.copysign(base_speed * math.sin(math.radians(angle)), ball.speed[1])

    def render(self):
        self.screen.fill((0, 0, 0))
        self.ball.draw(self.screen)
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)

        # Draw scores
        font = pygame.font.Font(None, 74)
        text = font.render(str(self.player1_score), 1, (200, 200, 200))
        self.screen.blit(text, (210,10))
        text = font.render(str(self.player2_score), 1, (200, 200, 200))
        self.screen.blit(text, (380,10))

        # Show
        pygame.display.flip()

if __name__ == '__main__':
    game = PongGame()
    game.run()