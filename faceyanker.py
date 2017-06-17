import os,platform
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.ttk import Treeview

import numpy as np
from stl import mesh
import svgwrite

from meshloader import *
from scene import Scene, SceneViewer

DEFAULT_MODEL_CANVAS_DIMENSIONS = (600,600)
DEBUG = False

class FaceYankerApp:
    def __init__(self,master, test=False):
        self.root = master
        self.model_screen = None
        self.init_ui()
        self.embed_sdl()
        self.scene = Scene()
        self.scene_viewer = SceneViewer(self.scene,DEFAULT_MODEL_CANVAS_DIMENSIONS)
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
        viewMenu.add_command(label="Toggle Normals", underline=7, command=self.on_toggle_normals)
        viewMenu.add_command(label="Toggle Grid", underline=7, command=self.on_toggle_grid)
        viewMenu.add_command(label="Toggle Model Tree", underline=7)
        menubar.add_cascade(label="View", menu=viewMenu, underline=0)

    def init_canvas(self):
        """ reserved for non pygame canvas stuff (placeholder) """
        w = Canvas(self.root, width=300, height=450)
        w.pack(side="right",fill="both")

    def embed_sdl(self):
        embed = Frame(self.root, width = DEFAULT_MODEL_CANVAS_DIMENSIONS[0], height = DEFAULT_MODEL_CANVAS_DIMENSIONS[1]) #creates embed frame for pygame window
        #embed.grid(columnspan = (600), rowspan = 500) # Adds grid
        embed.pack(side = LEFT) #packs window to the left
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'

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

        if DEBUG:
            if event.keysym_num > 0 and event.keysym_num < 60000:
                print('This is a printable key. The character is: %r keysym: %r %r' % \
                    (event.char, event.keysym, event.keysym_num))
            else:
                print('This key is unprintable. The character is: %r keysym: %r %r' % \
                    (event.char, event.keysym, event.keysym_num))

        if event.char == '-':
            self.scene_viewer.zoomIn(1)
        if event.char == '+':
            self.scene_viewer.zoomOut(1)
        if event.char == 'w':
            self.scene_viewer.move(0,-1)
        if event.char == 'd':
            self.scene_viewer.move(-1,0)
        if event.char == 's':
            self.scene_viewer.move(0,1)
        if event.char == 'a':
            self.scene_viewer.move(1,0)
        if event.char == '\r':
            self.flatten_model()

        self.scene_viewer.update()

    def on_toggle_grid(self):
        self.scene_viewer.toggleShowGrid()
        self.scene_viewer.update()

    def on_toggle_normals(self):
        self.scene_viewer.toggleShowNormals()
        self.scene_viewer.update()


    def on_flatten_model(self):
        """ called when flatten model is selected from menu
            allows for other processing if needed
        """
        self.flatten_model()
        self.scene_viewer.update()

    def flatten_model(self):
        for reference,model_placement in self.scene.model_placements.items():
            model = model_placement.model
            reduced_model = model.get_reduced_model()
            model_placement.model = reduced_model

    def test(self):
        print("testing")
        my_mesh = mesh.Mesh.from_file("//ORCHID/home/development/faceyanker/source-files/testcube_35mm.stl")
        model = model_from_mesh(my_mesh)
        self.scene.addModel("my_model",model,(0,0,0),None)
        self.scene_viewer.update()
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
        item = self.model_explorer.focus()
        print("you clicked on", self.model_explorer.item(item,"text"))

    def on_open(self):
        filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("STL files", "*.stl"),("all files","*.*")))
        my_mesh = mesh.Mesh.from_file(filename)
        model = model_from_mesh(my_mesh)

        self.scene.addModel("my_model",model,(0,0,0),None)
        self.scene_viewer.update()
        self.update_model_explorer()


def main():
    root = Tk()
    root.geometry("1200x800+300+10")
    app = FaceYankerApp(root,test=False)

if __name__ == '__main__':
    main()

#w = Label(root, text="Hello, world!")
#w.pack()

#root.mainloop()
