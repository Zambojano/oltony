import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import asdict

from main import *


BG = '#f4efe6'
NAV = '#243044'
ACCENT = '#7a3b3b'
MUTED = '#8a8175'


def tell(result):
    if result['status'] == 'success':
        messagebox.showinfo('Kész', result['message'])
    else:
        messagebox.showerror('Hiba', result['message'])


class Table:
    def __init__(self, frame, fields, datas, headers=None):
        self.frame = frame
        self.fields = fields
        self.datas = datas
        self.headers = headers if headers else fields

    def show(self, row=0, column=0):
        clear_frame(self.frame)

        tree_scroll = tk.Scrollbar(self.frame)
        tree = ttk.Treeview(
            self.frame,
            columns=self.fields,
            show='headings',
            yscrollcommand=tree_scroll.set
        )
        tree_scroll.config(command=tree.yview)
        tree.tag_configure('even', background='#fffdf8')
        tree.tag_configure('odd', background='#f3ece1')

        for field, header in zip(self.fields, self.headers):
            tree.heading(field, text=header)
            width = 130 if field in ('brand', 'style', 'first_name', 'last_name', 'phone', 'color') else 90
            tree.column(field, width=width, anchor='center')

        for i, data in enumerate(self.datas):
            data = asdict(data)
            values = []
            for field in self.fields:
                val = data[field]
                if hasattr(val, 'strftime'):
                    val = val.strftime('%Y.%m.%d')
                if field == 'is_male':
                    val = 'férfi' if val else 'nő'
                values.append(val)
            tree.insert('', 'end', values=values, tags=('even' if i % 2 == 0 else 'odd',))

        tree.grid(row=row, column=column, sticky='nsew')
        tree_scroll.grid(row=row, column=column + 1, sticky='ns')
        self.frame.grid_rowconfigure(row, weight=1)
        self.frame.grid_columnconfigure(column, weight=1)


class InputWithHint:
    def __init__(self, root, hint):
        self.hint = hint
        self.entry = tk.Entry(
            root,
            bg='white',
            fg=MUTED,
            font=('Segoe UI', 10),
            relief='flat',
            highlightthickness=1,
            highlightbackground='#c8bfb0',
            highlightcolor=ACCENT,
        )
        self.entry.insert(0, self.hint)
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)

    def get(self):
        self.entry.get_val = lambda: self.entry.get() if self.entry.get() != self.hint else None
        return self.entry

    def on_focus_in(self, event):
        if self.entry.get() == self.hint:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=NAV)

    def on_focus_out(self, event):
        if self.entry.get() == '':
            self.entry.insert(0, self.hint)
            self.entry.config(fg=MUTED)


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def show_page(frame):
    global current_frame
    if current_frame is not None:
        current_frame.pack_forget()
    current_frame = frame
    current_frame.pack(fill='both', expand=True, padx=16, pady=14)


def mark(name):
    for key, btn in menu_buttons.items():
        btn.config(bg=ACCENT if key == name else NAV)


def begin(frame, name):
    mark(name)
    show_page(frame)
    clear_frame(frame)
    frame.grid_columnconfigure(0, weight=1)


def title(parent, text):
    tk.Label(parent, text=text, bg=BG, fg=NAV, font=('Segoe UI', 13, 'bold')).grid(
        row=0, column=0, sticky='w', pady=(0, 8)
    )


def form_box(parent, text):
    box = tk.LabelFrame(
        parent,
        text=text,
        bg=BG,
        fg=NAV,
        font=('Segoe UI', 10, 'bold'),
        padx=12,
        pady=8,
        labelanchor='n',
    )
    box.grid(row=0, column=1, rowspan=3, sticky='n', padx=(18, 4))
    return box


def field(box, row, hint):
    entry = InputWithHint(box, hint).get()
    entry.grid(row=row, column=0, sticky='ew', pady=4, ipady=3)
    return entry


