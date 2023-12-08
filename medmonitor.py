import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Database setup
def setup_database():
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS medications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        medication_name TEXT NOT NULL,
                        dose TEXT NOT NULL,
                        timing TEXT NOT NULL,
                        inventory_count INTEGER DEFAULT 0,
                        last_taken TEXT,
                        refill_threshold INTEGER DEFAULT 5,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

# Adding a new user profile
def add_user(name, age):
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "User profile added successfully.")

# Adding a new medication
def add_medication(user_id, medication_name, dose, timing, inventory_count, refill_threshold):
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO medications (user_id, medication_name, dose, timing, inventory_count, refill_threshold) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, medication_name, dose, timing, inventory_count, refill_threshold))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Medication added successfully.")

# Updated Medication Form
def medication_form():
    medication_window = tk.Toplevel()
    medication_window.title("Add/Update Medication")

    tk.Label(medication_window, text="User ID").grid(row=0, column=0)
    tk.Label(medication_window, text="Medication Name").grid(row=1, column=0)
    tk.Label(medication_window, text="Dose").grid(row=2, column=0)
    tk.Label(medication_window, text="Timing").grid(row=3, column=0)
    tk.Label(medication_window, text="Inventory Count").grid(row=4, column=0)
    tk.Label(medication_window, text="Refill Threshold").grid(row=5, column=0)

    user_id_entry = tk.Entry(medication_window)
    medication_name_entry = tk.Entry(medication_window)
    dose_entry = tk.Entry(medication_window)
    timing_entry = tk.Entry(medication_window)
    inventory_count_entry = tk.Entry(medication_window)
    refill_threshold_entry = tk.Entry(medication_window)

    user_id_entry.grid(row=0, column=1)
    medication_name_entry.grid(row=1, column=1)
    dose_entry.grid(row=2, column=1)
    timing_entry.grid(row=3, column=1)
    inventory_count_entry.grid(row=4, column=1)
    refill_threshold_entry.grid(row=5, column=1)

    tk.Button(medication_window, text="Add/Update Medication", 
              command=lambda: add_medication(user_id_entry.get(), 
                                             medication_name_entry.get(), 
                                             dose_entry.get(), 
                                             timing_entry.get(),
                                             inventory_count_entry.get(),
                                             refill_threshold_entry.get())).grid(row=6, column=0, columnspan=2)

# User profile form
def user_profile_form():
    user_window = tk.Toplevel()
    user_window.title("Add User Profile")

    tk.Label(user_window, text="Name").grid(row=0, column=0)
    tk.Label(user_window, text="Age").grid(row=1, column=0)

    name_entry = tk.Entry(user_window)
    age_entry = tk.Entry(user_window)

    name_entry.grid(row=0, column=1)
    age_entry.grid(row=1, column=1)

    tk.Button(user_window, text="Add Profile", command=lambda: add_user(name_entry.get(), age_entry.get())).grid(row=2, column=0, columnspan=2)


