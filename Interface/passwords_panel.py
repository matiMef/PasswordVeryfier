import customtkinter, pyperclip, os
from Backend.vault import VaultHandler, StoredPasswords
from Interface.panel_components import ScrollablePasswordFrame, DeletionDialog, GeneratedPasswordPanel

class PasswordPanel(customtkinter.CTkToplevel): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x250")
        self.title("Vault")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.gen_panel = None
        self.confirmation_dialog = None

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.vault = VaultHandler("vault.json", self.current_dir, "password")
        self.stored_passwords = StoredPasswords()
        self.vault.create_file()
        raw_data = self.vault.decrypt_and_load()
        self.stored_passwords.set_passwords(raw_data)
        self.passwords_list = self.stored_passwords.get_passwords()
        self.names_list = [p.name for p in self.passwords_list if getattr(p, 'name', None)]
        
        self.scrollable_checkbox_frame = ScrollablePasswordFrame(
            self, 
            title="Saved passwords", 
            values=self.passwords_list)
        self.scrollable_checkbox_frame.grid(
            row=0, 
            column=0, 
            padx=10, 
            pady=(10, 0), 
            sticky="nsew")

        self.gen_button = customtkinter.CTkButton(
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

        self.copy_button = customtkinter.CTkButton(
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

        self.del_button = customtkinter.CTkButton(
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
        
        self.exit_button = customtkinter.CTkButton(
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
    
        self.update_vault()
        
    def update_vault(self):
        self.passwords_list = self.stored_passwords.get_passwords()
        self.names_list = [p.name for p in self.passwords_list if getattr(p, 'name', None)]
        self.scrollable_checkbox_frame.update_values(self.passwords_list)
        self.vault._encrypt_file(self.passwords_list)
        
    def gen_callback(self):
        if self.gen_panel is None or not self.gen_panel.winfo_exists():
            self.gen_panel = GeneratedPasswordPanel(
                self, 
                stored_passwords=self.stored_passwords, 
                on_update_callback=self.update_vault  
            )
        else:
            self.gen_panel.focus() 

    def del_callback(self):
        if self.confirmation_dialog is None or not self.confirmation_dialog.winfo_exists():
            deletion_id = self.scrollable_checkbox_frame.get()
            self.confirmation_dialog = DeletionDialog(stored_passwords=self.stored_passwords, password_id=deletion_id, on_update_callback=self.update_vault)
        else:
            self.confirmation_dialog.focus() 

    def clear(self):
        pyperclip.copy(' ')
        self.destroy

    def copy_callback(self):
        selected_id = self.scrollable_checkbox_frame.get()
    
        if selected_id is None:
            return

        copy_id = self.scrollable_checkbox_frame.get()
        matching_password = self.stored_passwords.get_password(copy_id)

        if matching_password:
            pure_password_string = matching_password[0]
        
        pyperclip.copy(pure_password_string)
        self.after(30000, self.clear)