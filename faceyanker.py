import os,platform
import pygame
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.ttk import Treeview

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

    def init_ui(self):
        frame = Frame(self.root)
        frame.pack()
        frame.bind("<KeyPress>", self.keydown)
        frame.focus_set()

        self.init_menu(frame)
        self.init_canvas()
        self.model_explorer = self.init_model_explorer()
        self.init_pygame_canvas()

    def init_menu(self,frame):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Import Model", command=self.on_open, accelerator="Ctrl+O", underline=0)
        fileMenu.add_command(label="Export SVG", command=self.on_export, accelerator="Ctrl+S", underline=0)
        fileMenu.add_command(label="Exit", command=frame.quit, accelerator="Ctrl+X", underline=1)
        menubar.add_cascade(label="File", menu=fileMenu, underline=0)

        modelMenu = Menu(menubar)
        modelMenu.add_command(label="Reduce Model", command=self.on_flatten_model, underline=0)
        menubar.add_cascade(label="Model", menu=modelMenu, underline=0)

        viewMenu = Menu(menubar)
        viewMenu.add_command(label="Toggle Normals", underline=7)
        viewMenu.add_command(label="Toggle Grid", underline=7)
        viewMenu.add_command(label="Toggle Model Tree", underline=7)
        menubar.add_cascade(label="View", menu=viewMenu, underline=0)

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

    def init_model_explorer(self):
        tree = ttk.Treeview(self.root,columns=("normal"), displaycolumns="normal", height=35)
        tree.column("normal", width=75)
        tree.heading("normal", text="Normal")
        tree.tag_bind("face","<ButtonRelease-1>", self.on_face_select)
        my_scroll = ttk.Scrollbar(orient="vertical")
        my_scroll.configure(command=tree.yview)
        tree.configure(yscrollcommand=my_scroll)
        tree.pack(side=LEFT, fill="y")
        my_scroll.pack(side=LEFT, fill="y", expand=False)#grid(row=1, column=2, sticky="W")

        return tree

    def update_model_explorer(self):
        tree = self.model_explorer
        for reference,model_placement in self.scene.model_placements.items():
            print(model_placement.reference)
            model_root = tree.insert("", 1, model_placement.reference, text=model_placement.reference, open=True)
            model = model_placement.model
            i = 0
            for face in model.faces:
                print(face.get_unit_normal())
                tree.insert(
                    model_root,
                    "end",
                    model_placement.reference + "-" + str(i),
                    text=hex(i),
                    values=(face.get_unit_normal(),),
                    tags=("face",)
                )

                i = i + 1

        ##alternatively:
        #tree.insert("", 3, "dir3", text="Dir 3")
        #tree.insert("dir3", 3, text=" sub dir 3",values=("3A"," 3B"))

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

    def on_flatten_model(self):
        """ called when flatten model is selected from menu
            allows for other processing if needed
        """
        self.flatten_model()
        self.update_model_view()

    def flatten_model(self):
        for reference,model_placement in self.scene.model_placements.items():
            model = model_placement.model
            reduced_model = model.get_reduced_model()
            model_placement.model = reduced_model

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

    def on_face_select(self, e):
        #print(e)
        #selected_items = self.model_explorer.selection()
        item = self.model_explorer.focus()
        #print(len(selected_items))
        #for item in selected_items:
        print("you clicked on", self.model_explorer.item(item,"text"))

    def on_open(self):
        filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("STL files", "*.stl"),("all files","*.*")))

        #print(filename)

        my_mesh = mesh.Mesh.from_file(filename)

        model = model_from_mesh(my_mesh)

        self.scene.setModelPlacement(ModelPlacement("my_model",model,(0,0,0),None))
        self.update_model_view()
        self.update_model_explorer()


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
