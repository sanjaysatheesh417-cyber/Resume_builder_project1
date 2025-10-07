from tkinter import Tk, Frame, Label, Button, messagebox, Entry
from reportlab.pdfgen import canvas

def g():
    n = e1.get()
    a = e2.get()

    if not n or not a.isdigit():
        messagebox.showerror("Error", "Please enter a valid integer")
        return

    fn = f"{n.replace(' ','_')}.pdf"
    c = canvas.Canvas(fn)
    c.drawString(100, 750,f"Name: {n}")
    c.drawString(100, 730,f"Age: {a}")
    c.save()

    messagebox.showinfo("Success", "PDF file saved")

r = Tk()
Label(r, text="Name").pack()
e1 = Entry(r)
e1.pack()

Label(r, text="Age").pack()
e2 = Entry(r)
e2.pack()

Button(r, text="Gen pdf", command=g).pack()
r.mainloop()