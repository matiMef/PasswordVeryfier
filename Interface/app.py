import customtkinter

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