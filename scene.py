import time
from math import tan
import numpy as np
import pygame

from geometry import get_ordered_points_from_edges

#constants to describe different screen perspectives
SCENE_PERSPECTIVE_FRONT = 0
SCENE_PERSPECTIVE_TOP = 1
SCENE_PERSPECTIVE_LEFT = 2
SCENE_PERSPECTIVE_RIGHT = 3
SCENE_PERSPECTIVE_BOTTOM = 4
SCENE_PERSPECTIVE_BACK = 5

DEFAULT_PERSPECTIVE = SCENE_PERSPECTIVE_FRONT

MAX_ZOOM_LEVEL = -10
MIN_ZOOM_LEVEL = -400
DEFAULT_ZOOM_LEVEL = -30

MAX_OFFSET = 500
MIN_OFFSET = -500

DEFAULT_NORMAL_COLOR = (0,200,0)
DEFAULT_GRID_COLOR = (200,200,200)
DEFAULT_EDGE_COLOR = (0,0,200)
DEFAULT_BACKGROUND_COLOR = (255,255,255)
DEFAULT_ACTIVE_FACE_COLOR = (30,30,200,100)

from geometry import Point

class ModelPlacement:
    """The model in the context of a scene"""
    def __init__(self,reference,model,location,orientation):
        self.model = model
        self.location = location
        self.orientation = orientation
        self.reference = reference
        self.active_face = None

    def set_active_face_index(self,face_index):
        self.active_face = face_index

    def get_active_face(self):
        if None is not self.active_face:
            return self.model.faces[self.active_face]

        return None

    def hash_face_by_index(self,face_index):
        #todo, some unique hash using face coords and normal
        return hex(face_index)

class Scene:
    """A collection of modelplacements"""
    def __init__(self):
        self.model_placements = {}

    def add_model(self,reference,model,location,orientation):
        placement = ModelPlacement(reference, model, location, orientation)
        self.model_placements[placement.reference] = placement

    def get_model(self,reference):
        placement = self.get_model_placement(reference)
        return placement.model

    def get_model_placement(self,reference):
        return self.model_placements[reference]

class SceneViewer():
    def __init__(self, scene, dimensions):
        self.scene = scene
        self.dimensions = dimensions
        self.viewport = Viewport(dimensions)
        self.screen = self.init_pygame_canvas()

        self.show_normals = True
        self.normal_color = DEFAULT_NORMAL_COLOR

        self.show_grid = True
        self.grid_color = DEFAULT_NORMAL_COLOR

        self.update()

    def init_pygame_canvas(self):
        screen = pygame.display.set_mode(self.dimensions)
        screen.fill(DEFAULT_BACKGROUND_COLOR)
        pygame.display.init()
        pygame.display.update()
        return screen

    def set_perspective(self, perspective):
        self.viewport.perspective = perspective

    def zoom_in(self,amt):
        #self.zoom_level = min(self.zoom_level + amt, MAX_ZOOM_LEVEL)
        self.viewport.zoom_level = np.clip(self.viewport.zoom_level + amt, MIN_ZOOM_LEVEL, MAX_ZOOM_LEVEL)

    def zoom_out(self,amt):
        self.viewport.zoom_level = max(self.viewport.zoom_level - amt, MIN_ZOOM_LEVEL)

    def move(self, x, y):
        self.viewport.offset = [
            np.clip(self.viewport.offset[0]+x,MIN_OFFSET,MAX_OFFSET),
            np.clip(self.viewport.offset[1]+y,MIN_OFFSET,MAX_OFFSET)
        ]

    def toggle_show_normals(self, val=None):
        if None is val:
            val = not self.show_normals

        self.show_normals = val

    def toggle_show_grid(self, val=None):
        if None is val:
            val = not self.show_grid

        self.show_grid = val

    def update(self):
        self.screen.fill(DEFAULT_BACKGROUND_COLOR)

        if self.show_grid:
            self.draw_model_grid()

        #make a list of active faces to render last
        #so they appear above all other rendering
        active_faces = []

        for reference,model_placement in self.scene.model_placements.items():
            model = model_placement.model

            for index,face in enumerate(model.faces):
                if self.show_normals:
                    face_midpoint = face.get_midpoint()
                    normal_origin = self.viewport.project_point(face_midpoint)
                    normal_coords = (face.unit_normal*3) + np.array([face_midpoint.x,face_midpoint.y,face_midpoint.z])
                    normal_coords = self.viewport.project_point(Point(normal_coords[0],normal_coords[1],normal_coords[2]))

                    pygame.draw.line(
                        self.screen,
                        self.normal_color,
                        normal_origin,
                        normal_coords,
                        1
                    )

                if index == model_placement.active_face:
                    active_faces.append(face)

                for edge in face.edges:
                    start_coords,end_coords = self.viewport.project_point_list(edge.to_vector())

                    pygame.draw.circle(
                        self.screen,
                        (1,1,1),
                        start_coords,
                        2,
                        2
                    )
                    pygame.draw.line(self.screen,
                        DEFAULT_EDGE_COLOR,
                        start_coords,
                        end_coords,
                        1
                    )

        for face in active_faces:
            face_points = self.viewport.project_point_list(face.to_vector())

            #draw this face to a new surface to support alpha transparency
            #TODO, make surface as small as possible for faster blitting
            #or use this surface for the whole redraw. could be faster
            #than drawing to the main buffer
            #also consider dbl buffering
            s = pygame.Surface(self.dimensions, pygame.SRCALPHA)  # the size of your rect
            s.fill((255,255,255,50))           # this fills the entire surface
            pygame.draw.polygon(
                s, DEFAULT_ACTIVE_FACE_COLOR, face_points, 0
            )

            self.screen.blit(s, (0,0))

        pygame.display.update()

    def draw_model_grid(self):
        for i in range(-10,10):
            pygame.draw.circle(
                self.screen,
                (1,1,1),
                self.viewport.project_point(Point(i*10,-5,100)),
                2,
                2
            )

            pygame.draw.line(self.screen,DEFAULT_GRID_COLOR,
                self.viewport.project_point(Point(i*10,-5,-10)),
                self.viewport.project_point(Point(i*10,-5,2000)),
                1
            )

        return

