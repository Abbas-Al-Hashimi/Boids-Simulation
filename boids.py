from typing import Any
import pygame
import random
import math

SCREEN_X = 1024
SCREEN_Y = 768
BG_FILENAME = "pictures/background.jpg"
OBSTICAL = "pictures/obstical.jpg"
BOID = "pictures/boid.png"
HOIK = "pictures/hoik.png"

pygame.init()
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
background = pygame.image.load(BG_FILENAME)
background = pygame.transform.scale(background, (SCREEN_X, SCREEN_Y))
background.convert()

obstical = pygame.image.load(OBSTICAL).convert_alpha()
hoik = pygame.image.load(HOIK).convert_alpha()
boid = pygame.image.load(BOID).convert_alpha()


class Vector:
    def __init__(self, x, y): # initializes the vector with values x and y 
        self.x = x
        self.y = y
        

    def __add__(self, other): #this method adds vectors objects togheter(self + other)
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other): # this method subtracts one vector object from another(self - other)
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):# this method multiplies a vector by a scalar value(self * scalar)
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):# divides a vector by a scalar value(self / scalar)
        return Vector(self.x / scalar, self.y / scalar)

class moving_objects(pygame.sprite.Sprite): 

    def __init__(self): #Initializes moving_objects
        super().__init__()
    def rule1(self, boids): #Calculates the perceived center of the group of objects
        perceived_center = Vector(0, 0)

        for other_boid in boids:
            if other_boid != self:
                perceived_center += Vector(other_boid.rect.centerx, other_boid.rect.centery)  

        perceived_center /= len(boids) - 1

        return (perceived_center - Vector(self.rect.centerx, self.rect.centery)) / 100 # Returns a vector indicating the adjustment needed for alignment.

    def rule2(self, boids): #Calculates a vector to avoid collisions with nearby objects
        avoidance_vector = Vector(0, 0)

        for other_boid in boids:
            if other_boid != self:
                distance = math.sqrt((other_boid.rect.centerx - self.rect.centerx) ** 2 +
                                     (other_boid.rect.centery - self.rect.centery) ** 2 +
                                     (other_boid.rect.centerx - self.rect.centerx) ** 2)

                if distance < 70:
                    avoidance_vector -= Vector(other_boid.rect.centerx - self.rect.centerx,
                                               other_boid.rect.centery - self.rect.centery)

        return avoidance_vector #Returns a vector indicating the adjustment needed for avoidance

    def rule3(self, boids): #Calculates the perceived velocity of the group of objects 
        perceived_velocity = Vector(0, 0)

        for other_boid in boids:
            if other_boid != self:
                perceived_velocity += Vector(other_boid.velocity.x, other_boid.velocity.y)

        perceived_velocity /= len(boids) - 1

        return (perceived_velocity - Vector(self.velocity.x, self.velocity.y)) / 8 #Returns a vector indicating the adjustment needed for cohesion

    def limit_velocity(self, vlim): #Limits the velocity of the object to a specified maximum (vlim)
        velocity_magnitude = math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2)

        if velocity_magnitude > vlim:
            self.velocity = Vector((self.velocity.x / velocity_magnitude) * vlim,
                                   (self.velocity.y / velocity_magnitude) * vlim)

    def bound_position(self, Xmin, Xmax, Ymin, Ymax): #Adjusts the position of the object if it goes beyond specified bounds (Xmin, Xmax, Ymin, Ymax, Zmin, Zmax)
        bound_vector = Vector(0, 0)

        if self.rect.centerx < Xmin:
            bound_vector.x = 10
        elif self.rect.centerx > Xmax:
            bound_vector.x = -10

        if self.rect.centery < Ymin:
            bound_vector.y = 10
        elif self.rect.centery > Ymax:
            bound_vector.y = -10

        return bound_vector

    def move_all_boids_to_new_positions(self, boids,obstical_group, vlim, Xmin, Xmax, Ymin, Ymax,):
        if self.perching:
            if self.perch_timer > 0:
                self.perch_timer -= 1
                return
            else:
                self.perching = False

        v1 = self.rule1(boids)
        v2 = self.rule2(boids)
        v3 = self.rule3(boids)

        # Consider obstacles
        avoidance_vector_obsticals = Vector(0, 0)
        for obstical in obstical_group:
            distance_obstical = math.sqrt(
                (obstical.rect.centerx - self.rect.centerx) ** 2 +
                (obstical.rect.centery - self.rect.centery) ** 2 +
                (obstical.rect.centerx - self.rect.centerx) ** 2
        )

        if distance_obstical < 200:  
            avoidance_vector_obsticals -= Vector(
                obstical.rect.centerx - self.rect.centerx,
                obstical.rect.centery - self.rect.centery
            )


        self.velocity = self.velocity + v1 + v2 + v3 #Combines the effects of the rules to update the object's velocity.

        self.limit_velocity(vlim) #Limits velocity 

        bound_vector = self.bound_position(Xmin, Xmax, Ymin, Ymax) #applies bounds
        self.velocity += bound_vector

        self.rect.centerx += self.velocity.x #Updates the position of the object based on its velocity
        self.rect.centery += self.velocity.y #Updates the position of the object based on its velocity

        if self.rect.centery < 0: #Introduces a perching behavior if the object's rect.centery is less than 0
            self.rect.centery = 0
            self.perching = True
            self.perch_timer = random.randint(50, 200)

