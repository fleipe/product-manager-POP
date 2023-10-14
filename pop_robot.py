import threading
import time
import tkinter as tk
from tkinter import messagebox

from pop import login, mine, creator


class AsyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POP_robot")
        self.keys = {"usr": "toni.tort92@gmail.com", "pwd": "Superantonio92!"}
        self.driver1 = login(self.keys)
        self.filename = ""

        # Entry for integer
        self.int_label = tk.Label(root, text="Número Inteiro:")
        self.int_label.grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        self.int_var = tk.IntVar()
        self.int_entry = tk.Entry(root, textvariable=self.int_var, width=10)
        self.int_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

        # Checkboxes
        self.is_visible_var, self.images_var = tk.BooleanVar(), tk.BooleanVar()
        self.is_visible_checkbox = tk.Checkbutton(root, text="is_visible", variable=self.is_visible_var)
        self.images_checkbox = tk.Checkbutton(root, text="salvar imagens", variable=self.images_var)
        self.is_visible_checkbox.grid(row=1, column=1, pady=5, sticky=tk.W)
        self.images_checkbox.grid(row=2, column=1, pady=5, sticky=tk.W)

        # Buttons
        self.save_button = tk.Button(root, text="Salvar", command=self.save_data_async, width=15)
        self.create_button = tk.Button(root, text="Criar", command=self.create_data_async, width=15)
        self.save_button.grid(row=3, column=0, padx=10, pady=10)
        self.create_button.grid(row=3, column=1, padx=10, pady=10)

    def save_data_async(self):
        threading.Thread(target=self.save_data).start()

    def create_data_async(self):
        threading.Thread(target=self.create_data).start()

    def save_data(self):
        # Simulating a time-consuming task
        num_value = self.int_var.get()
        is_visible = self.is_visible_var.get()
        has_images = self.images_var.get()
        print("Saving")
        self.filename = mine(self.driver1)

        print(f"Data saved as {self.filename}.")
        messagebox.showinfo("Save Data", f"Data saved as {self.filename}.")

    def create_data(self):
        # Simulating a time-consuming task
        num_value = self.int_var.get()
        print(f"Creating {num_value} products")
        i = 0
        while i < num_value:
            print(f"Creating product {i+1}/{num_value}")
            creator(self.driver1, self.filename, is_visible=self.is_visible_var.get(), has_images=self.images_var.get())
            print(f"Product {i+1}/{num_value} created.")
            time.sleep(1)
            i += 1
        print(f"Data creation loop completed.")
        messagebox.showinfo("Create Data", "Data creation loop completed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AsyncApp(root)
    root.mainloop()