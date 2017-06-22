import math
import numpy as np
import copy

def normalize_vector(v):
    return v/math.sqrt(sum([i*i for i in v]))

def merge_faces(face_a, face_b):
    if not np.array_equal(face_a.get_unit_normal(), face_b.get_unit_normal()):
        raise Exception("cannot merge faces, not on same plane")
    if not face_a.adjacent_to(face_b):
        raise Exception("cannot merge faces, not touching")

    new_edges = [
        edge for edge in face_a.edges if not face_b.contains_edge(edge)
    ] + [
        edge for edge in face_b.edges if not face_a.contains_edge(edge)
    ]

    new_face = Face(new_edges, face_a.normal)

    return new_face

def get_ordered_points_from_edges(edges):
    """ chain edges together into a list of points, should
    be able to handle edges that are out of order """
    ret = []
    if len(edges) < 1:
        return ret

    #track list of edge indexes we processed
    done = []
    last_point = None
    while len(done) < len(edges):
        old_len = len(done)
        for i in range(len(edges)):
            if last_point is None:
                ret.append(edges[i][0])
                ret.append(edges[i][1])
                done.append(i)
            else:
                #if edges[i][0] == last_point:
                #(a, b, rtol=1e-05, atol=1e-08, equal_nan=False)[source]¶
                if np.allclose(edges[i][0], last_point, rtol=1e-9, atol=0.0):
                    ret.append(edges[i][1])
                    done.append(i)
            if len(done):
                last_point = edges[done[-1]][1]
        #if there are edges left, but we found nothing new
        if len(done) != len(edges) and len(done) == old_len:
            raise Exception("could not chain all edges")
    return ret

class Polygon2d:
    def __init__(self):
        self.edges = []

    def add_edge(self, edge):
        #this should keep edges sorted
        self.edges.append(edge)

    def get_points(self):
        return get_ordered_points_from_edges(self.edges)

    def get_points_scaled(self,scale_factors):
        return self.get_points()*scale_factors


    def get_extents(self):
        coords = self.get_points()
        extents = [np.amin(coords, axis=0),np.amax(coords, axis=0)]
        return extents

    def get_dimensions(self):
        vals = self.get_extents()
        return (
                (vals[1][0] - vals[0][0]),
                (vals[1][1] - vals[0][1])
                )

    def get_width(self):
        return self.get_dimensions()[0]

    def get_height(self):
        return self.get_dimensions()[1]


class Point:
    def __init__(self,x=0,y=0,z=0):
        self.x,self.y,self.z = x,y,z

    def to_vector(self):
        return np.array([self.x,self.y,self.z])

    def __eq__(self, other):
        return np.array_equal(self.to_vector(),other.to_vector())

    def __str__(self):
        return str([self.x,self.y,self.z])

    def __repr__(self):
        return self.__str__()

    def __sub__(self,other):
        new_point = self.to_vector() - other.to_vector()
        return Point(new_point[0],new_point[1],new_point[2])

    def __getitem__(self, i):
        return self.to_vector()[i]

    def __iter__(self):
        for i in self.to_vector():
            yield i

class Edge:
    def __init__(self, points):
        if len(points) != 2:
            raise Exception("invalid edge")

        self.points = points

    def __eq__(self, other):
        return (
            self.points[0] == other.points[0]
            and self.points[1] == other.points[1]
        ) or (
            self.points[0] == other.points[1]
            and self.points[1] == other.points[0]
        )

    def to_vector(self):
        return np.array([[point.x,point.y,point.z] for point in self.points])

    def __str__(self):
        return str(self.to_vector())

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, i):
        return self.to_vector()[i]

    def __iter__(self):
        for i in self.to_vector():
            yield i

