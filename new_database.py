import sqlite3
import tkinter as tk
from tkinter import messagebox

# Connect to DB
conn = sqlite3.connect("test_database.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS People (
        FirstName TEXT,
        LastName TEXT,
        Age INT
    );
''')
conn.commit()

# GUI
root = tk.Tk()
root.title("People Database")

# Global variable to track selected record
current_rowid = None

# Entries and labels
entry_fname = tk.Entry(root)
entry_lname = tk.Entry(root)
entry_age = tk.Entry(root)
entry_fname.grid(row=0, column=1)
entry_lname.grid(row=1, column=1)
entry_age.grid(row=2, column=1)

tk.Label(root, text="First Name").grid(row=0, column=0)
tk.Label(root, text="Last Name").grid(row=1, column=0)
tk.Label(root, text="Age").grid(row=2, column=0)

# Insert function
def insert_data():
    fname = entry_fname.get()
    lname = entry_lname.get()
    age = entry_age.get()
    if fname and lname and age.isdigit():
        cursor.execute("INSERT INTO People VALUES (?, ?, ?);", (fname, lname, int(age)))
        conn.commit()
        messagebox.showinfo("Success", "Data inserted successfully!")
        entry_fname.delete(0, tk.END)
        entry_lname.delete(0, tk.END)
        entry_age.delete(0, tk.END)
        refresh_list()
    else:
        messagebox.showerror("Error", "Please enter valid values.")

# Refresh listbox
def refresh_list():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT rowid, * FROM People")
    for row in cursor.fetchall():
        listbox.insert(tk.END, f"{row[0]}: {row[1]} {row[2]}, Age {row[3]}")

# Handle selection
def on_select(event):
    global current_rowid
    if not listbox.curselection():
        return
    idx = listbox.curselection()[0]
    selected_text = listbox.get(idx)
    rowid = selected_text.split(":")[0]
    cursor.execute("SELECT * FROM People WHERE rowid = ?", (rowid,))
    record = cursor.fetchone()
    if record:
        entry_fname.delete(0, tk.END)
        entry_fname.insert(0, record[0])
        entry_lname.delete(0, tk.END)
        entry_lname.insert(0, record[1])
        entry_age.delete(0, tk.END)
        entry_age.insert(0, str(record[2]))
        current_rowid = rowid

# Update function
def update_data():
    if current_rowid is None:
        messagebox.showerror("Error", "No record selected to update.")
        return
    fname = entry_fname.get()
    lname = entry_lname.get()
    age = entry_age.get()
    if fname and lname and age.isdigit():
        cursor.execute("UPDATE People SET FirstName=?, LastName=?, Age=? WHERE rowid=?", 
                       (fname, lname, int(age), current_rowid))
        conn.commit()
        messagebox.showinfo("Success", "Record updated successfully!")
        refresh_list()
    else:
        messagebox.showerror("Error", "Please enter valid values.")

# Buttons
btn_insert = tk.Button(root, text="Insert", command=insert_data)
btn_insert.grid(row=3, column=0, pady=10)

btn_update = tk.Button(root, text="Update", command=update_data)
btn_update.grid(row=3, column=1, pady=10)

# Listbox
listbox = tk.Listbox(root, width=50)
listbox.grid(row=4, column=0, columnspan=2)
listbox.bind('<<ListboxSelect>>', on_select)

# Search
tk.Label(root, text="Search").grid(row=5, column=0)
entry_search = tk.Entry(root)
entry_search.grid(row=5, column=1)

def search_data():
    term = entry_search.get()
    listbox.delete(0, tk.END)
    cursor.execute("SELECT rowid, * FROM People WHERE FirstName LIKE ? OR LastName LIKE ?", 
                   (f'%{term}%', f'%{term}%'))
    results = cursor.fetchall()
    if not results:
        listbox.insert(tk.END, "No matching records found.")
    for row in results:
        listbox.insert(tk.END, f"{row[0]}: {row[1]} {row[2]}, Age {row[3]}")

btn_search = tk.Button(root, text="Search", command=search_data)
btn_search.grid(row=6, column=0, columnspan=2, pady=5)

# Load existing records
refresh_list()

# Run app
root.mainloop()

# Close DB on exit
conn.close()
