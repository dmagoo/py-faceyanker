from geometry import Model,Triangle,Point,Edge

def model_from_mesh(mesh):
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
