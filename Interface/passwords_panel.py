from os import path
from pyperclip import copy
from customtkinter import CTkToplevel, CTkButton
from Backend.vault import VaultHandler, StoredPasswords
from Interface.panel_components import ItemsFrame, DeletePasswordDialog, GeneratePasswordPanel

class PasswordsPanel(CTkToplevel): 
    def __init__(self, master=None, password=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.title("Vault")
        self.wait_visibility()
        self.geometry("600x350")
        self.resizable(False, False)
        self.lift()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.generate_password_panel = None
        self.confirm_deletion_dialog = None
    
        current_dir = path.dirname(path.abspath(__file__))
        self.vault = VaultHandler("vault.json", current_dir, password)
        self.stored_passwords = StoredPasswords()

        if self.vault.check_file() is False:
            self.destroy()
            raise ValueError("Vault file doesn't exist")

        self.stored_passwords.set_passwords(self.vault.decrypt_and_load())
        self.passwords_list = self.stored_passwords.get_passwords()
        
        self.items_frame = ItemsFrame(
            self, 
            title="Saved passwords", 
            values=self.passwords_list)
        self.items_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.generate_password_button = CTkButton(
            self,
            width=140,
            height=30,
            text="Generate",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self._generate_password_callback)
        self.generate_password_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.copy_button = CTkButton(
            self,
            width=140,
            height=30, 
            text="Copy",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self._copy_callback)
        self.copy_button.grid(row=3, column=0, padx=157, pady=10, sticky="w")

        self.del_button = CTkButton(
            self,
            width=140,
            height=30,
            text="Delete",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self._delete_password_callback)
        self.del_button.grid(row=3, column=0, padx=157, pady=10, sticky="e")
        
        self.exit_button = CTkButton(
            self,
            width=140,
            height=30,
            text="Exit",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self.destroy)
        self.exit_button.grid(row=3, column=0, padx=10, pady=10, sticky="e")

        self._verify_is_any_checked()

    def _verify_is_any_checked(self) -> bool:
        if self.items_frame.check_state():
            self.del_button.configure(state="normal")
            self.copy_button.configure(state="normal")
            self.after(100, self._verify_is_any_checked)
            return
        self.del_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.after(100, self._verify_is_any_checked)
            
    def _update_vault(self) -> None:
        try:
            self.passwords_list = self.stored_passwords.get_passwords()
            self.items_frame.update_values(self.passwords_list)
            self.vault.encrypt_file(self.passwords_list)
        except Exception as e:
            raise ValueError(f"{e}")
        
    def _generate_password_callback(self) -> None:
        if self.generate_password_panel is None or not self.generate_password_panel.winfo_exists():
            self.generate_password_panel = GeneratePasswordPanel(
                stored_passwords = self.stored_passwords,
                on_update_callback = self._update_vault)
            self.generate_password_panel.focus() 
        else:
            self.generate_password_panel.focus() 

    def _delete_password_callback(self) -> None:
        if self.confirm_deletion_dialog is None or not self.confirm_deletion_dialog.winfo_exists():
            deletion_id = self.items_frame.get()
            self.confirm_deletion_dialog = DeletePasswordDialog(
                stored_passwords = self.stored_passwords, 
                password_id = deletion_id, 
                on_update_callback = self._update_vault)
            self.confirm_deletion_dialog.focus() 
        else:
            self.confirm_deletion_dialog.focus()

    def clear(self) -> None:
        copy('')

    def _copy_callback(self) -> None:
        selected_id = self.items_frame.get()
    
        if selected_id is None:
            return

        matching_password = self.stored_passwords.get_password(selected_id)

        if matching_password:
            password_string = matching_password[0]
            copy(password_string)
            self.after(30000, self.clear)