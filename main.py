import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class SSIS:
    def __init__(self):
        self.editing_student_id = None
        self.app = tk.Tk()
        self.app.title("Simple Student Information System")
        self.app.geometry("1200x400")
        self.frame = ttk.Frame(self.app)
        self.treeview = None
        self.course_manager_window = None
        self.conn = sqlite3.connect('university.db')
        self.create_tables()
        self.setup_widgets()
        self.get_coursecode_list()

    def setup_widgets(self):
        self.frame.grid(sticky="nsew")
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.widgets_frame = ttk.LabelFrame(self.frame, text="Register here!")
        self.widgets_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.entry_name = tk.Entry(self.widgets_frame)
        self.entry_name.insert(0, "Name")
        self.entry_name.bind("<FocusIn>", lambda e: self.entry_name.delete('0', 'end'))
        self.entry_name.grid(row=0, column=0, sticky="ew", padx=5, pady=10)

        self.entry_idnum = tk.Entry(self.widgets_frame)
        self.entry_idnum.insert(0, "ID Number")
        self.entry_idnum.bind("<FocusIn>", lambda e: self.entry_idnum.delete('0', 'end'))
        self.entry_idnum.grid(row=1, column=0, sticky="ew", padx=5, pady=10)

        level = ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year", "6th Year"]
        self.entry_yrlvl = ttk.Combobox(self.widgets_frame, values=level)
        self.entry_yrlvl.insert("0", "Year Level")
        self.entry_yrlvl.grid(row=2, column=0, sticky="ew", padx=5, pady=10)

        gender_list = ["Male", "Female", "Other"]
        self.entry_gender = ttk.Combobox(self.widgets_frame, values=gender_list)
        self.entry_gender.insert("0", "Gender")
        self.entry_gender.grid(row=3, column=0, sticky="ew", padx=5, pady=10)

        # Populate the course code combobox
        course_codes = self.get_coursecode_list()
        self.entry_courseCode = ttk.Combobox(self.widgets_frame, values=course_codes)
        self.entry_courseCode.insert("0", "Course Code")
        self.entry_courseCode.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        self.button_submit = tk.Button(self.widgets_frame, text="SUBMIT", command=self.on_button_submit)
        self.button_submit.grid(row=6, column=0, padx=5, pady=5)

        self.seperator = ttk.Separator(self.widgets_frame)
        self.seperator.grid(row=7, column=0, sticky="ew", padx=(20, 10), pady=5)

        self.treeFrame = ttk.Frame(self.frame)
        self.treeFrame.grid(row=0, column=1, pady=10, sticky="nsew")
        self.treeFrame.columnconfigure(0, weight=1)
        self.treeFrame.rowconfigure(0, weight=1)

        self.button_frame1 = ttk.Frame(self.treeFrame)
        self.button_frame1.pack(side="bottom", pady=10, anchor="e")

        self.button_edit = tk.Button(self.button_frame1, text="EDIT", command=self.on_button_edit)
        self.button_edit.pack(side="left", padx=5)

        self.button_del = tk.Button(self.button_frame1, text="DELETE", command=self.on_button_del)
        self.button_del.pack(side="left", padx=5)

        self.button_load = tk.Button(self.button_frame1, text="LOAD", command=self.on_button_load)
        self.button_load.pack(side="right", padx=5)

        self.button_manage = tk.Button(self.button_frame1, text="COURSES", command=self.on_button_courses)
        self.button_manage.pack(side="right", padx=5)

        self.search_frame = ttk.Frame(self.treeFrame)
        self.search_frame.pack(side="top", pady=10, anchor="e")

        self.entry_search = tk.Entry(self.search_frame)
        self.entry_search.insert(0, "Search Name or ID")
        self.entry_search.bind("<FocusIn>", lambda e: self.entry_search.delete('0', 'end'))
        self.entry_search.pack(side="left", padx=5)

        self.button_search = tk.Button(self.search_frame, text="SEARCH", command=self.search_student)
        self.button_search.pack(side="left", padx=5)

        self.button_save = tk.Button(self.widgets_frame, text="SAVE", command=self.on_button_save)

        self.treeScroll = ttk.Scrollbar(self.treeFrame)
        self.treeScroll.pack(side="right", fill="y")

        # Define the column names
        cols = ["Name", "ID_Number", "Year_Level", "Gender", "Course_Code", "Course_Title", "Status"]

        # Create the Treeview widget
        self.treeview = ttk.Treeview(self.treeFrame, show="headings", yscrollcommand=self.treeScroll.set, columns=cols,
                                     height=13)

        # Set up headings
        for col in cols:
            self.treeview.heading(col, text=col)

        # Set up columns
        for col in cols:
            self.treeview.column(col, width=200, anchor="center")

        self.treeview.column("Name", width=200, anchor="center")
        self.treeview.column("ID_Number", width=100, anchor="center")
        self.treeview.column("Year_Level", width=80, anchor="center")
        self.treeview.column("Gender", width=80, anchor="center")
        self.treeview.column("Course_Code", width=100, anchor="center")
        self.treeview.column("Course_Title", width=300, anchor="center")
        self.treeview.column("Status", width=100, anchor="center")

        self.treeview.pack(expand=True, fill="both")
        self.treeScroll.config(command=self.treeview.yview)

    def create_tables(self):
        try:
            # Check if the university.db file exists
            if not os.path.exists("university.db"):
                # Set up a SQLite3 database and make a connection to it
                conn = sqlite3.connect("university.db")
                cursor = conn.cursor()

                # Create necessary tables with foreign key constraint
                cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                                    name TEXT,
                                    id_number TEXT UNIQUE,
                                    year_level TEXT,
                                    gender TEXT,
                                    course_code TEXT,
                                    FOREIGN KEY (course_code) REFERENCES courses(code) ON DELETE CASCADE
                                  )''')

                # Commit changes and close connection
                conn.commit()
                conn.close()

                print("university.db has been created and initialized.")
            else:
                # Connect to the existing university.db file
                conn = sqlite3.connect("university.db")
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                print("Existing tables:", cursor.fetchall())
                cursor.close()
                print("Connection to university.db established.")
        except sqlite3.Error as e:
            print("Error creating tables:", e)

    def on_button_submit(self):
        # Retrieve input values from entry widgets
        name = self.entry_name.get().strip()
        id_num = self.entry_idnum.get().strip()
        yr_lvl = self.entry_yrlvl.get()
        gender = self.entry_gender.get()
        course_code = self.entry_courseCode.get().strip().upper()  # Capitalize the input

        c = self.conn.cursor()

        # Create a table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS students
                                 (              name TEXT,
                                                id_number TEXT UNIQUE,
                                                year_level TEXT,
                                                gender TEXT,
                                                course_code TEXT,
                                                status TEXT)''')

        # Check if any of the required fields are placeholders
        if name == "Name" or yr_lvl == "Year Level" or gender == "Gender" or course_code == "Course Code":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Validate the input data
        if not (name and id_num and yr_lvl and gender and course_code):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Validate ID number format
        if not re.match(r'\d{4}-\d{4}', id_num):
            messagebox.showerror("Error", "Invalid ID number format. Please enter in the format: YYYY-NNNN")
            return

        # Check if ID number already exists
        c.execute("SELECT id_number FROM students WHERE id_number = ?", (id_num,))
        if c.fetchone():
            messagebox.showerror("Error", "Invalid ID number. Already existing ID number.")
            c.close()
            return

        # Insert student information into the database
        c.execute("INSERT INTO students (name, id_number, year_level, gender, course_code) VALUES (?, ?, ?, ?, ?)",
                  (name, id_num, yr_lvl, gender, course_code))

        self.conn.commit()
        c.close()

        # Update the Treeview
        self.on_button_load()

        # Clear entry widgets
        self.entry_name.delete(0, tk.END)
        self.entry_idnum.delete(0, tk.END)
        self.entry_yrlvl.delete(0, tk.END)
        self.entry_gender.delete(0, tk.END)
        self.entry_courseCode.delete(0, tk.END)

        # Make the guides appear
        self.entry_name.insert(0, "Name")
        self.entry_idnum.insert(0, "ID Number")
        self.entry_yrlvl.insert(0, "Year Level")
        self.entry_gender.insert(0, "Gender")
        self.entry_courseCode.insert(0, "Course Code")

        # Display success message
        messagebox.showinfo("Success", "Information added successfully.")

        # Display students table in terminal
        self.on_button_load()

        # Determine the status based on whether there is a match in the courses table
        status = self.get_student_status(course_code)

        # Update the status column in the database
        self.update_student_status(id_num, status)

    def on_button_edit(self):
        # Get the selected item in the treeview
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a row to edit.")
            return

        # Get the student ID (assuming it's in the second column)
        student_id = self.treeview.item(selected_item, 'values')[1]

        print("Selected student ID:", student_id)  # Debugging statement

        # Retrieve existing values of the selected student from the database
        try:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT Name, ID_Number, Year_Level, Gender, Course_Code
                              FROM students
                              WHERE ID_Number=?''', (student_id,))
            student_data = cursor.fetchone()
            cursor.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving student data: {str(e)}")
            return

        print("Retrieved student data:", student_data)  # Debugging statement

        # Check if student_data is None
        if student_data is None:
            messagebox.showerror("Error", "Selected student data not found.")
            return

        # Populate the entry widgets with the existing values
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, student_data[0])

        self.entry_idnum.delete(0, tk.END)
        self.entry_idnum.insert(0, student_data[1])

        self.entry_yrlvl.set(student_data[2])
        self.entry_gender.set(student_data[3])
        self.entry_courseCode.set(student_data[4])

        self.button_submit.grid_remove()
        self.button_save.grid(row=6, column=0, padx=5, pady=5)

        # Display success message
        messagebox.showinfo("Success", "Student data loaded successfully.")

    def on_button_del(self):
        # Get the selected item in the Treeview
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a row to delete.")
            return

        # Get the unique identifier (ID number) of the selected row
        selected_id = self.treeview.item(selected_item)['values'][1]

        # Confirm deletion with the user
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this row?")
        if not confirmation:
            return

        # Delete the corresponding row from the SQLite database
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM students WHERE ID_Number = ?", (selected_id,))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete row: {e}")
            return

        # Update the Treeview to reflect the changes
        self.on_button_load()

        # Show a success message
        messagebox.showinfo("Success", "Information deleted successfully.")
        pass

    def on_button_load(self, edited_course_code=None):
        # Clear existing items in the treeview
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        cursor = self.conn.cursor()
        cursor.execute('''SELECT students.name, students.id_number, students.year_level,
                            students.gender, students.course_code, 
                            COALESCE(courses.course_title, 'Unknown') as course_title,
                            CASE WHEN courses.course_code IS NOT NULL THEN 'Enrolled' ELSE 'Unenrolled' END as status
                            FROM students
                            LEFT JOIN courses ON students.course_code = courses.course_code''')
        rows = cursor.fetchall()

        for row in rows:
            # Insert each row into the treeview
            self.treeview.insert("", "end", values=row)

        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()

        print("Students Table:")
        print("ID | Name | ID Number | Year Level | Gender | Course Code")
        print("-" * 60)
        for row in rows:
            print(row)

        # Determine the status based on whether there is a match in the courses table
        status = self.get_student_status(edited_course_code)

        # Update the status column in the database
        self.update_student_status(self.editing_student_id, status)

        cursor.close()

        # Update the course code combobox with the latest values
        course_codes = self.get_coursecode_list()
        self.entry_courseCode['values'] = course_codes

    def on_button_courses(self):
        self.course_manager_window = tk.Toplevel(self.app)
        self.course_manager_window.title("Course Manager")
        course_manager = CourseManager(self.course_manager_window, self.app)
        pass

    def search_student(self):
        # Get the search query from the user input
        search_query = self.entry_search.get().strip()

        # Construct the SQL query to search for students
        query = "SELECT * FROM students WHERE name LIKE ? OR id_number LIKE ?"
        params = ('%' + search_query + '%', '%' + search_query + '%')  # Wildcard search

        # Execute the query and retrieve the matching student records
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        search_results = cursor.fetchall()
        cursor.close()

        # Clear the existing rows in the Treeview
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        # Populate the Treeview with the search results
        for student in search_results:
            self.treeview.insert('', 'end', values=student)
        pass

    def on_button_save(self):
        # Get the selected item in the treeview
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a row to edit.")
            return

        # Get the student ID (assuming it's in the second column)
        student_id = self.treeview.item(selected_item, 'values')[1]

        # Get the updated values from the entry widgets
        name = self.entry_name.get().strip()
        id_num = self.entry_idnum.get().strip()
        yr_lvl = self.entry_yrlvl.get()
        gender = self.entry_gender.get()
        course_code = self.entry_courseCode.get()

        # Validate the input data
        if not (name and id_num and yr_lvl and gender and course_code):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Validate ID number format
        if not re.match(r'\d{4}-\d{4}', id_num):
            messagebox.showerror("Error", "Invalid ID number format. Please enter in the format: YYYY-NNNN")
            return

        # Check for duplicate ID number (excluding the current student being edited)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id_number FROM students WHERE id_number=? AND id_number!=?",
                           (id_num, student_id))
            if cursor.fetchone():
                messagebox.showerror("Error", "Invalid ID number. Already existing ID number.")
                return
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error checking for duplicate ID number: {str(e)}")
            return
        finally:
            cursor.close()

        # Update the student information in the database
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE students SET name=?, id_number=?, year_level=?, gender=?, course_code=? WHERE id_number=?",
                (name, id_num, yr_lvl, gender, course_code, student_id))
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating student information: {str(e)}")
            return
        finally:
            cursor.close()

        # Update the Treeview
        self.on_button_load()

        # Clear entry widgets
        self.entry_name.delete(0, tk.END)
        self.entry_idnum.delete(0, tk.END)
        self.entry_yrlvl.delete(0, tk.END)
        self.entry_gender.delete(0, tk.END)
        self.entry_courseCode.delete(0, tk.END)

        # Make the guides appear
        self.entry_name.insert(0, "Name")
        self.entry_idnum.insert(0, "ID Number")
        self.entry_yrlvl.insert(0, "Year Level")
        self.entry_gender.insert(0, "Gender")
        self.entry_courseCode.insert(0, "Course Code")

        # Display success message
        messagebox.showinfo("Success", "Information edited successfully.")

        # Restore the submit button and remove the save button
        self.button_save.grid_remove()
        self.button_submit.grid(row=6, column=0, padx=5, pady=5)

        # Clear the editing_student_id attribute
        self.editing_student_id = None

    def get_student_status(self, course_code):
        if course_code:
            # Check if the course code exists in the courses table
            cursor = self.conn.cursor()
            cursor.execute("SELECT EXISTS(SELECT 1 FROM courses WHERE course_code = ?)", (course_code,))
            exists = cursor.fetchone()[0]
            cursor.close()
            if exists:
                return "Enrolled"
        return "Unenrolled"

    def update_student_status(self, id_num, status):
        global cursor
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE students SET status = ? WHERE id_number = ?", (status, id_num))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error updating student status:", e)
        finally:
            cursor.close()

    @staticmethod
    def get_coursecode_list():
        global connect
        course_codes = []
        try:
            connect = sqlite3.connect("university.db")
            cur = connect.cursor()
            cur.execute("SELECT course_code FROM courses")
            rows = cur.fetchall()
            for row in rows:
                course_codes.append(row[0])
        except sqlite3.Error as e:
            print("Error loading course codes:", e)
        finally:
            connect.close()

        return course_codes


class CourseManager:
    def __init__(self, parent, ssis_root):
        self.selected_course_index = None
        self.parent = parent
        self.ssis_root = ssis_root  # Store the root window of the SSIS application
        self.parent.geometry("580x300")  # Increase the window size
        self.parent.transient(self.ssis_root)  # Set ssis_root as the transient master to keep it always on top
        self.parent.grab_set()  # Grab all events for the CourseManager window

        self.setup_widgets()
        self.create_table()

    def setup_widgets(self):
        # Create widgets for CourseManager GUI
        self.course_frame = ttk.LabelFrame(self.parent, text="Manage Courses")
        self.course_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.entry_course_code = ttk.Entry(self.course_frame)
        self.entry_course_code.insert(0, "Course Code")
        self.entry_course_code.bind("<FocusIn>", lambda e: self.entry_course_code.delete('0', 'end'))
        self.entry_course_code.grid(row=0, column=0, padx=5, pady=5)

        self.entry_course_title = ttk.Entry(self.course_frame)
        self.entry_course_title.insert(0, "Course Title")
        self.entry_course_title.bind("<FocusIn>", lambda e: self.entry_course_title.delete('0', 'end'))
        self.entry_course_title.grid(row=0, column=1, padx=5, pady=5)

        self.button_add_course = ttk.Button(self.course_frame, text="Add Course", command=self.add_course)
        self.button_add_course.grid(row=0, column=2, padx=5, pady=5)

        self.button_edit_course = ttk.Button(self.course_frame, text="Edit Course", command=self.edit_course)
        self.button_edit_course.grid(row=0, column=3, padx=5, pady=5)

        self.button_delete_course = ttk.Button(self.course_frame, text="Delete Course", command=self.delete_course)
        self.button_delete_course.grid(row=0, column=4, padx=5, pady=5)

        # Create a Treeview widget
        self.course_tree = ttk.Treeview(self.course_frame, columns=("Course Code", "Course Title"), selectmode="browse")

        # Add columns to the Treeview
        self.course_tree.heading("#0", text="", anchor="w")
        self.course_tree.heading("Course Code", text="Course Code")
        self.course_tree.heading("Course Title", text="Course Title")

        self.course_tree.column("#0", width=0, stretch=tk.NO)
        self.course_tree.column("Course Code", width=100)
        self.course_tree.column("Course Title", width=400)

        self.course_tree.grid(row=1, column=0, columnspan=5, padx=5, pady=5)

        self.load_course_list()

    def create_table(self):
        global conn
        try:
            conn = sqlite3.connect("university.db")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                                course_code TEXT PRIMARY KEY,
                                course_title TEXT NOT NULL
                              )''')
            conn.commit()
        except sqlite3.Error as e:
            print("Error creating table:", e)
        finally:
            conn.close()

    def add_course(self):
        global conn
        course_code = self.entry_course_code.get().strip().upper()
        course_title = self.entry_course_title.get().strip()

        # Check if the entry fields still contain the placeholder strings
        if course_code == "Course Code" or course_title == "Course Title":
            messagebox.showerror("Error", "Please enter both course code and title.")
            return

        # Validate inputs
        if not course_code or not course_title:
            messagebox.showerror("Error", "Please enter both course code and title.")
            return

        # Check for duplicate course code
        if self.check_duplicate_course_code(course_code):
            messagebox.showerror("Error", "Course code already exists.")
            return

        # Add the new course to the database
        try:
            conn = sqlite3.connect("university.db")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO courses (course_code, course_title) VALUES (?, ?)", (course_code, course_title))
            conn.commit()
        except sqlite3.Error as e:
            print("Error adding course:", e)
            messagebox.showerror("Error", "Failed to add course.")
            return
        finally:
            conn.close()

        # Clear entry widgets
        self.entry_course_code.delete(0, tk.END)
        self.entry_course_title.delete(0, tk.END)

        self.entry_course_code.insert(0, "Course Code")
        self.entry_course_title.insert(0, "Course Title")

        # Update course list
        self.load_course_list()

        messagebox.showinfo("Success", "Course added successfully.")

    def delete_course(self):
        global conn
        selected_item = self.course_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to delete.")
            return

        # Get the selected course code from the Treeview
        course_code = self.course_tree.item(selected_item, "values")[0]

        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {course_code}?")
        if not confirmation:
            return

        # Delete the course from the database
        try:
            conn = sqlite3.connect("university.db")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM courses WHERE course_code=?", (course_code,))
            conn.commit()
        except sqlite3.Error as e:
            print("Error deleting course:", e)
            messagebox.showerror("Error", "Failed to delete course.")
            return
        finally:
            conn.close()

        # Update the course list
        self.load_course_list()

        messagebox.showinfo("Success", "Course deleted successfully.")

    def edit_course(self):
        selected_item = self.course_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to edit.")
            return

        # Get the selected course details from the Treeview
        course_code, course_title = self.course_tree.item(selected_item, "values")

        # Populate the entry widgets with the selected course details for editing
        self.entry_course_code.delete(0, tk.END)
        self.entry_course_code.insert(0, course_code)
        self.entry_course_title.delete(0, tk.END)
        self.entry_course_title.insert(0, course_title)

        # Disable the delete and add buttons
        self.button_delete_course.config(state="disabled")
        self.button_add_course.config(state="disabled")

        # Replace the edit button with a save button
        self.button_edit_course.grid_remove()  # Remove the edit button
        self.button_save_course = ttk.Button(self.course_frame, text="Save Course Changes",
                                             command=self.save_course_changes)
        self.button_save_course.grid(row=0, column=3, padx=5, pady=5)

    def save_course_changes(self):
        global conn
        selected_item = self.course_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to save changes.")
            return

        # Get the selected course details from the Treeview
        course_code = self.entry_course_code.get().strip().upper()
        course_title = self.entry_course_title.get().strip()

        # Check for duplicate course code
        if course_code != self.course_tree.item(selected_item, "values")[0] and self.check_duplicate_course_code(course_code):
            messagebox.showerror("Error", "Course code already exists.")
            return

        # Update the course details in the database
        try:
            conn = sqlite3.connect("university.db")
            cursor = conn.cursor()

            cursor.execute("UPDATE courses SET course_code=?, course_title=? WHERE course_code=?",
                           (course_code, course_title, self.course_tree.item(selected_item, "values")[0]))
            conn.commit()
        except sqlite3.Error as e:
            print("Error updating course:", e)
            messagebox.showerror("Error", "Failed to save changes.")
            return
        finally:
            conn.close()

        # Update the course list
        self.load_course_list()

        # Return button to original state
        self.button_save_course.grid_remove()
        self.button_edit_course.grid(row=0, column=3, padx=5, pady=5)
        self.button_delete_course.config(state="normal")
        self.button_add_course.config(state="normal")

        messagebox.showinfo("Success", "Changes saved successfully.")

    def check_duplicate_course_code(self, course_code):
        # Check if the entered course code already exists in the database
        global conn
        try:
            conn = sqlite3.connect("university.db")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM courses WHERE course_code=?", (course_code,))
            count = cursor.fetchone()[0]

            return count > 0
        except sqlite3.Error as e:
            print("Error checking duplicate course code:", e)
            return False
        finally:
            conn.close()

    def load_course_list(self):
        # Clear current course list in Treeview
        global conn
        self.course_tree.delete(*self.course_tree.get_children())

        # Load courses from the database and populate Treeview
        try:
            conn = sqlite3.connect("university.db")
            cursor = conn.cursor()

            cursor.execute("SELECT course_code, course_title FROM courses")
            courses = cursor.fetchall()

            for course in courses:
                self.course_tree.insert("", tk.END, values=course)
        except sqlite3.Error as e:
            print("Error loading courses:", e)
        finally:
            conn.close()


# Instantiate the SSIS class
ssis = SSIS()

# Start the main event loop
ssis.app.mainloop()
