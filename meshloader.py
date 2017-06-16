from geometry import Model,Triangle,Point,Edge

#from numpy import matrix

def model_from_mesh(mesh):
    model = Model()

    for i in range(len(mesh.vectors)):

        #my_normal = np.cross(
        #    mesh.vectors[i][1]-mesh.vectors[i][0],
        #    mesh.vectors[i][2]-mesh.vectors[i][0]
        #)

        #magnitude  = sqrt( x2+ y2+ z2)
        #unit vector  = ( x / magnitude ,  y / magnitude,  z / magnitude )
        #my_normal = mesh.normals[i]
        #my_normal = my_normal/math.sqrt( my_normal[0]*my_normal[0] + my_normal[1]*my_normal[1]+ my_normal[2]*my_normal[2])

        #print(my_normal)e
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
