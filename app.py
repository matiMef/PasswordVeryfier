from customtkinter import CTk, CTkLabel, CTkEntry, CTkCheckBox, CTkButton, CTkToplevel, StringVar, CTkProgressBar, CTkInputDialog
from Backend.vault import AuthService
from Backend.checker import Password
from Interface.passwords_panel import PasswordPanel

class App(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        self.resizable(False, False)
        self.toplevel_window = None
        self.grid_columnconfigure(0, weight=1)
        vpf=(self.register(self._validate_pass_field), "%P")

        self.auth_service = AuthService()

        self.app_title = CTkLabel(
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

        self.checker_field = CTkEntry(
            self,
            width=500,
            height=45,
            placeholder_text="Password",
            validate="key",
            validatecommand=vpf,
            font=("Helvetica", 16), 
            show="*")
        self.checker_field.grid(
            row=1,
            column=0,
            padx=50,
            pady=(20, 10))
        
        self.default_var = StringVar(value="off")
        self.checkbox = CTkCheckBox(
            self,
            text="Show password",
            command=self.onchange_show,
            variable=self.default_var,
            font=("Helvetica", 14, "bold"), 
            onvalue="on",
            offvalue="off")
        self.checkbox.grid(
            row=2,
            column=0,
            padx=50,
            pady=(10,20),
            sticky="w")

        self.submit_button = CTkButton(
            self,
            width=200,
            height=40,
            text="Submit",
            fg_color="#1f6aa5",
            hover_color="#144871",
            command=self.on_submit,
            font=("Helvetica", 16, "bold"))
        self.submit_button.grid(
            row=4,
            column=0,
            padx=50,
            pady=(10,20),
            columnspan=2,
            sticky="w")
        
        self.panel_button = CTkButton(
            self,
            width=200,
            height=40,
            text="Saved passwords",
            fg_color="#1BD625",
            hover_color="#11841D",
            command=self.auth_access,
            font=("Helvetica", 16, "bold"))
        self.panel_button.grid(
            row=4,
            column=0,
            padx=50,
            pady=(10,20),
            columnspan=2,
            sticky="e")

        self.progressbar = CTkProgressBar(
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

        self.crack_time_label = CTkLabel(
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

    def onchange_show(self) -> None:
        self.checkbox_state = self.checkbox.get()
        if self.checkbox_state == "on":
            self.checker_field.configure(show="")
        else:
            self.checker_field.configure(show="*")

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

        elif password.complexity in ("Strong", "Average") and (years > 100):
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

    def on_submit(self) -> None:
        password = Password(self.checker_field.get())
        self.show_label(password)
        self.update_progressbar(password)

    def open_panel(self, user_input) -> None:
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = PasswordPanel(user_input)  
        else:
            self.toplevel_window.focus()

    def auth_access(self) -> None:
        dialog = CTkToplevel(self)
        dialog.title("Authorization")
        dialog.geometry("360x140")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        entry = CTkEntry(
            dialog,
            width=300,
            placeholder_text="Password",
            show="*",
            font=("Helvetica", 16))
        entry.grid(
            row=0, 
            column=0, 
            columnspan=2, 
            padx=20, 
            pady=(20, 6))

        show_var = StringVar(value="off")
        checkbox = CTkCheckBox(
            dialog,
            text="Show password",
            variable=show_var,
            onvalue="on",
            offvalue="off",
            command=lambda: entry.configure(show="" if show_var.get() == "on" else "*"))
        checkbox.grid(row=1, 
                      column=0, 
                      padx=20, 
                      pady=(0, 8), 
                      sticky="w")

        result = {"password": None}

        def on_ok():
            result["password"] = entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ok_button = CTkButton(
            dialog, 
            width=100, 
            height=30, 
            text="OK", 
            command=on_ok)
        ok_button.grid(
            row=2, 
            column=0, 
            padx=(40, 10), 
            pady=10, 
            sticky="e")

        cancel_button = CTkButton(
            dialog, 
            width=100, 
            height=30, 
            text="Cancel", 
            command=on_cancel)
        cancel_button.grid(
            row=2, 
            column=1, 
            padx=(10, 40), 
            pady=10, 
            sticky="w")

        self.wait_window(dialog)

        user_input = result["password"]
        if user_input and self.auth_service.verify_password(user_input):
            self.open_panel(user_input)
        
app = App()
app.mainloop()