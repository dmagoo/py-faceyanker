from math import tan
import numpy as np

MAX_ZOOM_LEVEL = 300
MIN_ZOOM_LEVEL = -300

MAX_OFFSET = 500
MIN_OFFSET = -500

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

    def zoomIn(self,amt):
        self.zoom_level = min(self.zoom_level + amt, MAX_ZOOM_LEVEL)
        print(self.zoom_level)

    def zoomOut(self,amt):
        self.zoom_level = max(self.zoom_level - amt, MIN_ZOOM_LEVEL)
        print(self.zoom_level)

    def move(self, x, y):
        self.offset = [
            np.clip(self.offset[0]+x,MIN_OFFSET,MAX_OFFSET),
            #max(MIN_OFFSET, min(MAX_OFFSET,self.offset[0]+x)),
            np.clip(self.offset[1]+y,MIN_OFFSET,MAX_OFFSET)
            #max(MIN_OFFSET, min(MAX_OFFSET,self.offset[1]+y))

        ]
        print(self.offset)

    def project_point(self,point):
        """ Given a point, return the coordinates within this viewport """
        #return [ self.midpoint[0]+self.zoom_level*point.x, self.midpoint[1]+self.zoom_level*point.y]
        #x = screen.width/2 + view.x / view.z / tan(h_fov/2) * screen.width/2;
        #y = screen.height/2 - view.y / view.z / tan(h_fov/2) * screen.width/2;
        #print("point")
        #print(point.x, point.y, point.z)

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
