# Importação das bibliotecas
from customtkinter import *            
from tkinter import messagebox         
import openpyxl                        
import os                              
from reportlab.pdfgen import canvas    
import subprocess                      
import requests                        
from datetime import datetime          



# Criação da janela principal
janela = CTk()                         
janela.title("Cadastro de Clientes - Tenta Doces") 
janela.geometry("600x700")             

# Variáveis globais dos clientes
clientes_cadastrados = []
produtos_cadastrados = []
nome_cliente = ""
telefone_cliente = ""

# Função para buscar o CEP e validação
def buscar_cep():
    cep = entry_cep.get()
    if len(cep) == 8:  
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            dados = response.json()
            if "erro" not in dados:
                entry_rua.delete(0, 'end')
                entry_rua.insert(0, dados['logradouro'])
                entry_bairro.delete(0, 'end')
                entry_bairro.insert(0, dados['bairro'])
                entry_cidade.delete(0, 'end')
                entry_cidade.insert(0, dados['localidade'])
            else:
                messagebox.showerror("Erro", "CEP não encontrado.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro ao buscar o CEP: {e}")
    else:
        messagebox.showwarning("Atenção", "O CEP deve ter 8 dígitos.")

# Função para limpar os campos dos clientes
def limpar_campos_cliente():
    entry_nome.delete(0, 'end')
    entry_telefone.delete(0, 'end')
    entry_email.delete(0, 'end')
    entry_rua.delete(0, 'end')
    entry_numero.delete(0, 'end')
    entry_bairro.delete(0, 'end')
    entry_cidade.delete(0, 'end')
    entry_cep.delete(0, 'end')
    entry_cpf.delete(0, 'end')  

# Função para limpar campos dos produtos
def limpar_campos_produto():
    combo_produto.set('')
    entry_quantidade.delete(0, 'end')
    entry_preco.delete(0, 'end')
    entry_observacoes.delete("1.0", "end")
    atualizar_lista_produtos()  
    lista_produtos.delete("1.0", "end")  

# Função para salvar os clientes
def salvar_cliente():
    global nome_cliente, telefone_cliente
    nome_cliente = entry_nome.get()
    telefone_cliente = entry_telefone.get()
    email_cliente = entry_email.get()
    rua_cliente = entry_rua.get()
    numero_cliente = entry_numero.get()
    bairro_cliente = entry_bairro.get()
    cidade_cliente = entry_cidade.get()
    cep_cliente = entry_cep.get()
    cpf_cliente = entry_cpf.get()  

    # Validação do CPF para não cadastrar cliente repetidos
    if cpf_cliente in [cliente['cpf'] for cliente in clientes_cadastrados]:
        messagebox.showerror("Erro", "Cliente já cadastrado.")
        return

    # Salva o cliente
    cliente = {
        "nome": nome_cliente,
        "telefone": telefone_cliente,
        "email": email_cliente,
        "rua": rua_cliente,
        "numero": numero_cliente,
        "bairro": bairro_cliente,
        "cidade": cidade_cliente,
        "cep": cep_cliente,
        "cpf": cpf_cliente  
    }
    clientes_cadastrados.append(cliente)
    messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
    limpar_campos_cliente()  

# salvar o produto
def salvar_produto():
    produto = combo_produto.get()
    quantidade = entry_quantidade.get()
    preco = entry_preco.get()
    observacoes = entry_observacoes.get("1.0", "end-1c")  

    if produto and quantidade and preco:
        try:
            preco_float = float(preco)
            produto_inserido = {
                "produto": produto,
                "quantidade": quantidade,
                "preco": preco_float,
                "observacoes": observacoes
            }
            produtos_cadastrados.append(produto_inserido)
            messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")
            limpar_campos_produto()  
            atualizar_lista_produtos()  
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número.")
    else:
        messagebox.showwarning("Aviso", "Preencha todos os campos do produto.")

