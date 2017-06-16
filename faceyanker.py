import os,platform
import pygame
from tkinter import *
from tkinter import filedialog
import numpy as np
from stl import mesh

import svgwrite

from meshloader import *

from geometry import Scene, ModelPlacement
from viewport import *

DEFAULT_MODEL_CANVAS_DIMENSIONS = (600,600)
class FaceYankerApp:

    def __init__(self,master, test=False):
        self.root = master
        self.model_screen = None
        self.model_viewport = Viewport(DEFAULT_MODEL_CANVAS_DIMENSIONS)
        self.scene = Scene()
        self.init_ui()
        if test:
            self.test()
        else:
            self.root.mainloop()

        try:
            self.root.destroy()
        except:
            pass

    def init_menu(self,frame):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Import Model", command=self.on_open)
        fileMenu.add_command(label="Export SVG", command=self.on_export)
        fileMenu.add_command(label="Exit", command=frame.quit)

        menubar.add_cascade(label="File", menu=fileMenu)

    def init_canvas(self):
        w = Canvas(self.root, width=300, height=450)
        w.pack(side="right",fill="both")

    def init_pygame_canvas(self):
        embed = Frame(self.root, width = DEFAULT_MODEL_CANVAS_DIMENSIONS[0], height = DEFAULT_MODEL_CANVAS_DIMENSIONS[1]) #creates embed frame for pygame window
        #embed.grid(columnspan = (600), rowspan = 500) # Adds grid
        embed.pack(side = LEFT) #packs window to the left
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.model_screen = pygame.display.set_mode(DEFAULT_MODEL_CANVAS_DIMENSIONS)
        self.model_screen.fill(pygame.Color(210,210,255))
        self.draw_model_grid()
        pygame.display.init()
        pygame.display.update()

    def draw_model_grid(self):
        pygame.draw.line(self.model_screen,(0,0,200),(0,0),(DEFAULT_MODEL_CANVAS_DIMENSIONS[0]-1,0),1)
        pygame.draw.line(self.model_screen,(0,0,200),(DEFAULT_MODEL_CANVAS_DIMENSIONS[0]-1,0),(DEFAULT_MODEL_CANVAS_DIMENSIONS[0]-1,DEFAULT_MODEL_CANVAS_DIMENSIONS[1]-1),1)
        pygame.draw.line(self.model_screen,(0,0,200),(DEFAULT_MODEL_CANVAS_DIMENSIONS[0]-1,DEFAULT_MODEL_CANVAS_DIMENSIONS[1]-1),(0,DEFAULT_MODEL_CANVAS_DIMENSIONS[1]-1),1)
        pygame.draw.line(self.model_screen,(0,0,200),(0,DEFAULT_MODEL_CANVAS_DIMENSIONS[1]-1),(0,0),1)


        for i in range(-5,5):
            pygame.draw.circle(
                self.model_screen,
                (1,1,1),
                self.model_viewport.project_point(Point(i*10,-5,100)),
                2,
                2
            )

            pygame.draw.line(self.model_screen,(200,0,0),
                self.model_viewport.project_point(Point(i*10,-5,1)),
                self.model_viewport.project_point(Point(i*10,-5,2000)),
                1
            )


        return

    def update_model_view(self):
        self.model_screen.fill(pygame.Color(210,210,255))

        self.draw_model_grid()

        for reference,model_placement in self.scene.model_placements.items():
            model = model_placement.model
            #print(model)

            for face in model.faces:
                #normal_coords = self.model_viewport.project_point(Point(face.normal[0],face.normal[1],face.normal[2]))
                face_midpoint = face.get_midpoint()
                normal_origin = self.model_viewport.project_point(face_midpoint)
                normal_coords = (face.unit_normal*3) + np.array([face_midpoint.x,face_midpoint.y,face_midpoint.z])
                normal_coords = self.model_viewport.project_point(Point(normal_coords[0],normal_coords[1],normal_coords[2]))

                pygame.draw.line(
                    self.model_screen,
                    (0,200,0),
                    normal_origin,
                    normal_coords,
                    1
                )

                for edge in face.edges:
                    #TODO, map coords to 2d canvas using environment (viewport object)
                    #coords = 5*int(30+point.x),5*int(30+point.y)
                    start_coords = self.model_viewport.project_point(edge.points[0])
                    end_coords = self.model_viewport.project_point(edge.points[1])
                    #print(coords)
                    #print("------------")
                    pygame.draw.circle(
                        self.model_screen,
                        (1,1,1),
                        start_coords,
                        2,
                        2
                    )
                    pygame.draw.line(self.model_screen,
                        (0,0,200),
                        start_coords,
                        end_coords,
                        1
                    )

        pygame.display.update()
        #print("model view updated")

    def keydown(self,event):
        if event.keysym_num > 0 and event.keysym_num < 60000:
            print('This is a printable key. The character is: %r keysym: %r %r' % \
                (event.char, event.keysym, event.keysym_num))
        else:
            print('This key is unprintable. The character is: %r keysym: %r %r' % \
                (event.char, event.keysym, event.keysym_num))

        if event.char == '-':
            self.model_viewport.zoomIn(1)
        if event.char == '+':
            self.model_viewport.zoomOut(1)
        if event.char == 'w':
            self.model_viewport.move(0,-1)
        if event.char == 'd':
            self.model_viewport.move(-1,0)
        if event.char == 's':
            self.model_viewport.move(0,1)
        if event.char == 'a':
            self.model_viewport.move(1,0)
        if event.char == '\r':
            self.flatten_model()
        self.update_model_view()

    def flatten_model(self):
        for reference,model_placement in self.scene.model_placements.items():
            model = model_placement.model
            reduced_model = model.get_reduced_model()
            model_placement.model = reduced_model


    def init_ui(self):
        frame = Frame(self.root)
        frame.pack()
        #self.root.bind("<KeyPress>", self.keydown)
        frame.bind("<KeyPress>", self.keydown)
        #frame.bind("<Left>", self.keydown)
        #frame.bind("<Left>", lambda event: print("press"))
        frame.focus_set()

        self.init_menu(frame)
        self.init_canvas()
        self.init_pygame_canvas()
