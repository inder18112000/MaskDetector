
from tkinter import *
from tkinter.messagebox import *
import connection
from tkinter.ttk import Combobox, Style, Treeview
import otp
import cv2
import PIL.Image, PIL.ImageTk
from datetime import datetime
import sms_sending
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class showsurv:
    def getValues(self):
        conn = connection.Connect()
        cr = conn.cursor()
        q = 'SELECT * FROM `survielance`'
        cr.execute(q)
        result = cr.fetchall()
        x = []
        for row in result:
            lst = list(row)
            x.append(lst)
        for k in self.obj.get_children():
            self.obj.delete(k)
        count = 0
        for i in x:
            self.obj.insert('', index=count, values=i)
            count += 1

    def __init__(self):
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title('Mask Detector - View Admin')

        self.f1 = Frame(self.root)
        Label(self.root, text='History', font=('arial', 38, 'bold')).pack(pady=30)
        col = ('SID', 'SURVILLIANCE LOC', 'DATE OF SURVILLIANCE','START TIME','END TIME','MASKED POPULATION','UNMASKED POPULATION',)
        self.obj = Treeview(self.root, columns=col)
        for i in col:
            self.obj.heading(i, text=i.capitalize())
        self.obj['show'] = 'headings'
        # self.getValues()
        self.getValues()
        # self.obj.bind('<Double-1>', self.onDoubleClick)
        self.obj.pack()
        self.f1.pack()
        self.root.mainloop()

class comp_show:

    def __init__(self):
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title('Mask Detector - Registered Compalaints')
        self.root.config(bg="orange")
        self.f1 = Frame(self.root,bg="orange")
        Label(self.root, text='Registered Complaints', bg="orange",fg="white",font=('arial', 38, 'bold')).pack(padx=10,pady=30)
        self.f1.pack(pady=30)
        Label(self.f1, text = 'Surviellance Locations: ', bg = "orange", fg = "white",
              font = ('arial', 14, 'bold')).grid(row=0,column=0,padx = 5, pady = 5)
        cr = conn.cursor()
        q2 = 'select * from surv_loc'
        cr.execute(q2)
        self.res = cr.fetchall()

        self.l = []
        for i in self.res:
            self.l.append(i[0])
        self.l.append("All Locations")

        style = Style()
        style.configure('my.TCombobox', arrowsize = 30)
        style.configure('Vertical.TScrollbar', arrowsize = 25)

        self.s_loc = Combobox(self.f1, value = self.l, font = ('Comic Sans MS', 12), width = 25,
                              state = 'readonly', style = 'my.TCombobox')
        self.s_loc.grid(row=0,column=1, padx = 5, pady = 5)




        col = ('CID', 'NAME', 'MOBILE', 'EMAIL', 'REPORT', 'SURVILLIANCE LOC', 'STATUS')
        self.obj = Treeview(self.root, columns=col)
        for i in col:

            self.obj.heading(i, text=i.capitalize())
        self.obj['show'] = 'headings'
        # self.getValues()
        self.search = Button(self.f1,text="Search",bg="orange",fg = "white",
              font = ('arial', 16, 'bold'),command=self.search)
        self.search.grid(row=1,column=0,columnspan=2,padx=10,pady=30)

        # self.obj.bind('<Double-1>', self.onDoubleClick)
        self.obj.pack(padx=10,pady=10)

        self.root.mainloop()

    def search(self):
        s = self.s_loc.get()

        if self.s_loc.get() == "All Locations" or self.s_loc.get() == "":
            cr = conn.cursor()
            q = 'SELECT * FROM `complaint`'
            cr.execute(q)
            result = cr.fetchall()
            x = []
            for row in result:
                lst = list(row)
                x.append(lst)
            for k in self.obj.get_children():
                self.obj.delete(k)
            count = 0
            for i in x:
                self.obj.insert('', index = count, values = i)
                count += 1
        else:
            cr = conn.cursor()
            q = 'select * from complaint where s_loc like "{}"'.format(s)
            cr.execute(q)
            result = cr.fetchall()
            count = 0
            for i in self.obj.get_children():
                self.obj.delete(i)
            for i in result:
                self.obj.insert('',index = count, value=i)
                count += 1


class view:

    def getValues(self):
        conn = connection.Connect()
        cr = conn.cursor()
        q = 'select username,email,role from login'
        cr.execute(q)
        result = cr.fetchall()
        x = []
        for row in result:
            lst = list(row)
            x.append(lst)
        for k in self.obj.get_children():
            self.obj.delete(k)
        count = 0
        for i in x:
            self.obj.insert('', index=count, values=i)
            count += 1

    def __init__(self):
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title('Mask Detector - View Admin')

        self.f1 = Frame(self.root)
        Label(self.root, text='View Admins', font=('arial', 38, 'bold')).pack(pady=10)
        col = ('Username', 'email', 'role')
        self.obj = Treeview(self.root, columns=col)
        for i in col:
            self.obj.heading(i, text=i.capitalize())
        self.obj['show'] = 'headings'
        self.getValues()
        # self.getValues()
        self.obj.bind('<Double-1>', self.onDoubleClick)
        self.obj.pack()
        self.f1.pack()
        self.root.mainloop()

    def onDoubleClick(self, event):
        print(self.obj.focus())
        # print(self.obj.selection())
        self.items = self.obj.item(self.obj.focus())['values']
        print(self.items)
        conn = connection.Connect()
        cr = conn.cursor()
        # q = 'select password from login where email="{}"'.format(self.items[1])
        # cr.execute(q)
        # result = cr.fetchone()
        self.r1 = Toplevel()
        self.r1.title('Update Users')
        self.r1.geometry('500x500')
        Label(self.r1, text='Admin', font=('arial', 26, 'bold')).pack()
        Label(self.r1, text='Email').pack(pady=10)
        self.txt1 = Entry(self.r1, width=50)
        self.txt1.pack(pady=10)
        Label(self.r1, text='Enter Username').pack(pady=10)
        self.txt2 = Entry(self.r1, width=50)
        self.txt2.pack(pady=10)
        Label(self.r1, text='Select Role').pack(pady=10)
        col = ['Super Admin', 'Admin']
        current = col.index(self.items[2])
        self.txt3 = Combobox(self.r1, width=47, value=col, state='readonly')
        self.txt3.pack(pady=10)
        Button(self.r1, text='Update', command=self.updateUser).pack()
        Button(self.r1, text='Delete', command=self.deleteUser).pack(pady=5)
        self.txt3.current(current)
        self.txt1.insert(0, self.items[1])
        self.txt1.config(state='readonly')
        self.txt2.insert(0, self.items[0])
        self.r1.mainloop()

    def updateUser(self):
        self.email = self.txt1.get()
        self.username = self.txt2.get()
        self.role = self.txt3.get()
        conn = connection.Connect()
        cr = conn.cursor()
        q = 'update login set username="{}", role="{}" where email="{}"'.format(self.username, self.role, self.email)
        cr.execute(q)
        conn.commit()
        showinfo("Update","Updated Successfully")
        self.getValues()
        self.r1.destroy()

    def deleteUser(self):
        self.email = self.txt1.get()
        conn= connection.Connect()

        cr = conn.cursor()
        q = 'delete from login where email="{}"'.format(self.email)
        cr.execute(q)
        conn.commit()
        self.getValues()
        self.r1.destroy()

