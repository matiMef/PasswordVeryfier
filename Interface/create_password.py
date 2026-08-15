from os import path

from customtkinter import (
    CTkToplevel,
    CTkButton,
    CTkEntry,
    CTkCheckBox,
    StringVar,
)

from Backend.vault import VaultHandler

class CreatePasswordPanel(CTkToplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.geometry("350x250")
        self.title("Create Password Panel")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.resizable(False, False)

        self.current_dir = path.dirname(path.abspath(__file__))

        self.checker_field = CTkEntry(
            self,
            width=300,
            height=45,
            placeholder_text="Password",
            font=("Helvetica", 16),
            show="*",
        )
        self.checker_field.grid(row=1, column=0, padx=50, pady=(20, 10))

        self.default_var = StringVar(value="off")
        self.checkbox = CTkCheckBox(
            self,
            text="Show password",
            command=self.onchange_show,
            variable=self.default_var,
            font=("Helvetica", 14, "bold"),
            onvalue="on",
            offvalue="off",
        )
        self.checkbox.grid(row=2, column=0, padx=50, pady=(10, 20), sticky="w")

        self.create_password_button = CTkButton(
            self,
            width=137,
            height=30,
            text="Save password",
            font=("Helvetica", 16, "bold"),
            fg_color="#1BD625",
            hover_color="#11841D",
            command=self.gen_callback,
        )
        self.create_password_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.exit_button = CTkButton(
            self,
            width=137,
            height=30,
            text="Copy",
            font=("Helvetica", 16, "bold"),
            fg_color="#1391E0",
            hover_color="#104483",
            command=self.exit_callback,
        )
        self.exit_button.grid(row=3, column=0, padx=157, pady=10, sticky="w")


    def onchange_show(self) -> None:
        if self.default_var.get() == "on":
            self.checker_field.configure(show="")
        else:
            self.checker_field.configure(show="*")

    def gen_callback(self) -> None:
        self.accept_new_password(self.checker_field.get())

    def accept_new_password(self, password) -> None:
        self.password = password
        if self._validate_password(password):
            self.vault = VaultHandler("vault.json", self.current_dir, self.password)
            self.vault.create_file()
            self.destroy()
        else:
            self._update_field_event()

    def _validate_password(self, new_pass) -> bool:
        if new_pass is None or new_pass == "":
            return False

        if new_pass.strip() == "":
            return False

        if not all(ch.isprintable() for ch in new_pass):
            return False

        if len(new_pass) > 128:
            return False

        return True

    def _update_field_event(self) -> None:
        self.checker_field.focus()
        self.checker_field.delete(0, "end")
        self.checker_field.configure(placeholder_text="Invalid password")

    def exit_callback(self) -> None:
        self.destroy()