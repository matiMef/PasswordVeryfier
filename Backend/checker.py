from math import pow
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

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
        return True if any(char in ascii_lowercase for char in self.password) else False
        
    def is_any_upper(self) -> bool:
        return True if any(char in ascii_uppercase for char in self.password) else False
        
    def is_any_digit(self) -> bool:
        return True if any(char in digits for char in self.password) else False
        
    def is_any_special(self) -> bool:
        return True if any(char in punctuation for char in self.password) else False
    
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

    # To do
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