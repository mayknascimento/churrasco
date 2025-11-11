import streamlit as st
import pandas as pd

st.set_page_config(page_title="Divisão do Churrasco 🥩", page_icon="🥩")

st.title("🥩 Divisão do Churrasco - estilo Splitwise")

# ---------- INICIALIZAÇÃO ----------
if "participantes" not in st.session_state:
    st.session_state.participantes = []
if "despesas" not in st.session_state:
    st.session_state.despesas = []
if "novo_nome" not in st.session_state:
    st.session_state.novo_nome = ""
if "selecionar_todos" not in st.session_state:
    st.session_state.selecionar_todos = False

# ---------- FUNÇÕES ----------
def adicionar_participante():
    nome = st.session_state.novo_nome.strip().capitalize()
    if nome and nome not in st.session_state.participantes:
        st.session_state.participantes.append(nome)
        st.session_state.novo_nome = ""
        st.success(f"{nome} adicionado!")
    elif nome in st.session_state.participantes:
        st.warning("Esse nome já foi adicionado.")
    else:
        st.warning("Digite um nome válido.")

def converter_valor(valor_str):
    try:
        return float(valor_str.replace(",", "."))
    except:
        return 0.0

# ---------- PARTICIPANTES ----------
st.header("1️⃣ Participantes")

st.text_input(
    "Digite o nome e pressione TAB ou ENTER para adicionar:",
    key="novo_nome",
    on_change=adicionar_participante,
    placeholder="Exemplo: Mayk",
)

if st.session_state.participantes:
    st.write("**Participantes adicionados:**", ", ".join(st.session_state.participantes))

# ---------- DESPESAS ----------
st.header("2️⃣ Despesas")

if not st.session_state.participantes:
    st.info("Adicione os participantes primeiro.")
else:
    st.subheader("➕ Adicionar uma nova despesa")

    col1, col2 = st.columns(2)
    with col1:
        pagador = st.selectbox("Quem pagou?", st.session_state.participantes)
    with col2:
        valor_str = st.text_input("Valor pago (R$) — use vírgula:", placeholder="Ex: 50,00")

    # Botão para selecionar todos
    st.write("Selecione quem participou desse gasto:")
    if st.button("Selecionar todos"):
        st.session_state.selecionar_todos = True
    if st.button("Limpar seleção"):
        st.session_state.selecionar_todos = False

    if st.session_state.selecionar_todos:
        envolvidos = st.multiselect(
            "Quem participou?", st.session_state.participantes, default=st.session_state.participantes, key=f"envolvidos_{len(st.session_state.despesas)}"
        )
    else:
        envolvidos = st.multiselect(
            "Quem participou?", st.session_state.participantes, key=f"envolvidos_{len(st.session_state.despesas)}"
        )

    if st.button("Adicionar despesa"):
        valor = converter_valor(valor_str)
        if valor <= 0:
            st.error("Digite um valor válido.")
        elif not envolvidos:
            st.error("Selecione quem participou do gasto.")
        else:
            st.session_state.despesas.append({
                "pagador": pagador,
                "valor": valor,
                "envolvidos": envolvidos
            })
            st.success(f"{pagador} pagou R${valor:.2f} por {', '.join(envolvidos)}")

# ---------- LISTA DE DESPESAS ----------
if st.session_state.despesas:
    st.subheader("💸 Despesas registradas")
    for i, d in enumerate(st.session_state.despesas):
        st.text(f"{i+1}. {d['pagador']} pagou R${d['valor']:.2f} por {', '.join(d['envolvidos'])}")

# ---------- RESULTADO ----------
st.header("3️⃣ Resultado final 💰")

if st.button("Calcular resultado"):
    participantes = st.session_state.participantes
    despesas = st.session_state.despesas

    pagos = {p: 0 for p in participantes}
    deve_gastar = {p: 0 for p in participantes}
    saldos = {p: 0 for p in participantes}

    for despesa in despesas:
        valor = despesa["valor"]
        pagador = despesa["pagador"]
        envolvidos = despesa["envolvidos"]
        valor_por_pessoa = valor / len(envolvidos)

        pagos[pagador] += valor
        for pessoa in envolvidos:
            deve_gastar[pessoa] += valor_por_pessoa

    for p in participantes:
        saldos[p] = pagos[p] - deve_gastar[p]

    st.subheader("📊 Resumo individual")
    for p in participantes:
        st.write(f"- {p}: pagou R${pagos[p]:.2f}, deveria gastar R${deve_gastar[p]:.2f} → saldo {saldos[p]:+.2f}")

    # ---------- TRANSFERÊNCIAS ----------
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

    st.subheader("💵 Transferências necessárias")
    if resultado:
        for r in resultado:
            st.write(r)
    else:
        st.success("Todos estão equilibrados! 🎉")
