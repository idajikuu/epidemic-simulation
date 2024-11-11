# map.py
import random
from OpenGL.GL import *
from PIL import Image  # For loading and processing image files
import pygame

class Map:
    """Class to handle the city layout including buildings and roads with center lines."""

    def __init__(self, city_size, building_size, road_width, building_height):
        self.city_size = city_size
        self.building_size = building_size
        self.road_width = road_width
        self.building_height = building_height
        self.road_texture = self.load_texture(r"C:\Users\sofis\OneDrive\Desktop\Projects\project 2\asphalt-road-texture-dark-gray-color_1017-20231.jpg")
        self.single_texture = self.load_texture(r"C:\Users\sofis\OneDrive\Desktop\Projects\project 2\clouds-reflected-windows-modern-office.png")
        self.graveyard_width, self.graveyard_height = 2, 2  # Define size
        self.graveyard_start_x = -self.city_size -self.graveyard_width
        self.graveyard_start_y = 4
        # Precompute heights for all building clusters in the grid
        self.building_heights = self.generate_building_heights()
        #self.grave_texture = self.load_texture("./graves.png")
        self.graves = []  # Store grave positions
        self.grass_texture = self.load_texture("./th.jpeg")
        self.grave_texture = self.load_texture_gravestone("./gravestone.png")


    def load_texture_gravestone(self, file_path):
        """Load a texture with alpha transparency."""
        texture_surface = pygame.image.load(file_path).convert_alpha()  # Load with alpha
        texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
        width, height = texture_surface.get_size()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return texture_id

    def load_texture(self, image_path):
        """Loads an image file as a texture for OpenGL."""
        img = Image.open(image_path)
        img = img.convert("RGB")  # Convert to RGB for OpenGL compatibility
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # Flip vertically for OpenGL
        img_data = img.tobytes()
        width, height = img.size

        # Generate a texture ID
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        # Load the texture into OpenGL
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        
        return texture_id

    def draw_roads(self):
        """Draws textured roads with centered dotted lines between segments, excluding intersections."""
        cell_size = self.building_size + self.road_width
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.road_texture)

        glColor3f(1.0, 1.0, 1.0)  # Set color to white to use the texture colors

        # Draw the main roads
        glBegin(GL_QUADS)
        for i in range(self.city_size - 1):
            y_pos = (i + 1) * cell_size - self.road_width
            x_pos = (i + 1) * cell_size - self.road_width

            # Horizontal road
            glTexCoord2f(0.0, 0.0); glVertex3f(0, y_pos, 0)
            glTexCoord2f(1.0, 0.0); glVertex3f(self.city_size * cell_size - self.road_width, y_pos, 0)
            glTexCoord2f(1.0, 1.0); glVertex3f(self.city_size * cell_size - self.road_width, y_pos + self.road_width, 0)
            glTexCoord2f(0.0, 1.0); glVertex3f(0, y_pos + self.road_width, 0)

            # Vertical road
            glTexCoord2f(0.0, 0.0); glVertex3f(x_pos, 0, 0)
            glTexCoord2f(1.0, 0.0); glVertex3f(x_pos + self.road_width, 0, 0)
            glTexCoord2f(1.0, 1.0); glVertex3f(x_pos + self.road_width, self.city_size * cell_size - self.road_width, 0)
            glTexCoord2f(0.0, 1.0); glVertex3f(x_pos, self.city_size * cell_size - self.road_width, 0)
        
        # Top and bottom horizontal roads
        # Bottom
        glTexCoord2f(0.0, 0.0); glVertex3f(-self.road_width, -self.road_width, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(self.city_size * (self.building_size + self.road_width) - self.road_width, -self.road_width, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(self.city_size * (self.building_size + self.road_width) - self.road_width, 0, 0)
        glTexCoord2f(0.0, 1.0); glVertex3f(-self.road_width, 0, 0)

        # Top
        glTexCoord2f(0.0, 0.0); glVertex3f(-self.road_width, self.city_size * (self.building_size + self.road_width) - self.road_width, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(self.city_size * (self.building_size + self.road_width) - self.road_width, self.city_size * (self.building_size + self.road_width) - self.road_width, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(self.city_size * (self.building_size + self.road_width) - self.road_width, self.city_size * (self.building_size + self.road_width), 0)
        glTexCoord2f(0.0, 1.0); glVertex3f(-self.road_width, self.city_size * (self.building_size + self.road_width), 0)


        # Left and right vertical roads
        # Left
        glTexCoord2f(0.0, 0.0); glVertex3f(-self.road_width, 0, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(0, 0, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(0, self.city_size * (self.building_size + self.road_width) - self.road_width, 0)
        glTexCoord2f(0.0, 1.0); glVertex3f(-self.road_width, self.city_size * (self.building_size + self.road_width) - self.road_width, 0)

        # Right
        glTexCoord2f(0.0, 0.0); glVertex3f(self.city_size * (self.building_size + self.road_width) - self.road_width, -self.road_width, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(self.city_size * (self.building_size + self.road_width), -self.road_width, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(self.city_size * (self.building_size + self.road_width), self.city_size * (self.building_size + self.road_width), 0)
        glTexCoord2f(0.0, 1.0); glVertex3f(self.city_size * (self.building_size + self.road_width) - self.road_width, self.city_size * (self.building_size + self.road_width), 0)


        glEnd()
        glDisable(GL_TEXTURE_2D)

        # Parameters for centered dotted lines
        dash_length = 0.3  # Length of each dash
        dash_spacing = 0.2  # Space between each dash
        line_offset = self.road_width / 2 - 0.05  # Center line offset within the road width

        # Draw centered dotted lines on horizontal and vertical road segments between buildings
        glColor3f(0.7, 0.7, 0.7)  # White color for dotted line

        glBegin(GL_QUADS)
        
        # Horizontal dotted lines (4 rows between 5 segments)
        for i in range(self.city_size - 1):
            y_pos = (i + 1) * cell_size - self.road_width / 2  # Centered on the road width
            for j in range(self.city_size ):
                x_start = (j ) * cell_size 

                # Draw dashes along the road segment, avoiding intersections
                x = x_start
                while x < x_start + self.building_size:
                    glVertex3f(x, y_pos, 0.01)
                    glVertex3f(x + dash_length, y_pos, 0.01)
                    glVertex3f(x + dash_length, y_pos + 0.05, 0.01)
                    glVertex3f(x, y_pos + 0.05, 0.01)
                    x += dash_length + dash_spacing

        # Vertical dotted lines (4 columns between 5 segments)
        for j in range(self.city_size - 1):
            x_pos = (j + 1) * cell_size - self.road_width / 2  # Centered on the road width
            for i in range(self.city_size ):
                y_start = (i ) * cell_size 

                # Draw dashes along the road segment, avoiding intersections
                y = y_start
                while y < y_start + self.building_size:
                    glVertex3f(x_pos, y, 0.01)
                    glVertex3f(x_pos + 0.05, y, 0.01)
                    glVertex3f(x_pos + 0.05, y + dash_length, 0.01)
                    glVertex3f(x_pos, y + dash_length, 0.01)
                    y += dash_length + dash_spacing

        glEnd()

    def get_road_boundaries(self):
        """Returns a list of valid road areas where agents can move, excluding buildings."""
        road_boundaries = []
        cell_size = self.building_size + self.road_width

        # Horizontal and vertical road segments
        for i in range(self.city_size - 1):
            y_pos = (i + 1) * cell_size - self.road_width
            for j in range(self.city_size - 1):
                x_pos = (j + 1) * cell_size - self.road_width

                # Horizontal road segment
                road_boundaries.append((0, self.city_size * cell_size, y_pos, y_pos + self.road_width))
                
                # Vertical road segment
                road_boundaries.append((x_pos, x_pos + self.road_width, 0, self.city_size * cell_size))

        return road_boundaries

    def generate_building_heights(self):
        """Generates fixed heights for each cluster of buildings in the grid."""
        heights = []
        for _ in range(self.city_size):
            row_heights = []
            for _ in range(self.city_size):
                # Generate heights for the four buildings in the cell
                cell_heights = [
                    random.uniform(self.building_height * 0.3, self.building_height * 1.1),
                    random.uniform(self.building_height * 0.4, self.building_height * 2),
                    random.uniform(self.building_height * 0.7, self.building_height * 2),
                    random.uniform(self.building_height * 0.5, self.building_height * 1.1)
                ]
                row_heights.append(cell_heights)
            heights.append(row_heights)
        return heights           

    def draw_shadow(self, x, y, height, size, is_last_row=False):
        """Draws a lighter, dented shadow below the building based on height, with adjustments for the last row."""
        # Limit shadow length for the last row to avoid extending beyond the grid
        shadow_length = min(height * 0.9 , self.road_width * 0.9) if is_last_row else height * 0.9
    
        """Draws a simple shadow projected from the bottom points of the building, angled slightly to the side."""
        shadow_offset_x = -shadow_length * 0.5  # Offset shadow slightly to the left
        shadow_offset_y = -shadow_length  # Offset shadow downwards

        glColor4f(0.2, 0.2, 0.2, 0.15)  # Light, semi-transparent shadow color
        glBegin(GL_QUADS)
        # Use the bottom points of the building as the basis for the shadow
        glVertex3f(x, y, 0.01)  # Bottom-left of building
        glVertex3f(x + size, y, 0.01)  # Bottom-right of building
        # Project the shadow points from the bottom points, angled with shadow offsets
        glVertex3f(x + size + shadow_offset_x, y + shadow_offset_y, 0.01)  # Shadow top-right
        glVertex3f(x + shadow_offset_x, y + shadow_offset_y, 0.01)  # Shadow top-left
        glEnd()



    def draw_building(self, x, y, height, size, base_top_color):
        """Draws a single building at (x, y) with a specified height, size, and top color adjusted for height."""
        glPushMatrix()
        glTranslatef(x, y, 0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.single_texture)

        # Draw the sides
        # Front face
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex3f(0, 0, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(size, 0, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(size, 0, height)
        glTexCoord2f(0.0, 1.0); glVertex3f(0, 0, height)
        glEnd()

        # Back face
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex3f(0, size, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(size, size, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(size, size, height)
        glTexCoord2f(0.0, 1.0); glVertex3f(0, size, height)
        glEnd()

        # Left face
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex3f(0, 0, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(0, size, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(0, size, height)
        glTexCoord2f(0.0, 1.0); glVertex3f(0, 0, height)
        glEnd()

        # Right face
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex3f(size, 0, 0)
        glTexCoord2f(1.0, 0.0); glVertex3f(size, size, 0)
        glTexCoord2f(1.0, 1.0); glVertex3f(size, size, height)
        glTexCoord2f(0.0, 1.0); glVertex3f(size, 0, height)
        glEnd()

        shadow_factor = 1 - (height / (self.building_height * 5))
        shadowed_top_color = (
            base_top_color[0] * shadow_factor,
            base_top_color[1] * shadow_factor,
            base_top_color[2] * shadow_factor
        )

        # Top face with shadow effect
        glDisable(GL_TEXTURE_2D)
        glColor3f(*shadowed_top_color)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, height)
        glVertex3f(size, 0, height)
        glVertex3f(size, size, height)
        glVertex3f(0, size, height)
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glPopMatrix()
        
    def draw_quarantine_zone(self):
        """Draws the quarantine zone as a box with a red border on the left side of the map."""
        glColor3f(1.0, 0.0, 0.0)  # Red for quarantine border
        quarantine_size = 2  # Define size of the quarantine zone
        quarantine_x = -self.city_size - quarantine_size  # Left side of the main map
        quarantine_y = 0  # Bottom of the quarantine area
        # Draw the border of the quarantine box
        glBegin(GL_LINE_LOOP)
        glVertex3f(quarantine_x, quarantine_y, 0)
        glVertex3f(quarantine_x + quarantine_size, quarantine_y, 0)
        glVertex3f(quarantine_x + quarantine_size, quarantine_y + quarantine_size, 0)
        glVertex3f(quarantine_x, quarantine_y + quarantine_size, 0)
        glEnd()

    def draw_graveyard(self):
        """Draw the graveyard zone with a grass texture and grave markers."""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.grass_texture)
        glColor3f(1.0, 1.0, 1.0)  # Ensure no color tint on texture

        # Draw the graveyard base with grass texture
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(self.graveyard_start_x, self.graveyard_start_y, 0)
        glTexCoord2f(1, 0); glVertex3f(self.graveyard_start_x + self.graveyard_width, self.graveyard_start_y, 0)
        glTexCoord2f(1, 1); glVertex3f(self.graveyard_start_x + self.graveyard_width, self.graveyard_start_y + self.graveyard_height, 0)
        glTexCoord2f(0, 1); glVertex3f(self.graveyard_start_x, self.graveyard_start_y + self.graveyard_height, 0)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        # Draw grave markers on top of the grass texture
        for x, y in self.graves:
            self.draw_grave_marker(x, y)

    def draw_grave_marker(self, x, y):
        """Draw a grave marker with transparency."""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.grave_texture)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1.0, 1.0, 1.0)  # No color tint

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(x, y, 0)
        glTexCoord2f(1, 0); glVertex3f(x + 0.5, y, 0)
        glTexCoord2f(1, 1); glVertex3f(x + 0.5, y + 0.5, 0)
        glTexCoord2f(0, 1); glVertex3f(x, y + 0.5, 0)
        glEnd()

        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)



    def add_grave(self):
        """Add a grave for a deceased agent in an orderly grid layout."""
        grid_x = self.graveyard_start_x + (len(self.graves) % 4) * 0.5  # Columns of 4
        grid_y = self.graveyard_start_y + (len(self.graves) // 4) * 0.5  # New row after 4 graves
        if (grid_x, grid_y) not in self.graves:  # Ensure no duplicate graves at the same position
            self.graves.append((grid_x, grid_y))

    def draw_map(self):
        """Draws the entire city layout with clusters of four smaller buildings in each cell and adjusts shadow length for the last row."""
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.draw_roads()

        cell_size = self.building_size + self.road_width
        sub_building_size = self.building_size / 2  # Each smaller building occupies half of the original building size

        # Define fixed base colors for each of the four buildings in a cell
        top_colors = [
            (1, 1, 1),  # Off-white for bottom-left
            (1, 1, 1),  # Off-white for bottom-right
            (0.9, 0.9, 0.9),  # Off-white for top-left
            (0.9, 0.9, 0.9)   # Off-white for top-right
        ]

        for i in range(self.city_size):
            for j in range(self.city_size):
                x = i * cell_size
                y = j * cell_size
                    
                # Check if we're in the last row
                is_last_row = (j == 0 )
                
                # Retrieve precomputed heights for the current cluster
                heights = self.building_heights[i][j]
                
                # Draw shadows for all four buildings in each grid cell
                self.draw_shadow(x, y, heights[3], sub_building_size, is_last_row)                     # Bottom-left
                self.draw_shadow(x + sub_building_size, y, heights[2], sub_building_size, is_last_row) # Bottom-right
                self.draw_shadow(x, y + sub_building_size, heights[1], sub_building_size)              # Top-left
                self.draw_shadow(x + sub_building_size, y + sub_building_size, heights[0], sub_building_size ) # Top-right
                
                # Draw the buildings in the cell
                self.draw_building(x, y, heights[0], sub_building_size, top_colors[0])                    # Bottom-left
                self.draw_building(x + sub_building_size, y, heights[1], sub_building_size, top_colors[1]) # Bottom-right
                self.draw_building(x, y + sub_building_size, heights[2], sub_building_size, top_colors[2]) # Top-left
                self.draw_building(x + sub_building_size, y + sub_building_size, heights[3], sub_building_size, top_colors[3]) # Top-right
                # Call the verification overlay function to visualize road boundaries
        self.draw_quarantine_zone()  # Draw quarantine box
        glDisable(GL_DEPTH_TEST)
        self.draw_graveyard()
        glEnable(GL_DEPTH_TEST)
            