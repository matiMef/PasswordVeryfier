import string
import secrets
import hashlib
from math import pow
import customtkinter
import pyperclip
import time
import json
import os

class Password:
    def __init__(self, password: str):
        self.password = str(password)
        self.length = len(password)
        self.pool_size = self._calculate_pool_size() 
        self.complexity = self._check_password_complexity()
        self.crack_time = self._format_crack_time()

    def check_is_short(self) -> bool:
        return True if self.length < 6 else False

    def is_any_lower(self) -> bool:
        return True if any(char in string.ascii_lowercase for char in self.password) else False
        
    def is_any_upper(self) -> bool:
        return True if any(char in string.ascii_uppercase for char in self.password) else False
        
    def is_any_digit(self) -> bool:
        return True if any(char in string.digits for char in self.password) else False
        
    def is_any_special(self) -> bool:
        return True if any(char in string.punctuation for char in self.password) else False
    
    def _calculate_pool_size(self) -> int:
        pool_size = 0
        if self.is_any_lower(): pool_size += 26
        if self.is_any_upper(): pool_size += 26
        if self.is_any_digit(): pool_size += 10
        if self.is_any_special(): pool_size += 32
        return pool_size
    
    def _check_password_complexity(self) -> tuple:
        complexity_map = {
            10: "Weak",
            26: "Weak",
            32: "Weak",
            36: "Weak",
            42: "Weak",
            52: "Average",
            58: "Average",
            62: "Average",
            68: "Strong",
            84: "Strong",
            94: "Strong+"
        }
        return complexity_map.get(self.pool_size, "Unknown")

    def estimate_crack_time(self, computional_capacity: float = 3e11) -> float:
        T = pow(self.pool_size, self.length)/computional_capacity
        return T

    def map_crack_time(self) -> str | dict: 
        total_time = {"years": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}
        total_seconds = int(self.estimate_crack_time())
        
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        
        minutes = total_minutes % 60
        total_hours = total_minutes // 60
       
        hours = total_hours % 24
        total_days = total_hours // 24
        
        days = total_days % 365
        years = total_days // 365
        
        total_time.update({"years": years, "days": days, "hours": hours, "minutes": minutes, "seconds": seconds})

        return total_time
    
    def _format_crack_time(self) -> str:
        crack_time_dict = self.map_crack_time()
        years, days, hours, minutes, seconds = crack_time_dict["years"], crack_time_dict["days"], crack_time_dict["hours"], crack_time_dict["minutes"], crack_time_dict["seconds"]
        
        if years > 0:
            if years < 1_000_000:
                return f"{years} years"
            else:
                return f"{years:.2e} years"
        elif days > 0:
            return f"{days} days"
        else:
            return f"{hours}h:{minutes}m:{seconds}s"

class PasswordGenerator:
    def __init__(self, length: int):
        self.length = length
        self.password = self._generate_password()

    def _generate_password(self) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        secure_password = ''.join(secrets.choice(alphabet) for i in range(self.length))
        return secure_password

class JsonPassword:
    def __init__(self, id: int, name: str, password: str):
        self.id = id
        self.name = name
        self.encrypted_password = password

class StoredPasswords:
    def __init__(self):
        self.passwords = []

    def _encrypt_password(self, password: str) -> str:
        pass

    def _decrypt_password(self, id: int) -> str:
        pass

    def get_passwords(self) -> None:
        return self.passwords

    def set_passwords(self, passwords: list) -> None:
        self.passwords = passwords

    def add_password(self, name: str, password: str) -> None:
        new_id = len(self.passwords) + 1
        new_name = name
        new_password = self._encrypt_password(password)
        new_password_obj = JsonPassword(new_id, new_name, new_password)
        self.passwords.append(new_password_obj)

    def delete_password(self, id: int) -> None:
        self.passwords = [p for p in self.passwords if p.id != id]
        