#        self.button = Button(
#            frame, text="QUIT", fg="red", command=frame.quit
#        )
#        self.button.pack(side=LEFT)

    def test(self):
        print("testing")
        my_mesh = mesh.Mesh.from_file("//ORCHID/home/development/faceyanker/source-files/testcube_35mm.stl")
        model = model_from_mesh(my_mesh)
        self.scene.setModelPlacement(ModelPlacement("my_model",model,(0,0,0),None))
        self.update_model_view()
        self.flatten_model()

    def on_export(self):
        if 0 == len(self.scene.model_placements):
            raise Exception("nothing to export")

        filename = filedialog.asksaveasfilename(filetypes=[("SVG files", "*.svg")])

        if filename:
            dwg = svgwrite.Drawing(filename)
        else:
            return

        for reference,placement in self.scene.model_placements.items():
            for face in placement.model.faces:
                poly_2d = face.to2D()
                print("adding coordinates to a polygon")
                poly_points = poly_2d.get_points()
                #try converting to normal floats, dwg validator does not recognize numpy.float32
                poly_points = [[float(coord) for coord in point] for point in poly_points[:-1]]
                dwg.add(dwg.polygon(poly_points,stroke="black"))

        dwg.save()

    def on_open(self):
        filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("STL files", "*.stl"),("all files","*.*")))

        #print(filename)

        my_mesh = mesh.Mesh.from_file(filename)

        model = model_from_mesh(my_mesh)

        self.scene.setModelPlacement(ModelPlacement("my_model",model,(0,0,0),None))
        self.update_model_view()
        # The mesh vectors
        #print((my_mesh.v0, my_mesh.v1, my_mesh.v2))



def main():
    root = Tk()
    root.geometry("1200x800+300+10")
    app = FaceYankerApp(root,test=False)

if __name__ == '__main__':
    main()

#w = Label(root, text="Hello, world!")
#w.pack()

#root.mainloop()
