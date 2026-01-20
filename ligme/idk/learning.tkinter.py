import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Ilans test thingy")

tk.Label(root, text="test").pack()
something_cool= tk.Entry(root)
something_cool.pack()
tk.Button(root, text="press me", command=something_cool).pack(pady= 6)

def something_cool():
    canvas = tk.canvas(root, width= 300, height = 90, bg= "black")
    canvas.pack(pady=6)



root.mainloop()