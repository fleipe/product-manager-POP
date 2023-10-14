import json
import threading
import time
import tkinter as tk
from tkinter import messagebox

from pop import login, mine, creator


class AsyncApp:
    def __init__(self, root):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines all attributes that will be used by instances of this class.


        :param self: Represent the instance of the class
        :param root: Pass the window (Tk) object to the class
        :doc-author: Felipe Linares
        """
        self.root = root
        self.root.title("POP_robot")
        with open("user_data", "r") as f:
            self.keys = json.load(f)
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
        """
        The save_data_async function is a wrapper for the save_data function.
        It starts a new thread to run the save_data function in, so that it can be called asynchronously.

        :param self: Represent the instance of the object that calls this method
        :doc-author: Felipe Linares
        """
        threading.Thread(target=self.save_data).start()

    def create_data_async(self):
        """
        The create_data_async function is a wrapper for the create_data function.
        It starts a new thread to run the create_data function in, so that it can be called asynchronously.

        :param self: Represent the instance of the object that calls this method
        :doc-author: Felipe Linares
        """
        threading.Thread(target=self.create_data).start()

    def save_data(self):
        """
        The save_data function is called when the user clicks on the "Save Data" button.
        It calls a function from another file, mine(), which scrapes data from the website and saves it to a json file.
        The filename of that json file is then saved as an attribute of this class, so that it can be used in other functions.

        :param self: Represent the instance of the class
        :doc-author: Felipe Linares
        """
        print("Saving")
        self.filename = mine(self.driver1)

        print(f"Data saved as {self.filename}.")
        messagebox.showinfo("Save Data", f"Data saved as {self.filename}.")

    def create_data(self):
        """
        The create_data function is the function that actually creates the data.
        It takes in a number of products to create, and then loops through creating each product.
        The loop will continue until it has created all the products specified by num_value.

        :param self: Represent the instance of the object that calls this method
        :doc-author: Felipe Linares
        """
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


def main():
    """
    The main function is the entry point for the program.
    It creates a Tk root widget, instantiates an AsyncApp object, and calls mainloop on it.


    :return: None
    :doc-author: Felipe Linares
    """
    root = tk.Tk()
    app = AsyncApp(root)
    root.attributes("-topmost", True)
    root.mainloop()


if __name__ == "__main__":
    main()
