from geometry import Face,Edge,Point

origin = 0
side_length = 10

#bottom square
my_face = Face([
        Edge([
            Point(origin,origin,origin),
            Point(origin,origin,origin+side_length)
        ]),
        Edge([
            Point(origin,origin,origin+side_length),
            Point(origin+side_length,origin,origin+side_length)
        ]),
        Edge([
            Point(origin+side_length,origin,origin+side_length),
            Point(origin+side_length,origin,origin)
        ]),
        Edge([
            Point(origin+side_length,origin,origin),
            Point(origin,origin,origin)
        ])
])


#bottom square
my_face = Face([
        Edge([
            Point(origin,origin,origin),
            Point(origin,origin+side_length,origin)
        ]),
        Edge([
            Point(origin,origin+side_length,origin),
            Point(origin+side_length,origin+side_length,origin)
        ]),
        Edge([
            Point(origin+side_length,origin+side_length,origin),
            Point(origin+side_length,origin,origin)
        ]),
        Edge([
            Point(origin+side_length,origin,origin),
            Point(origin,origin,origin)
        ])
])



print("prepping face")
print(my_face)
print(my_face.to2D().get_points())
