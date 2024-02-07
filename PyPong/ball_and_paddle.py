import pygame
import random
import math

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.initial_speed = 300
        self.speed = [self.initial_speed, self.initial_speed]
        self.rect = pygame.Rect(x, y, radius*2, radius*2)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self, delta_t):
        seconds = delta_t / 1000
        self.x += self.speed[0] * seconds
        self.y += self.speed[1] * seconds

        # Collision with the top boundary
        if self.rect.top < 0:
            self.y = 0 + self.radius  # Reposition inside the play area
            self.speed[1] = -self.speed[1]  # Invert the vertical speed

        # Collision with the bottom boundary
        elif self.rect.bottom > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.radius  # Reposition inside the play area
            self.speed[1] = -self.speed[1]  # Invert the vertical speed

        # Update rect position
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def get_position(self):
        return self.x, self.y

    def reset_position(self, x, y, direction):
        self.x = x
        self.y = y
        self.rect.center = (x, y)

        # Randomize the starting angle of the ball
        min_angle = 0  # Minimum angle in degrees
        max_angle = 60  # Maximum angle in degrees

        # Randomize starting direction
        direction_x = 1 if direction == 'left' else -1
        direction_y = random.choice([-1, 1])  # Up or Down

        # Generate a random angle within specified range
        angle = random.uniform(min_angle, max_angle)

        # Calculate x and y components of the speed based on the angle
        self.speed[0] = direction_x * self.initial_speed * math.cos(math.radians(angle))
        self.speed[1] = direction_y * self.initial_speed * math.sin(math.radians(angle))

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 0
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self, speed, delta_t):
        seconds = delta_t / 1000
        self.y += speed * seconds
        self.speed = speed
        self.y = max(self.y, 0)  # Top boundary
        self.y = min(self.y, WINDOW_HEIGHT - self.height)  # Bottom boundary
        self.rect.y = self.y

    def get_position(self):
        return self.x, self.y