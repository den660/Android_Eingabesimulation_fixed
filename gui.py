import tkinter as tk
from adb import get_smartphones
from dao import MySQLDAO
from error import show_error
from tkinter import messagebox

# dient als container für die restlichen Klassen
# ermöglicht die Menüführung
class MainPage(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.test = True
        self.minsize(350,300)
        self.title("Android Eingabesimulation")
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Seiten Instanzen erzeugen
        # dadurch ist nur noch ein update beim Seitenaufruf notwendig
        for F in (StartPage,RecordPage, EditRecordPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    # Seite wechseln
    # Seiten inhalt updaten
    def show_frame(self, page_name, optional=None):
        frame = self.frames[page_name]
        frame.update_frame(optional)
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        print("init")
        tk.Frame.__init__(self, parent)
        refresh_button = tk.Button(self, text="Refresh", command=self.update_frame)
        refresh_button.pack()
        records_button = tk.Button(self, text="Records", command=lambda: controller.show_frame("RecordPage"))
        records_button.pack()
        self.listbox = tk.Listbox(self)
        self.listbox.pack()
        self.smartphones = []
        self.start_button = tk.Button(self, text="Start Record", command=self.start_record)
        self.start_button.pack()
        self.stop_button = tk.Button(self, text="Stop Record", command=self.stop_record, state=tk.DISABLED)
        self.stop_button.pack()
        replay_button = tk.Button(self, text="Replay Record", command=lambda: self.choose_record())
        replay_button.pack()
        self.text_box = tk.Text(self)
        self.text_box.pack()

    # Ausgabe der Toucheingaben
    def update_text_box(self, line):
        self.text_box.insert(tk.END, line + "\n")
        self.text_box.see(tk.END)

    def start_record(self):
        try:
            smartphone = self.smartphones[self.listbox.index(self.listbox.curselection())]
        except:
            show_error("please choose a smartphone")
            return
        if smartphone.get_status() == "unauthorized":
            show_error("device unauthorized\nplease accept the RSA-key on the smartphone")
            return
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listbox.config(state=tk.DISABLED)
        smartphone.start_record(self)

    def stop_record(self):
        self.window = tk.Toplevel(self)
        self.window.minsize(200,100)
        label = tk.Label(self.window, text="Record Title:")
        label.pack()
        self.record_title_input = tk.Entry(self.window)
        self.record_title_input.pack()
        btn = tk.Button(self.window, text="Safe", command=self.safe_record)
        btn.pack()

    def safe_record(self):
        record_title = self.record_title_input.get()
        if record_title == "":
            show_error("Record title to short")
            return
        elif len(record_title) > 100:
            show_error("Record title to long\nmax character: 100")
            return

        RecordPage.dao.connect()
        is_available = RecordPage.dao.is_record_title_available(record_title)
        RecordPage.dao.close_connection()

        if not is_available:
            show_error("title is already taken")
            return
        self.window.destroy()
        self.smartphones[self.listbox.index(self.listbox.curselection())].stop_record(record_title)
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.listbox.config(state=tk.NORMAL)


    def choose_record(self):
        try:
            smartphone = self.smartphones[self.listbox.index(self.listbox.curselection())]
        except:
            show_error("please choose a smartphone")
            return
        if smartphone.get_status() == "unauthorized":
            show_error("device unauthorized\nplease accept the RSA-key on the smartphone")
            return
        self.window = tk.Toplevel(self)
        listbox = tk.Listbox(self.window)
        listbox.pack()
        RecordPage.dao.connect()
        records = RecordPage.dao.get_records()
        RecordPage.dao.close_connection()
        i = 1
        for record in records:
            listbox.insert(tk.END, str(i) + ". " + record.title)
            i += 1
        btn = tk.Button(self.window, text="Replay",
                        command=lambda: self.replay_record(records[listbox.index(listbox.curselection())],
                                                              smartphone))
        btn.pack()

    def replay_record(self, record, smartphone):
        smartphone.replay(record)


    def update_frame(self, optional=None):
        self.listbox.delete(0, tk.END)
        self.text_box.delete(1.0, tk.END)
        self.smartphones = get_smartphones()
        for smartphone in self.smartphones:
            self.listbox.insert(tk.END, smartphone)
            print(smartphone.get_status())


class RecordPage(tk.Frame):
    dao = MySQLDAO()
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        button = tk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage"))
        button.pack()
        self.controller = controller
        self.listbox = tk.Listbox(self)
        self.listbox.pack()
        self.records = []
        edit_button = tk.Button(self, text="Edit", command=lambda: self.edit_record())
        edit_button.pack()
        delete_button = tk.Button(self, text="Delete", command=lambda: self.delete_record())
        delete_button.pack()

    def edit_record(self):
        try:
            record_id = self.records[self.listbox.index(self.listbox.curselection())].id
        except:
            show_error("please choose a record")
            return
        self.controller.show_frame("EditRecordPage", record_id)

    def delete_record(self):
        msg_box = messagebox.askyesno("", "Are you sure you want to delete the chosen record?")
        print(msg_box)
        if not msg_box :
            return
        RecordPage.dao.connect()
        try:
            RecordPage.dao.delete_record(self.records[self.listbox.index(self.listbox.curselection())].id)
        except:
            show_error("please choose a record")
        RecordPage.dao.close_connection()
        self.update_frame()

    def update_frame(self, optional=None):
        self.listbox.delete(0, tk.END)
        RecordPage.dao.connect()
        self.records = RecordPage.dao.get_records()
        RecordPage.dao.close_connection()
        i = 1
        for record in self.records:
            self.listbox.insert(tk.END, str(i) + ". " + record.title)
            i += 1


class EditRecordPage(tk.Frame):
    dao = MySQLDAO()
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        button = tk.Button(self, text="Back", command=lambda: controller.show_frame("RecordPage"))
        button.pack()
        self.controller = controller
        self.listbox = tk.Listbox(self)
        self.listbox.pack()
        self.inputs = []
        self.delay_input = tk.Entry(self)
        self.delay_input.pack()
        edit_button = tk.Button(self, text="Edit Delay", command=lambda: self.edit_delay())
        edit_button.pack()
        delete_button = tk.Button(self, text="Delete", command=lambda: self.delete_input())
        delete_button.pack()
        integrate_button = tk.Button(self, text="Integrate", command=lambda: self.choose_record())
        integrate_button.pack()

    def delete_input(self):
        try:
            listbox_index = self.listbox.index(self.listbox.curselection())
        except:
            show_error("please choose an element")
            return
        EditRecordPage.dao.connect()
        EditRecordPage.dao.delete_input(self.inputs[listbox_index].id)
        EditRecordPage.dao.close_connection()
        self.update_frame(self.target_record_id)

    def edit_delay(self):
        try:
            listbox_index = self.listbox.index(self.listbox.curselection())
        except:
            show_error("please choose an element")
            return
        try:
            new_delay = int(self.delay_input.get())
        except:
            show_error("please enter a numeric value")
            return
        if new_delay > 60000:
            show_error("new delay is to hight\nmust be <=60000")
            return
        else:
            EditRecordPage.dao.connect()
            EditRecordPage.dao.update_input_delay(self.inputs[listbox_index].id, new_delay)
            EditRecordPage.dao.close_connection()
            self.update_frame(self.target_record_id)
            self.delay_input.delete(0, tk.END)


    def choose_record(self):
        try:
            target_input = self.inputs[self.listbox.index(self.listbox.curselection())]
        except:
            show_error("please choose an element")
            return
        self.window = tk.Toplevel(self)
        listbox = tk.Listbox(self.window)
        listbox.pack()
        RecordPage.dao.connect()
        records = RecordPage.dao.get_records()
        RecordPage.dao.close_connection()
        i = 1
        for record in records:
            listbox.insert(tk.END, str(i) + ". " + record.title)
            i += 1
        btn = tk.Button(self.window, text="Integrate", command=lambda: self.integrate_record(records[listbox.index(listbox.curselection())],target_input))
        btn.pack()

    def integrate_record(self, source_record, target_input):
        self.window.destroy()
        RecordPage.dao.connect()
        RecordPage.dao.integrate_record(self.target_record_id, source_record.id, target_input.id)
        RecordPage.dao.close_connection()

    def update_frame(self, optional):
        self.target_record_id = optional
        self.listbox.delete(0, tk.END)
        EditRecordPage.dao.connect()
        self.inputs = EditRecordPage.dao.get_inputs(self.target_record_id)
        EditRecordPage.dao.close_connection()

        if len(self.inputs) == 0:
            show_error("no elements left, record was deleted")
            EditRecordPage.dao.connect()
            EditRecordPage.dao.delete_record(self.target_record_id)
            EditRecordPage.dao.close_connection()
            self.controller.show_frame("RecordPage")
            return
        i = 1
        for input in self.inputs:
            self.listbox.insert(tk.END, str(i) + ".  Delay: " + str(input.delay))
            i += 1


app = MainPage()
app.mainloop()