class log:

    def __init__(self):

        # THIS IS OUR MAIN WINDOW/LOGIN SCREEN
        self.root = Tk()
        self.root.state("zoomed")

        self.root.geometry("1550x766")
        self.root.title("MASK DETECTOR")
        self.photo = PhotoImage(file = "icon.png")
        self.root.iconphoto(False, self.photo)
        self.open = PhotoImage(file = "front_login.png")
        self.front_label1 = Label(self.root, image = self.open)
        self.front_label1.place(x = 0, y = 0)


        self.bf1 = Frame(self.root, padx = 20, pady = 20, bg = "white", height = 40, width = 60)
        self.bf1.place(x = 150, y = 380)

        self.bf2 = Button(self.root,text="Register Complaints\n{ Only for user }",height=2,bg = "red",fg="white",font = ('Comic Sans MS', 14, 'bold'),command=self.complaint)
        self.bf2.pack(padx=10,pady=10,anchor=NE)
        Label(self.bf1, text = 'Enter Email', font = ('Comic Sans MS', 14, 'bold')).grid(row = 1, column = 0, padx = 5, pady = 10)

        self.txt1 = Entry(self.bf1, font = ('arial', 14, 'bold'), width = 40)
        self.txt1.grid(row = 1, column = 1, pady = 10)
        Label(self.bf1, text = 'Enter Password', font = ('Comic Sans MS', 14, 'bold')).grid(row = 2, column = 0, padx = 5, pady = 10)
        self.txt2 = Entry(self.bf1, font = ('arial', 14, 'bold'), width = 40, show = '*')
        self.txt2.grid(row = 2, column = 1, pady = 10)

        self.log_butt = Button(self.bf1, text = 'Login', font = ('arial', 16, 'bold'), bg="#4267B2", fg="white",width = 20, command=self.checkLogin)
        self.log_butt.grid(row=3, column=0, columnspan=2, pady=25)
        Button(self.bf1, text = 'Forgot Password', font = ('arial', 16, 'bold'), relief=FLAT, bg = "orange", fg = "white", width = 20,command = self.fp).grid(row = 4, column = 0, columnspan = 2)

        #Button(self.bf1, text = 'Create new account', borderwidth = 2
        #, font = ('arial', 16, 'bold'), bg = "Orange", fg = "white", width = 20, command = se lf.create).grid(row = 5, column = 0, columnspan = 2, pady = 10)

        self.root.mainloop()

    def complaint(self):
        self.root.destroy()
        comp()


    def create(self):
        self.root.destroy()
        add()


    def fp(self):
        self.root.destroy()
        obj1 = forgot()
        obj1.password()
        log()

    def checkLogin(self):

        # print(self.password,self.email)
        if self.txt1.get() == '' and self.txt2.get() == '':
            showerror('', 'Please Enter the data')
        else:

            cr = conn.cursor()
            q = 'select * from login where email="{}" and password="{}"'.format(self.txt1.get(), self.txt2.get())
            cr.execute(q)

            self.result = cr.fetchone()
            print(self.result)
            if self.result is None:
                showerror('', 'Invalid Email/Password')
            else:
                if self.result[3] == "Super Admin":
                    self.str1 = otp.send(self.result[1])
                    self.root1 = Tk()
                    self.root1.title("")
                    self.root1.config(bg="sky blue")
                    self.bf = Frame(self.root1, padx = 20, pady = 20, bg = "sky blue", height = 40, width = 60)
                    self.bf.pack()
                    Label(self.bf, text="ENTER OTP ",font = ('Comic Sans MS', 12, 'bold'),bg="orange",fg="white",width=25).grid(row=0, column=0,padx=5,pady=5)
                    self.e1 = Entry(self.bf, font = ('Comic Sans MS', 12), width=25,fg="blue",justify="center")
                    self.e1.grid(row=1, column=0, padx=5, pady=5)
                    Button(self.bf, text = 'VERIFY', font = ('Comic Sans MS', 12, 'bold'), bg = "green", fg = "white", width = 25, command = self.press).grid(row = 2, column = 0,columnspan=2,pady=5)
                    self.root1.mainloop()

                else:
                    showinfo('', 'Login Successful')
                    self.root.destroy()
                    global result
                    result = self.result
                    dasboard_light(result)

    def press(self):
        if str(self.str1) == str(self.e1.get()):
            showinfo('', 'Login Successful')
            self.root.destroy()
            self.root1.destroy()
            global result
            result = self.result
            dasboard_light(result)


        elif str(self.e1.get()) == "":
            showerror("Error", "Please enter otp...")
        else:
            showerror("Error", "Please enter correct otp !")

#Complaint form
class comp:
    def back(self):
        self.com.destroy()
        log()

    def sub_comp(self):
        if str(self.r.get())=="a":
            self.report = str(self.T.get(1.0, "end-2c"))
        else:
            self.report = str(self.r.get())

        cr = conn.cursor()
        if str(self.email.get()) == '' and str(self.phone.get()) == '' and str(self.name.get()) == '' and str(self.s_loc.get()) == "":
            showerror('', 'Please Enter the data')
        else:
            q = 'select * from complaint where email="{}"'.format(self.email.get())
            cr.execute(q)
            result = cr.fetchone()
            if result == None:
                q1 = 'insert into complaint (name,mobile,email,report,s_loc) values("{}","{}","{}","{}","{}")'.format(str(self.name.get()), str(self.phone.get()),str(self.email.get()), self.report, str(self.s_loc.get()))

                cr.execute(q1)
                conn.commit()
                showinfo("","Complaint registered successfully")
                sms_sending.send_sms(str(self.phone.get()))

                self.com.destroy()
                log()
            else:
                showerror('', 'Complaint already registered')

    def ShowChoice(self):
        self.T.delete(1.0, END)
        self.T.config(state = DISABLED)

        if str(self.r.get()) == "a":
            self.T.config(state = NORMAL)


    def __init__(self):
        self.com = Tk()
        self.com.state("zoomed")
        self.com.geometry("1550x766")
        self.com.title("MASK DETECTOR")
        self.photo = PhotoImage(file = "icon.png")
        self.com.iconphoto(False, self.photo)
        self.open = PhotoImage(file = "comp_bg.png")
        self.front_label1 = Label(self.com, image = self.open)
        self.front_label1.place(x = 0, y = 0)
        self.bf1 = Frame(self.com, padx = 10, pady = 10, bg = "white", height = 40, width = 60)
        self.bf1.place(x = 800, y = 100, anchor = CENTER)
        Label(self.bf1, text = 'Complaint Form', font = ('Comic Sans MS', 30, 'bold')).pack()
        self.bf2 = Frame(self.com, padx = 10, pady = 10, bg = "white", height = 40, width = 60)
        self.bf2.place(x = 800, y = 450, anchor = CENTER)
        Label(self.bf2, text = 'Name', font = ('Comic Sans MS', 14, 'bold'), bg = "orange", fg = "white",
              width = 17).grid(row = 0, column = 0, padx = 15,
                               pady = 10)
        Label(self.bf2, text = 'Phone No.', font = ('Comic Sans MS', 14, 'bold'), bg = "orange", fg = "white",
              width = 17).grid(row = 1, column = 0, padx = 15,
                               pady = 1)
        Label(self.bf2, text = 'E-Mail', font = ('Comic Sans MS', 14, 'bold'), bg = "orange", fg = "white",
              width = 17).grid(row = 2, column = 0, padx = 15,
                               pady = 1)
        Label(self.bf2, text = 'Surveillance Loc.', font = ('Comic Sans MS', 14, 'bold'), bg = "orange", fg = "white",
              width = 17).grid(row = 3, column = 0, padx = 15,
                               pady = 1)
        Label(self.bf2, text = 'Report', font = ('Comic Sans MS', 14, 'bold'), bg = "orange", fg = "white",
              width = 17).grid(row = 4, column = 0, padx = 15,
                               pady = 1)
        self.name = Entry(self.bf2, font = ('arial', 14), width = 35)
        self.name.grid(row = 0, column = 1, pady = 10)
        self.phone = Entry(self.bf2, font = ('arial', 14), width = 35)
        self.phone.grid(row = 1, column = 1, pady = 10)
        self.email = Entry(self.bf2, font = ('arial', 14), width = 35)
        self.email.grid(row = 2, column = 1, pady = 10)

        cr = conn.cursor()
        q2='select * from surv_loc'
        cr.execute(q2)
        self.res = cr.fetchall()

        print(self.res)
        self.l = []
        for i in self.res:
            self.l.append(i[0])

        style = Style()
        style.configure('my.TCombobox', arrowsize = 30)
        style.configure('Vertical.TScrollbar', arrowsize = 25)

        self.s_loc = Combobox(self.bf2, value = self.l, font = ('arial', 14), width = 33,
                             state = 'readonly', style='my.TCombobox')
        self.s_loc.grid(row = 3, column = 1, pady = 10)
        self.r = StringVar()
        self.r.set("Wearing Mask Violation")

        Radiobutton(self.bf2, text = "Wearing Mask Violation          ", font = ('arial', 14, 'bold'), variable = self.r,
                    value = "Wearing Mask Violation", command = self.ShowChoice).grid(row = 4, column = 1, padx = 5,
                                                                                      pady = 1)
        Radiobutton(self.bf2, text = "Social Distancing Violation    ", font = ('arial', 14, 'bold'), variable = self.r,
                    value = "Social Distancing Violation",
                    command = self.ShowChoice).grid(row = 5, column = 1, padx = 5,
                                                    pady = 1)
        Radiobutton(self.bf2, text = "Other                                           ", font = ('arial', 14, 'bold'),
                    variable = self.r, value = "a",
                    command = self.ShowChoice).grid(row = 6, column = 1, padx = 5, pady = 1)


        self.T = Text(self.bf2, font = ('Comic Sans MS', 12), height = 7, width = 30,borderwidth=5)
        self.T.grid(row = 7, column = 1,pady=20)
        self.T.config(state=DISABLED)
        Button(self.bf2, text = "Back", font = ('Comic Sans MS', 14, 'bold'), bg = "sky blue", fg = "white",
               command = self.back, borderwidth = 0,width=15).grid(row = 8, column = 0, padx = 10,
                                                              pady = 20)
        Button(self.bf2, text="Submit",font = ('Comic Sans MS', 14, 'bold'),width=15, bg = "sky blue",fg="white", command = self.sub_comp, borderwidth = 0).grid(row = 8,column = 1, padx = 10,
                                                                                                        pady = 20)


        self.com.mainloop()

