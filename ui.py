import tkinter as tk
from tkinter import ttk, messagebox
import mng
import pyperclip
from tkinter import font
import os

class UI:
    def __init__(self):
        self.appdata_path = os.path.join(os.getenv('LOCALAPPDATA'), 'PwdMng')
        if not os.path.exists(self.appdata_path):
            os.makedirs(self.appdata_path)
        self.link = os.path.join(self.appdata_path, "mng.pwd")
        self.mng = None
        self.pwdLst = None
        self.unlockPwd = False
        self.root = tk.Tk()
        self.root.title("PwdMng")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TFrame", padding=10)
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ttk.Label(self.login_frame, text="PwdMng", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(self.login_frame, text="Enter your privKey :").pack(pady=5)
        self.ePrivKey = ttk.Entry(self.login_frame, width=40)
        self.ePrivKey.pack(pady=10)
        self.ePrivKey.focus()
        self.eSubmit = ttk.Button(self.login_frame, text="Open", command=self.unlock)
        self.eSubmit.pack(pady=10)
        self.ePrivKey.bind("<Return>", lambda event: self.unlock())
        self.root.mainloop()

    def unlock(self):
        try:
            self.mng = mng.initMng(self.ePrivKey.get())
            self.login_frame.destroy()
            self.show()
        except Exception as e:
            self.mng = mng.initMng()
            self.login_frame.destroy()
            self.create_privkey_frame()

    def create_privkey_frame(self):
        self.privkey_frame = ttk.Frame(self.root)
        self.privkey_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ttk.Label(self.privkey_frame, text="Your privKey is :", font=("Arial", 12, "bold")).pack(pady=5)
        key_entry = ttk.Entry(self.privkey_frame, width=60, font=("Courier", 10))
        key_entry.insert(0, self.mng.privKey_hex)
        key_entry.configure(state="readonly")
        key_entry.pack(pady=10)
        ttk.Label(self.privkey_frame, text="Keep it safe !", font=("Arial", 10, "italic"),
                 foreground="red").pack(pady=5)
        button_frame = ttk.Frame(self.privkey_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Copy", 
                  command=lambda: self.copy(self.mng.privKey_hex)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Continue", 
                  command=lambda: (self.privkey_frame.destroy(), self.show())).pack(side=tk.LEFT, padx=5)
        self.unlockPwd = True

    def show(self):
        self.pwdLst = mng.pwdLst()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")
        action_frame = ttk.LabelFrame(self.main_frame, text="Add Pwd")
        action_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(action_frame, text="Domain:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.eDomain = ttk.Entry(action_frame, width=30)
        self.eDomain.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Label(action_frame, text="Username:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.eUser = ttk.Entry(action_frame, width=30)
        self.eUser.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        ttk.Label(action_frame, text="Pwd:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ePwd = ttk.Entry(action_frame, width=30, show="•")
        self.ePwd.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        button_frame = ttk.Frame(action_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Add", command=self.add).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=lambda: [e.delete(0, tk.END) for e in [self.eDomain, self.eUser, self.ePwd]]).pack(side=tk.LEFT, padx=5)
        list_frame = ttk.LabelFrame(self.main_frame, text="Mots de Passe Enregistrés")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("domaine", "utilisateur", "motdepasse")
        self.passwordTree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.passwordTree.heading("domaine", text="Domaine")
        self.passwordTree.heading("utilisateur", text="Nom d'utilisateur")
        self.passwordTree.heading("motdepasse", text="Mot de passe")
        self.passwordTree.column("domaine", width=150)
        self.passwordTree.column("utilisateur", width=150)
        self.passwordTree.column("motdepasse", width=150)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.passwordTree.yview)
        self.passwordTree.configure(yscroll=scrollbar.set)
        self.passwordTree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.context_menu = tk.Menu(self.passwordTree, tearoff=0)
        self.context_menu.add_command(label="Copy name", command=lambda: self.copy_from_tree("utilisateur"))
        self.context_menu.add_command(label="Copy pwd", command=lambda: self.copy_from_tree("motdepasse"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_password)
        self.passwordTree.bind("<Button-3>", self.show_context_menu)
        self.load_passwords()

    def show_context_menu(self, event):
        item = self.passwordTree.identify_row(event.y)
        if item:
            self.passwordTree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_from_tree(self, column):
        selected = self.passwordTree.selection()
        if selected:
            item_values = self.passwordTree.item(selected[0], "values")
            col_idx = {"domaine": 0, "utilisateur": 1, "motdepasse": 2}
            self.copy(item_values[col_idx[column]])

    def delete_password(self):
        selected = self.passwordTree.selection()
        if selected:
            item_id = selected[0]
            all_items = self.passwordTree.get_children()
            try:
                record_index = all_items.index(item_id)
            except ValueError:
                print(f"Item ID {item_id} not found in tree.")
                return

            offset = record_index * 3
            lines_to_remove = [offset, offset + 1, offset + 2]

            with open(self.link, 'r') as file:
                lines = file.readlines()

            with open(self.link, 'w') as f:
                for idx, line in enumerate(lines):
                    if idx not in lines_to_remove:
                        f.write(line)
                        
        self.mng = mng.initMng(self.mng.privKey_hex)
        self.load_passwords()

    def load_passwords(self):
        self.passwordTree.delete(*self.passwordTree.get_children())
        data = self.mng.getPwdDecrypt()
        for entry in data:
            self.passwordTree.insert("", tk.END, values=entry)

    def add(self):
        domaine = self.eDomain.get().strip()
        utilisateur = self.eUser.get().strip()
        motdepasse = self.ePwd.get().strip()
        if not (domaine and utilisateur and motdepasse):
            messagebox.showerror("Error", "Please fill all fields.")
            return
        
        self.pwdLst = mng.pwdLst()

        self.pwdLst.add(domaine, utilisateur, motdepasse)
        self.mng.cryptPwd(self.pwdLst.getPwd())
        self.load_passwords()
        for e in [self.eDomain, self.eUser, self.ePwd]:
            e.delete(0, tk.END)

    def copy(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "The text has been copied to the clipboard.")