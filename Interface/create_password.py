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
        self.title("Set Master Password")
        self.wait_visibility()
        self.geometry("400x200")
        self.resizable(False, False)
        self.lift()

        self.password = None
        self.current_dir = path.dirname(path.abspath(__file__))

        self.new_password_field = CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text="Password",
            font=("Helvetica", 18, "bold"),
            show="*",
        )
        self.new_password_field.grid(row=0, column=0, padx=50, pady=(20, 10), sticky="w")

        self.show_var = StringVar(value="off")
        self.show_password_checkbox = CTkCheckBox(
            self,
            text="Show password",
            variable=self.show_var,
            fg_color="#111111",
            hover_color="#111111",
            onvalue="on",
            offvalue="off",
            command=lambda: self.new_password_field.configure(show="" if self.show_var.get() == "on" else "*"))
        self.show_password_checkbox.grid(row=1, column=0, padx=50, pady=(10, 20), sticky="w")

        self.exit_button = CTkButton(
            self,
            width=100,
            height=30,
            text="Exit",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self.exit_callback,
        )
        self.exit_button.grid(row=2, column=0, padx=50, pady=10, sticky="w")

        self.create_password_button = CTkButton(
            self,
            width=100,
            height=30,
            text="Accept",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self._create_password_callback,
        )
        self.create_password_button.grid(row=2, column=0, padx=(0,50), pady=10, sticky="e")

    def _create_password_callback(self) -> None:
        try:
            self._accept_new_password(self.new_password_field.get())
        except Exception as e:
            raise e

    def _accept_new_password(self, password) -> None:
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
        self.new_password_field.focus()
        self.new_password_field.configure(placeholder_text="Invalid password")

    def exit_callback(self) -> None:
        self.destroy()