# Add new admin
class add:
    def back(self):
        global result

        self.roota.destroy()
        global mode
        if mode==1:
            dasboard(result)
        else:
            dasboard_light(result)

    def press(self):
        if str(self.str1) == str(self.e1.get()):
            cr = conn.cursor()
            q = 'insert into login value("{}","{}","{}","{}")'.format(self.username, self.email, self.password,
                                                                      self.role)
            cr.execute(q)
            conn.commit()
            showinfo('', 'User added succesfully')
            global result

            self.roota.destroy()
            dasboard(result)
            self.root1.destroy()
        elif str(self.e1.get()) == "":
            showerror("Error", "Please enter otp...")
        else:
            showerror("Error", "Please enter correct otp !")

    def checkLogin(self):
        self.username=self.txt4.get()
        self.email = self.txt1.get()
        self.password = self.txt2.get()

        self.role = self.txt3.get()
        # print(self.password,self.email)
        conn = connection.Connect()
        cr = conn.cursor()
        if self.email == '' and self.password == '' and self.role == '':
            showerror('', 'Please Enter the data')
        else:

            q = 'select * from login where email="{}"'.format(self.email)
            cr.execute(q)
            result = cr.fetchone()
            if result == None:
                    self.str1 = otp.send(self.email)
                    self.root1 = Tk()
                    self.root1.title("Mask Detector - Verify ")

                    self.root1.config(bg = "sky blue")
                    self.bf = Frame(self.root1, padx = 20, pady = 20, bg = "sky blue", height = 40, width = 60)
                    self.bf.pack()
                    Label(self.bf, text = "ENTER OTP ", font = ('Comic Sans MS', 12, 'bold'), bg = "orange",
                          fg = "white", width = 25).grid(row = 0, column = 0, padx = 5, pady = 5)
                    self.e1 = Entry(self.bf, font = ('Comic Sans MS', 12), width = 25, fg = "blue", justify = "center")
                    self.e1.grid(row = 1, column = 0, padx = 5, pady = 5)
                    Button(self.bf, text = 'VERIFY', font = ('Comic Sans MS', 12, 'bold'), bg = "green", fg = "white",
                           width = 25, command = self.press).grid(row = 2, column = 0, columnspan = 2, pady = 5)
                    self.root1.mainloop()




            else:
                showerror('', 'User Already Registered')

    def __init__(self):
        self.roota = Tk()
        self.roota.geometry("1920x1080")
        self.roota.state("zoomed")

        self.roota.title("MASK DETECTOR")
        self.photo = PhotoImage(file = "icon.png")
        self.roota.iconphoto(False, self.photo)
        self.open = PhotoImage(file = "add.png")

        self.front_label1 = Label(self.roota, image = self.open)
        self.front_label1.place(x = 0, y = 0)

        # self.bf3 = Frame(self.roota, padx = 0, pady = 0, bg = "black", height = 40, width = 60)
        # self.bf3.place(x=0, y=0)
        self.bf1 = Frame(self.roota, padx = 20, pady = 20, bg = "white", height = 40, width = 60)
        self.bf1.place(x = 150, y = 350)
        self.bf2 = Frame(self.roota, padx = 20, pady = 20, bg = "white", height = 40, width = 60)
        self.bf2.place(x = 180, y = 600)
        Label(self.bf1, text = 'Enter Username', font = ('Comic Sans MS', 14, 'bold'), bg = "grey", fg = "white",width = 15).grid(row = 0, column = 0, padx = 15,pady = 10)

        self.txt4 = Entry(self.bf1, font = ('arial', 14), width = 35)
        self.txt4.grid(row = 0, column = 1, pady = 10)
        Label(self.bf1, text = 'Enter E-mail', font = ('Comic Sans MS', 14, 'bold'), bg = "grey", fg = "white",width = 15).grid(row = 1, column = 0, padx = 15,pady = 10)

        self.txt1 = Entry(self.bf1, font = ('arial', 14), width = 35)
        self.txt1.grid(row = 1, column = 1, pady = 10)
        Label(self.bf1, text = 'Enter Password', font = ('Comic Sans MS', 14, 'bold'), bg = "grey", fg = "white",width = 15).grid(row = 2, column = 0, padx = 15,pady = 10)

        self.txt2 = Entry(self.bf1, font = ('arial', 14),show="*",
                          width = 35)
        self.txt2.grid(row = 2, column = 1, pady = 10)
        Label(self.bf1, text = 'Select Role', font = ('Comic Sans MS', 14, 'bold'), bg = "grey", fg = "white",width = 15).grid(row = 3, column = 0, padx = 15,pady = 10)
        self.txt3 = Combobox(self.bf1, value = ('Super Admin', 'Admin'),font = ('arial', 14), width = 33, state = 'readonly')
        self.txt3.grid(row = 3, column = 1, pady = 10)
        Button(self.bf2, text = 'Back', font = ('Comic Sans MS', 14, 'bold'), bg = "sky blue", width = 20,
               command = self.back).grid(row = 4, column = 0, pady = 10, padx = 10)
        Button(self.bf2, text = 'Create New Account',font = ('Comic Sans MS', 14, 'bold'),bg="sky blue", width = 20, command = self.checkLogin).grid(row=4,column=1,pady=10,padx=10)
        # self.back = PhotoImage(file = "back.png")
        #
        # self.back = self.back.subsample(5)
        # Button(self.bf3, image = self.back,command=self.back).grid(row = 0, column = 0, pady = 0)

        self.roota.mainloop()


