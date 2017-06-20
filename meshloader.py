from geometry import Model,Triangle,Point,Edge
import numpy as np

def get_mesh_extents(mesh):
    all_points = np.concatenate((mesh.v0, mesh.v1,mesh.v2))

    extents = [np.amin(all_points, axis=0),np.amax(all_points, axis=0)]

    return extents

def remove_negatives(mesh):
    """ Translate the mesh so that all points are positive """
    extents = get_mesh_extents(mesh)

    mesh.translate(
        np.amin([extents[0],[0,0,0]],axis=0)*-1
    )

def center_mesh(mesh, point):
    """ center the mesh on the given point """
    mesh.translate(
        np.array(mesh.get_mass_properties()[1])-np.array(point)
    )



def model_from_mesh(mesh):
    extents = get_mesh_extents(mesh)
    center_mesh(mesh,[0,(extents[0][1]-extents[1][1])/2,extents[0][2]])

    model = Model()
    for i in range(len(mesh.vectors)):
        e1 = Edge([
            Point(mesh.vectors[i][0][0],mesh.vectors[i][0][1],mesh.vectors[i][0][2]),
            Point(mesh.vectors[i][1][0],mesh.vectors[i][1][1],mesh.vectors[i][1][2])
        ])
        e2 = Edge([
            Point(mesh.vectors[i][1][0],mesh.vectors[i][1][1],mesh.vectors[i][1][2]),
            Point(mesh.vectors[i][2][0],mesh.vectors[i][2][1],mesh.vectors[i][2][2])
        ])
        e3 = Edge([
            Point(mesh.vectors[i][2][0],mesh.vectors[i][2][1],mesh.vectors[i][2][2]),
            Point(mesh.vectors[i][0][0],mesh.vectors[i][0][1],mesh.vectors[i][0][2])
        ])

        model.add_face(
            Triangle(e1,e2,e3, mesh.normals[i])
        )
    return model