class Viewport:
    """ Store any abstract data about the 3d environment
        Used in calculating rendering information
     """
    def __init__(self, dimensions):
        self.dimensions=dimensions
        self.midpoint = dimensions[0]/2, dimensions[1]/2
        self.zoom_level = DEFAULT_ZOOM_LEVEL
        self.offset = [0,0] #viewport offset x,y
        self.h_fov = 1.042 # 60deg in radians
        self.perspective = DEFAULT_PERSPECTIVE

    def project_point(self,point):
        return self.project_point_list([point])[0]


    def project_point_list(self,point_list):
        """ Given a list of points, return the coordinates within this viewport """
        mid_x = self.dimensions[0]/2
        mid_y = self.dimensions[1]/2
        fov_tan = tan(self.h_fov/2)

        coordinate_list = []

        #dirty trick to cast a 3d vector into a Point object
        #if it is already a Point object, a redundant point is returned
        for point in point_list:
            if self.perspective == SCENE_PERSPECTIVE_FRONT:
                point = Point(point[0],point[1],point[2])
            elif self.perspective == SCENE_PERSPECTIVE_TOP:
                point = Point(point[0],point[2],point[1])
            elif self.perspective == SCENE_PERSPECTIVE_LEFT:
                point = Point(-point[2],point[1],point[0])
            elif self.perspective == SCENE_PERSPECTIVE_RIGHT:
                point = Point(point[2],point[1],-point[0])
            elif self.perspective == SCENE_PERSPECTIVE_BOTTOM:
                point = Point(point[0],-point[2],point[1])
            elif self.perspective == SCENE_PERSPECTIVE_BACK:
                point = Point(-point[0],point[1],-point[2])

            #cheap way to avoid div/zero, I guess
            if point.z == 0:
                z_actual = -.001
            else:
                z_actual = point.z

            z_actual = z_actual - self.zoom_level
            x_actual = point.x + self.offset[0]
            y_actual = point.y + self.offset[1]

            x = mid_x + x_actual / z_actual / fov_tan * mid_x
            y = mid_y - y_actual / z_actual / fov_tan * mid_x

            #x = np.clip(x,self.dimensions[0]-1,self.dimensions[0]+1)
            #y = np.clip(y,self.dimensions[1]-1,self.dimensions[1]+1)
            #todo deal w infinity x or y
            coordinate_list.append((int(x),int(y)))

        return coordinate_list