class Boid(moving_objects):
    
    def __init__(self, position, velocity):
        super().__init__()
        self.image = pygame.transform.scale(boid, (20, 20)) #size of image
        self.rect = self.image.get_rect()
        self.rect.center = (position.x, position.y) #sets position based on position vector
        self.velocity = velocity #sets velocity based on velocity vector
        self.perching = False 
        self.perch_timer = 0

class Hoik(moving_objects):

    def __init__(self, position, velocity):
        super().__init__()
        self.image = pygame.transform.scale(hoik, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (position.x, position.y)
        self.velocity = velocity
        self.perching = False
        self.perch_timer = 0
    
    def hunt_boids(self, boids_group):
        hunted_boids = pygame.sprite.spritecollide(self, boids_group, False)
        for boid in hunted_boids:
            distance = math.sqrt((boid.rect.centerx - self.rect.centerx) ** 2 +
                                 (boid.rect.centery - self.rect.centery) ** 2) #calculates distance

            if distance < 20:
                boids_group.remove(boid) #if a boid is less than 20 units away its  removed from the group

class Obstical(moving_objects):
    def __init__(self, position, velocity):
        super().__init__()
        self.image = pygame.transform.scale(obstical, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (position.x, position.y)
        self.velocity = 0
# obsticals inherit from the moving_objects class, but the velocity is set to 0        
        


def main():
    # Initialize boids
    num_boids = 100
    boids_group = pygame.sprite.Group()

    # Create boids and add them to the group
    for _ in range(num_boids):
        position = Vector(random.uniform(0, SCREEN_X), random.uniform(0, SCREEN_Y))
        velocity = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        boid_sprite = Boid(position, velocity)
        boids_group.add(boid_sprite)

    # Initialize hoiks
    num_hoiks = 5
    hoiks_group = pygame.sprite.Group()

    # Create hoiks and add them to the group
    for _ in range(num_hoiks):
        position = Vector(random.uniform(0, SCREEN_X), random.uniform(0, SCREEN_Y))
        velocity = Vector(random.uniform(-1, 1), random.uniform(-1, 1))
        hoik_sprite = Hoik(position, velocity)
        hoiks_group.add(hoik_sprite)

    # Initialize obstacles
    num_obstacles = 1
    obstacle_group = pygame.sprite.Group()

    # Create obstacles and add them to the group
    for _ in range(num_obstacles):
        position = Vector(random.uniform(0, SCREEN_X), random.uniform(0, SCREEN_Y))
        velocity = 0
        obstacle_sprite = Obstical(position, velocity)
        obstacle_group.add(obstacle_sprite)

    # Simulation parameters
    vlim = 10
    Xmin, Xmax, Ymin, Ymax = 0, SCREEN_X, 0, SCREEN_Y

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen with the background
        screen.blit(background, (0, 0))

        # Update and draw boids
        for boid in boids_group.sprites():
            boid.move_all_boids_to_new_positions(boids_group.sprites(), obstacle_group, vlim, Xmin, Xmax, Ymin, Ymax)

        # Update and draw hoiks, and allow them to hunt boids
        for hoik in hoiks_group.sprites():
            hoik.move_all_boids_to_new_positions(hoiks_group.sprites(), obstacle_group, vlim, Xmin, Xmax, Ymin, Ymax)
            hoik.hunt_boids(boids_group)

        # Draw all sprites on the screen
        boids_group.draw(screen)
        hoiks_group.draw(screen)
        obstacle_group.draw(screen)

        # Update the display
        pygame.display.flip()

if __name__ == "__main__":
    main()
