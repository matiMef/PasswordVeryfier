from customtkinter import CTk, CTkLabel, CTkEntry, CTkCheckBox, CTkButton, StringVar, CTkProgressBar, CTkToplevel
from Backend.vault import AuthService, VaultHandler
from Backend.checker import Password
from Interface.passwords_panel import PasswordsPanel
from Interface.create_password import CreatePasswordPanel
from pathlib import Path

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Vault and Veryfier")
        self.geometry("600x350")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        vpf=(self.register(self._validate_pass_field), "%P")

        self.filepath = self._make_filepath()

        self.create_panel = None
        self.auth_access_panel = None
        self.password_panel = None

        self.app_title_field = CTkLabel(
            self,
            text="Check password strength",
            fg_color="transparent",
            font=("Helvetica", 24, "bold"))
        self.app_title_field.grid(row=0, column=0, padx=20, pady=(20, 0), columnspan=2)

        self.password_checker_field = CTkEntry(
            self,
            width=500,
            height=45,
            placeholder_text="Password",
            validate="key",
            validatecommand=vpf,
            font=("Helvetica", 16, "bold"), 
            show="*")
        self.password_checker_field.grid(row=1, column=0, padx=50, pady=(20, 10))
        
        self.show_var = StringVar(value="off")
        self.checkbox = CTkCheckBox(
            self,
            text="Show password",
            variable=self.show_var,
            font=("Helvetica", 14, "bold"), 
            fg_color="#111111",
            hover_color="#111111",
            onvalue="on",
            offvalue="off",
            command=lambda: self.password_checker_field.configure(show="" if self.show_var.get() == "on" else "*"))
        self.checkbox.grid(row=2, column=0, padx=50, pady=(10,20), sticky="w")

        self.check_password_button = CTkButton(
            self,
            width=200,
            height=40,
            text="Check password",
            fg_color="#606363",
            hover_color="#111111",
            font=("Helvetica", 16, "bold"),
            command=self._on_submit)
        self.check_password_button.grid(row=4, column=0, padx=50, pady=(10,20), columnspan=2, sticky="w")
        
        self.open_password_panel_button = CTkButton(
            self,
            width=200,
            height=40,
            text="Vault",
            fg_color="#606363",
            hover_color="#111111",
            command=self._verify_file,
            font=("Helvetica", 16, "bold"))
        self.open_password_panel_button.grid(row=4, column=0, padx=50, pady=(10,20), columnspan=2, sticky="e")

        self.password_strength_bar = CTkProgressBar(
            self,
            width=500,
            height=5,
            orientation="horizontal")
        self.password_strength_bar.grid(row=3, column=0, padx=20, pady=20, columnspan=2)
        self.password_strength_bar.set(0.1)
        self.password_strength_bar.configure(progress_color="gray")

        self.crack_time_label = CTkLabel(
            self, text="",
            fg_color="transparent", 
            font=("Helvetica", 20, "bold"))
        self.crack_time_label.grid(row=5, column=0, padx=0, pady=20, columnspan=2)

    def _make_filepath(self) -> Path:
        try:
            current_file = Path(__file__).resolve()
            current_dir = current_file.parent
            filepath = current_dir / "Interface"
            return filepath
        except Exception as e:
            raise ValueError(f"Error while creating filepath: {e}")

    def _validate_pass_field(self, new_pass: str) -> bool:
        if new_pass == "":
            return True
        
        if len(new_pass) > 128:
            return False
        
        return True

    def _verify_file(self) -> None:
        handler = VaultHandler("vault.json", self.filepath)

        if not handler.check_file():
            self._create_password_event()
            return

        self._auth_access_event()

    def _empty_password_notification(self):
        self.password_checker_field.configure(
            border_color="#ff4d4d",
            border_width=2)
        self.password_checker_field.focus_set()

    def _ok_notification(self):
        self.password_checker_field.configure(
            border_color="gray",
            border_width=1)
        self.password_checker_field.focus_set()

    def _on_submit(self) -> None:
        password = Password(self.password_checker_field.get())

        if password.password is None or password.password == "":
            self._empty_password_notification()
            raise ValueError("Password cannot be empty")
        self._ok_notification()

        self.show_label(password)
        self.update_progressbar(password)

    def show_label(self, password: str) -> None:
        crack_time = password.crack_time
        self.crack_time_label.configure(text=f"Estimated time to crack: {crack_time}")

    def update_progressbar(self, password: str) -> None:
        try:
            crack_time_dict = password.map_crack_time()
            years, days = crack_time_dict["years"], crack_time_dict["days"]

            if password.length < 8:
                self.password_strength_bar.set(0.1)
                self.password_strength_bar.configure(progress_color="red")

            elif password.complexity in ("Strong+", "Strong") and years > 10_000:
                self.password_strength_bar.set(1)
                self.password_strength_bar.configure(progress_color="green")

            elif password.complexity in ("Strong", "Average") and (years > 100):
                self.password_strength_bar.set(0.8)
                self.password_strength_bar.configure(progress_color="green")

            elif password.complexity == "Average" and (days > 120 or years >= 1):
                self.password_strength_bar.set(0.5)
                self.password_strength_bar.configure(progress_color="yellow")

            elif password.complexity == "Weak" and (days < 120 and years < 1):
                self.password_strength_bar.set(0.2)
                self.password_strength_bar.configure(progress_color="red")

            else:
                self.password_strength_bar.set(0.2)
                self.password_strength_bar.configure(progress_color="red")
        except ValueError as e:
            raise e

    def _password_panel_event(self, plain_password: str) -> None:
        try:
            if self.password_panel is None or not self.password_panel .winfo_exists():
                self.password_panel  = PasswordsPanel(password=plain_password, master=self)
                self.wait_visibility()
                self.wait_window(self.password_panel)
            else:
                self.password_panel.focus()
        except Exception as e:
            raise e
    
    def _create_password_event(self) -> None:
        try:
            if self.create_panel is None or not self.create_panel.winfo_exists():
                self.create_panel = CreatePasswordPanel(master=self)
                self.create_panel.focus()
                self.wait_window(self.create_panel)
            else:
                self.create_panel.focus()
        except Exception as e:
            raise e

    def _auth_access_event(self) -> None:
        dialog = CTkToplevel(self)
        dialog.title("Authorization")
        dialog.wait_visibility()
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self)
        self.lift()

        auth_service = AuthService()

        entry = CTkEntry(
            dialog,
            width=300,
            height=40,
            placeholder_text="Password",
            show="*",
            font=("Helvetica", 18, "bold"))
        entry.grid(row=0, column=0, padx=50, pady=(20, 10))

        show_var = StringVar(value="off")
        checkbox = CTkCheckBox(
            dialog,
            text="Show password",
            variable=show_var,
            onvalue="on",
            offvalue="off",
            fg_color="#111111",
            hover_color="#111111",
            command=lambda: entry.configure(show="" if show_var.get() == "on" else "*"))
        checkbox.grid(row=1, column=0, padx=50, pady=(10, 20), sticky="w")

        result = {"password": None}

        def _wrong_password_notification():
            entry.configure(
                border_color="#ff4d4d",
                border_width=2,
            )
            entry.focus_set()

        def _empty_password_notification():
            entry.configure(
                border_color="#ff4d4d",
                border_width=2,
            )
            entry.focus_set()

        def on_ok():
            result["password"] = entry.get()

            if result["password"] is None or result["password"] == "":
                _empty_password_notification()
                return

            if auth_service.verify_password(result["password"]) is False:
                _wrong_password_notification()
                return

            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        cancel_button = CTkButton(
            dialog, 
            width=100, 
            height=30,
            fg_color="#606363",
            hover_color="#111111",
            text="Cancel",
            font=("Helvetica", 16, "bold"),
            command=on_cancel)
        cancel_button.grid(row=2, column=0, padx=50, pady=10, sticky="w")

        ok_button = CTkButton(
            dialog, 
            width=100, 
            height=30,
            fg_color="#606363",
            hover_color="#111111",            
            font=("Helvetica", 16, "bold"),
            text="OK", 
            command=on_ok)
        ok_button.grid(row=2, column=0, padx=(0,50), pady=10, sticky="e")

        self.wait_window(dialog)

        try:
            user_input = result["password"]
            if user_input and auth_service.verify_password(user_input):
                self._password_panel_event(user_input)
 
        except Exception as e:
            print("Authentication error")
        
app = App()
app.mainloop()