# Function to update inventory and record dose action
def update_inventory_and_record_dose(medication_id, action, inventory_change):
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()

    # Update inventory count
    if action == "taken":
        cursor.execute('UPDATE medications SET inventory_count = inventory_count - ? WHERE id = ?', (inventory_change, medication_id))
    
    # Record the action in medication history
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO medication_history (medication_id, action, action_time)
                      VALUES (?, ?, ?)''', (medication_id, action, now))

    # Check and notify for refill if needed
    cursor.execute('SELECT inventory_count, refill_threshold FROM medications WHERE id = ?', (medication_id,))
    inventory_count, refill_threshold = cursor.fetchone()
    if inventory_count <= refill_threshold:
        messagebox.showinfo("Refill Reminder", f"Medication ID {medication_id} inventory is low. Consider refilling.")

    conn.commit()
    conn.close()

# Function triggered when a medication is selected
def on_medication_selected(event, user_list, medication_list):
    selected_item = medication_list.selection()[0]
    medication_id = medication_list.item(selected_item, 'values')[0]
    dose_tracking_form(medication_id)

# Dose Tracking Form
def dose_tracking_form(medication_id):
    dose_window = tk.Toplevel()
    dose_window.title("Dose Tracking")

    # Button for dose taken
    tk.Button(dose_window, text="Dose Taken", command=lambda: update_inventory_and_record_dose(medication_id, "taken", 1)).pack()

    # Button for dose postponed
    tk.Button(dose_window, text="Dose Postponed", command=lambda: update_inventory_and_record_dose(medication_id, "postponed", 0)).pack()

    # Button for dose skipped
    tk.Button(dose_window, text="Dose Skipped", command=lambda: update_inventory_and_record_dose(medication_id, "skipped", 0)).pack()

    # Close button
    tk.Button(dose_window, text="Close", command=dose_window.destroy).pack()

# Check for medication reminders
def check_reminders():
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, medication_name, timing FROM medications')
    medications = cursor.fetchall()
    current_time = datetime.now().strftime("%H:%M")

    for medication in medications:
        user_id, medication_name, timing = medication
        if timing == current_time:
            messagebox.showinfo("Medication Reminder", f"It's time for user {user_id} to take their {medication_name}.")
    
    window.after(60000, check_reminders)

# Retrieve all medications for a user
def get_medications(user_id):
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medications WHERE user_id = ?', (user_id,))
    medications = cursor.fetchall()
    conn.close()
    return medications

# Display user's medications with a button to track doses
def display_user_medications(event, user_list, medication_list):
    selected_item = user_list.selection()[0]
    user_id = user_list.item(selected_item)['values'][0]
    medications = get_medications(user_id)

    for i in medication_list.get_children():
        medication_list.delete(i)
    for medication in medications:
        medication_list.insert('', 'end', values=(medication[2], medication[3], medication[4], medication[5], medication[6], medication[7]))

        # Button to open dose tracking form for each medication
        dose_button = tk.Button(medication_list, text="Track Dose", command=lambda m_id=medication[0]: dose_tracking_form(m_id))
        medication_list.window_create('end', window=dose_button)
        medication_list.insert('', 'end', '')

# Search for a user
def search_users(search_query, user_list):
    conn = sqlite3.connect('medmonitor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name LIKE ?', ('%' + search_query + '%',))
    users = cursor.fetchall()
    conn.close()
    update_user_list(users, user_list)

# Update user list display
def update_user_list(users, user_list):
    for i in user_list.get_children():
        user_list.delete(i)
    for user in users:
        user_list.insert('', 'end', values=user)

# Open search window
def open_search_window():
    search_window = tk.Toplevel()
    search_window.title("Search Users")
    search_window.geometry("800x400")

    tk.Label(search_window, text="Search User:").pack(pady=5)
    search_entry = tk.Entry(search_window)
    search_entry.pack(pady=5)
    tk.Button(search_window, text="Search", command=lambda: search_users(search_entry.get(), user_list)).pack(pady=5)
   

    # User list
    user_list = ttk.Treeview(search_window, columns=(1, 2, 3), show="headings", height=5)
    user_list.pack()
    user_list.heading(1, text="ID")
    user_list.heading(2, text="Name")
    user_list.heading(3, text="Age")

    # Medication list with new columns
    tk.Label(search_window, text="User Medications:").pack(pady=5)
    medication_list = ttk.Treeview(search_window, columns=(1, 2, 3, 4, 5, 6), show="headings", height=5)
    medication_list.pack()
    medication_list.heading(1, text="Medication Name")
    medication_list.heading(2, text="Dose")
    medication_list.heading(3, text="Timing")
    medication_list.heading(4, text="Inventory Count")
    medication_list.heading(5, text="Last Taken")
    medication_list.heading(6, text="Refill Threshold")

    user_list.bind('<<TreeviewSelect>>', lambda event: display_user_medications(event, user_list, medication_list))

def main_window():
    global window
    window = tk.Tk()
    window.title("MedMonitor")
    window.geometry("500x350")

    tk.Button(window, text="Add User Profile", command=user_profile_form).pack(pady=5)
    tk.Button(window, text="Add Medication", command=medication_form).pack(pady=5)
    tk.Button(window, text="Search Users", command=open_search_window).pack(pady=5)

    check_reminders()

    window.mainloop()

if __name__ == "__main__":
    setup_database()
    main_window()
