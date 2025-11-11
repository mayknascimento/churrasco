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
    st.write("Selecione quem participou dessa despesa e quanto cada um gastou:")

    participantes_env = st.multiselect(
        "Quem participou do gasto?",
        st.session_state.participantes,
        default=st.session_state.participantes,
    )

    valores_gastos = {}
    cols = st.columns(2)
    for i, nome in enumerate(participantes_env):
        with cols[i % 2]:
            valores_gastos[nome] = st.text_input(
                f"{nome} (R$):",
                key=f"gasto_{nome}_{len(st.session_state.despesas)}",
                placeholder="Ex: 25,50",
            )

    if st.button("Adicionar despesa"):
        despesa_atual = {}
        total = 0
        for nome in participantes_env:
            valor = converter_valor(valores_gastos.get(nome, "0"))
            if valor > 0:
                despesa_atual[nome] = valor
                total += valor

        if not participantes_env:
            st.error("Selecione ao menos uma pessoa.")
        elif total == 0:
            st.error("Adicione pelo menos um valor válido.")
        else:
            st.session_state.despesas.append({"envolvidos": participantes_env, "valores": despesa_atual})
            st.success(f"Despesa adicionada com sucesso! (Total R${total:.2f})")

# ---------- LISTA DE DESPESAS ----------
if st.session_state.despesas:
    st.subheader("💸 Despesas registradas")
    for i, d in enumerate(st.session_state.despesas):
        env = ", ".join(d["envolvidos"])
        detalhes = ", ".join([f"{p}: R${v:.2f}" for p, v in d["valores"].items()])
        st.text(f"{i+1}. [{env}] → {detalhes}")

# ---------- RESULTADO ----------
st.header("3️⃣ Resultado final 💰")

if st.button("Calcular resultado"):
    participantes = st.session_state.participantes
    despesas = st.session_state.despesas

    pagos = {p: 0 for p in participantes}
    deve_gastar = {p: 0 for p in participantes}
    saldos = {p: 0 for p in participantes}

    for despesa in despesas:
        envolvidos = despesa["envolvidos"]
        valores = despesa["valores"]
        total_despesa = sum(valores.values())

        if not envolvidos:
            continue

        valor_por_pessoa = total_despesa / len(envolvidos)

        for pagador, valor in valores.items():
            pagos[pagador] += valor
        for p in envolvidos:
            deve_gastar[p] += valor_por_pessoa

    for p in participantes:
        saldos[p] = pagos[p] - deve_gastar[p]

    # ---------- RESULTADO INDIVIDUAL ----------
    st.subheader("📊 Resumo individual")
    for p in participantes:
        st.write(
            f"- {p}: pagou R${pagos[p]:.2f}, deveria gastar R${deve_gastar[p]:.2f} → saldo {saldos[p]:+.2f}"
        )

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
