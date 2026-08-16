from customtkinter import CTkScrollableFrame, CTkCheckBox, CTkToplevel, CTkProgressBar, CTkLabel, CTkButton
from Backend.generator import PasswordGenerator
from Utilities.time import TimeObject

class ItemsFrame(CTkScrollableFrame):
    def __init__(self, master: object, title: str, values: list):
        super().__init__(master, label_text=title)
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
                checkbox.configure(text=value.id)
                checkbox.configure(state="normal")
                checkbox.deselect()
            else:
                checkbox = CTkCheckBox(
                    self,
                    text=value.id,
                    text_color="white",
                    text_color_disabled="gray",
                    command=self._verifyState)
                self.checkboxes.append(checkbox)

            checkbox.database_id = value.id
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")

        self._verifyState()

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
        self.geometry("500x200")
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
        new_password = self.label.cget("text")
        self.stored_passwords.add_password("test", new_password)
        if self.on_update_callback:
            self.on_update_callback()
        self.destroy()
        
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
   
class DeletePasswordDialog(CTkToplevel):
    def __init__(self, stored_passwords, password_id, on_update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if password_id is None or password_id is "":
            self.destroy()
            raise ValueError("Password ID cannot be None")
        
        self.title("Delete password")
        self.wait_visibility()
        self.geometry("400x150")
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
        self.stored_passwords.delete_password(self.password_id)
        
        if self.on_update_callback:
            self.on_update_callback()
        
        self.destroy()