class Face:
    def __init__(self, edges = [], normal = None):
        self.edges = edges
        self.normal = normal
        self.unit_normal = None

        if None is normal:
            self.normal = self.get_normal()

        self.unit_normal = self.get_unit_normal()

    def to2D(self):
        local_origin = (self.edges[0].points[0]).to_vector()
        local_x_axis = normalize_vector(self.edges[0].points[1].to_vector() - local_origin)
        local_y_axis = normalize_vector(np.cross(self.normal, local_x_axis))
        poly = Polygon2d()
        new_edges = []
        for edge in self.edges:
            new_edge = []
            for point in edge.points:
                p = point.to_vector()
                new_point = [
                    np.dot(p - local_origin, local_x_axis),  # local X coordinate
                    np.dot(p - local_origin, local_y_axis)
                ]
                new_edge.append(new_point)
            poly.add_edge(new_edge)

        return poly



    def get_midpoint(self):
        return Point(
                    sum([edge.points[0].x for edge in self.edges])/len(self.edges),
                    sum([edge.points[0].y for edge in self.edges])/len(self.edges),
                    sum([edge.points[0].z for edge in self.edges])/len(self.edges)
        )

    def get_unit_normal(self):
        if None is not self.normal:
            return normalize_vector(self.normal)
        else:
            return None

    def get_normal(self):

        normal = np.cross(
            #two points from first edge
            (self.edges[0].points[1] - self.edges[0].points[0]).to_vector(),
            #point connecting last edge to origin, assume last edge connects to first
            (self.edges[len(self.edges)-1].points[0] - self.edges[len(self.edges)-1].points[1]).to_vector()
        )

        return normal

    def contains_edge(self, edge):
        #return any([(edge[0]==my_edge[0] and edge[1]==my_edge[1]) or (edge[1]==my_edge[0] and edge[0]==my_edge[1]) for my_edge in self.edges()])
        return any([my_edge == edge for my_edge in self.edges])

    def adjacent_to(self, other):
        """ return true if any edge matches """
        return any([other.contains_edge(edge) for edge in self.edges])

    def to_vector(self):
        return np.array([point for point in get_ordered_points_from_edges(self.edges)][:-1])

    def __str__(self):
        return str([edge.to_vector() for edge in self.edges]) + ":" + str(self.unit_normal)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not np.array_equal(self.normal, other.normal):
            return False

        if len(self.edges) != len(other.edges):
            return False
        #print("checking edges")
        #for i in range(len(self.edges)):
            #print("comparing edges")
            #print(self.edges[i])
            #print(other.edges[i])
            #print(self.edges[i] == other.edges[i])
        return all([self.edges[i] == other.edges[i] for i in range(len(self.edges))])

class Triangle(Face):
    def __init__(self, a, b, c, normal = None):
        super().__init__([a,b,c], normal)
        #print("old normal")
        #print(self.normal)
        #print("face midpoint")
        #print(midpoint)
        #print("normalized normal")
        #print(self.normal)
        pass

    def get_midpoint(self):
        return Point(
            (self.edges[0].points[0].x + self.edges[1].points[0].x + self.edges[2].points[0].x)/3,
            (self.edges[0].points[0].y + self.edges[1].points[0].y + self.edges[2].points[0].y)/3,
            (self.edges[0].points[0].z + self.edges[1].points[0].z + self.edges[2].points[0].z)/3
        )

class Model:
    """A collection of faces"""
    def __init__(self):
        self.faces = []
        origin = Point(0,0,0)

    def to_vector(self):
        return np.array([face.to_vector() for face in self.faces])

    def add_face(self, face):
        self.faces.append(face)
        #print("============== face ==============")
        #print(face.points)
        #print(face.normal)

    def get_reduced_model(self):
        """ Merge adjacent / coplanar surfaces into new polygons"""

        face_dict = {}
        #create a lookup dictionary of faces by normal for faster processing

        for face in self.faces:
            face_list = face_dict.setdefault(tuple(face.get_unit_normal()),[])
            face_list.append({"face":face,"assimilated":False})

        for normal,processed_faces in face_dict.items():
            #print("Side")
            #print(normal)
            #print("=======================================================")
            done = False
            while not done:
                #every time we find something, we need another run through
                found_something = False
                for i in range(len(processed_faces)):
                    #print("-----------------------")
                    #print("comparing face against %i faces" % len(processed_faces))
                    if not processed_faces[i]["assimilated"]:
                        for j in range(len(processed_faces)):
                            if processed_faces[j]["face"] == processed_faces[i]["face"]:
                                #skip self
                                pass
                            elif processed_faces[j]["assimilated"]:
                                #skip other faces that have already been assimilated
                                pass
                            elif processed_faces[j]["face"].adjacent_to(processed_faces[i]["face"]):
                                #this face is adjacent and should be merged / assimilated
                                processed_faces[i]["face"] = merge_faces(processed_faces[i]["face"],processed_faces[j]["face"])
                                processed_faces[j]["assimilated"] = True
                                found_something = True
                            else:
                                #not adjacent, nothing to do
                                pass
                if not found_something:
                    done = True

        new_model = Model()

        for normal,processed_faces in face_dict.items():
            for processed_face in processed_faces:
                if not processed_face["assimilated"]:
                    new_model.add_face(processed_face["face"])

        return new_model
