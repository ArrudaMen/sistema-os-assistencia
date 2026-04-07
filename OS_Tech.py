import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
from datetime import datetime
import webbrowser
import urllib.parse
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- BANCO DE DADOS ---
def conectar_banco():
    conexao = sqlite3.connect('banco_os.db')
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            whatsapp TEXT,
            equipamento TEXT,
            acessorios TEXT,
            avarias TEXT,
            problema TEXT,
            status TEXT,
            valor_pecas REAL,
            valor_mao_obra REAL,
            data_entrada TEXT
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN servico_imediato TEXT")
    except sqlite3.OperationalError:
        pass 
        
    try:
        cursor.execute("ALTER TABLE ordens_servico ADD COLUMN data_entrega TEXT")
    except sqlite3.OperationalError:
        pass

    conexao.commit()
    return conexao

# --- FUNCOES DA OS ---
def salvar_os():
    cliente = entry_cliente.get().strip()
    whatsapp = entry_whatsapp.get().strip()
    equipamento = entry_equipamento.get().strip()
    acessorios = entry_acessorios.get().strip()
    avarias = entry_avarias.get().strip()
    problema = textbox_problema.get("1.0", "end-1c").strip()
    servico = textbox_servico.get("1.0", "end-1c").strip()

    if not cliente or not equipamento or not problema:
        messagebox.showwarning("Aviso", "Preencha pelo menos o Nome, Equipamento e o Problema!", parent=janela)
        return

    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    status_inicial = "Na Fila"

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO ordens_servico 
        (cliente, whatsapp, equipamento, acessorios, avarias, problema, status, valor_pecas, valor_mao_obra, data_entrada, servico_imediato)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0.0, 0.0, ?, ?)
    ''', (cliente, whatsapp, equipamento, acessorios, avarias, problema, status_inicial, data_hoje, servico))
    
    conexao.commit()
    os_id = cursor.lastrowid
    conexao.close()

    messagebox.showinfo("Sucesso", f"Ordem de Serviço #{os_id} gerada com sucesso!", parent=janela)
    
    entry_cliente.delete(0, 'end')
    entry_whatsapp.delete(0, 'end')
    entry_equipamento.delete(0, 'end')
    entry_acessorios.delete(0, 'end')
    entry_avarias.delete(0, 'end')
    textbox_problema.delete("1.0", 'end')
    textbox_servico.delete("1.0", 'end')

# --- TELA DE DETALHES ---
def ver_detalhes_os(id_os, janela_pai, tela_origem):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, cliente, whatsapp, equipamento, acessorios, avarias, problema, status, valor_pecas, valor_mao_obra, data_entrada, servico_imediato, data_entrega FROM ordens_servico WHERE id = ?", (id_os,))
    os_dados = cursor.fetchone()
    conexao.close()

    if not os_dados:
        return

    id_os, cliente, whatsapp, equipamento, acessorios, avarias, problema, status, valor_pecas, valor_mao_obra, data, servico_imediato, data_entrega = os_dados

    janela_detalhes = ctk.CTkToplevel(janela_pai)
    janela_detalhes.title(f"Detalhes da OS #{id_os}")
    janela_detalhes.geometry("650x700")
    
    # A Mágica do Foco
    janela_detalhes.grab_set()
    janela_detalhes.focus_force()

    ctk.CTkLabel(janela_detalhes, text=f"OS #{id_os} - {equipamento}", font=("Arial", 20, "bold")).pack(pady=10)

    frame_info = ctk.CTkFrame(janela_detalhes)
    frame_info.pack(pady=10, padx=20, fill="x")

    info_texto = f"👤 Cliente: {cliente} | 📱 WhatsApp: {whatsapp}\n"
    info_texto += f"📅 Entrada: {data}\n\n"
    info_texto += f"🔌 Acessórios: {acessorios if acessorios else 'Nenhum'}\n"
    info_texto += f"⚠️ Avarias: {avarias if avarias else 'Nenhuma'}\n\n"
    info_texto += f"📋 Problema (Cliente):\n{problema}\n\n"
    
    texto_servico = servico_imediato if servico_imediato else 'Não especificado'
    info_texto += f"🛠️ Serviço a ser feito (Técnico):\n{texto_servico}"

    label_info = ctk.CTkLabel(frame_info, text=info_texto, font=("Arial", 14), justify="left")
    label_info.pack(pady=10, padx=10, anchor="w")

    frame_edicao = ctk.CTkFrame(janela_detalhes, fg_color="transparent")
    frame_edicao.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(frame_edicao, text="Status Atual:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=5)
    
    opcoes_status = ["Na Fila", "Em Análise", "Aguardando Confirmação", "Tratando", "Aguardando Peça", "Pronto", "Entregue"]
    combo_status = ctk.CTkOptionMenu(frame_edicao, values=opcoes_status)
    combo_status.set(status)
    combo_status.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_edicao, text="Valor Peças (R$):", font=("Arial", 14, "bold")).grid(row=1, column=0, sticky="w", pady=5)
    entry_pecas = ctk.CTkEntry(frame_edicao, width=150)
    entry_pecas.insert(0, str(valor_pecas))
    entry_pecas.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_edicao, text="Valor Mão de Obra (R$):", font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w", pady=5)
    entry_mao_obra = ctk.CTkEntry(frame_edicao, width=150)
    entry_mao_obra.insert(0, str(valor_mao_obra))
    entry_mao_obra.grid(row=2, column=1, padx=10, pady=5)

    def atualizar_os():
        novo_status = combo_status.get()
        novo_v_pecas = entry_pecas.get().replace(',', '.')
        novo_v_mao_obra = entry_mao_obra.get().replace(',', '.')

        try:
            v_pecas_float = float(novo_v_pecas)
            v_mao_obra_float = float(novo_v_mao_obra)
        except ValueError:
            messagebox.showerror("Erro", "Digite apenas números nos valores!", parent=janela_detalhes)
            return

        conexao = conectar_banco()
        cursor = conexao.cursor()
        
        if novo_status == "Entregue" and status != "Entregue":
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            cursor.execute('''
                UPDATE ordens_servico 
                SET status = ?, valor_pecas = ?, valor_mao_obra = ?, data_entrega = ? 
                WHERE id = ?
            ''', (novo_status, v_pecas_float, v_mao_obra_float, data_hoje, id_os))
        else:
            cursor.execute('''
                UPDATE ordens_servico 
                SET status = ?, valor_pecas = ?, valor_mao_obra = ? 
                WHERE id = ?
            ''', (novo_status, v_pecas_float, v_mao_obra_float, id_os))
            
        conexao.commit()
        conexao.close()

        janela_detalhes.destroy()
        janela_pai.destroy()
        
        if tela_origem == "bancada":
            abrir_bancada()
        else:
            abrir_historico()

    def excluir_os():
        resposta = messagebox.askyesno("⚠️ ATENÇÃO", f"Tem certeza absoluta que deseja APAGAR a OS #{id_os}?\nIsso não pode ser desfeito.", parent=janela_detalhes)
        if resposta:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM ordens_servico WHERE id = ?", (id_os,))
            conexao.commit()
            conexao.close()
            
            janela_detalhes.destroy()
            janela_pai.destroy()
            if tela_origem == "bancada":
                abrir_bancada()
            else:
                abrir_historico()

    def avisar_whatsapp():
        numero = whatsapp.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        status_selecionado = combo_status.get()
        
        try:
            v_pecas = float(entry_pecas.get().replace(',', '.'))
            v_mao = float(entry_mao_obra.get().replace(',', '.'))
        except:
            v_pecas = 0.0
            v_mao = 0.0
            
        total = v_pecas + v_mao

        if status_selecionado == "Aguardando Confirmação":
            msg = f"Olá, {cliente}! Analisamos seu equipamento ({equipamento}).\n\n"
            msg += f"*Orçamento do Serviço:*\n"
            msg += f"Mão de obra: R$ {v_mao:.2f}\n"
            if v_pecas > 0:
                msg += f"Peças: R$ {v_pecas:.2f}\n"
            msg += f"*Total: R$ {total:.2f}*\n\n"
            msg += f"Podemos dar andamento no serviço?"
        elif status_selecionado == "Pronto":
            msg = f"Olá, {cliente}! Ótima notícia: seu equipamento ({equipamento}) está PRONTO e liberado para retirada!\n\n"
            msg += f"O valor total do serviço ficou em *R$ {total:.2f}*."
        else:
            msg = f"Olá, {cliente}! Passando para atualizar sobre o seu equipamento ({equipamento}). O status atual é: {status_selecionado}."
        
        msg_codificada = urllib.parse.quote(msg)
        link = f"https://wa.me/55{numero}?text={msg_codificada}"
        webbrowser.open(link)

    frame_botoes = ctk.CTkFrame(janela_detalhes, fg_color="transparent")
    frame_botoes.pack(pady=20)

    btn_salvar_edicao = ctk.CTkButton(frame_botoes, text="💾 SALVAR", fg_color="#ffc107", hover_color="#e0a800", text_color="black", height=40, font=("Arial", 14, "bold"), command=atualizar_os)
    btn_salvar_edicao.pack(side="left", padx=10)

    if whatsapp:
        btn_wpp = ctk.CTkButton(frame_botoes, text="📲 WHATSAPP", fg_color="#25D366", hover_color="#128C7E", height=40, font=("Arial", 14, "bold"), command=avisar_whatsapp)
        btn_wpp.pack(side="left", padx=10)

    btn_excluir = ctk.CTkButton(frame_botoes, text="🗑️ EXCLUIR", fg_color="#dc3545", hover_color="#c82333", height=40, font=("Arial", 14, "bold"), command=excluir_os)
    btn_excluir.pack(side="left", padx=10)


# --- TELA DA BANCADA ---
def abrir_bancada():
    janela_bancada = ctk.CTkToplevel(janela)
    janela_bancada.title("🛠️ Bancada de Manutenção")
    janela_bancada.geometry("850x500")
    
    # A Mágica do Foco
    janela_bancada.grab_set()
    janela_bancada.focus_force()

    ctk.CTkLabel(janela_bancada, text="📋 EQUIPAMENTOS NA BANCADA", font=("Arial", 20, "bold")).pack(pady=15)

    scroll_bancada = ctk.CTkScrollableFrame(janela_bancada, width=800, height=400)
    scroll_bancada.pack(pady=10, padx=10, fill="both", expand=True)

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, cliente, equipamento, status, data_entrada FROM ordens_servico WHERE status != 'Entregue' ORDER BY id DESC")
    ordens = cursor.fetchall()
    conexao.close()

    if not ordens:
        ctk.CTkLabel(scroll_bancada, text="Nenhum equipamento na bancada. Tudo limpo!", font=("Arial", 16)).pack(pady=30)
        return

    for os in ordens:
        id_os, cliente, equipamento, status, data = os

        frame_os = ctk.CTkFrame(scroll_bancada, fg_color="#333333", corner_radius=8)
        frame_os.pack(pady=5, padx=5, fill="x")

        texto_os = f"OS #{id_os} | 👤 {cliente} | 💻 {equipamento} | 📅 Entrada: {data[:10]}"
        ctk.CTkLabel(frame_os, text=texto_os, font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)

        btn_abrir = ctk.CTkButton(frame_os, text="🔍 ABRIR", width=70, fg_color="#007bff", hover_color="#0056b3", command=lambda i=id_os: ver_detalhes_os(i, janela_bancada, "bancada"))
        btn_abrir.pack(side="right", padx=10, pady=10)

        if status == "Na Fila":
            cor_status = "#ffc107"
        elif status == "Pronto":
            cor_status = "#28a745"
        elif status == "Aguardando Confirmação":
            cor_status = "#ff8c00"
        else:
            cor_status = "#17a2b8"
            
        ctk.CTkLabel(frame_os, text=f"[{status}]", font=("Arial", 14, "bold"), text_color=cor_status).pack(side="right", padx=10, pady=10)

# --- TELA DE HISTORICO E RELATÓRIO ---
def abrir_historico():
    janela_historico = ctk.CTkToplevel(janela)
    janela_historico.title("💰 Histórico e Faturamento")
    janela_historico.geometry("900x650")
    
    # A Mágica do Foco
    janela_historico.grab_set()
    janela_historico.focus_force()

    frame_topo = ctk.CTkFrame(janela_historico, fg_color="transparent")
    frame_topo.pack(pady=15, fill="x", padx=20)

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT DISTINCT SUBSTR(data_entrega, 4, 7) FROM ordens_servico WHERE status = 'Entregue' AND data_entrega IS NOT NULL")
    meses_banco = cursor.fetchall()
    conexao.close()
    
    lista_meses = ["Todos os Meses"] + [m[0] for m in meses_banco if m[0]]

    ctk.CTkLabel(frame_topo, text="Filtrar por Mês:", font=("Arial", 14, "bold")).pack(side="left", padx=5)
    combo_mes = ctk.CTkOptionMenu(frame_topo, values=lista_meses, command=lambda m: atualizar_lista_historico(m))
    combo_mes.pack(side="left", padx=5)

    def imprimir_relatorio():
        mes_atual = combo_mes.get()
        
        caminho_arquivo = filedialog.asksaveasfilename(
            parent=janela_historico,
            defaultextension=".txt",
            initialfile=f"Relatorio_OS_{mes_atual.replace('/', '-')}.txt",
            title="Salvar Relatório de Faturamento",
            filetypes=[("Arquivos de Texto", "*.txt")]
        )
        
        if caminho_arquivo:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            if mes_atual == "Todos os Meses":
                cursor.execute("SELECT id, cliente, equipamento, valor_pecas, valor_mao_obra, data_entrega FROM ordens_servico WHERE status = 'Entregue' ORDER BY id DESC")
            else:
                filtro = f"%{mes_atual}"
                cursor.execute("SELECT id, cliente, equipamento, valor_pecas, valor_mao_obra, data_entrega FROM ordens_servico WHERE status = 'Entregue' AND data_entrega LIKE ? ORDER BY id DESC", (filtro,))
            ordens = cursor.fetchall()
            conexao.close()
            
            t_pecas = sum(o[3] for o in ordens)
            t_mao = sum(o[4] for o in ordens)
            t_geral = t_pecas + t_mao
            
            texto = f"=== RELATÓRIO DE FATURAMENTO ({mes_atual}) ===\n\n"
            for o in ordens:
                texto += f"OS #{o[0]} | Cliente: {o[1]} | Equipamento: {o[2]} | Data: {o[5]}\n"
                texto += f"   Peças: R$ {o[3]:.2f} | Mão de Obra: R$ {o[4]:.2f} | Total: R$ {o[3]+o[4]:.2f}\n"
                texto += "-" * 55 + "\n"
                
            texto += f"\nRESUMO FINAL:\n"
            texto += f"Gasto c/ Peças: R$ {t_pecas:.2f}\n"
            texto += f"Lucro Mão de Obra: R$ {t_mao:.2f}\n"
            texto += f"FATURAMENTO TOTAL: R$ {t_geral:.2f}\n"
            
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(texto)
                
            os.startfile(caminho_arquivo)

    btn_imprimir = ctk.CTkButton(frame_topo, text="🖨️ IMPRIMIR RELATÓRIO", fg_color="#007bff", hover_color="#0056b3", font=("Arial", 12, "bold"), command=imprimir_relatorio)
    btn_imprimir.pack(side="right", padx=5)

    scroll_hist = ctk.CTkScrollableFrame(janela_historico, width=800, height=350)
    scroll_hist.pack(pady=10, padx=10, fill="both", expand=True)

    frame_totais = ctk.CTkFrame(janela_historico, fg_color="#1f1f1f")
    frame_totais.pack(pady=10, padx=20, fill="x")

    label_pecas = ctk.CTkLabel(frame_totais, text="Gasto c/ Peças: R$ 0.00", font=("Arial", 16), text_color="#dc3545")
    label_pecas.pack(side="left", padx=20, pady=15)
    
    label_mao = ctk.CTkLabel(frame_totais, text="Lucro Mão de Obra: R$ 0.00", font=("Arial", 16), text_color="#17a2b8")
    label_mao.pack(side="left", padx=20, pady=15)
    
    label_total = ctk.CTkLabel(frame_totais, text="FATURAMENTO TOTAL: R$ 0.00", font=("Arial", 18, "bold"), text_color="#28a745")
    label_total.pack(side="right", padx=20, pady=15)

    def atualizar_lista_historico(mes_selecionado="Todos os Meses"):
        for widget in scroll_hist.winfo_children():
            widget.destroy()

        conexao = conectar_banco()
        cursor = conexao.cursor()
        
        if mes_selecionado == "Todos os Meses":
            cursor.execute("SELECT id, cliente, equipamento, valor_pecas, valor_mao_obra, data_entrega FROM ordens_servico WHERE status = 'Entregue' ORDER BY id DESC")
        else:
            filtro = f"%{mes_selecionado}"
            cursor.execute("SELECT id, cliente, equipamento, valor_pecas, valor_mao_obra, data_entrega FROM ordens_servico WHERE status = 'Entregue' AND data_entrega LIKE ? ORDER BY id DESC", (filtro,))
            
        ordens_entregues = cursor.fetchall()
        conexao.close()

        total_pecas = 0.0
        total_mao_obra = 0.0

        if not ordens_entregues:
            ctk.CTkLabel(scroll_hist, text="Nenhum equipamento entregue neste período.", font=("Arial", 16)).pack(pady=30)
        else:
            for os_item in ordens_entregues:
                id_os, cliente, equipamento, v_pecas, v_mao, data_fim = os_item
                total_os = v_pecas + v_mao
                total_pecas += v_pecas
                total_mao_obra += v_mao
                
                data_exibicao = data_fim if data_fim else "Sem data"
                
                frame_os = ctk.CTkFrame(scroll_hist, fg_color="#2b2b2b", corner_radius=8)
                frame_os.pack(pady=5, padx=5, fill="x")

                texto_os = f"OS #{id_os} | {cliente} | {equipamento} | 📅 Finalizado em: {data_exibicao}"
                ctk.CTkLabel(frame_os, text=texto_os, font=("Arial", 14)).pack(side="left", padx=15, pady=10)
                
                btn_abrir = ctk.CTkButton(frame_os, text="🔍 ABRIR", width=70, fg_color="#007bff", hover_color="#0056b3", command=lambda i=id_os: ver_detalhes_os(i, janela_historico, "historico"))
                btn_abrir.pack(side="right", padx=10, pady=10)

                ctk.CTkLabel(frame_os, text=f"R$ {total_os:.2f}", font=("Arial", 14, "bold"), text_color="#28a745").pack(side="right", padx=15, pady=10)

        faturamento_geral = total_pecas + total_mao_obra
        label_pecas.configure(text=f"Gasto c/ Peças: R$ {total_pecas:.2f}")
        label_mao.configure(text=f"Lucro Mão de Obra: R$ {total_mao_obra:.2f}")
        label_total.configure(text=f"FATURAMENTO TOTAL: R$ {faturamento_geral:.2f}")

    atualizar_lista_historico()

# --- TELA PRINCIPAL ---
janela = ctk.CTk()
janela.title("Sistema de OS - Tech Support")
janela.geometry("550x830")

ctk.CTkLabel(janela, text="🖥️ NOVA ORDEM DE SERVIÇO", font=("Arial", 22, "bold")).pack(pady=20)

frame_form = ctk.CTkFrame(janela, fg_color="transparent")
frame_form.pack(pady=10, padx=20, fill="both", expand=True)

ctk.CTkLabel(frame_form, text="Nome do Cliente:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", pady=8)
entry_cliente = ctk.CTkEntry(frame_form, width=300)
entry_cliente.grid(row=0, column=1, padx=10, pady=8)

ctk.CTkLabel(frame_form, text="WhatsApp:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", pady=8)
entry_whatsapp = ctk.CTkEntry(frame_form, width=300, placeholder_text="Ex: 61999999999")
entry_whatsapp.grid(row=1, column=1, padx=10, pady=8)

ctk.CTkLabel(frame_form, text="Equipamento:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", pady=8)
entry_equipamento = ctk.CTkEntry(frame_form, width=300, placeholder_text="Ex: Desktop Gamer")
entry_equipamento.grid(row=2, column=1, padx=10, pady=8)

ctk.CTkLabel(frame_form, text="Acessórios deixados:", font=("Arial", 14)).grid(row=3, column=0, sticky="w", pady=8)
entry_acessorios = ctk.CTkEntry(frame_form, width=300, placeholder_text="Ex: Cabo de força")
entry_acessorios.grid(row=3, column=1, padx=10, pady=8)

ctk.CTkLabel(frame_form, text="Estado / Avarias:", font=("Arial", 14)).grid(row=4, column=0, sticky="w", pady=8)
entry_avarias = ctk.CTkEntry(frame_form, width=300, placeholder_text="Ex: Gabinete amassado")
entry_avarias.grid(row=4, column=1, padx=10, pady=8)

ctk.CTkLabel(frame_form, text="Problema (Visão Cliente):", font=("Arial", 14)).grid(row=5, column=0, sticky="nw", pady=8)
textbox_problema = ctk.CTkTextbox(frame_form, width=300, height=60)
textbox_problema.grid(row=5, column=1, padx=10, pady=8)

ctk.CTkLabel(frame_form, text="Serviço (Visão Técnico):", font=("Arial", 14)).grid(row=6, column=0, sticky="nw", pady=8)
textbox_servico = ctk.CTkTextbox(frame_form, width=300, height=60)
textbox_servico.grid(row=6, column=1, padx=10, pady=8)

btn_salvar = ctk.CTkButton(janela, text="💾 GERAR OS", fg_color="#28a745", hover_color="#218838", height=45, font=("Arial", 16, "bold"), command=salvar_os)
btn_salvar.pack(pady=5)

btn_bancada = ctk.CTkButton(janela, text="🛠️ ACESSAR BANCADA", fg_color="#17a2b8", hover_color="#138496", height=45, font=("Arial", 16, "bold"), command=abrir_bancada)
btn_bancada.pack(pady=5)

btn_historico = ctk.CTkButton(janela, text="💰 HISTÓRICO E CAIXA", fg_color="#6c757d", hover_color="#5a6268", height=45, font=("Arial", 16, "bold"), command=abrir_historico)
btn_historico.pack(pady=5)

conectar_banco()
janela.mainloop()