# produtos salvos e atualizar a lista
def atualizar_lista_produtos():
    lista_produtos.delete("1.0", "end")  
    for produto in produtos_cadastrados:
        lista_produtos.insert('end', f"Produto: {produto['produto']} - Quantidade: {produto['quantidade']} - Preço: R$ {produto['preco']:.2f} - Observações: {produto['observacoes']}\n")

# gerar o PDF do orçamento
def gerar_pdf_orcamento():
    arquivo_pdf = "orcamento.pdf"
    c = canvas.Canvas(arquivo_pdf)

    # data e hora atuais
    data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.drawString(100, 800, f"Data e Hora: {data_hora_atual}")

    c.drawString(100, 780, f"Orçamento para: {nome_cliente}")
    c.drawString(100, 760, f"Telefone: {telefone_cliente}")
    
    y_position = 740
    valor_total = sum([produto['preco'] for produto in produtos_cadastrados])

    for produto in produtos_cadastrados:
        c.drawString(100, y_position, f"Produto: {produto['produto']} - Quantidade: {produto['quantidade']} - Preço: R$ {produto['preco']:.2f} - Observações: {produto['observacoes']}")
        y_position -= 20

    c.drawString(100, y_position, f"Valor Total: R$ {valor_total:.2f}")
    c.save()
    
    # Abre o PDF após a criação
    subprocess.Popen([arquivo_pdf], shell=True)

#  finalizar o orçamento
def finalizar_orcamento():
    gerar_pdf_orcamento()

# iniciar um novo orçamento
def novo_orcamento():
    global produtos_cadastrados
    produtos_cadastrados = []
    limpar_campos_produto()  # Limpa os campos após iniciar novo orçamento
    lista_produtos.delete("1.0", "end")  # Limpa a lista de produtos ao iniciar um novo orçamento
    messagebox.showinfo("Sucesso", "Novo orçamento iniciado!")


abas = CTkTabview(janela)
abas.pack(pady=10, padx=10)

# Aba "Clientes"
aba_clientes = abas.add("Clientes")

# cadastro de cliente
label_nome = CTkLabel(aba_clientes, text="Nome:", font=("Helvetica", 12))
label_nome.grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_nome = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_nome.grid(row=0, column=1, padx=10, pady=5)

label_telefone = CTkLabel(aba_clientes, text="Telefone:", font=("Helvetica", 12))
label_telefone.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_telefone = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_telefone.grid(row=1, column=1, padx=10, pady=5)

label_email = CTkLabel(aba_clientes, text="Email:", font=("Helvetica", 12))
label_email.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_email = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_email.grid(row=2, column=1, padx=10, pady=5)

label_cpf = CTkLabel(aba_clientes, text="CPF:", font=("Helvetica", 12))
label_cpf.grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_cpf = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_cpf.grid(row=3, column=1, padx=10, pady=5)

label_rua = CTkLabel(aba_clientes, text="Rua:", font=("Helvetica", 12))
label_rua.grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_rua = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_rua.grid(row=4, column=1, padx=10, pady=5)

label_numero = CTkLabel(aba_clientes, text="Número:", font=("Helvetica", 12))
label_numero.grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_numero = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_numero.grid(row=5, column=1, padx=10, pady=5)

label_bairro = CTkLabel(aba_clientes, text="Bairro:", font=("Helvetica", 12))
label_bairro.grid(row=6, column=0, padx=10, pady=5, sticky="w")
entry_bairro = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_bairro.grid(row=6, column=1, padx=10, pady=5)

label_cidade = CTkLabel(aba_clientes, text="Cidade:", font=("Helvetica", 12))
label_cidade.grid(row=7, column=0, padx=10, pady=5, sticky="w")
entry_cidade = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_cidade.grid(row=7, column=1, padx=10, pady=5)