def ok_button(parent, text, command, row):
    tk.Button(
        parent,
        text=text,
        command=command,
        bg=ACCENT,
        fg='white',
        activebackground='#5e2e2e',
        activeforeground='white',
        relief='flat',
        font=('Segoe UI', 10),
        padx=8,
        pady=4,
    ).grid(row=row, column=0, sticky='ew', pady=(8, 2))


def add_io_buttons(parent, entity, refresh, row):
    def do_export(kind):
        ext = {'csv': '.csv', 'json': '.json', 'xlsx': '.xlsx'}[kind]
        full_path = filedialog.asksaveasfilename(
            initialfile=f'{entity}{ext}',
            defaultextension=ext,
            filetypes=[(kind.upper(), f'*{ext}'), ('All files', '*.*')]
        )
        if not full_path:
            return
        folder, file_name = os.path.split(full_path)
        try:
            tell(export_entity(entity, folder, kind, file_name))
        except Exception as e:
            messagebox.showerror('Hiba', str(e))

    def do_import(kind):
        ext = {'csv': '.csv', 'json': '.json', 'xlsx': '.xlsx'}[kind]
        full_path = filedialog.askopenfilename(
            filetypes=[(kind.upper(), f'*{ext}'), ('All files', '*.*')]
        )
        if not full_path:
            return
        folder, file_name = os.path.split(full_path)
        try:
            tell(import_entity(entity, folder, kind, file_name))
            refresh()
        except Exception as e:
            messagebox.showerror('Hiba', str(e))

    box = tk.Frame(parent, bg=BG)
    box.grid(row=row, column=0, sticky='w', pady=(8, 0))
    buttons = [
        ('CSV mentés', lambda: do_export('csv')),
        ('Excel mentés', lambda: do_export('xlsx')),
        ('JSON mentés', lambda: do_export('json')),
        ('CSV betöltés', lambda: do_import('csv')),
        ('Excel betöltés', lambda: do_import('xlsx')),
        ('JSON betöltés', lambda: do_import('json')),
    ]
    for i, (text, cmd) in enumerate(buttons):
        tk.Button(
            box,
            text=text,
            command=cmd,
            bg='#e7dfd2',
            fg=NAV,
            activebackground='#d9cfc0',
            relief='flat',
            font=('Segoe UI', 9),
            padx=8,
            pady=3,
        ).grid(row=i // 3, column=i % 3, padx=(0, 6), pady=3, sticky='w')


def show_suits():
    def add_suit_command():
        result = add_suit(
            brand.get_val(),
            style.get_val(),
            size.get_val(),
            color.get_val(),
            cost_category_id.get_val(),
        )
        tell(result)
        if result['status'] == 'success':
            show_suits()

    suits = get_suits()
    begin(suits_frame, 'suits')
    suits_frame.grid_rowconfigure(1, weight=1)
    title(suits_frame, f'Öltönyök  ·  {len(suits)} db')

    holder = tk.Frame(suits_frame, bg=BG)
    holder.grid(row=1, column=0, sticky='nsew')
    Table(
        holder,
        ['id', 'brand', 'style', 'size', 'color', 'cost_category_id'],
        suits,
        ['Azonosító', 'Márka', 'Fazon', 'Méret', 'Szín', 'Ár id'],
    ).show()

    box = form_box(suits_frame, 'Új öltöny')
    brand = field(box, 0, 'Márka')
    style = field(box, 1, 'Fazon')
    size = field(box, 2, 'Méret, pl. 50')
    color = field(box, 3, 'Szín')
    cost_category_id = field(box, 4, 'Árkategória id')
    ok_button(box, 'Hozzáad', add_suit_command, 5)
    add_io_buttons(suits_frame, 'suits', show_suits, row=2)


def show_customers():
    def add_customer_command():
        result = add_customer(
            first_name.get_val(),
            last_name.get_val(),
            date_of_birth.get_val(),
            gender.get_val(),
            phone.get_val(),
        )
        tell(result)
        if result['status'] == 'success':
            show_customers()

    customers = get_customers()
    begin(customers_frame, 'customers')
    customers_frame.grid_rowconfigure(1, weight=1)
    title(customers_frame, f'Ügyfelek  ·  {len(customers)} fő')

    holder = tk.Frame(customers_frame, bg=BG)
    holder.grid(row=1, column=0, sticky='nsew')
    Table(
        holder,
        ['id', 'first_name', 'last_name', 'date_of_birth', 'is_male', 'phone'],
        customers,
        ['Azonosító', 'Keresztnév', 'Vezetéknév', 'Születés', 'Nem', 'Telefon'],
    ).show()

    box = form_box(customers_frame, 'Új ügyfél')
    first_name = field(box, 0, 'Keresztnév')
    last_name = field(box, 1, 'Vezetéknév')
    date_of_birth = field(box, 2, 'Születés (ÉÉÉÉ.HH.NN)')
    gender = field(box, 3, 'férfi / nő')
    phone = field(box, 4, 'Telefon')
    ok_button(box, 'Hozzáad', add_customer_command, 5)
    add_io_buttons(customers_frame, 'customers', show_customers, row=2)


def show_costcategories():
    categories = get_costcategories()
    begin(costcategories_frame, 'prices')
    costcategories_frame.grid_rowconfigure(1, weight=1)
    title(costcategories_frame, 'Árkategóriák')

    holder = tk.Frame(costcategories_frame, bg=BG)
    holder.grid(row=1, column=0, sticky='nsew')
    Table(
        holder,
        ['id', 'name', 'price_per_day', 'cleaning_fee', 'penalty_per_day_late'],
        categories,
        ['Azonosító', 'Név', 'Napidíj', 'Tisztítás', 'Késedelmi díj'],
    ).show()


def show_rentals():
    def add_rental_command():
        try:
            result = add_rental(suit_id.get_val(), customer_id.get_val(), rental_start.get_val(), rental_end.get_val())
        except Exception as e:
            messagebox.showerror('Hiba', str(e))
            return
        tell(result)
        if result['status'] == 'success':
            show_rentals()

    def end_rental_command():
        try:
            result = end_rental(rental_id.get_val(), damage_fee.get_val())
        except Exception as e:
            messagebox.showerror('Hiba', str(e))
            return
        tell(result)
        if result['status'] == 'success':
            show_rentals()

    rentals = get_rentals()
    begin(rentals_frame, 'rentals')
    rentals_frame.grid_rowconfigure(1, weight=1)
    title(rentals_frame, f'Kölcsönzések  ·  {len(rentals)} nyitott')

    holder = tk.Frame(rentals_frame, bg=BG)
    holder.grid(row=1, column=0, sticky='nsew')
    Table(
        holder,
        ['id', 'suit_id', 'customer_id', 'rental_start', 'rental_end'],
        rentals,
        ['Azonosító', 'Öltöny', 'Ügyfél', 'Kezdet', 'Vég'],
    ).show()

    side = tk.Frame(rentals_frame, bg=BG)
    side.grid(row=0, column=1, rowspan=3, sticky='n', padx=(18, 4))

    new_box = tk.LabelFrame(side, text='Új kölcsönzés', bg=BG, fg=NAV, font=('Segoe UI', 10, 'bold'), padx=12, pady=8)
    new_box.pack(fill='x')
    suit_id = field(new_box, 0, 'Öltöny id')
    customer_id = field(new_box, 1, 'Ügyfél id')
    rental_start = field(new_box, 2, 'Kezdet (ÉÉÉÉ.HH.NN)')
    rental_end = field(new_box, 3, 'Vég (ÉÉÉÉ.HH.NN)')
    ok_button(new_box, 'Kiadás', add_rental_command, 4)

    end_box = tk.LabelFrame(side, text='Visszahozás', bg=BG, fg=NAV, font=('Segoe UI', 10, 'bold'), padx=12, pady=8)
    end_box.pack(fill='x', pady=(14, 0))
    rental_id = field(end_box, 0, 'Kölcsönzés id')
    damage_fee = field(end_box, 1, 'Kárdíj Ft, 0 ha ép')
    ok_button(end_box, 'Lezárás', end_rental_command, 2)

    add_io_buttons(rentals_frame, 'rentals', show_rentals, row=2)


def show_initialize():
    def run():
        try:
            result = generate_suits_and_customers_and_categories(
                n_suits.get_val(),
                n_customers.get_val(),
                male_ratio.get_val(),
                category_distribution.get_val(),
                customers_locale.get_val(),
            )
            tell(result)
        except Exception as e:
            messagebox.showerror('Hiba', str(e))

    begin(initialize_frame, 'init')
    title(initialize_frame, 'Mintaadatok')

    tk.Label(
        initialize_frame,
        text='Üres mezőnél az alap érték megy be. A régi öltönyös táblák törlődnek.',
        bg=BG,
        fg=MUTED,
        font=('Segoe UI', 9),
    ).grid(row=1, column=0, sticky='w', pady=(0, 10))

    box = tk.Frame(initialize_frame, bg=BG)
    box.grid(row=2, column=0, sticky='w')

    n_suits = field(box, 0, 'Hány öltöny (1000)')
    category_distribution = field(box, 1, 'Eloszlás: 25,25,25,25')
    n_customers = field(box, 2, 'Hány ügyfél (1000)')
    male_ratio = field(box, 3, 'Férfi arány (0.5)')
    customers_locale = field(box, 4, 'Nyelv (hu_HU)')
    ok_button(box, 'Generálás', run, 5)


def menu_button(name, text, command):
    btn = tk.Button(
        side,
        text=text,
        command=command,
        bg=NAV,
        fg='white',
        activebackground=ACCENT,
        activeforeground='white',
        relief='flat',
        anchor='w',
        font=('Segoe UI', 11),
        padx=16,
        pady=8,
    )
    btn.pack(fill='x', pady=2)
    menu_buttons[name] = btn


window = tk.Tk()
window.title('Öltöny kölcsönző')
window.geometry('1120x680')
window.minsize(980, 600)
window.configure(bg=BG)

style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview', background='#fffdf8', fieldbackground='#fffdf8', foreground=NAV, rowheight=26, font=('Segoe UI', 9), borderwidth=0)
style.configure('Treeview.Heading', background=NAV, foreground='white', font=('Segoe UI', 9, 'bold'), relief='flat')
style.map('Treeview', background=[('selected', ACCENT)], foreground=[('selected', 'white')])

header = tk.Frame(window, bg=NAV, height=62)
header.pack(fill='x')
header.pack_propagate(False)
tk.Label(header, text='Öltöny kölcsönző', bg=NAV, fg='#f6f1e7', font=('Segoe UI', 18, 'bold')).pack(anchor='w', padx=18, pady=(8, 0))
tk.Label(header, text='méret  ·  fazon  ·  kölcsönzés', bg=NAV, fg='#c9bfb0', font=('Segoe UI', 9)).pack(anchor='w', padx=18)

body = tk.Frame(window, bg=BG)
body.pack(fill='both', expand=True)

side = tk.Frame(body, bg=NAV, width=176)
side.pack(side='left', fill='y')
side.pack_propagate(False)

content = tk.Frame(body, bg=BG)
content.pack(side='left', fill='both', expand=True)

menu_buttons = {}
tk.Frame(side, bg=NAV, height=10).pack()
menu_button('suits', 'Öltönyök', show_suits)
menu_button('customers', 'Ügyfelek', show_customers)
menu_button('rentals', 'Kölcsönzések', show_rentals)
menu_button('prices', 'Árak', show_costcategories)
menu_button('init', 'Mintaadatok', show_initialize)

suits_frame = tk.Frame(content, bg=BG)
customers_frame = tk.Frame(content, bg=BG)
costcategories_frame = tk.Frame(content, bg=BG)
rentals_frame = tk.Frame(content, bg=BG)
initialize_frame = tk.Frame(content, bg=BG)

current_frame = None
show_suits()

window.mainloop()