class VaultHandler:
    def __init__(self, name: str, path: str):
        self.filename = name
        self.filepath = path + "/" + name
        self.encoded_file = self.create_file()
        
    def check_file(self) -> bool:
        return os.path.exists(self.filepath)

    def create_file(self) -> json:
        if self.check_file():
            with open(self.filepath, "r", encoding="utf-8") as file:
                return file
        
        with open(self.filepath, "w", encoding="utf-8") as file:
            file.write("{}")
            return file

    def _decrypt_file(self) -> json:
        secret_key = "key"
        # otwarcie pliku
        # zcyztanie soli
        # odkodowanie pliku
        # zwrócenie pliku

    def _encrypt_file(self) -> None:
        secret_key = "key"
        new_encoded_file = None
        # zaszyfrowanie pliku
        self.encoded_file = new_encoded_file
        # zapisanie pliku

    def map_password(self) -> tuple:
        # uruchomienie dekodowania pliku
        # pobranie haseł z pliku
        with open(self.filepath, "r", encoding="utf-8") as file:
            passwords_obj = json.load(self.file)
        # mapowanie passwords_obj na tablice obiektów JSONpassword
        return passwords_obj
    
class AuthService:
    def __init__(self):
        self.stored_hash="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

    def verify_password(self, plain_password: str) -> bool:
        if not plain_password:
            return False
        
        input_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return input_hash == self.stored_hash

class ScrollablePasswordFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.checkboxes = []

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(
                self, 
                text=value, 
                text_color="white", 
                text_color_disabled="gray",
                command=self.verifyState
            )
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

    def get(self) -> str | None:
        for checkbox in self.checkboxes:
            if checkbox.get():
                return checkbox.cget("text")
        return None
    
class TimeObject:
    def __init__(self, duration: int):
        self.start = time.time()
        self.duration = duration

    def count_time(self) -> int:
        current_time = time.time() 
        return int(current_time - self.start)

    def is_elapsed(self) -> bool:
        current_time = time.time()
        if self.start + self.duration - current_time <= 0:
            return True
        else:
            return False

