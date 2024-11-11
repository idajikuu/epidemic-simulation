import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from map import Map
from agent import Agent
import time
import matplotlib.pyplot as plt
import os 
import json 

# Initialize Pygame and OpenGL
pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D City Layout with Moving Agents")

# Initialize Pygame Font
pygame.font.init()
font_path = "./Minecraftia-Regular.ttf"

# Map parameters
city_size = 5  # 5x5 grid
building_size = 2
building_height = 1  # Fixed height for all buildings
road_width = 1  # Fixed road width
num_agents = 50  # Number of moving agents

# Load or initialize simulation results
results_file = "simulation_results.json"
if os.path.exists(results_file):
    with open(results_file, "r") as file:
        try:
            all_results = json.load(file)
        except json.JSONDecodeError:
            print("Invalid or empty JSON file detected, initializing a new results list.")
            all_results = []
else:
    all_results = []


# Set up camera for a straight top-down perspective
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    gluPerspective(80, (width / height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        city_size * (building_size + road_width) / 2,  # Centered X
        city_size * (building_size + road_width) / 2,  # Centered Y
        20,  # Height above the grid
        city_size * (building_size + road_width) / 2,  # Look at X (centered)
        city_size * (building_size + road_width) / 2,  # Look at Y (centered)
        0,  # Look at Z (ground level)
        0, 1, 0  # Up vector
    )

# Function to track infection data
def update_infection_data(agents, time_series, infected_counts, healthy_counts, recovered_counts, deceased_counts, start_time):
    infected = sum(1 for agent in agents if agent.state == Agent.INFECTED)
    healthy = sum(1 for agent in agents if agent.state == Agent.HEALTHY)
    recovered = sum(1 for agent in agents if agent.state == Agent.REMOVED and agent.color == (0.0, 0.0, 1.0))
    deceased = sum(1 for agent in agents if agent.state == Agent.REMOVED and agent.color == (1.0, 0.65, 0.0))

    time_series.append(time.time() - start_time)
    infected_counts.append(infected)
    healthy_counts.append(healthy)
    recovered_counts.append(recovered)
    deceased_counts.append(deceased)

def draw_text_clean(x, y, text, color=(255, 255, 255), font_size = 15):
    """Render text using Pygame, convert it into a texture, and display it in OpenGL."""
    # Render the text to a Pygame surface
    custom_font = pygame.font.Font(font_path, font_size)
    text_surface = custom_font.render(text, True, color)  # Explicit white background

    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    # Enable blending for transparency (no background)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Create and bind the texture
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    # Set up orthogonal 2D projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw text quad
    glEnable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)  # Ensure text is not tinted
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, height - y - text_surface.get_height())
    glTexCoord2f(1, 0); glVertex2f(x + text_surface.get_width(), height - y - text_surface.get_height())
    glTexCoord2f(1, 1); glVertex2f(x + text_surface.get_width(), height - y)
    glTexCoord2f(0, 1); glVertex2f(x, height - y)
    glEnd()
    
    # Cleanup
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glDeleteTextures([texture_id])
    glDisable(GL_BLEND)

def display_counts(agents, params):
    infected = sum(1 for agent in agents if agent.state == Agent.INFECTED)
    healthy = sum(1 for agent in agents if agent.state == Agent.HEALTHY)
    recovered = sum(1 for agent in agents if agent.state == Agent.REMOVED and agent.color == (0.0, 0.0, 1.0))
    removed = sum(1 for agent in agents if agent.state == Agent.REMOVED and agent.color == (1.0, 0.65, 0.0))

    # Define cube drawing for legend
    def draw_legend_cube(x, y, color):
        glPushMatrix()
        glTranslatef(x, y, 0)  # Position the cube at the desired location
        glColor3f(*color)      # Set the color
        size = 0.1             # Size of the cube

        # Draw cube faces
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-size, -size, 0.0)
        glVertex3f(size, -size, 0.0)
        glVertex3f(size, size, 0.0)
        glVertex3f(-size, size, 0.0)
        glEnd()

        glPopMatrix()

    # Display text with corresponding colored cubes
    draw_text_clean(45, 169, f"Infected: {infected}", color=(255, 0, 0), font_size=13)
    #draw_legend_cube(-3.3, 20, (1.0, 0.0, 0.0))  # Red cube for infected

    draw_text_clean(155, 169, f"Healthy: {healthy}", color=(0, 255, 0), font_size=13)
    #draw_legend_cube(1.6, 20, (0.0, 1.0, 0.0))  # Green cube for healthy

    draw_text_clean(270, 169, f"Diseased: {removed}", color=(255, 165, 0), font_size=13)
    #draw_legend_cube(6.3, 20, (1.0, 0.65, 0.0))  # Orange cube for diseased

    draw_text_clean(380, 169, f"Recovered: {recovered}", color=(0, 0, 255), font_size=13)
    #draw_legend_cube(11.6, 20, (0.0, 0.0, 1.0))  # Blue cube for recovered

    # Display parameters in a table format on the right with smaller text
    x_offset = width - 290  # Align to the right
    y_offset = 80
    row_height = 30
    table_color = (0,0,0)

    table_data = [
        ("Infection Radius", f"{params[0]:.2f} units"),  # Add units for radius
        ("Infection Probability", f"{params[1] * 100:.2f}%"),  # Convert to percentage
        ("Duration of Infection", f"{params[2]} s"),  # Keep seconds for duration
        ("Mortality Rate", f"{params[3] * 100:.2f}%"),  # Convert to percentage
    ]

    for i, (label, value) in enumerate(table_data):
        draw_text_clean(x_offset + 10, y_offset + i * row_height, f"{label}:", color=table_color, font_size=12)
        draw_text_clean(x_offset + 200, y_offset + i * row_height, value, color=table_color, font_size=12)

    draw_text_clean(50, 580, "Quarantine", color=(139, 0, 0), font_size=9)
    draw_text_clean(50, 485, "Graveyard", color=(64, 64, 64), font_size=9)  # Deep gray color

