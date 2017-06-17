from math import tan
import numpy as np
import pygame

MAX_ZOOM_LEVEL = 300
MIN_ZOOM_LEVEL = -300

MAX_OFFSET = 500
MIN_OFFSET = -500

from geometry import Point

class ModelPlacement:
    """The model in the context of a scene"""
    def __init__(self,reference,model,location,orientation):
        self.model = model
        self.location = location
        self.orientation = orientation
        self.reference = reference

class Scene:
    """A collection of modelplacements"""
    def __init__(self):
        self.model_placements = {}

    def addModel(self,reference,model,location,orientation):
        placement = ModelPlacement(reference, model, location, orientation)
        self.model_placements[placement.reference] = placement

class SceneViewer():
    def __init__(self, scene, dimensions):
        self.scene = scene
        self.dimensions = dimensions
        self.viewport = Viewport(dimensions)
        self.screen = self.init_pygame_canvas()
        self.update()

    def init_pygame_canvas(self):
        screen = pygame.display.set_mode(self.dimensions)
        screen.fill(pygame.Color(210,210,255))
        pygame.display.init()
        pygame.display.update()
        return screen

    def zoomIn(self,amt):
        #self.zoom_level = min(self.zoom_level + amt, MAX_ZOOM_LEVEL)
        self.viewport.zoom_level = np.clip(self.viewport.zoom_level + amt, MIN_ZOOM_LEVEL, MAX_ZOOM_LEVEL)
    def zoomOut(self,amt):
        self.viewport.zoom_level = max(self.viewport.zoom_level - amt, MIN_ZOOM_LEVEL)

    def move(self, x, y):
        self.viewport.offset = [
            np.clip(self.viewport.offset[0]+x,MIN_OFFSET,MAX_OFFSET),
            np.clip(self.viewport.offset[1]+y,MIN_OFFSET,MAX_OFFSET)
        ]

    def update(self):
        self.screen.fill(pygame.Color(210,210,255))
        self.draw_model_grid()
        print("updating, man")
        for reference,model_placement in self.scene.model_placements.items():
            print("model")
            model = model_placement.model
            #print(model)

            for face in model.faces:
                face_midpoint = face.get_midpoint()
                normal_origin = self.viewport.project_point(face_midpoint)
                normal_coords = (face.unit_normal*3) + np.array([face_midpoint.x,face_midpoint.y,face_midpoint.z])
                normal_coords = self.viewport.project_point(Point(normal_coords[0],normal_coords[1],normal_coords[2]))

                pygame.draw.line(
                    self.screen,
                    (0,200,0),
                    normal_origin,
                    normal_coords,
                    1
                )

                for edge in face.edges:
                    #TODO, map coords to 2d canvas using environment (viewport object)
                    #coords = 5*int(30+point.x),5*int(30+point.y)
                    start_coords = self.viewport.project_point(edge.points[0])
                    end_coords = self.viewport.project_point(edge.points[1])
                    #print(coords)
                    #print("------------")
                    pygame.draw.circle(
                        self.screen,
                        (1,1,1),
                        start_coords,
                        2,
                        2
                    )
                    pygame.draw.line(self.screen,
                        (0,0,200),
                        start_coords,
                        end_coords,
                        1
                    )

        pygame.display.update()

    def draw_model_grid(self):
        pygame.draw.line(self.screen,(0,0,200),(0,0),(self.dimensions[0]-1,0),1)
        pygame.draw.line(self.screen,(0,0,200),(self.dimensions[0]-1,0),(self.dimensions[0]-1,self.dimensions[1]-1),1)
        pygame.draw.line(self.screen,(0,0,200),(self.dimensions[0]-1,self.dimensions[1]-1),(0,self.dimensions[1]-1),1)
        pygame.draw.line(self.screen,(0,0,200),(0,self.dimensions[1]-1),(0,0),1)

        for i in range(-5,5):
            pygame.draw.circle(
                self.screen,
                (1,1,1),
                self.viewport.project_point(Point(i*10,-5,100)),
                2,
                2
            )

            pygame.draw.line(self.screen,(200,0,0),
                self.viewport.project_point(Point(i*10,-5,1)),
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
        self.zoom_level = -10
        self.offset = [0,0] #viewport offset x,y
        self.h_fov = 1.042 # 60deg in radians

    def project_point(self,point):
        """ Given a point, return the coordinates within this viewport """
        if point.z == 0:
            z_actual = -.001
        else:
            z_actual = point.z

        z_actual = z_actual - self.zoom_level

        x_actual = point.x + self.offset[0]
        y_actual = point.y + self.offset[1]

        x = self.dimensions[0]/2 + x_actual / z_actual / tan(self.h_fov/2) * self.dimensions[0]/2;
        y = self.dimensions[1]/2 - y_actual / z_actual / tan(self.h_fov/2) * self.dimensions[0]/2;
        #print((x,y))
        return (int(x),int(y))