class GeneratedPasswordPanel(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x200")
        self.title("Generator")
        self.grid_columnconfigure(0, weight=1)
        self.lift()
        self.time = TimeObject(30)

        new_password = PasswordGenerator(32)

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
        vault = VaultHandler()
        new_password = self.label.cget("text")
        vault.save_password(self, new_password)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("350x120")
        self.title("Confirm")
        self.lift()
        self.grid_columnconfigure(0, weight=1)

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
        pass

class PasswordPanel(customtkinter.CTkToplevel): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x250")
        self.title("Vault")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.gen_panel = None
        self.confirmation_dialog = None

        values = ["value 1", "value 2", "value 3", "value 4", "value 5", "value 6"]
        self.scrollable_checkbox_frame = ScrollablePasswordFrame(
            self, 
            title="Saved passwords", 
            values=values)
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
    
    def gen_callback(self):
        if self.gen_panel is None or not self.gen_panel.winfo_exists():
            self.gen_panel = GeneratedPasswordPanel()
        else:
            self.gen_panel.focus() 

    def del_callback(self):
        if self.confirmation_dialog is None or not self.confirmation_dialog.winfo_exists():
            self.confirmation_dialog = DeletionDialog()
        else:
            self.confirmation_dialog.focus() 

    def copy_callback(self):
        pyperclip.copy('password')
        pyperclip.copy('')

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        self.auth_service = AuthService()
        self.toplevel_window = None
        self.grid_columnconfigure(0, weight=1)

        vpf=(self.register(self._validate_pass_field), "%P")

        self.app_title = customtkinter.CTkLabel(
            self,
            text="Check password strength",
            fg_color="transparent",
            font=("Helvetica", 24, "bold"))
        
        self.app_title.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 0),
            columnspan=2)

        self.password_field = customtkinter.CTkEntry(
            self,
            width=500,
            height=45,
            placeholder_text="Password",
            validate="key",
            validatecommand=vpf,
            font=("Helvetica", 16), show="*")
        self.password_field.grid(
            row=1,
            column=0,
            padx=50,
            pady=(20, 10))
        
        self.check_var = customtkinter.StringVar(value="off")
        self.checkbox = customtkinter.CTkCheckBox(
            self,
            text="Show password",
            command=self.checkbox_event,
            variable=self.check_var,
            font=("Helvetica", 14, "bold"), 
            onvalue="on",
            offvalue="off")
        self.checkbox.grid(
            row=2,
            column=0,
            padx=50,
            pady=(10,20),
            sticky="w")

        self.submit_button = customtkinter.CTkButton(
            self,
            width=200,
            height=40,
            text="Submit",
            fg_color="#1f6aa5",
            hover_color="#144871",
            command=self.submit_password,
            font=("Helvetica", 16, "bold"))
        self.submit_button.grid(
            row=4,
            column=0,
            padx=50,
            pady=(10,20),
            columnspan=2,
            sticky="w")
        
        self.open_panel_button = customtkinter.CTkButton(
            self,
            width=200,
            height=40,
            text="Saved passwords",
            fg_color="#1BD625",
            hover_color="#11841D",
            command=self.auth_access,
            font=("Helvetica", 16, "bold"))
        self.open_panel_button.grid(
            row=4,
            column=0,
            padx=50,
            pady=(10,20),
            columnspan=2,
            sticky="e")

        self.progressbar = customtkinter.CTkProgressBar(
            self,
            width=500,
            height=5,
            orientation="horizontal")
        self.progressbar.grid(
            row=3,
            column=0,
            padx=20,
            pady=20,
            columnspan=2)
        self.progressbar.set(0.1)
        self.progressbar.configure(progress_color="gray")

        self.crack_time_label = customtkinter.CTkLabel(
            self, text="",
            fg_color="transparent", 
            font=("Helvetica", 20, "bold"))
        self.crack_time_label.grid(
            row=5,
            column=0,
            padx=0,
            pady=20,
            columnspan=2)
    
    def _validate_pass_field(self, new_pass: str) -> bool:
        if new_pass == "":
            return True
        
        if len(new_pass) > 128:
            return False
        
        return True

    def auth_access(self) -> None:
        self.dialog = customtkinter.CTkInputDialog(text="Type in password:", title="Authorization")
        user_input = self.dialog.get_input()
        if self.auth_service.verify_password(user_input):
            self.open_panel()
    
    def open_panel(self) -> None:
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = PasswordPanel()  
        else:
            self.toplevel_window.focus()

    def checkbox_event(self) -> None:
        self.checkbox_state = self.checkbox.get()
        if self.checkbox_state == "on":
            self.password_field.configure(show="")
        else:
            self.password_field.configure(show="*")

    def submit_password(self) -> None:
        password = Password(self.password_field.get())
        self.show_label(password)
        self.update_progressbar(password)

    def show_label(self, password: str) -> None:
        crack_time = password.crack_time
        self.crack_time_label.configure(text=f"Estimated time to crack: {crack_time}")

    def update_progressbar(self, password: str) -> None:
        crack_time_dict = password.map_crack_time()
        years, days = crack_time_dict["years"], crack_time_dict["days"]

        if password.length < 8:
            self.progressbar.set(0.1)
            self.progressbar.configure(progress_color="red")
        elif password.complexity in ("Strong+", "Strong") and years > 10_000:
            self.progressbar.set(1)
            self.progressbar.configure(progress_color="green")
        elif password.complexity in ("Strong" or "Average") and (years > 100):
            self.progressbar.set(0.8)
            self.progressbar.configure(progress_color="green")
        elif password.complexity == "Average" and (days > 120 or years >= 1):
            self.progressbar.set(0.5)
            self.progressbar.configure(progress_color="yellow")
        elif password.complexity == "Weak" and (days < 120 and years < 1):
            self.progressbar.set(0.2)
            self.progressbar.configure(progress_color="red")
        else:
            self.progressbar.set(0.2)
            self.progressbar.configure(progress_color="red")
            
app = App()
app.mainloop()