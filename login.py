import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class Usuarios:
    def __init__(self):
        self.conn = sqlite3.connect('sistema.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def inserir_usuario(self, nome, email, senha):
        self.cursor.execute('''
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        ''', (nome, email, senha))
        self.conn.commit()

    def atualizar_usuario(self, id_usuario, nome, email, senha):
        self.cursor.execute('''
            UPDATE usuarios 
            SET nome = ?, email = ?, senha = ?
            WHERE id = ?
        ''', (nome, email, senha, id_usuario))
        self.conn.commit()

    def excluir_usuario(self, id_usuario):
        self.cursor.execute('''
            DELETE FROM usuarios WHERE id = ?
        ''', (id_usuario,))
        self.conn.commit()

    def listar_usuarios(self):
        self.cursor.execute('SELECT * FROM usuarios')
        return self.cursor.fetchall()

    def fechar_conexao(self):
        self.conn.close()


class TelaCadastroUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Usuário")
        self.root.geometry("500x400")
        self.usuarios = Usuarios()

        self.id_usuario_selecionado = None

        # Widgets
        self.lbl_nome = tk.Label(root, text="Nome:")
        self.lbl_nome.pack(pady=5)
        self.ent_nome = tk.Entry(root)
        self.ent_nome.pack(pady=5)

        self.lbl_email = tk.Label(root, text="Email:")
        self.lbl_email.pack(pady=5)
        self.ent_email = tk.Entry(root)
        self.ent_email.pack(pady=5)

        self.lbl_senha = tk.Label(root, text="Senha:")
        self.lbl_senha.pack(pady=5)
        self.ent_senha = tk.Entry(root, show='*')
        self.ent_senha.pack(pady=5)

        self.btn_cadastrar = tk.Button(root, text="Cadastrar", command=self.cadastrar_usuario)
        self.btn_cadastrar.pack(pady=10)

        self.btn_atualizar = tk.Button(root, text="Atualizar", command=self.atualizar_usuario)
        self.btn_atualizar.pack(pady=5)

        self.btn_excluir = tk.Button(root, text="Excluir", command=self.excluir_usuario)
        self.btn_excluir.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Nome", "Email"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.pack(pady=20)

        self.carregar_usuarios()

        self.tree.bind("<ButtonRelease-1>", self.selecionar_usuario)

    def carregar_usuarios(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in self.usuarios.listar_usuarios():
            self.tree.insert('', 'end', values=row)

    def cadastrar_usuario(self):
        nome = self.ent_nome.get()
        email = self.ent_email.get()
        senha = self.ent_senha.get()

        if nome and email and senha:
            self.usuarios.inserir_usuario(nome, email, senha)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.limpar_campos()
            self.carregar_usuarios()
        else:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")

    def atualizar_usuario(self):
        if self.id_usuario_selecionado is None:
            messagebox.showwarning("Erro", "Selecione um usuário para atualizar!")
            return

        nome = self.ent_nome.get()
        email = self.ent_email.get()
        senha = self.ent_senha.get()

        if nome and email and senha:
            self.usuarios.atualizar_usuario(self.id_usuario_selecionado, nome, email, senha)
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            self.limpar_campos()
            self.carregar_usuarios()
        else:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")

    def excluir_usuario(self):
        if self.id_usuario_selecionado is None:
            messagebox.showwarning("Erro", "Selecione um usuário para excluir!")
            return

        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este usuário?")
        if resposta:
            self.usuarios.excluir_usuario(self.id_usuario_selecionado)
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
            self.limpar_campos()
            self.carregar_usuarios()

    def selecionar_usuario(self, event):
        item_selecionado = self.tree.focus()
        if item_selecionado:
            valores = self.tree.item(item_selecionado, 'values')
            self.id_usuario_selecionado = valores[0]
            self.ent_nome.delete(0, tk.END)
            self.ent_nome.insert(0, valores[1])
            self.ent_email.delete(0, tk.END)
            self.ent_email.insert(0, valores[2])
            self.ent_senha.delete(0, tk.END)

    def limpar_campos(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_senha.delete(0, tk.END)
        self.id_usuario_selecionado = None


if __name__ == "__main__":
    root = tk.Tk()
    app = TelaCadastroUsuario(root)
    root.mainloop()
