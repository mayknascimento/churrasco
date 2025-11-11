import streamlit as st
import pandas as pd

st.set_page_config(page_title="Divisão do Churrasco 🥩", page_icon="🥩")

st.title("🥩 Divisão do Churrasco - estilo Splitwise")

# Inicializa sessão
if "participantes" not in st.session_state:
    st.session_state.participantes = []
if "despesas" not in st.session_state:
    st.session_state.despesas = []

st.header("1️⃣ Participantes")
novo_nome = st.text_input("Adicionar participante:")
if st.button("Adicionar"):
    nome = novo_nome.strip()
    if nome and nome not in st.session_state.participantes:
        st.session_state.participantes.append(nome)
        st.success(f"{nome} adicionado!")
    elif nome in st.session_state.participantes:
        st.warning("Esse nome já foi adicionado.")
    novo_nome = ""

st.write("**Participantes:**", ", ".join(st.session_state.participantes))

st.header("2️⃣ Despesas")
if not st.session_state.participantes:
    st.info("Adicione os participantes primeiro.")
else:
    col1, col2 = st.columns(2)
    with col1:
        pagador = st.selectbox("Quem pagou?", st.session_state.participantes)
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

    envolvidos = st.multiselect("Quem participou dessa despesa?", st.session_state.participantes)

    if st.button("Adicionar despesa"):
        if valor <= 0:
            st.error("Valor deve ser maior que zero.")
        elif not envolvidos:
            st.error("Selecione pelo menos um participante.")
        else:
            st.session_state.despesas.append({"pagador": pagador, "valor": valor, "participantes": envolvidos})
            st.success(f"{pagador} pagou R${valor:.2f} por {', '.join(envolvidos)}")

if st.session_state.despesas:
    st.subheader("💸 Despesas registradas")
    for i, d in enumerate(st.session_state.despesas):
        st.text(f"{i+1}. {d['pagador']} pagou R${d['valor']:.2f} por {', '.join(d['participantes'])}")

    # Permitir edição
    indice_editar = st.number_input("Editar número da despesa (0 para nenhuma):", min_value=0, max_value=len(st.session_state.despesas))
    if indice_editar > 0:
        d = st.session_state.despesas[indice_editar - 1]
        st.write("### ✏️ Editar despesa")
        novo_pagador = st.selectbox("Novo pagador:", st.session_state.participantes, index=st.session_state.participantes.index(d["pagador"]))
        novo_valor = st.number_input("Novo valor (R$):", min_value=0.0, format="%.2f", value=d["valor"])
        novos_env = st.multiselect("Novos participantes:", st.session_state.participantes, default=d["participantes"])
        if st.button("Salvar alterações"):
            d["pagador"], d["valor"], d["participantes"] = novo_pagador, novo_valor, novos_env
            st.success("Despesa atualizada com sucesso ✅")

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
            envolvidos = despesa["participantes"]
            valor_por_pessoa = valor / len(envolvidos)

            pagos[pagador] += valor
            for pessoa in envolvidos:
                deve_gastar[pessoa] += valor_por_pessoa

        for p in participantes:
            saldos[p] = pagos[p] - deve_gastar[p]

        st.subheader("📊 Resumo individual")
        for p in participantes:
            st.write(f"- {p} pagou R${pagos[p]:.2f}, deveria gastar R${deve_gastar[p]:.2f} → saldo {saldos[p]:+.2f}")

        # Cálculo das transferências
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
