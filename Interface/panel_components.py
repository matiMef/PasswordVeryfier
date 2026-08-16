from customtkinter import CTkScrollableFrame, CTkCheckBox, CTkToplevel, CTkProgressBar, CTkLabel, CTkButton, CTkEntry
from Backend.generator import PasswordGenerator
from Utilities.time import TimeObject

class ItemsFrame(CTkScrollableFrame):
    def __init__(self, master: object, title: str, values: list):
        super().__init__(master, label_text=title, label_font=("Helvetica", 20, "bold"))
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.checkboxes = []

        self.update_values(values)

    def update_values(self, new_values: list) -> None:
        target_count = len(new_values)

        for checkbox in self.checkboxes[target_count:]:
            checkbox.grid_remove()

        self.checkboxes = self.checkboxes[:target_count]

        for i, value in enumerate(new_values):
            if i < len(self.checkboxes):
                checkbox = self.checkboxes[i]
                checkbox.configure(text=value.name)
                checkbox.configure(state="normal")
                checkbox.deselect()
            else:
                checkbox = CTkCheckBox(
                    self,
                    text=value.name,
                    text_color="white",
                    text_color_disabled="gray",
                    fg_color="#111111",
                    hover_color="#111111",
                    command=self._verifyState,
                    font=("Helvetica", 20, "bold"))
                self.checkboxes.append(checkbox)

            checkbox.database_id = value.id
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")

        self._verifyState()

    def check_state(self) -> bool:
        any_checked = any(cb.get() for cb in self.checkboxes)
        if any_checked:
            return True
        return False

    def _verifyState(self) -> None:
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

class GeneratePasswordPanel(CTkToplevel):
    def __init__(self, stored_passwords, on_update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Generate password")
        self.wait_visibility()
        self.geometry("500x150")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grab_set()
        self.lift()

        self.stored_passwords = stored_passwords
        self.on_update_callback = on_update_callback

        self.time = TimeObject(30)
        new_password = PasswordGenerator(32)

        self.remaining_timebar = CTkProgressBar(
            self,
            width=500,
            height=5,
            orientation="horizontal")
        self.remaining_timebar.grid(row=0, column=0, padx=20, pady=(20,10))
        self.remaining_timebar.configure(progress_color="green")
        self.remaining_timebar.set(1)

        self.label = CTkLabel(
            self,
            text=new_password.password,
            font=("Helvetica", 20, "bold"))
        self.label.grid(row=1, column=0, padx=(0,0), pady=(10,10))

        self.exit_button = CTkButton(
            self,
            width=100,
            height=30,
            text="Exit",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self.destroy) 
        self.exit_button.grid(row=2, column=0, padx=(50,0), pady=(20,10), sticky="w")

        self.save_password_button = CTkButton(
            self,   
            width=100,
            height=30,
            text="Save",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self._save_password_callback) 
        self.save_password_button.grid(row=2, column=0, padx=(0,50), pady=(20,10), sticky="e")

        self._update_timebar()

    def _save_password_callback(self) -> str:
        try:
            new_password = self.label.cget("text")
            self._create_password_name(new_password)
            if self.on_update_callback:
                self.on_update_callback()
            self.destroy()
        except Exception as e:
            raise ValueError(f"{e}")
        
    def _update_timebar(self) -> None:
        if self.time.is_elapsed() != True:
            progress = (30 - self.time.count_time())/30
            self.remaining_timebar.set(progress)
            if progress <= 0.33:
                self.remaining_timebar.configure(progress_color="red")
            elif progress <= 0.67:
                self.remaining_timebar.configure(progress_color="yellow")
            else:
                self.remaining_timebar.configure(progress_color="green")
            self.after(1000, self._update_timebar)
        else:
            self.destroy()

    def _create_password_name(self, password: str) -> None:
        dialog = CTkToplevel(self)
        dialog.title("Configure password")
        dialog.wait_visibility()
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self)
        self.lift()

        entry = CTkEntry(
            dialog,
            width=300,
            height=40,
            placeholder_text="Name",
            font=("Helvetica", 18, "bold"))
        entry.grid(row=0, column=0, padx=50, pady=(20, 10))

        result = {"name": None}

        def _empty_name_notification():
            entry.configure(
                border_color="#ff4d4d",
                border_width=2,
            )
            entry.focus_set()

        def on_ok():
            result["name"] = entry.get()

            if result["name"] is None or result["name"] == "":
                _empty_name_notification()
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
            user_input = result["name"]
            if user_input is None or user_input == "":
                raise ValueError("Name cannot be empty")

            self.stored_passwords.add_password(user_input, password)
        except Exception as e:
            raise ValueError(f"{e}")
        
   
class DeletePasswordDialog(CTkToplevel):
    def __init__(self, stored_passwords, password_id, on_update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if password_id is None or password_id == "":
            self.destroy()
            raise ValueError("Password ID cannot be None")
        
        self.title("Delete password")
        self.wait_visibility()
        self.geometry("350x150")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grab_set()
        self.lift()

        self.stored_passwords = stored_passwords
        self.password_id = password_id
        self.on_update_callback = on_update_callback

        self.label = CTkLabel(
            self, 
            text=f"Confirm deletion",
            font=("Helvetica", 20, "bold"))
        self.label.grid(row=0, column=0, padx=0, pady=(20,10), columnspan=2)
        
        self.cancel_button = CTkButton(
            self,
            width=100,
            height=30,
            text="Cancel",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self.destroy) 
        self.cancel_button.grid(row=1, column=0, padx=(50, 0), pady=(20,10), sticky="w")
        
        self.delete_password_button = CTkButton(
            self,
            width=100,
            height=30,
            text="Delete",
            font=("Helvetica", 16, "bold"),
            fg_color="#606363",
            hover_color="#111111",
            command=self._delete_password_callback) 
        self.delete_password_button.grid(row=1, column=0, padx=(0, 50), pady=(20,10), sticky="e")

    def _delete_password_callback(self) -> None:
        if self.password_id is None or self.password_id == "":
            raise ValueError("Password cannot be empty")

        self.stored_passwords.delete_password(self.password_id)
        
        if self.on_update_callback:
            self.on_update_callback()
        
        self.destroy()