#Forgot password
class forgot:
    def password(self):
        self.rootf = Tk()
        self.rootf.geometry("1920x1080")
        self.rootf.state("zoomed")

        self.rootf.title("MASK DETECTOR")
        self.photo = PhotoImage(file = "icon.png")
        self.rootf.iconphoto(False, self.photo)
        self.open = PhotoImage(file = "bg_fg.png")
        self.front_label1 = Label(self.rootf, image = self.open)
        self.front_label1.place(x = 0, y = 0)

        self.bf1 = Frame(self.rootf, padx = 20, pady = 20, bg = "white", height = 40, width = 60)
        self.bf1.place(x = 800, y = 100, anchor = CENTER)

        Label(self.bf1, text = 'FORGOT PASSWORD', font = ('cooper black', 32, 'bold', 'underline')).pack()


        self.bf2 = Frame(self.rootf, padx = 20, pady = 20, bg = "white", height = 40, width = 60)
        self.bf2.place(x = 800, y = 400, anchor = CENTER)

        Label(self.bf2, text = 'ENTER EMAIL', font = ('arial', 14, 'bold')).grid(row = 0, column = 0, padx = 5, pady = 10)
        self.e1 = Entry(self.bf2, font = ('arial', 14, 'bold'), width = 40)
        self.e1.grid(row =0, column=1)
        Button(self.bf2, text="GENERATE OTP", font = ('arial', 14, 'bold'), bg = "#4ac959", fg = "white", width = 20, command = self.gen).grid(row = 1, column = 0, columnspan =2, padx = 5, pady = 20)
        self.rootf.mainloop()



    def gen(self):
        if self.e1.get() == "":
            showerror("MD","Please enter email id !")
        else:
            conn = connection.Connect()
            cr = conn.cursor()
            q = 'select * from login where email="{}"'.format(self.e1.get())
            cr.execute(q)
            self.result = cr.fetchone()
            print(self.result)
            if self.result is None:
                showerror('', 'Invalid Email/Password')
            else:
                self.str1 = otp.send(self.result[1])
                Label(self.bf2, text = 'ENTER OTP', font = ('arial', 14, 'bold')).grid(row = 2, column = 0, padx = 5,
                                                                                       pady = 10)
                self.eotp = Entry(self.bf2, font = ('arial', 14, 'bold'), width = 40)
                self.eotp.grid(row = 2, column = 1)
                Label(self.bf2, text = 'NEW PASSWORD', font = ('arial', 14, 'bold')).grid(row = 3, column = 0, padx = 5,
                                                                                       pady = 10)
                self.new = Entry(self.bf2, font = ('arial', 14, 'bold'), width = 40,show="*")
                self.new.grid(row = 3, column = 1)

                Label(self.bf2, text = 'RE-TYPE PASSWORD', font = ('arial', 14, 'bold')).grid(row = 4, column = 0, padx = 5,
                                                                                          pady = 10)
                self.ren = Entry(self.bf2, font = ('arial', 14, 'bold'), width = 40,show="*")
                self.ren.grid(row = 4, column = 1)

                Button(self.bf2, text="press", font = ('arial', 14, 'bold'), bg = "#4ac959", fg = "white", width = 20, command = self.press).grid(row = 5, column = 0, columnspan =2, padx = 5, pady = 20)

    def press(self):
        if (self.str1) == (self.eotp.get()):

            if (self.result[2]) != self.new.get():

                if (self.new.get()) == (self.ren.get()):
                    conn = connection.Connect()
                    cr = conn.cursor()
                    query = 'update login set password ="{}" where email="{}"'.format(self.new.get(), self.e1.get())
                    cr.execute(query)
                    conn.commit()
                    showinfo('Updated Successfully', 'Password updated successfully...')
                    self.rootf.destroy()
                else:
                    showerror("Error", "Password mismatch error !")
            else:
                showerror("Error","Your previous is same as new password.\nPlease enter another password")
        else:
            showerror("One Time Password", "Please enter correct OTP !")


