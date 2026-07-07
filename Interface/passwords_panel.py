from os import path
from pyperclip import copy
from customtkinter import CTkToplevel, CTkButton
from Backend.vault import VaultHandler, StoredPasswords
from Interface.panel_components import ItemsFrame, DeletionDialog, GeneratedPasswordPanel

class PasswordPanel(CTkToplevel): 
    def __init__(self, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x250")
        self.resizable(False, False)
        self.title("Vault")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.gen_panel = None
        self.confirmation_dialog = None
    
        current_dir = path.dirname(path.abspath(__file__))
        self.vault = VaultHandler("vault.json", current_dir, password)
        self.vault.create_file()

        self.stored_passwords = StoredPasswords()
        self.stored_passwords.set_passwords(self.vault.decrypt_and_load())
        self.passwords_list = self.stored_passwords.get_passwords()
        
        self.items_frame = ItemsFrame(
            self, 
            title="Saved passwords", 
            values=self.passwords_list)
        self.items_frame.grid(
            row=0, 
            column=0, 
            padx=10, 
            pady=(10, 0), 
            sticky="nsew")

        self.gen_button = CTkButton(
            self,
            width=137,
            height=30,
            text="Generate",
            font=("Helvetica", 16, "bold"),
            fg_color="#1BD625",
            hover_color="#11841D",
            command=self.gen_callback)
        self.gen_button.grid(
            row=3, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="w")

        self.copy_button = CTkButton(
            self,
            width=137,
            height=30, 
            text="Copy",
            font=("Helvetica", 16, "bold"),
            fg_color="#1391E0",
            hover_color="#104483",
            command=self.copy_callback)
        self.copy_button.grid(
            row=3, 
            column=0, 
            padx=157,
            pady=10, 
            sticky="w")

        self.del_button = CTkButton(
            self,
            width=137,
            height=30,
            text="Delete",
            font=("Helvetica", 16, "bold"),
            fg_color="#E03913",
            hover_color="#831010",
            command=self.del_callback)
        self.del_button.grid(
            row=3, 
            column=0, 
            padx=157, 
            pady=10, 
            sticky="e")
        
        self.exit_button = CTkButton(
            self,
            width=137,
            height=30,
            text="Exit",
            font=("Helvetica", 16, "bold"),
            fg_color="#C8C511",
            hover_color="#7F8310",
            command=self.destroy)
        self.exit_button.grid(
            row=3, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="e")
            
    def update_vault(self) -> None:
        self.passwords_list = self.stored_passwords.get_passwords()
        self.items_frame.update_values(self.passwords_list)
        self.vault.encrypt_file(self.passwords_list)
        
    def gen_callback(self) -> None:
        if self.gen_panel is None or not self.gen_panel.winfo_exists():
            self.gen_panel = GeneratedPasswordPanel(
                self, 
                stored_passwords = self.stored_passwords, 
                on_update_callback = self.update_vault)
        else:
            self.gen_panel.focus() 

    def del_callback(self) -> None:
        if self.confirmation_dialog is None or not self.confirmation_dialog.winfo_exists():
            deletion_id = self.items_frame.get()
            self.confirmation_dialog = DeletionDialog(
                stored_passwords = self.stored_passwords, 
                password_id = deletion_id, 
                on_update_callback = self.update_vault)
        else:
            self.confirmation_dialog.focus()

    def clear(self):
        copy(' ')
        self.destroy

    def copy_callback(self):
        selected_id = self.items_frame.get()
    
        if selected_id is None:
            return

        copy_id = self.items_frame.get()
        matching_password = self.stored_passwords.get_password(copy_id)

        if matching_password:
            password_string = matching_password[0]
        
        copy(password_string)
        self.after(30000, self.clear())