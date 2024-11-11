import random
import math
import time
from OpenGL.GL import *
from map import Map

class Agent:
    HEALTHY = "healthy"
    INFECTED = "infected"
    REMOVED = "removed"
    QUARANTINE_THRESHOLD = 5  # Seconds before moving to quarantine
    QUARANTINE_SIZE = 2
    QUARANTINE_DELAY = 10  
    ANIMATION_SPEED = 0.3  # Speed of arc animation to quarantine

    def __init__(self, city_size, building_size, road_width, city_map, step_size=0.05,
                 infection_radius=0.5, detection_radius=3.0,
                 infection_probability=0.75, infection_duration=15,
                 mortality_rate=0.2, road_buffer=0.3, quarantine_start_time=5):
        self.city_size = city_size
        self.building_size = building_size
        self.road_width = road_width
        self.step_size = step_size
        self.infection_radius = infection_radius
        self.detection_radius = detection_radius
        self.infection_probability = infection_probability
        self.infection_duration = infection_duration
        self.mortality_rate = mortality_rate
        self.road_buffer = road_buffer
        self.state = Agent.HEALTHY
        self.color = (0.0, 1.0, 0.0)  # Green for healthy
        self.infection_start_time = None
        self.cube_size = 0.15
        self.x, self.y = self._random_road_position()
        self.direction = random.choice(["up", "down", "left", "right"])
        self.steps_remaining = random.uniform(0, 0.05)
        self.quarantine_start_time = quarantine_start_time
        self.in_quarantine = False  # Track if the agent is in quarantine
        self.moving_to_quarantine = False  # Track if the agent is animating to quarantine
        self.moving_to_graveyard = False  
        self.arc_progress = 0  # Track progress along the arc path
        self.deceased_start_time = None  # Track when agent was marked as deceased

     # Quarantine-related attributes
        self.moving_to_quarantine = False
        self.in_quarantine = False
        self.arc_progress = 0  # Initialize here
        self.arc_start = (0, 0)
        self.arc_mid = (0, 0)
        self.arc_end = (0, 0)
        self.quarantine_box_position = (-self.city_size - Agent.QUARANTINE_SIZE, 0)
        self.map_instance= city_map
        self.in_graveyard =  None

    def _random_road_position(self):
        cell_size = self.building_size + self.road_width
        x = random.randint(0, self.city_size - 2) * cell_size + self.building_size + self.road_buffer
        y = random.randint(0, self.city_size - 2) * cell_size + self.building_size + self.road_buffer
        x += random.uniform(0, self.road_width - 2 * self.road_buffer)
        y += random.uniform(0, self.road_width - 2 * self.road_buffer)
        return x, y

    def infect(self):
        """Set the agent's state to infected with a probability."""
        if self.state == Agent.HEALTHY:
            if random.random() < self.infection_probability:
                self.state = Agent.INFECTED
                self.color = (1.0, 0.0, 0.0)  # Red for infected
                self.infection_start_time = time.time()

    def update_infection_status(self):
        """Update the infection status based on duration and mortality rate."""
        if self.state == Agent.INFECTED:
            elapsed_time = time.time() - self.infection_start_time

            # Infection duration complete, determine next state
            if elapsed_time >= self.infection_duration:
                if random.random() < self.mortality_rate:
                    self.state = Agent.REMOVED
                    self.color = (1.0, 0.65, 0.0)  
                    self.deceased_start_time = time.time()  # Mark the time of death
                else:
                    self.state = Agent.REMOVED
                    self.color = (0.0, 0.0, 1.0)  # Blue for recovered

            # Quarantine logic
            elif elapsed_time >= Agent.QUARANTINE_THRESHOLD and not self.in_quarantine:
                self.move_in_quarantine()  # Only infected agents can move to quarantine



    def start_moving_to_quarantine(self):
        """Initialize the arc animation to quarantine."""
        self.moving_to_quarantine = True
        self.arc_progress = 0  # Reset arc progress for the animation
        self.arc_start = (self.x, self.y)  # Start position for arc
        self.arc_mid = ((self.x + self.quarantine_box_position[0]) / 2, 
                        (self.y + self.quarantine_box_position[1]) / 2 + 5)  # Midpoint for an arc effect
        self.arc_end = (
            self.quarantine_box_position[0] + random.uniform(0, Agent.QUARANTINE_SIZE),
            self.quarantine_box_position[1] + random.uniform(0, Agent.QUARANTINE_SIZE)
        )  # Random end position within quarantine

    def animate_to_quarantine(self):
        """Animate the agent along an arc to the quarantine box."""
        self.arc_progress += Agent.ANIMATION_SPEED  # Adjust speed for faster movement
        if self.arc_progress >= 1.0:
            self.in_quarantine = True
            self.moving_to_quarantine = False
            # Randomize position within quarantine box on arrival
            self.x = self.quarantine_box_position[0] + random.uniform(0, Agent.QUARANTINE_SIZE)
            self.y = self.quarantine_box_position[1] + random.uniform(0, Agent.QUARANTINE_SIZE)
            return

        # Quadratic Bezier interpolation for arc movement
        t = self.arc_progress
        self.x = (1 - t)**2 * self.arc_start[0] + 2 * (1 - t) * t * self.arc_mid[0] + t**2 * self.arc_end[0]
        self.y = (1 - t)**2 * self.arc_start[1] + 2 * (1 - t) * t * self.arc_mid[1] + t**2 * self.arc_end[1]

    def move_in_quarantine(self):
        """Move randomly within the quarantine zone."""
        quarantine_x_start = self.quarantine_box_position[0]
        quarantine_y_start = self.quarantine_box_position[1]
        self.x = max(quarantine_x_start, min(self.x + random.uniform(-0.02, 0.02), quarantine_x_start + Agent.QUARANTINE_SIZE))
        self.y = max(quarantine_y_start, min(self.y + random.uniform(-0.02, 0.02), quarantine_y_start + Agent.QUARANTINE_SIZE))

    def stay_in_quarantine(self):
        """Keeps the agent in quarantine box with no movement."""
        self.x, self.y = self.quarantine_box_position  # Fixed position in the quarantine box


    def check_infection(self, other_agent):
        """Attempt to infect another agent if they are healthy."""
        if self.state == Agent.INFECTED and other_agent.state == Agent.HEALTHY:
            distance = math.sqrt((self.x - other_agent.x) ** 2 + (self.y - other_agent.y) ** 2)
            if distance <= self.infection_radius and random.random() < self.infection_probability:
                other_agent.infect()


    def choose_new_direction_with_bias(self):
        """Choose a new direction with a slight bias to keep agents near the center."""
        possible_directions = ["up", "down", "left", "right"]

        # Add bias if near edges
        map_center_x = self.city_size * (self.building_size + self.road_width) / 2
        map_center_y = self.city_size * (self.building_size + self.road_width) / 2

        if self.x < map_center_x and "left" in possible_directions:
            possible_directions.remove("left")
        if self.x > map_center_x and "right" in possible_directions:
            possible_directions.remove("right")
        if self.y < map_center_y and "down" in possible_directions:
            possible_directions.remove("down")
        if self.y > map_center_y and "up" in possible_directions:
            possible_directions.remove("up")

        # Favor current direction or pick a random valid direction
        self.direction = random.choice(possible_directions)
        self.steps_remaining = random.uniform(0, 0.05)


    def random_move(self):
        new_x, new_y = self.x, self.y
        if self.direction == "up":
            new_y += self.step_size
        elif self.direction == "down":
            new_y -= self.step_size
        elif self.direction == "left":
            new_x -= self.step_size
        elif self.direction == "right":
            new_x += self.step_size

        if self.is_on_road(new_x, new_y):
            self.x, self.y = new_x, new_y
            self.steps_remaining -= random.uniform(0, 0.02)

        else:
            self.change_direction()

    def draw(self):
        """Draw the agent as a 3D cube unless deceased in graveyard."""
        if self.in_graveyard and self.state == Agent.REMOVED and self.color == (1.0, 0.65, 0.0):
            # Ensure the grave is added only once
            if not getattr(self, 'grave_added', False):
                self.map_instance.add_grave()
                self.grave_added = True
            return  # Skip cube drawing for deceased agents

        # Shadow and agent cube drawing as before for other agents
        glColor4f(0.0, 0.0, 0.0, 0.3)
        glPushMatrix()
        glTranslatef(self.x, self.y, 0.01)
        glScalef(1.0, 1.0, 0.1)
        self._draw_shape()
        glPopMatrix()

        glColor3f(*self.color)
        glPushMatrix()
        glTranslatef(self.x, self.y, self.cube_size / 2)
        self._draw_shape()
        glPopMatrix()

    def _draw_shape(self):
        """Base shape for Agent, overridden by subclasses."""
        half_size = self.cube_size / 2
        glBegin(GL_QUADS)
        glVertex3f(-half_size, -half_size, half_size)
        glVertex3f(half_size, -half_size, half_size)
        glVertex3f(half_size, half_size, half_size)
        glVertex3f(-half_size, half_size, half_size)
        glEnd()

    def is_on_road(self, x, y):
        cell_size = self.building_size + self.road_width
        buffer = 0.05
        for i in range(self.city_size):
            y_pos = (i + 1) * cell_size - self.road_width
            if buffer <= x <= self.city_size * cell_size - buffer and y_pos + buffer <= y <= y_pos + self.road_width - buffer:
                return True

        for j in range(self.city_size):
            x_pos = (j + 1) * cell_size - self.road_width
            if buffer <= y <= self.city_size * cell_size - buffer and x_pos + buffer <= x <= x_pos + self.road_width - buffer:
                return True
            # Explicitly handle bottom horizontal road boundary with buffer
            if buffer <= x <= self.city_size * cell_size - buffer and -self.road_width <= y <= buffer:
                return True

            # Explicitly handle left vertical road boundary with buffer
            if buffer <= y <= self.city_size * cell_size - buffer and -self.road_width <= x <= buffer:
                return True

        return False
    
    def change_direction(self):
        self.choose_new_direction_with_bias()

    def animate_to_graveyard(self):
        """Animate the agent along an arc to the graveyard."""
        self.arc_progress += Agent.ANIMATION_SPEED
        if self.arc_progress >= 1.0:
            self.in_graveyard = True
            self.moving_to_graveyard = False
            return

        # Quadratic Bezier interpolation for arc movement
        t = self.arc_progress
        self.x = (1 - t)**2 * self.arc_start[0] + 2 * (1 - t) * t * self.arc_mid[0] + t**2 * self.arc_end[0]
        self.y = (1 - t)**2 * self.arc_start[1] + 2 * (1 - t) * t * self.arc_mid[1] + t**2 * self.arc_end[1]

    def start_moving_to_graveyard(self, graveyard_start_x, graveyard_start_y):
        """Start animating the agent to a specific graveyard location."""
        if not hasattr(self, "grave_position"):  # Assign only if not already assigned
            self.moving_to_graveyard = True
            self.arc_progress = 0
            self.arc_start = (self.x, self.y)  # Start position for arc
            self.arc_mid = ((self.x + graveyard_start_x) / 2, 
                            (self.y + graveyard_start_y) / 2 + 5)  # Arc midpoint for animation

            # Assign a unique grave position within the graveyard zone
            grave_x = graveyard_start_x + random.uniform(0, self.map_instance.graveyard_width - 0.2)
            grave_y = graveyard_start_y + random.uniform(0, self.map_instance.graveyard_height - 0.2)
            self.arc_end = (grave_x, grave_y)
            self.grave_position = self.arc_end  # Set the final resting position


    def stay_in_graveyard(self):
        """Keeps the deceased agent at its grave position."""
        if hasattr(self, "grave_position"):
            self.x, self.y = self.grave_position

    def move(self, agents):
        """Move the agent or animate movement to quarantine or graveyard if needed."""

        # REMOVED agents (recovered or deceased) shouldn't move further
        if self.state == Agent.REMOVED:
            if self.color == (1.0, 0.65, 0.0):  # Deceased agents move to graveyard
                if not self.moving_to_graveyard:
                    if time.time() - self.deceased_start_time >= 1:  # 1-second delay before moving to graveyard
                        self.start_moving_to_graveyard(
                            self.map_instance.graveyard_start_x, 
                            self.map_instance.graveyard_start_y
                        )
                elif not self.moving_to_graveyard:
                    self.stay_in_graveyard()  # Ensure they stay at the grave position
                else:
                    self.animate_to_graveyard()
                return

        # Normal movement logic for healthy or quarantined agents
        current_time = time.time()

        if self.in_quarantine:
            self.move_in_quarantine()
            return

        # Infected agents: move to quarantine after threshold
        if self.state == Agent.INFECTED and (current_time - self.infection_start_time) >= Agent.QUARANTINE_THRESHOLD:
            if not self.moving_to_quarantine:
                self.start_moving_to_quarantine()
            self.animate_to_quarantine()
        else:
            self.random_move()  # Healthy agents move randomly