class dasboard:
    def addl(self):
        cr = conn.cursor()
        s = self.loc.get()
        q = 'select * from surv_loc where s_loc like "{}"'.format(s)
        cr.execute(q)
        self.r = cr.fetchone()
        if self.r == None:
            cr2 = conn.cursor()
            q2='INSERT INTO `surv_loc`(`s_loc`) VALUES ("{}")'.format(s)
            cr2.execute(q2)
            conn.commit()
            showinfo("Add Location","Location inserted successfully...")
            self.rootadd.destroy()
        else:
            showerror("Error","Location already exist !!!")
            self.rootadd.destroy()

    def addloc(self):
        self.rootadd = Tk()
        self.rootadd.geometry("400x500")
        self.rootadd.title("MASK DETECTOR - Add new location")
        # self.photo1 = PhotoImage(file = "icon2.png")
        # self.rootadd.iconphoto(False, self.photo1)

        Label(self.rootadd,text="Add Surviellance Location",font = ('Comic Sans MS', 12, "bold"),width=30).pack(pady=20,padx=20)
        self.loc = Entry(self.rootadd,font = ('Comic Sans MS', 12, "bold"),width=30)
        self.loc.pack(padx=20,pady=20)
        Button(self.rootadd,text="ADD LOCATION",width=30,bg="white",fg="black",command=self.addl).pack(padx=20,pady=20)

        self.rootadd.mainloop()

    def comp_show(self):
        comp_show()
    def showsurv(self):
        showsurv()
    def sur(self):
        cr = conn.cursor()
        q1 = 'INSERT INTO `survielance`(`s_loc`, `dos`, `start_time`, `end_time`, `with_mask`, `without`) VALUES ("{}","{}","{}","{}","{}","{}")'.format(str(self.s_loc.get()), str(self.txt2.get()), str(self.txt1.get()), str(self.txt3.get()), str(self.mp.get()), str(self.up.get()))

        cr.execute(q1)
        conn.commit()
        showinfo("Recorded Successfully","Your surveillance data is saved successfully...")
    def light(self):
        self.rootd.destroy()
        dasboard_light(result)

    def __init__(self, result):

        global mode
        mode=1
        self.rootd = Tk()

        self.rootd.state("zoomed")
        self.rootd.geometry("1550x766")
        self.rootd.title("MASK DETECTOR")
        self.photo = PhotoImage(file = "icon.png")
        self.rootd.iconphoto(False, self.photo)
        self.rootd.config(bg = "#181818")




        self.bf1 = Frame(self.rootd, padx = 20, pady = 20, bg = "#404040", height = self.rootd.winfo_screenheight(),
                         width = 300)
        self.bf1.pack(side=LEFT, fill=Y)
        self.bf2 = Frame(self.rootd, padx = 20, pady = 20, bg = "#181818", height = self.rootd.winfo_screenheight(),
                         width = 300)
        self.bf2.pack(side = BOTTOM, fill = Y)
        self.addloc = Button(self.bf2, text = "Add Surviellance Location", font = ('Comic Sans MS', 12, "bold"),
                             width = 20, command = self.addloc)
        self.addloc.grid(row = 0, column = 0, padx = 40)
        self.light = Button(self.bf2, text = "Light Mode", font = ('Comic Sans MS', 12, "bold"), width = 20,
                            command = self.light)
        self.light.grid(row = 0, column = 1, padx = 40)


        self.menu = Frame(self.rootd, padx = 27, pady = 5, bg = "#404040", height =30,
                         width = (self.rootd.winfo_width()-300))
        self.menu.place(x =(self.rootd.winfo_width()), y = 0, anchor=NE)
        self.view = Button(self.menu, text = "VIEW ADMIN", borderwidth=0,font = ('Comic Sans MS', 14), width = 20, bg = "#404040", fg = "white",
               command = self.view)
        self.view.grid(row = 0, column = 1, padx = 10,
                                                          pady = 5)
        self.ad = Button(self.menu, text = "ADD ADMIN",borderwidth=0, font = ('Comic Sans MS', 14), width = 20, bg = "#404040", fg = "white",
               command = self.add)
        self.ad.grid(row = 0, column = 0, padx = 10,
                                                         pady = 5)
        Button(self.menu, text = "COMPLAINTS",borderwidth=0, font = ('Comic Sans MS', 14), width = 20, bg = "#404040", fg = "white",
               command = self.comp_show).grid(row = 0, column = 2, padx = 10,
                                                         pady = 5)
        Button(self.menu, text = "HISTORY",borderwidth=0, font = ('Comic Sans MS', 14), width = 20, bg = "#404040",
               fg = "white",
               command = self.showsurv).grid(row = 0, column = 3, padx = 10,
                                        pady = 5)


        self.flag = False
        self.ds_login = PhotoImage(file = "dashboard.png")

        self.ds_login = self.ds_login.subsample(10)
        my_button = Button(self.bf1, image = self.ds_login, bg = "#404040")
        my_button.grid(row = 0, column = 0,columnspan=2, pady = 20)
        my_button.bind("<Enter>", self.logout)
        my_button.bind("<Leave>", self.leave)
        my_button.bind("<Button-1>", self.logout)

        Label(self.bf1, text = result[0] + " { " + result[3] + " }", font = ('Comic Sans MS', 14), bg = "#404040",
              fg = "white").grid(row = 1, column = 0,columnspan=2, padx = 10, pady = 5)

        Label(self.bf1, text = result[1], font = ('Comic Sans MS', 14), bg = "#404040", fg = "white").grid(row = 2,
                                                                                                           column = 0,columnspan=2,
                                                                                                           padx = 10,
                                                                                                           pady = 5)
        Label(self.bf1, text = "-----------------------------------------------------------------------", font = ('Comic Sans MS', 10), bg = "#404040", fg = "white").grid(row = 3, column = 0,columnspan=2, padx = 5, pady = 5)
        Label(self.bf1, text = "Surveillance Loc.: ", font = ('Comic Sans MS', 12), justify= LEFT,bg = "#222222", fg = "white").grid(row = 4, column = 0, padx = 5, pady = 5)
        Label(self.bf1, text = "Start Time: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#222222", fg = "white").grid(row = 6, column = 0, padx = 5, pady = 5)
        Label(self.bf1, text = "End Time: ", font = ('Comic Sans MS', 12), bg = "#222222", justify= LEFT,fg = "white").grid(row = 7, column = 0, padx = 5, pady = 5)

        Label(self.bf1, text = "Date of Surv.: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#222222", fg = "white").grid(row = 5, column = 0, padx = 5, pady = 5)

        Label(self.bf1, text = "-----------------------------------------------------------------------", font = ('Comic Sans MS', 10), bg = "#222222",
              fg = "white").grid(row = 8, column = 0, columnspan = 2, padx = 5, pady = 5)
        self.start = Button(self.bf1, text = "Start",font = ('Comic Sans MS', 12), width=8, command = self.start_camera)
        self.start.grid(row = 12, column = 0, padx = 10, pady = 10)
        self.stop = Button(self.bf1, text = "Stop",font = ('Comic Sans MS', 12),width=8, command = self.stop_camera)
        self.stop.grid(row = 12, column = 1, padx = 10, pady = 10)
        self.stop["state"] = DISABLED
        self.submit = Button(self.bf1, text = "Save Surveillance", font = ('Comic Sans MS', 16), width = 30, command = self.sur)
        self.submit.grid(row = 14, column = 0,columnspan=2, padx = 10, pady = 20)
        self.submit["state"] = DISABLED
        Label(self.bf1, text = "Masked Population: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#404040", fg = "white").grid(row = 9, column = 0, padx = 5, pady = 5)
        self.mp = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))

        self.mp.config(state = "disabled")
        self.mp.grid(row = 9, column = 1, padx = 5, pady = 5)
        Label(self.bf1, text = "Unmasked Population: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#404040", fg = "white").grid(row = 10, column = 0, padx = 5, pady = 5)
        self.up = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))

        self.up.config(state = "disabled")
        self.up.grid(row = 10, column = 1, padx = 5, pady = 5)
        Label(self.bf1, text = "-----------------------------------------------------------------------",
              font = ('Comic Sans MS', 10), bg = "#404040",
              fg = "white").grid(row = 11, column = 0, columnspan = 2, padx = 5, pady = 5)


        cr = conn.cursor()
        q2 = 'select * from surv_loc'
        cr.execute(q2)
        self.res = cr.fetchall()

        print(self.res)
        self.l = []
        for i in self.res:
            self.l.append(i[0])

        style = Style()
        style.configure('my.TCombobox', arrowsize = 30)
        style.configure('Vertical.TScrollbar', arrowsize = 25)

        self.s_loc = Combobox(self.bf1, value = self.l, font = ('Comic Sans MS', 12), width =25,
                              state = 'readonly', style = 'my.TCombobox')
        self.s_loc.grid(row=4, column=1, padx=5, pady=5)
        self.txt2 = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))

        self.txt2.config(state = "disabled")
        self.txt2.grid(row = 5, column = 1, padx = 5, pady = 5)
        self.txt1 = Entry(self.bf1,fg="black", width=27, font = ('Comic Sans MS', 12))

        self.txt1.config(state="disabled")
        self.txt1.grid(row=6, column=1, padx=5, pady=5)
        self.txt3 = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))
        self.txt3.config(state = "disabled")
        self.txt3.grid(row = 7, column = 1, padx = 5, pady = 5)

        #video capture mode
        Label(self.bf1, text = "Camera Preference: ", font = ('Comic Sans MS', 12), justify = LEFT, bg = "#404040",
              fg = "white").grid(row = 13, column = 0, padx = 5, pady = 5)
        self.mode = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))
        self.mode.insert(0, "0")
        self.mode.grid(row = 13, column = 1, padx = 5, pady = 5)

        # text_speech = pyttsx3.init()
        # text_speech.setProperty('rate', 150)
        # text_speech.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
        # ans = "Hello " + result[0] + ", welcome to mask detector's dashboard"
        # text_speech.say(ans)
        # text_speech.runAndWait()
        if result[3] == "Admin":
            self.ad["state"] = DISABLED
            self.view["state"] = DISABLED
            self.addloc["state"] = DISABLED
        self.rootd.mainloop()
    def leave2(self,event):
        self.m2.destroy()
    def view(self):
        view()
    def add(self):
        self.rootd.destroy()
        add()
    def av(self,event):
        self.m2 = Frame(self.rootd, height = 20, bg = "white", width = 30, borderwidth = 0)
        self.m2.place(x = (self.rootd.winfo_screenwidth()-200), y = 50)
        Button(self.m2, text = "View Admin", font = ('Comic Sans MS', 10), width = 15, bg = "white", fg = "black",
               command = self.view, borderwidth = 0).grid(row = 0, column = 0, padx = 10,
                                                        pady = 5)
        Button(self.m2, text = "Add Admin", font = ('Comic Sans MS', 10), width = 15, bg = "white", fg = "black",
               command = self.add, borderwidth = 0).grid(row = 1, column = 0, padx = 10,
                                                        pady = 5)

    def lg(self):
        self.rootd.destroy()
        log()

    def logout(self, e):
        self.bf2 = Frame(self.rootd, height = 20, bg = "white", width = 30, borderwidth = 0)
        self.bf2.place(x = 180, y = 150)
        Button(self.bf2, text = "logout", font = ('Comic Sans MS', 10), width = 15, bg = "white", fg = "black",
               command = self.lg, borderwidth = 0).grid(row = 0, column = 0, padx = 10,
                                                        pady = 5)
    def leave(self,e):
        self.bf2.destroy()
    def start_camera(self):
        self.submit["state"] = DISABLED

        self.masked = 0
        self.unmasked = 0
        self.start["state"] = DISABLED
        self.txt2.config(state = "normal")
        self.txt2.delete(0, END)
        self.txt2.insert(0, datetime.today().date())
        self.txt2.config(state = "disabled")
        self.txt2.grid(row = 5, column = 1, padx = 5, pady = 5)
        self.txt1.config(state = "normal")
        self.txt1.delete(0, END)
        self.txt1.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.txt1.config(state = "disabled")
        self.txt1.grid(row = 6, column = 1, padx = 5, pady = 5)
        self.txt3.config(state = "normal")
        self.txt3.delete(0, END)
        self.txt3.config(state = "disabled")
        self.txt3.grid(row = 7, column = 1, padx = 5, pady = 5)
        self.mp.config(state = "normal")
        self.mp.delete(0, END)
        self.mp.config(state = "disabled")
        self.mp.grid(row = 9, column = 1, padx = 5, pady = 5)
        self.up.config(state = "normal")
        self.up.delete(0, END)
        self.up.config(state = "disabled")
        self.up.grid(row = 10, column = 1, padx = 5, pady = 5)


        self.camera = Frame(self.rootd, bg = "white", height = self.rootd.winfo_screenheight(),
                            width = self.rootd.winfo_screenwidth())
        self.cap = MyVideoCapture()
        self.cap.startVideo(int(str(self.mode.get())))

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(self.camera, width = self.cap.width+200, height = self.cap.height+100)
        self.canvas.pack()
        self.stop["state"] = NORMAL
        self.delay = 15
        self.update()

        self.camera.place(x = 570, y = 100)
        self.flag = True

    def stop_camera(self):

        self.submit["state"] = NORMAL

        self.start["state"] = NORMAL
        self.stop["state"] = DISABLED
        self.txt3.config(state = "normal")
        self.txt3.delete(0, END)
        self.txt3.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.txt3.config(state = "disabled")
        self.mp.config(state = "normal")
        self.mp.delete(0,END)
        self.m= (int(self.masked)/(int(self.masked)+int(self.unmasked)))*100
        self.u = (int(self.unmasked) / (int(self.masked) +int(self.unmasked))) * 100
        self.mp.insert(0, str(self.m)+" %")
        self.mp.config(state = "disabled")
        self.txt3.grid(row = 7, column = 1, padx = 5, pady = 5)
        self.mp.grid(row = 9, column = 1, padx = 5, pady = 5)
        self.up.config(state = "normal")
        self.up.delete(0, END)
        self.up.insert(0, str(self.u)+" %")
        self.up.config(state = "disabled")
        self.up.grid(row = 10, column = 1, padx = 5, pady = 5)
        if self.flag:
            #self.c2 = MyVideoCapture()
            self.cap.camera_release()
            self.canvas.destroy()
            global vid
            vid.release()

            self.flag = False
            self.camera.destroy()
        labelheading = ["Masked Population", "Unmasked Population"]
        count_pie = [self.masked, self.unmasked]

        fig = Figure()  # create a figure object
        ax = fig.add_subplot(111)  # add an Axes to the figure

        ax.pie(count_pie, radius = 1, labels = labelheading,autopct='%0.2f%%', shadow = True)
        ax.set_title("Surveillance: Masked Population Vs Unmasked Population")
        ax.legend(["Masked Population","Unmasked Population"],
                  title = "Surveillance",loc="lower right")

        chart1 = FigureCanvasTkAgg(fig, self.rootd)
        chart1.get_tk_widget().place(x=630,y=150)

    def update(self):
        # Get a frame from the video source
        face_cascade = cv2.CascadeClassifier('front1.xml')

        mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')

        faceCascade = cv2.CascadeClassifier('front1.xml')
        bw_threshold = 80

        # User message
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (30, 30)
        weared_mask_font_color = (255, 255, 255)
        not_weared_mask_font_color = (0, 0, 255)
        thickness = 2
        font_scale = 1
        weared_mask = "Thank You for wearing MASK"
        not_weared_mask = "Please wear MASK to defeat Corona"

        ret, img = self.cap.get_frame()
        faces = faceCascade.detectMultiScale(image = img, scaleFactor = 1.1, minNeighbors = 4)

        img = cv2.resize(img, (850, 600))

        img = cv2.flip(img, 1)

        # Convert Image into gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Convert image in black and white
        (thresh, black_and_white) = cv2.threshold(gray, bw_threshold, 255, cv2.THRESH_BINARY)
        # detect face
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # Face prediction for black and white
        faces_bw = face_cascade.detectMultiScale(black_and_white, 1.1, 4)

        if (len(faces) == 0 and len(faces_bw) == 0):
            cv2.putText(img, "No face found...", org, font, font_scale, weared_mask_font_color, thickness,
                        cv2.LINE_AA)
        elif (len(faces) == 0 and len(faces_bw) == 1):
            # It has been observed that for white mask covering mouth, with gray image face prediction is not happening
            cv2.putText(img, weared_mask, org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
            self.masked += 1


        else:
            # Draw rectangle on gace
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = img[y:y + h, x:x + w]

                # Detect lips counters
                mouth_rects = mouth_cascade.detectMultiScale(gray, 1.5, 5)

            # Face detected but Lips not detected which means person is wearing mask
                if (len(mouth_rects) == 0):
                    cv2.putText(img, weared_mask, org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    self.masked += 1
                    # frequency = 2500  # Set Frequency To 2500 Hertz
                    # duration = 1000  # Set Duration To 1000 ms == 1 second
                    # winsound.Beep(frequency, duration)
                else:
                    for (mx, my, mw, mh) in mouth_rects:

                        if (y < my < y + h):
                            # Face and Lips are detected but lips coordinates are within face cordinates which `means lips prediction is true and
                            # person is not waring mask
                            cv2.putText(img, not_weared_mask, org, font, font_scale, not_weared_mask_font_color,
                                        thickness,
                                        cv2.LINE_AA)
                            self.unmasked += 1



        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

        self.rootd.after(self.delay, self.update)


class dasboard_light:
    def sur(self):
        cr = conn.cursor()
        q1 = 'INSERT INTO `survielance`(`s_loc`, `dos`, `start_time`, `end_time`, `with_mask`, `without`) VALUES ("{}","{}","{}","{}","{}","{}")'.format(str(self.s_loc.get()), str(self.txt2.get()), str(self.txt1.get()), str(self.txt3.get()), str(self.mp.get()), str(self.up.get()))

        cr.execute(q1)
        conn.commit()
        cr = conn.cursor()
        q2= 'UPDATE `complaint` SET `status`="Surviellance done successfully" where `s_loc`="{}"'.format(str(self.s_loc.get()))
        cr.execute(q2)
        conn.commit()
        showinfo("Recorded Successfully", "Your surveillance data is saved successfully...")
    def showsurv(self):
        showsurv()
    def dark_mode(self):
        self.rootl.destroy()
        dasboard(result)

    def comp_show(self):
        comp_show()
    def addl(self):
        cr = conn.cursor()
        s = self.loc.get()
        q = 'select * from surv_loc where s_loc like "{}"'.format(s)
        cr.execute(q)
        self.r = cr.fetchone()
        if self.r == None:
            cr2 = conn.cursor()
            q2='INSERT INTO `surv_loc`(`s_loc`) VALUES ("{}")'.format(s)
            cr2.execute(q2)
            conn.commit()
            showinfo("Add Location","Location inserted successfully...")
            self.rootadd.destroy()
        else:
            showerror("Error","Location already exist !!!")
            self.rootadd.destroy()

    def addloc(self):
        self.rootadd = Tk()
        self.rootadd.geometry("400x500")
        self.rootadd.title("MASK DETECTOR - Add new location")
        # self.photo1 = PhotoImage(file = "icon2.png")
        # self.rootadd.iconphoto(False, self.photo1)

        Label(self.rootadd,text="Add Surviellance Location",font = ('Comic Sans MS', 12, "bold"),width=30).pack(pady=20,padx=20)
        self.loc = Entry(self.rootadd,font = ('Comic Sans MS', 12, "bold"),width=30)
        self.loc.pack(padx=20,pady=20)
        Button(self.rootadd,text="ADD LOCATION",width=30,bg="white",fg="black",command=self.addl).pack(padx=20,pady=20)

        self.rootadd.mainloop()



    def __init__(self, result):
        global mode
        mode = 2
        self.rootl = Tk()

        self.rootl.state("zoomed")
        self.rootl.geometry("1550x766")
        self.rootl.title("MASK DETECTOR")
        self.photo = PhotoImage(file = "icon.png")
        self.rootl.iconphoto(False, self.photo)
        self.rootl.config(bg = "white")


        self.bf1 = Frame(self.rootl, padx = 20, pady = 20, bg = "#d2d3db", height = self.rootl.winfo_screenheight(),
                         width = 300)
        self.bf1.pack(side=LEFT, fill=Y)
        self.bf2 = Frame(self.rootl, padx = 20, pady = 20, bg = "white", height = self.rootl.winfo_screenheight(),
                         width = 300)
        self.bf2.pack(side = BOTTOM, fill =Y)
        self.addloc = Button(self.bf2, text = "Add Surviellance Location", font = ('Comic Sans MS', 12, "bold"), width = 20,
                           bg = "#484b6a",
                           fg = "white", command = self.addloc)
        self.addloc.grid(row = 0, column = 0, padx = 40)
        self.dark = Button(self.bf2, text = "Dark Mode", font = ('Comic Sans MS', 12,"bold"), width = 20, bg = "#484b6a",
                            fg = "white", command = self.dark_mode)
        self.dark.grid(row=0,column=1,padx=40)

        self.menu = Frame(self.rootl, padx = 27, pady = 5, bg = "#d2d3db", height =30,
                         width = (self.rootl.winfo_width()-300))
        self.menu.place(x =(self.rootl.winfo_width()), y = 0, anchor=NE)
        self.view=Button(self.menu, text = "VIEW ADMIN", borderwidth=0,font = ('Comic Sans MS', 14), width = 20, bg = "#d2d3db", fg = "#484b6a",
               command = self.view)
        self.view.grid(row = 0, column = 1, padx = 10,pady = 5)
        self.ad=Button(self.menu, text = "ADD ADMIN",borderwidth=0, font = ('Comic Sans MS', 14), width = 20, bg = "#d2d3db", fg = "#484b6a",
               command = self.add)
        self.ad.grid(row = 0, column = 0, padx = 10,
                                                         pady = 5)
        Button(self.menu, text = "COMPLAINTS",borderwidth=0, font = ('Comic Sans MS', 14), width = 20, bg = "#d2d3db", fg = "#484b6a",
               command = self.comp_show).grid(row = 0, column = 2, padx = 10,
                                                         pady = 5)
        Button(self.menu, text = "HISTORY",borderwidth=0, font = ('Comic Sans MS', 14), width = 20, bg = "#d2d3db",
               fg = "#484b6a",
               command = self.showsurv).grid(row = 0, column = 3, padx = 10,
                                        pady = 5)


        self.flag = False
        self.ds_login = PhotoImage(file = "dashboard.png")

        self.ds_login = self.ds_login.subsample(10)
        my_button = Button(self.bf1, image = self.ds_login, bg = "#484b6a")
        my_button.grid(row = 0, column = 0,columnspan=2, pady = 20)
        my_button.bind("<Enter>", self.logout)
        my_button.bind("<Leave>", self.leave)
        my_button.bind("<Button-1>", self.logout)

        Label(self.bf1, text = result[0] + " { " + result[3] + " }", font = ('Comic Sans MS', 14), bg = "#d2d3db",
              fg = "#484b6a").grid(row = 1, column = 0,columnspan=2, padx = 10, pady = 5)

        Label(self.bf1, text = result[1], font = ('Comic Sans MS', 14), bg = "#d2d3db", fg = "#484b6a").grid(row = 2,
                                                                                                           column = 0,columnspan=2,
                                                                                                           padx = 10,
                                                                                                           pady = 5)
        Label(self.bf1, text = "-----------------------------------------------------------------------", font = ('Comic Sans MS', 10), bg = "#d2d3db", fg = "#484b6a").grid(row = 3, column = 0,columnspan=2, padx = 5, pady = 5)
        Label(self.bf1, text = "Surveillance Loc.: ", font = ('Comic Sans MS', 12), justify= LEFT,bg = "#d2d3db", fg = "#484b6a").grid(row = 4, column = 0, padx = 5, pady = 5)
        Label(self.bf1, text = "Start Time: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#d2d3db", fg = "#484b6a").grid(row = 6, column = 0, padx = 5, pady = 5)
        Label(self.bf1, text = "End Time: ", font = ('Comic Sans MS', 12), bg = "#d2d3db", justify= LEFT,fg = "#484b6a").grid(row = 7, column = 0, padx = 5, pady = 5)

        Label(self.bf1, text = "Date of Surv.: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#d2d3db", fg = "#484b6a").grid(row = 5, column = 0, padx = 5, pady = 5)

        Label(self.bf1, text = "-----------------------------------------------------------------------", font = ('Comic Sans MS', 10), bg = "#d2d3db",
              fg = "#484b6a").grid(row = 8, column = 0, columnspan = 2, padx = 5, pady = 5)
        self.start = Button(self.bf1, text = "Start",font = ('Comic Sans MS', 12), width=8,bg="#484b6a",fg="white", command = self.start_camera)
        self.start.grid(row = 12, column = 0, padx = 10, pady = 10)
        self.stop = Button(self.bf1, text = "Stop",font = ('Comic Sans MS', 12),width=8,bg="#484b6a",fg="white", command = self.stop_camera)
        self.stop.grid(row = 12, column = 1, padx = 10, pady = 10)
        self.stop["state"] = DISABLED
        self.submit = Button(self.bf1, text = "Save Surveillance", font = ('Comic Sans MS', 16),bg="#484b6a",fg="white", width = 30, command = self.sur)
        self.submit.grid(row = 14, column = 0,columnspan=2, padx = 10, pady = 20)
        self.submit["state"] = DISABLED
        Label(self.bf1, text = "Masked Population: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#d2d3db", fg = "#484b6a").grid(row = 9, column = 0, padx = 5, pady = 5)
        self.mp = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))

        self.mp.config(state = "disabled")
        self.mp.grid(row = 9, column = 1, padx = 5, pady = 5)
        Label(self.bf1, text = "Unmasked Population: ", font = ('Comic Sans MS', 12),justify= LEFT, bg = "#d2d3db", fg = "#484b6a").grid(row = 10, column = 0, padx = 5, pady = 5)
        self.up = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))

        self.up.config(state = "disabled")
        self.up.grid(row = 10, column = 1, padx = 5, pady = 5)
        Label(self.bf1, text = "-----------------------------------------------------------------------",
              font = ('Comic Sans MS', 10), bg = "#d2d3db",
              fg = "#484b6a").grid(row = 11, column = 0, columnspan = 2, padx = 5, pady = 5)


        cr = conn.cursor()
        q2 = 'select * from surv_loc'
        cr.execute(q2)
        self.res = cr.fetchall()

        print(self.res)
        self.l = []
        for i in self.res:
            self.l.append(i[0])

        style = Style()
        style.configure('my.TCombobox', arrowsize = 30)
        style.configure('Vertical.TScrollbar', arrowsize = 25)

        self.s_loc = Combobox(self.bf1, value = self.l, font = ('Comic Sans MS', 12), width =25,
                              state = 'readonly', style = 'my.TCombobox')
        self.s_loc.grid(row=4, column=1, padx=5, pady=5)
        self.txt2 = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))

        self.txt2.config(state = "disabled")
        self.txt2.grid(row = 5, column = 1, padx = 5, pady = 5)
        self.txt1 = Entry(self.bf1,fg="black", width=27, font = ('Comic Sans MS', 12))

        self.txt1.config(state="disabled")
        self.txt1.grid(row=6, column=1, padx=5, pady=5)
        self.txt3 = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))
        self.txt3.config(state = "disabled")
        self.txt3.grid(row = 7, column = 1, padx = 5, pady = 5)

        #video capture mode
        Label(self.bf1, text = "Camera Preference: ", font = ('Comic Sans MS', 12), justify = LEFT, bg = "#d2d3db",
              fg = "#484b6a").grid(row = 13, column = 0, padx = 5, pady = 5)
        self.mode = Entry(self.bf1, fg = "black", width = 27, font = ('Comic Sans MS', 12))
        self.mode.insert(0, "0")
        self.mode.grid(row = 13, column = 1, padx = 5, pady = 5)

        # text_speech = pyttsx3.init()
        # text_speech.setProperty('rate', 150)
        #
        # ans = "Hello " + result[0] + ", welcome to mask detector's dashboard"
        # text_speech.say(ans)
        # text_speech.runAndWait()
        if result[3] == "Admin":
            self.ad["state"] = DISABLED
            self.view["state"] = DISABLED
            self.addloc["state"] = DISABLED


        self.rootl.mainloop()

    def view(self):
        view()
    def add(self):
        self.rootl.destroy()
        add()
    def lg(self):
        self.rootl.destroy()
        log()

    def logout(self, e):
        self.bf2 = Frame(self.rootl, height = 20, bg = "white", width = 30, borderwidth = 0)
        self.bf2.place(x = 180, y = 150)
        Button(self.bf2, text = "logout", font = ('Comic Sans MS', 10), width = 15, bg = "white", fg = "#484b6a",
               command = self.lg, borderwidth = 0).grid(row = 0, column = 0, padx = 10,
                                                        pady = 5)
    def leave(self,e):
        self.bf2.destroy()
    def start_camera(self):
        self.submit["state"] = DISABLED

        self.masked = 0
        self.unmasked = 0
        self.start["state"] = DISABLED
        self.txt2.config(state = "normal")
        self.txt2.delete(0, END)
        self.txt2.insert(0, datetime.today().date())
        self.txt2.config(state = "disabled")
        self.txt2.grid(row = 5, column = 1, padx = 5, pady = 5)
        self.txt1.config(state = "normal")
        self.txt1.delete(0, END)
        self.txt1.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.txt1.config(state = "disabled")
        self.txt1.grid(row = 6, column = 1, padx = 5, pady = 5)
        self.txt3.config(state = "normal")
        self.txt3.delete(0, END)
        self.txt3.config(state = "disabled")
        self.txt3.grid(row = 7, column = 1, padx = 5, pady = 5)
        self.mp.config(state = "normal")
        self.mp.delete(0, END)
        self.mp.config(state = "disabled")
        self.mp.grid(row = 9, column = 1, padx = 5, pady = 5)
        self.up.config(state = "normal")
        self.up.delete(0, END)
        self.up.config(state = "disabled")
        self.up.grid(row = 10, column = 1, padx = 5, pady = 5)


        self.camera = Frame(self.rootl, bg = "white", height = self.rootl.winfo_screenheight(),
                            width = self.rootl.winfo_screenwidth())
        self.cap = MyVideoCapture()
        self.cap.startVideo(int(str(self.mode.get())))

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(self.camera, width = self.cap.width+200, height = self.cap.height+100)
        self.canvas.pack()
        self.stop["state"] = NORMAL
        self.delay = 15
        self.update()

        self.camera.place(x = 570, y = 100)
        self.flag = True

    def stop_camera(self):

        self.submit["state"] = NORMAL

        self.start["state"] = NORMAL
        self.stop["state"] = DISABLED
        self.txt3.config(state = "normal")
        self.txt3.delete(0, END)
        self.txt3.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.txt3.config(state = "disabled")
        self.mp.config(state = "normal")
        self.mp.delete(0,END)
        self.m= (int(self.masked)/(int(self.masked)+int(self.unmasked)))*100
        self.u = (int(self.unmasked) / (int(self.masked) +int(self.unmasked))) * 100
        self.mp.insert(0, str(self.m)+" %")
        self.mp.config(state = "disabled")
        self.txt3.grid(row = 7, column = 1, padx = 5, pady = 5)
        self.mp.grid(row = 9, column = 1, padx = 5, pady = 5)
        self.up.config(state = "normal")
        self.up.delete(0, END)
        self.up.insert(0, str(self.u)+" %")
        self.up.config(state = "disabled")
        self.up.grid(row = 10, column = 1, padx = 5, pady = 5)
        if self.flag:
            #self.c2 = MyVideoCapture()
            self.cap.camera_release()
            self.canvas.destroy()
            global vid
            vid.release()

            self.flag = False
            self.camera.destroy()
        labelheading = ["Masked Population", "Unmasked Population"]
        count_pie = [self.masked, self.unmasked]

        fig = Figure()  # create a figure object
        ax = fig.add_subplot(111)  # add an Axes to the figure

        ax.pie(count_pie, radius = 1, labels = labelheading,autopct='%0.2f%%', shadow = True)
        ax.set_title("Surveillance: Masked Population Vs Unmasked Population")
        ax.legend(["Masked Population","Unmasked Population"],
                  title = "Surveillance",loc="lower right")

        chart1 = FigureCanvasTkAgg(fig, self.rootl)
        chart1.get_tk_widget().place(x=630,y=150)

    def update(self):
        # Get a frame from the video source
        face_cascade = cv2.CascadeClassifier('front1.xml')

        mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')

        faceCascade = cv2.CascadeClassifier('front1.xml')
        bw_threshold = 80

        # User message
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (30, 30)
        weared_mask_font_color = (255, 255, 255)
        not_weared_mask_font_color = (0, 0, 255)
        thickness = 2
        font_scale = 1
        weared_mask = "Thank You for wearing MASK"
        not_weared_mask = "Please wear MASK to defeat Corona"

        ret, img = self.cap.get_frame()
        faces = faceCascade.detectMultiScale(image = img, scaleFactor = 1.1, minNeighbors = 4)

        img = cv2.resize(img, (850, 600))

        img = cv2.flip(img, 1)

        # Convert Image into gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Convert image in black and white
        (thresh, black_and_white) = cv2.threshold(gray, bw_threshold, 255, cv2.THRESH_BINARY)
        # detect face
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # Face prediction for black and white
        faces_bw = face_cascade.detectMultiScale(black_and_white, 1.1, 4)

        if (len(faces) == 0 and len(faces_bw) == 0):
            cv2.putText(img, "No face found...", org, font, font_scale, weared_mask_font_color, thickness,
                        cv2.LINE_AA)
        elif (len(faces) == 0 and len(faces_bw) == 1):
            # It has been observed that for white mask covering mouth, with gray image face prediction is not happening
            cv2.putText(img, weared_mask, org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
            self.masked += 1


        else:
            # Draw rectangle on gace
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = img[y:y + h, x:x + w]

                # Detect lips counters
                mouth_rects = mouth_cascade.detectMultiScale(gray, 1.5, 5)

            # Face detected but Lips not detected which means person is wearing mask
                if (len(mouth_rects) == 0):
                    cv2.putText(img, weared_mask, org, font, font_scale, weared_mask_font_color, thickness, cv2.LINE_AA)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    self.masked += 1
                    # frequency = 2500  # Set Frequency To 2500 Hertz
                    # duration = 1000  # Set Duration To 1000 ms == 1 second
                    # winsound.Beep(frequency, duration)
                else:
                    for (mx, my, mw, mh) in mouth_rects:

                        if (y < my < y + h):
                            # Face and Lips are detected but lips coordinates are within face cordinates which `means lips prediction is true and
                            # person is not waring mask
                            cv2.putText(img, not_weared_mask, org, font, font_scale, not_weared_mask_font_color,
                                        thickness,
                                        cv2.LINE_AA)
                            self.unmasked += 1



        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

        self.rootl.after(self.delay, self.update)



class MyVideoCapture:
    def startVideo(self, video_source=0):
        face_cascade = cv2.CascadeClassifier('front1.xml')
        eye_cascade = cv2.CascadeClassifier('eye.xml')
        mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')
        upper_body = cv2.CascadeClassifier('haarcascade_upperbody.xml')
        bw_threshold = 40


        # User message
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (30, 30)
        weared_mask_font_color = (255, 255, 255)
        not_weared_mask_font_color = (0, 0, 255)
        thickness = 2
        font_scale = 1
        weared_mask = "Thank You for wearing MASK"
        not_weared_mask = "Please wear MASK to defeat Corona"
        global vid
        vid=self.cap = cv2.VideoCapture(int(video_source))

        faceCascade = cv2.CascadeClassifier('front1.xml')
        flag = False
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)


    def get_frame(self):
       if self.cap.isOpened():
           ret, frame = self.cap.read()
           if ret:
               # Return a boolean success flag and the current frame converted to BGR
               return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
           else:
               return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

    def camera_release(self):
        if self.cap.isOpened():
            self.cap.release()


#connection to mysql on amazon
conn = connection.Connect()
log()
