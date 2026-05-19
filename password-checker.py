import string
import secrets
import hashlib
from math import pow
import customtkinter

class Password:
    def __init__(self, password: str):
        self.password = str(password)
        self.length = len(password)
        self.pool_size = self._calculate_pool_size
        self.complexity = self._check_password_complexity
        self.crack_time = self._map_crack_time

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
            52: "Weak",
            58: "Weak",
            62: "Average",
            68: "Average",
            84: "Strong",
            94: "Strong+"
        }
        return complexity_map.get(self.pool_size, "Unknown")

    def estimate_crack_time(self, computional_capacity: float = 3e11) -> float:
        T = pow(self.pool_size, self.length)/computional_capacity
        return T

    def _map_crack_time(self) -> str | tuple:
        total_time = []
        total_seconds = int(self.estimate_crack_time())
        
        if total_seconds == 0:
            return "Immediately"

        seconds = total_seconds % 60
        total_time.append(seconds)
        total_minutes = total_seconds // 60
        
        
        minutes = total_minutes % 60
        total_time.append(minutes)
        total_hours = total_minutes // 60
       
        
        hours = total_hours % 24
        total_time.append(hours)
        total_days = total_hours // 24
        

        days = total_days % 365
        total_time.append(days)
        years = float(total_days // 365)
        total_time.append(years)        

        return total_time
    
class PasswordGenerator:
    def __init__(self, length: int):
        self.length = length
        self.password = self._generate_password()

    def _generate_password(self) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        secure_password = ''.join(secrets.choice(alphabet) for i in range(self.length))
        return secure_password

class AuthService:
    def __init__(self):
        self.unlock_hash="abc"
        self.stored_hash="abc"

    def _claimStoredHash(self):
        pass
    
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
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes

class PasswordPanel(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x250")
        self.title("Vault")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

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
            fg_color="#1CE634",
            hover_color="#11841D",
            command=self.button_callback)
        self.gen_button.grid(
            row=3, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="w")

        self.del_button = customtkinter.CTkButton(
            self,
            width=137,
            height=30,
            text="Delete",
            fg_color="#E03913",
            hover_color="#831010",
            command=self.button_callback)
        self.del_button.grid(
            row=3, 
            column=0, 
            padx=157, 
            pady=10, 
            sticky="w")
        
        self.copy_button = customtkinter.CTkButton(
            self,
            width=137,
            height=30, 
            text="Copy",
            fg_color="#1391E0",
            hover_color="#104483",
            command=self.button_callback)
        self.copy_button.grid(
            row=3, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="e")
        
        self.exit_button = customtkinter.CTkButton(
            self,
            width=137,
            height=30,
            text="Exit",
            fg_color="#E0DC13",
            hover_color="#7F8310",
            command=self.button_callback)
        self.exit_button.grid(
            row=3, 
            column=0, 
            padx=157, 
            pady=10, 
            sticky="e")
    
    def button_callback(self):
        self.confirmation_dialog=ConfirmationDialog("deletion")

class ConfirmationDialog(customtkinter.CTkToplevel):
    def __init__(self, dialog_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x200")
        self.title("Confirm")
        self.dialog_type = dialog_type

        self.grid_rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(
            self, 
            text=f"Confirm {self.dialog_type}")
        self.label.grid(
            row=0, 
            column=0, 
            padx=0, 
            pady=(20,0))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        
        self.auth_service = AuthService()
        self.toplevel_window = None

        new_password = PasswordGenerator(32)
        print(new_password.password)

        self.grid_columnconfigure(0, weight=1)

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
        
        # , validatecommand=self.validate_field_input
        self.password_field = customtkinter.CTkEntry(
            self,
            width=500,
            height=45,
            placeholder_text="Password",
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

        self.password_submit = customtkinter.CTkButton(
            self,
            width=200,
            height=40,
            text="Submit",
            fg_color="#1f6aa5",
            hover_color="#144871",
            command=self.button_callback,
            font=("Helvetica", 14, "bold"))
        self.password_submit.grid(
            row=4,
            column=0,
            padx=50,
            pady=(10,20),
            columnspan=2,
            sticky="w")
        
        self.generate_password = customtkinter.CTkButton(
            self,
            width=200,
            height=40,
            text="Saved passwords",
            fg_color="#1CE634",
            hover_color="#11841D",
            command=self.auth_access,
            font=("Helvetica", 14, "bold"))
        self.generate_password.grid(
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
            font=("Helvetica", 14, "bold"))
        self.crack_time_label.grid(
            row=5,
            column=0,
            padx=20,
            pady=20,
            columnspan=2)
    
    def auth_access(self) -> None:
        self.dialog = customtkinter.CTkInputDialog(text="Type in a password:", title="Authorization")
        user_input = self.dialog.get_input()
        # if self.auth_service.verify_password(user_input):
        self.openPanel()
    
    def openPanel(self) -> None:
        print("something")
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

    def button_callback(self) -> None:
        password = Password(self.password_field.get())
        self.show_label(password)
        self.update_progressbar(password)

    def show_label(self, password: str) -> None:
        crack_time = password.crack_time[4]
        self.crack_time_label.configure(text=f"Estimated time to crack: {crack_time}")

    def update_progressbar(self, password: str) -> None:
        if password.length < 8 or (password.crack_time[3] < 60 and password.crack_time[4] < 1):
            self.progressbar.set(0.1)
            self.progressbar.configure(progress_color="red")
        elif password.complexity == "Weak" or (password.crack_time[3] <= 120 or password.crack_time[4] < 1):
            self.progressbar.set(0.2)
            self.progressbar.configure(progress_color="red")
        elif password.complexity == "Average" or (password.crack_time[3] > 120 or (password.crack_time[4] >= 1 and password.crack_time[4] < 10)):
            self.progressbar.set(0.5)
            self.progressbar.configure(progress_color="yellow")
        elif password.complexity == "Strong" and (password.crack_time[4] >= 10):
            self.progressbar.set(0.8)
            self.progressbar.configure(progress_color="green")
        elif password.complexity == "Strong+" and (password.crack_time[4] >= 100):
            self.progressbar.set(1)
            self.progressbar.configure(progress_color="green")
        else:
            self.progressbar.set(0.5)
            self.progressbar.configure(progress_color="gray")
            
app = App()
app.mainloop()