def reset_simulation():
    """Resets Pygame and OpenGL state for a fresh simulation."""
    pygame.display.quit()  # Close current window
    pygame.display.init()  # Reinitialize display
    global screen
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)  # Recreate the display
    pygame.display.set_caption("3D City Layout with Moving Agents")
    glLoadIdentity()  # Reset OpenGL modelview matrix

def run_simulation(params, time_limit=20):
    """Runs a single simulation with given parameters."""
    infection_radius, infection_probability, infection_duration, mortality_rate, quarantine_start_time = params

    # Initialize map and agents
    city_map = Map(city_size, building_size, road_width, building_height)
    agents = [
        Agent(city_size, building_size, road_width, city_map,
              step_size=0.05, infection_radius=infection_radius,
              infection_probability=infection_probability, infection_duration=infection_duration,
              mortality_rate=mortality_rate, road_buffer=0.001,
              quarantine_start_time=quarantine_start_time)  # Pass the new param
        for _ in range(num_agents)
    ]

    # Infect one agent to start the spread
    agents[0].state = Agent.INFECTED
    agents[0].color = (1.0, 0.0, 0.0)
    agents[0].infection_start_time = time.time()

    start_time = time.time()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Exit simulation after time limit
        if time.time() - start_time > time_limit:
            break

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        city_map.draw_map()

        # Move and draw agents
        for agent in agents:
            agent.move(agents)
            agent.draw()
        
        for agent in agents:
            if agent.state == Agent.INFECTED:
                for other_agent in agents:
                    if other_agent.state == Agent.HEALTHY:
                        agent.check_infection(other_agent)
            agent.update_infection_status()

        display_counts(agents, params)
        pygame.display.flip()
        clock.tick(30)  # Limit FPS

    # Final infection state counts
    infected = sum(1 for agent in agents if agent.state == Agent.INFECTED)
    healthy = sum(1 for agent in agents if agent.state == Agent.HEALTHY)
    recovered = sum(1 for agent in agents if agent.state == Agent.REMOVED and agent.color == (0.0, 0.0, 1.0))
    deceased = sum(1 for agent in agents if agent.state == Agent.REMOVED and agent.color == (1.0, 0.65, 0.0))

    return infected, healthy, recovered, deceased


def save_all_results(all_results):
    """Save all simulation results to a JSON file after all simulations."""
    results_file = "simulation_results.json"
    with open(results_file, "w") as file:
        json.dump(all_results, file, indent=4)

# Simulation parameters to test
param_sets = [
    (0.8, 1.0, 2, 0.15, 2),   # Very high radius, guaranteed infection, very short duration, moderate mortality, rapid quarantine
    (0.6, 0.6, 20, 0.5, 8),   # Medium-high radius, moderate probability, long infection, high mortality, late quarantine
    (0.3, 0.4, 10, 0.2, 7),   # Low radius, low probability, medium infection, moderate mortality, delayed quarantine
    (0.4, 0.7, 12, 0.1, 5),   # Low radius, high probability, medium infection, low mortality, standard quarantine
    (0.5, 0.9, 15, 0.25, 4),  # Moderate radius, high probability, long infection, moderate mortality, default quarantine
    (0.7, 0.95, 1, 1, 2),     # High radius, high probability, instant infection, 100% mortality, fast quarantine
]


final_results = []

for params in param_sets:
    reset_simulation()
    setup_camera()
    infected, healthy, recovered, deceased = run_simulation(params)

    result = {
        "parameters": {
            "infection_radius": params[0],
            "infection_probability": params[1],
            "infection_duration": params[2],
            "mortality_rate": params[3],
            "quarantine_start_time": params[4],
        },
        "final_counts": {
            "infected": infected,
            "healthy": healthy,
            "recovered": recovered,
            "deceased": deceased
        }
    }
    final_results.append(result)

# Save all results once at the end
with open(results_file, "w") as file:
    json.dump(final_results, file, indent=4)

