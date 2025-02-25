import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

class AdminPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DarkTikTok - Painel Admin")
        self.root.geometry("800x600")
        
        # URL do servidor
        self.api_url = "https://tktkcreate.onrender.com/api"
        self.admin_key = "DARKTK-MASTER-2024"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame para criar licença
        create_frame = ttk.LabelFrame(self.root, text="Criar Nova Licença", padding=10)
        create_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(create_frame, text="Email:").grid(row=0, column=0, sticky="w")
        self.email_entry = ttk.Entry(create_frame, width=40)
        self.email_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(create_frame, text="Tipo:").grid(row=1, column=0, sticky="w")
        self.type_combo = ttk.Combobox(create_frame, values=["standard", "professional"])
        self.type_combo.set("professional")
        self.type_combo.grid(row=1, column=1, padx=5)
        
        ttk.Label(create_frame, text="Duração (dias):").grid(row=2, column=0, sticky="w")
        self.duration_entry = ttk.Entry(create_frame, width=10)
        self.duration_entry.insert(0, "30")
        self.duration_entry.grid(row=2, column=1, sticky="w", padx=5)
        
        create_btn = ttk.Button(create_frame, text="Criar Licença", command=self.create_license)
        create_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame para listar licenças
        list_frame = ttk.LabelFrame(self.root, text="Licenças Ativas", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para listar licenças
        self.tree = ttk.Treeview(list_frame, columns=("email", "key", "type", "expires", "status"))
        self.tree.heading("email", text="Email")
        self.tree.heading("key", text="Chave")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("expires", text="Expira em")
        self.tree.heading("status", text="Status")
        self.tree.pack(fill="both", expand=True)
        
        # Botões de ação
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(action_frame, text="Atualizar Lista", command=self.refresh_licenses).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Revogar Licença", command=self.revoke_license).pack(side="left", padx=5)
        
    def create_license(self):
        try:
            data = {
                "admin_key": self.admin_key,
                "email": self.email_entry.get(),
                "type": self.type_combo.get(),
                "duration": int(self.duration_entry.get()),
                "purchase_id": f"ADMIN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            response = requests.post(f"{self.api_url}/create_license", json=data)
            
            if response.status_code == 200:
                result = response.json()
                messagebox.showinfo("Sucesso", 
                    f"Licença criada!\nChave: {result['license_key']}\n"
                    f"Expira em: {result['expires_at']}")
                self.refresh_licenses()
            else:
                messagebox.showerror("Erro", f"Erro ao criar licença: {response.text}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def refresh_licenses(self):
        try:
            # Limpar lista atual
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Buscar licenças do servidor
            response = requests.get(
                f"{self.api_url}/list_licenses",
                params={"admin_key": self.admin_key}
            )
            
            if response.status_code == 200:
                licenses = response.json()
                for license in licenses:
                    self.tree.insert("", "end", values=(
                        license["email"],
                        license["key"],
                        license["type"],
                        license["expires_at"],
                        license["status"]
                    ))
            else:
                messagebox.showerror("Erro", f"Erro ao buscar licenças: {response.text}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def revoke_license(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma licença para revogar")
            return
            
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja revogar esta licença?"):
            try:
                license_key = self.tree.item(selected[0])["values"][1]
                response = requests.post(
                    f"{self.api_url}/revoke_license",
                    json={
                        "admin_key": self.admin_key,
                        "key": license_key
                    }
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Licença revogada com sucesso!")
                    self.refresh_licenses()
                else:
                    messagebox.showerror("Erro", f"Erro ao revogar licença: {response.text}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def run(self):
        self.refresh_licenses()
        self.root.mainloop()

if __name__ == "__main__":
    panel = AdminPanel()
    panel.run() 