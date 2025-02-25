from license_activation import LicenseActivation
import tkinter as tk
from tkinter import messagebox

class MainApp:
    def __init__(self):
        self.license_activation = LicenseActivation()
        
        # Verifica licença ao iniciar
        if not self.check_license():
            self.show_activation_dialog()
        else:
            self.start_main_program()
    
    def check_license(self):
        return self.license_activation.check_license()
    
    def show_activation_dialog(self):
        """Mostra diálogo para ativar licença"""
        dialog = tk.Tk()
        dialog.title("Ativação de Licença")
        
        tk.Label(dialog, text="Digite sua chave de licença:").pack(pady=10)
        
        license_entry = tk.Entry(dialog, width=40)
        license_entry.pack(pady=5)
        
        def try_activate():
            license_key = license_entry.get()
            success, message = self.license_activation.activate(license_key)
            
            if success:
                messagebox.showinfo("Sucesso", message)
                dialog.destroy()
                self.start_main_program()
            else:
                messagebox.showerror("Erro", message)
        
        tk.Button(dialog, text="Ativar", command=try_activate).pack(pady=10)
        dialog.mainloop()
    
    def start_main_program(self):
        """Inicia o programa principal após validação da licença"""
        # Seu código principal aqui
        pass

if __name__ == "__main__":
    app = MainApp() 