label_cep = CTkLabel(aba_clientes, text="CEP:", font=("Helvetica", 12))
label_cep.grid(row=8, column=0, padx=10, pady=5, sticky="w")
entry_cep = CTkEntry(aba_clientes, width=300, font=("Helvetica", 12))
entry_cep.grid(row=8, column=1, padx=10, pady=5)

# buscar o CEP
botao_buscar_cep = CTkButton(aba_clientes, text="Buscar CEP", command=buscar_cep)
botao_buscar_cep.grid(row=8, column=2, padx=5)

# botões de cliente
frame_botoes_cliente = CTkFrame(aba_clientes)
frame_botoes_cliente.grid(row=9, column=0, columnspan=3, pady=20)

botao_salvar_cliente = CTkButton(frame_botoes_cliente, text="Salvar Cliente", command=salvar_cliente)
botao_salvar_cliente.grid(row=0, column=0, padx=10)

botao_limpar_cliente = CTkButton(frame_botoes_cliente, text="Limpar", command=limpar_campos_cliente)
botao_limpar_cliente.grid(row=0, column=1, padx=10)

# Aba "Produtos"
aba_produtos = abas.add("Produtos")

# cadastro de produto
label_produto = CTkLabel(aba_produtos, text="Produto:", font=("Helvetica", 12))
label_produto.grid(row=0, column=0, padx=10, pady=5, sticky="w")
combo_produto = CTkComboBox(aba_produtos, values=["Bolos", "Doces", "Cupcakes", "Salgados"], width=300, font=("Helvetica", 12))
combo_produto.grid(row=0, column=1, padx=10, pady=5)

label_quantidade = CTkLabel(aba_produtos, text="Quantidade:", font=("Helvetica", 12))
label_quantidade.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_quantidade = CTkEntry(aba_produtos, width=300, font=("Helvetica", 12))
entry_quantidade.grid(row=1, column=1, padx=10, pady=5)

label_preco = CTkLabel(aba_produtos, text="Preço:", font=("Helvetica", 12))
label_preco.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_preco = CTkEntry(aba_produtos, width=300, font=("Helvetica", 12))
entry_preco.grid(row=2, column=1, padx=10, pady=5)

# Campo de Observações
label_observacoes = CTkLabel(aba_produtos, text="Observações:", font=("Helvetica", 12))
label_observacoes.grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_observacoes = CTkTextbox(aba_produtos, width=300, height=100, font=("Helvetica", 12))
entry_observacoes.grid(row=3, column=1, padx=10, pady=5)

# botões de produto
frame_botoes_produto = CTkFrame(aba_produtos)
frame_botoes_produto.grid(row=4, column=0, columnspan=3, pady=20)

botao_salvar_produto = CTkButton(frame_botoes_produto, text="Salvar Produto", command=salvar_produto)
botao_salvar_produto.grid(row=0, column=0, padx=10)

botao_limpar_produto = CTkButton(frame_botoes_produto, text="Limpar", command=limpar_campos_produto)
botao_limpar_produto.grid(row=0, column=1, padx=10)

# mostrar os produtos salvos
label_lista_produtos = CTkLabel(aba_produtos, text="Produtos no Orçamento:", font=("Helvetica", 12))
label_lista_produtos.grid(row=5, column=0, padx=10, pady=5, sticky="w")

lista_produtos = CTkTextbox(aba_produtos, width=400, height=200, font=("Helvetica", 12))
lista_produtos.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

# finalizar e iniciar novo orçamento
frame_botoes_orcamento = CTkFrame(janela)
frame_botoes_orcamento.pack(pady=20)

botao_finalizar_orcamento = CTkButton(frame_botoes_orcamento, text="Imprimir Orçamento", command=finalizar_orcamento, fg_color="green")
botao_finalizar_orcamento.grid(row=0, column=0, padx=10)

botao_novo_orcamento = CTkButton(frame_botoes_orcamento, text="Novo Orçamento", command=novo_orcamento, fg_color="green")
botao_novo_orcamento.grid(row=0, column=1, padx=10)

janela.mainloop()
