import tkinter as tk
from tkinter import ttk, messagebox

class SplitwiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Divisão do Churrasco 🥩")
        self.root.geometry("600x500")

        self.participantes = []
        self.despesas = []

        self.frame_principal = ttk.Frame(self.root, padding=10)
        self.frame_principal.pack(fill="both", expand=True)

        self.montar_tela_participantes()

    def montar_tela_participantes(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Adicione os participantes:", font=("Arial", 12, "bold")).pack(pady=5)

        self.entry_nome = ttk.Entry(self.frame_principal, width=30)
        self.entry_nome.pack(pady=5)
        ttk.Button(self.frame_principal, text="Adicionar participante", command=self.adicionar_participante).pack(pady=5)

        self.lista_participantes = tk.Listbox(self.frame_principal, height=8)
        self.lista_participantes.pack(fill="x", pady=5)

        ttk.Button(self.frame_principal, text="Próximo ➡️", command=self.montar_tela_despesas).pack(pady=10)

    def adicionar_participante(self):
        nome = self.entry_nome.get().strip()
        if nome and nome not in self.participantes:
            self.participantes.append(nome)
            self.lista_participantes.insert(tk.END, nome)
            self.entry_nome.delete(0, tk.END)
        else:
            messagebox.showwarning("Atenção", "Nome vazio ou duplicado.")

    def montar_tela_despesas(self):
        if not self.participantes:
            messagebox.showerror("Erro", "Adicione pelo menos um participante.")
            return

        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Registrar despesas:", font=("Arial", 12, "bold")).pack(pady=5)

        self.pagador_var = tk.StringVar()
        ttk.Label(self.frame_principal, text="Quem pagou:").pack()
        self.pagador_menu = ttk.Combobox(self.frame_principal, textvariable=self.pagador_var, values=self.participantes, state="readonly")
        self.pagador_menu.pack(pady=5)

        ttk.Label(self.frame_principal, text="Valor pago (R$):").pack()
        self.valor_entry = ttk.Entry(self.frame_principal, width=20)
        self.valor_entry.pack(pady=5)

        ttk.Label(self.frame_principal, text="Quem participou dessa despesa:").pack()
        self.participantes_vars = {}
        for nome in self.participantes:
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.frame_principal, text=nome, variable=var)
            chk.pack(anchor="w")
            self.participantes_vars[nome] = var

        ttk.Button(self.frame_principal, text="Adicionar despesa", command=self.adicionar_despesa).pack(pady=5)
        ttk.Button(self.frame_principal, text="Ver resultado final 💰", command=self.calcular_resultado).pack(pady=5)

        ttk.Label(self.frame_principal, text="Duplo clique para editar uma despesa").pack()
        self.lista_despesas = tk.Listbox(self.frame_principal, height=8)
        self.lista_despesas.pack(fill="x", pady=5)
        self.lista_despesas.bind("<Double-Button-1>", self.editar_despesa)

    def adicionar_despesa(self):
        pagador = self.pagador_var.get()
        valor = self.valor_entry.get()
        try:
            valor = float(valor)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")
            return

        participantes_despesa = [p for p, v in self.participantes_vars.items() if v.get()]
        if not participantes_despesa:
            messagebox.showwarning("Aviso", "Selecione ao menos um participante.")
            return

        self.despesas.append({"pagador": pagador, "valor": valor, "participantes": participantes_despesa})
        self.atualizar_lista_despesas()

        self.valor_entry.delete(0, tk.END)
        for var in self.participantes_vars.values():
            var.set(False)

    def atualizar_lista_despesas(self):
        self.lista_despesas.delete(0, tk.END)
        for i, d in enumerate(self.despesas):
            texto = f"{i+1}. {d['pagador']} pagou R${d['valor']:.2f} por {', '.join(d['participantes'])}"
            self.lista_despesas.insert(tk.END, texto)

    def editar_despesa(self, event):
        selecao = self.lista_despesas.curselection()
        if not selecao:
            return
        index = selecao[0]
        despesa = self.despesas[index]

        janela_editar = tk.Toplevel(self.root)
        janela_editar.title("Editar Despesa ✏️")
        janela_editar.geometry("400x400")

        ttk.Label(janela_editar, text=f"Editar despesa {index+1}", font=("Arial", 12, "bold")).pack(pady=10)

        ttk.Label(janela_editar, text="Quem pagou:").pack()
        pagador_var = tk.StringVar(value=despesa["pagador"])
        pagador_menu = ttk.Combobox(janela_editar, textvariable=pagador_var, values=self.participantes, state="readonly")
        pagador_menu.pack(pady=5)

        ttk.Label(janela_editar, text="Valor pago (R$):").pack()
        valor_entry = ttk.Entry(janela_editar, width=20)
        valor_entry.insert(0, str(despesa["valor"]))
        valor_entry.pack(pady=5)

        ttk.Label(janela_editar, text="Quem participou:").pack()
        participantes_vars_edit = {}
        for nome in self.participantes:
            var = tk.BooleanVar(value=nome in despesa["participantes"])
            chk = ttk.Checkbutton(janela_editar, text=nome, variable=var)
            chk.pack(anchor="w")
            participantes_vars_edit[nome] = var

        def salvar_edicao():
            try:
                valor = float(valor_entry.get())
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")
                return

            novos_participantes = [p for p, v in participantes_vars_edit.items() if v.get()]
            if not novos_participantes:
                messagebox.showwarning("Aviso", "Selecione ao menos um participante.")
                return

            self.despesas[index] = {
                "pagador": pagador_var.get(),
                "valor": valor,
                "participantes": novos_participantes
            }
            self.atualizar_lista_despesas()
            janela_editar.destroy()

        ttk.Button(janela_editar, text="Salvar alterações", command=salvar_edicao).pack(pady=10)
        ttk.Button(janela_editar, text="Cancelar", command=janela_editar.destroy).pack()

    def calcular_resultado(self):
        if not self.despesas:
            messagebox.showinfo("Aviso", "Nenhuma despesa registrada.")
            return

        # Inicializa saldos
        pagos = {p: 0 for p in self.participantes}
        deve_gastar = {p: 0 for p in self.participantes}
        saldos = {p: 0 for p in self.participantes}

        for despesa in self.despesas:
            valor = despesa["valor"]
            pagador = despesa["pagador"]
            envolvidos = despesa["participantes"]
            valor_por_pessoa = valor / len(envolvidos)

            pagos[pagador] += valor
            for pessoa in envolvidos:
                deve_gastar[pessoa] += valor_por_pessoa

        for p in self.participantes:
            saldos[p] = pagos[p] - deve_gastar[p]

        resultado = self.minimizar_transferencias(saldos)
        self.mostrar_resultado(pagos, deve_gastar, saldos, resultado)

    def minimizar_transferencias(self, saldos):
        credores = [(p, v) for p, v in saldos.items() if v > 0]
        devedores = [(p, -v) for p, v in saldos.items() if v < 0]
        resultado = []

        i, j = 0, 0
        while i < len(devedores) and j < len(credores):
            devedor, deve = devedores[i]
            credor, tem = credores[j]
            valor = min(deve, tem)

            resultado.append(f"{devedor} deve pagar R${valor:.2f} para {credor}")

            devedores[i] = (devedor, deve - valor)
            credores[j] = (credor, tem - valor)

            if devedores[i][1] == 0:
                i += 1
            if credores[j][1] == 0:
                j += 1

        return resultado

    def mostrar_resultado(self, pagos, deve_gastar, saldos, resultado):
        janela_resultado = tk.Toplevel(self.root)
        janela_resultado.title("Resultado Final 💵")
        janela_resultado.geometry("500x500")

        ttk.Label(janela_resultado, text="Resumo individual:", font=("Arial", 12, "bold")).pack(pady=10)

        for p in self.participantes:
            texto = f"- {p} pagou R${pagos[p]:.2f}, deveria gastar R${deve_gastar[p]:.2f} → saldo {saldos[p]:+.2f}"
            ttk.Label(janela_resultado, text=texto).pack(anchor="w", padx=20)

        ttk.Separator(janela_resultado, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(janela_resultado, text="Transferências necessárias:", font=("Arial", 12, "bold")).pack(pady=5)
        for r in resultado:
            ttk.Label(janela_resultado, text=r).pack(anchor="w", padx=20)

        ttk.Button(janela_resultado, text="Fechar", command=janela_resultado.destroy).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = SplitwiseApp(root)
    root.mainloop()
