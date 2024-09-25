import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class Cidades:
    def __init__(self):
        self.conn = sqlite3.connect('sistema.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def listar_cidades(self):
        self.cursor.execute('SELECT id, nome FROM cidades')
        return self.cursor.fetchall()

class Professores:
    def __init__(self):
        self.conn = sqlite3.connect('sistema.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS professores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                cidade_id INTEGER,
                FOREIGN KEY (cidade_id) REFERENCES cidades (id)
            )
        ''')
        self.conn.commit()

    def inserir_professor(self, nome, email, cidade_id):
        self.cursor.execute('''
            INSERT INTO professores (nome, email, cidade_id)
            VALUES (?, ?, ?)
        ''', (nome, email, cidade_id))
        self.conn.commit()

    def atualizar_professor(self, id_professor, nome, email, cidade_id):
        self.cursor.execute('''
            UPDATE professores SET nome = ?, email = ?, cidade_id = ?
            WHERE id = ?
        ''', (nome, email, cidade_id, id_professor))
        self.conn.commit()

    def excluir_professor(self, id_professor):
        self.cursor.execute('''
            DELETE FROM professores WHERE id = ?
        ''', (id_professor,))
        self.conn.commit()

    def listar_professores(self):
        self.cursor.execute('''
            SELECT p.id, p.nome, p.email, c.nome AS cidade
            FROM professores p
            LEFT JOIN cidades c ON p.cidade_id = c.id
        ''')
        return self.cursor.fetchall()

class TelaCadastroProfessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Professores")
        self.root.geometry("600x400")

        self.professores = Professores()
        self.cidades = Cidades()

        # Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.menu_principal = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Opções", menu=self.menu_principal)
        self.menu_principal.add_command(label="Ir para Login", command=self.ir_para_login)
        self.menu_principal.add_command(label="Sair da Página", command=self.sair)

        self.id_professor_selecionado = None

        self.lbl_nome = tk.Label(root, text="Nome:")
        self.lbl_nome.pack(pady=5)
        self.ent_nome = tk.Entry(root)
        self.ent_nome.pack(pady=5)

        self.lbl_email = tk.Label(root, text="Email:")
        self.lbl_email.pack(pady=5)
        self.ent_email = tk.Entry(root)
        self.ent_email.pack(pady=5)

        self.lbl_cidade = tk.Label(root, text="Cidade:")
        self.lbl_cidade.pack(pady=5)

        self.combo_cidades = ttk.Combobox(root, state="readonly")
        self.combo_cidades.pack(pady=5)
        self.carregar_cidades()

        self.btn_cadastrar = tk.Button(root, text="Cadastrar", command=self.cadastrar_professor)
        self.btn_cadastrar.pack(pady=10)

        self.btn_atualizar = tk.Button(root, text="Atualizar", command=self.atualizar_professor)
        self.btn_atualizar.pack(pady=5)

        self.btn_excluir = tk.Button(root, text="Excluir", command=self.excluir_professor)
        self.btn_excluir.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Nome", "Email", "Cidade"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Cidade", text="Cidade")
        self.tree.pack(pady=20, fill=tk.BOTH, expand=True)

        self.carregar_professores()

        self.tree.bind("<ButtonRelease-1>", self.selecionar_professor)

    def carregar_cidades(self):
        cidades = self.cidades.listar_cidades()
        lista_cidades = [f"{cidade[1]}" for cidade in cidades]
        self.combo_cidades['values'] = lista_cidades

    def carregar_professores(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in self.professores.listar_professores():
            self.tree.insert('', 'end', values=row)

    def cadastrar_professor(self):
        nome = self.ent_nome.get()
        email = self.ent_email.get()
        cidade = self.combo_cidades.get()

        if nome and email and cidade:
            cidade_id = self.obter_cidade_id(cidade)
            self.professores.inserir_professor(nome, email, cidade_id)
            messagebox.showinfo("Sucesso", "Professor cadastrado com sucesso!")
            self.limpar_campos()
            self.carregar_professores()
        else:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")

    def atualizar_professor(self):
        if self.id_professor_selecionado is None:
            messagebox.showwarning("Erro", "Selecione um professor para atualizar!")
            return

        nome = self.ent_nome.get()
        email = self.ent_email.get()
        cidade = self.combo_cidades.get()

        if nome and email and cidade:
            cidade_id = self.obter_cidade_id(cidade)
            self.professores.atualizar_professor(self.id_professor_selecionado, nome, email, cidade_id)
            messagebox.showinfo("Sucesso", "Professor atualizado com sucesso!")
            self.limpar_campos()
            self.carregar_professores()
        else:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")

    def excluir_professor(self):
        if self.id_professor_selecionado is None:
            messagebox.showwarning("Erro", "Selecione um professor para excluir!")
            return

        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este professor?")
        if resposta:
            self.professores.excluir_professor(self.id_professor_selecionado)
            messagebox.showinfo("Sucesso", "Professor excluído com sucesso!")
            self.limpar_campos()
            self.carregar_professores()

    def selecionar_professor(self, event):
        item_selecionado = self.tree.focus()
        if item_selecionado:
            valores = self.tree.item(item_selecionado, 'values')
            self.id_professor_selecionado = valores[0]
            self.ent_nome.delete(0, tk.END)
            self.ent_nome.insert(0, valores[1])
            self.ent_email.delete(0, tk.END)
            self.ent_email.insert(0, valores[2])
            self.combo_cidades.set(valores[3])

    def limpar_campos(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.combo_cidades.set('')
        self.id_professor_selecionado = None

    def obter_cidade_id(self, nome_cidade):
        cidades = self.cidades.listar_cidades()
        for cidade in cidades:
            if cidade[1] == nome_cidade:
                return cidade[0]
        return None

    def ir_para_login(self):
        self.root.destroy()
        criar_tela_login()

    def sair(self):
        resposta = messagebox.askyesno("Confirmação", "Deseja realmente sair?")
        if resposta:
            self.root.quit()

def criar_tela_login():
    login_root = tk.Tk()
    TelaCadastroProfessor(login_root)
    login_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    TelaCadastroProfessor(root)
    root.mainloop()
