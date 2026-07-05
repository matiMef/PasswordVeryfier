import customtkinter, pyperclip, os

class ScrollablePasswordFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.checkboxes = []
    
        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(
                self, 
                text=value.name, 
                text_color="white", 
                text_color_disabled="gray",
                command=self.verifyState
            )
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

        self.update_values(values)

    def update_values(self, new_values: list):
        for checkbox in self.checkboxes:
            checkbox.destroy()
        self.checkboxes.clear()

        for i, value in enumerate(new_values):
            checkbox = customtkinter.CTkCheckBox(self,
                text=value.id, 
                text_color="white", 
                text_color_disabled="gray",
                command=self.verifyState)
            checkbox.database_id = value.id
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def verifyState(self):
        any_checked = any(cb.get() for cb in self.checkboxes)
        
        for checkbox in self.checkboxes:
            if checkbox.get():
                checkbox.configure(state="normal")
            else:
                new_state = "disabled" if any_checked else "normal"
                checkbox.configure(state=new_state)

    def get(self) -> int | None:
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                return checkbox.database_id
        return None

class GeneratedPasswordPanel(customtkinter.CTkToplevel):
    def __init__(self, master, stored_passwords, on_update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x200")
        self.title("Generator")
        self.grid_columnconfigure(0, weight=1)
        self.lift()
        self.time = TimeObject(30)
        self.on_update_callback = on_update_callback

        new_password = PasswordGenerator(32)
        self.stored_passwords = stored_passwords
    
        self.progressbar = customtkinter.CTkProgressBar(
            self,
            width=500,
            height=5,
            orientation="horizontal")
        self.progressbar.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20,10))
        self.progressbar.set(1)
        self.progressbar.configure(progress_color="green")

        self.label = customtkinter.CTkLabel(
            self,
            text=new_password.password,
            font=("Helvetica", 20, "bold"))
        self.label.grid(
            row=1,
            column=0,
            padx=(0,0),
            pady=(10,10)
        )

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
            row=2,
            column=0,
            padx=(50,0),
            pady=(20,10),
            sticky="w")

        self.save_button = customtkinter.CTkButton(
            self,   
            width=137,
            height=30,
            text="Save",
            font=("Helvetica", 16, "bold"),
            fg_color="#1BD625",
            hover_color="#11841D",
            command=self.save_callback) 
        self.save_button.grid(
            row=2,
            column=0,
            padx=(0,50),
            pady=(20,10),
            sticky="e")

        self.update_progressbar()

    def save_callback(self) -> str:
        new_password = self.label.cget("text")
        self.stored_passwords.add_password("test", new_password)
        if self.on_update_callback:
            self.on_update_callback()
        self.destroy()
        
    def update_progressbar(self) -> None:
        if self.time.is_elapsed() != True:
            progress = (30 - self.time.count_time())/30
            self.progressbar.set(progress)
            if progress <= 0.33:
                self.progressbar.configure(progress_color="red")
            elif progress <= 0.67:
                self.progressbar.configure(progress_color="yellow")
            else:
                self.progressbar.configure(progress_color="green")
            self.after(1000, self.update_progressbar)
        else:
            self.destroy()
   
class DeletionDialog(customtkinter.CTkToplevel):
    def __init__(self, stored_passwords, password_id, on_update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("350x120")
        self.title("Confirm")
        self.lift()
        self.grid_columnconfigure(0, weight=1)
        self.stored_passwords = stored_passwords
        self.password_id = password_id
        self.on_update_callback = on_update_callback

        self.label = customtkinter.CTkLabel(
            self, 
            text=f"Confirm Deletion",
            font=("Helvetica", 20, "bold"))
        self.label.grid(
            row=0, 
            column=0, 
            padx=0, 
            pady=(20,10),
            columnspan=2)
        
        self.cancel_button = customtkinter.CTkButton(
            self,
            width=137,
            height=30,
            text="Cancel",
            font=("Helvetica", 16, "bold"),
            fg_color="#1391E0",
            hover_color="#104483",
            command=self.destroy) 
        self.cancel_button.grid(
            row=1,
            column=0,
            padx=(0,170),
            pady=(20,10))
        
        self.delete_button = customtkinter.CTkButton(
            self,
            width=137,
            height=30,
            text="Delete",
            font=("Helvetica", 16, "bold"),
            fg_color="#E03913",
            hover_color="#831010",
            command=self.delete_callback) 
        self.delete_button.grid(
            row=1,
            column=0,
            padx=(170,0),
            pady=(20,10))

    def delete_callback(self):
        self.stored_passwords.delete_password(self.password_id)
        if self.on_update_callback:
            self.on_update_callback()
        self.destroy()

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
        self.vault = VaultHandler("vault.json", self.current_dir)
        self.stored_passwords = StoredPasswords()
        self.vault.create_file()
        raw_data = self.vault.decrypt_and_load("password")
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
        self.vault._encrypt_file(self.passwords_list, "password")
        
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