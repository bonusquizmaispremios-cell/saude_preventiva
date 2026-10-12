import streamlit as st
from groq import Groq
from datetime import datetime
import json

st.set_page_config(page_title="Saúde Preventiva IA", page_icon="💊", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp { background-color:#FFF5F5; font-family:'Inter',sans-serif; }
[data-testid="stSidebar"] { display:none; }
.stTextInput>div>div>input, .stTextArea>div>textarea,
.stSelectbox>div>div>div, .stNumberInput>div>div>input {
    background-color:#FFFFFF !important; color:#1A1A2E !important;
    border:1px solid #CED4DA !important; font-family:'Inter',sans-serif !important;
}
.stButton>button {
    width:100%; border-radius:10px; height:3.2em;
    background:linear-gradient(135deg,#DC2626,#B91C1C) !important; color:white !important;
    font-weight:600; border:none; box-shadow:2px 2px 8px rgba(0,0,0,0.1);
    font-family:'Inter',sans-serif !important; transition:all 0.2s ease;
}
.stButton>button:hover { background:linear-gradient(135deg,#B91C1C,#DC2626) !important; transform:translateY(-1px); }
.stApp .stButton>button, .stApp .stButton>button p,
.stApp .stButton>button span, .stApp .stButton>button div { color:white !important; }
.stApp h1, .stApp h2, .stApp h3 { color:#7F1D1D !important; font-family:'Inter',sans-serif !important; font-weight:700 !important; }
.card { background:linear-gradient(135deg,#FFF5F5,#FEE2E2); padding:20px; border-radius:14px; border:1px solid #FECACA; margin-bottom:14px; white-space:normal; word-wrap:break-word; }
.stApp .card, .stApp .card p, .stApp .card span, .stApp .card div, .stApp .card strong { color:#7F1D1D !important; }
.card-blue { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; }
.stApp .card-blue, .stApp .card-blue p, .stApp .card-blue div { color:#1E3A8A !important; }
.card-green { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); padding:20px; border-radius:14px; border:1px solid #86EFAC; margin-bottom:14px; }
.stApp .card-green, .stApp .card-green p, .stApp .card-green div { color:#14532D !important; }
.card-yellow { background:linear-gradient(135deg,#FFFBEB,#FEF3C7); padding:18px; border-radius:12px; border:1px solid #FCD34D; margin-bottom:12px; }
.stApp .card-yellow, .stApp .card-yellow p, .stApp .card-yellow div { color:#78350F !important; }
.badge { background:#DC2626; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
.badge-verde { background:#059669; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
.badge-amarelo { background:#B45309; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
.divider { border:none; height:1px; background:linear-gradient(to right,transparent,#FECACA,transparent); margin:18px 0; }
.chat-user { background:#FFFFFF; border:1px solid #FECACA; border-radius:12px 12px 4px 12px; padding:12px 16px; margin:8px 0; }
.stApp .chat-user, .stApp .chat-user p, .stApp .chat-user div { color:#1A1A2E !important; }
.chat-ia { background:#FEE2E2; border:1px solid #FECACA; border-radius:4px 12px 12px 12px; padding:12px 16px; margin:8px 0; }
.stApp .chat-ia, .stApp .chat-ia p, .stApp .chat-ia div { color:#7F1D1D !important; }
.sugestao-btn { display:inline-block; background:#FEE2E2; border:1px solid #FECACA; border-radius:20px; padding:5px 12px; font-size:0.8em; color:#7F1D1D !important; cursor:pointer; margin:3px; }
.guia-box { background:#fff; border:1px solid #FECACA; border-radius:12px; padding:18px; margin-bottom:16px; }
.stApp .guia-box, .stApp .guia-box p, .stApp .guia-box div, .stApp .guia-box span { color:#1A1A2E !important; }
.stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #FECACA; }
.stApp .stat-box div, .stApp .stat-box span { color:#7F1D1D !important; }
</style>
""", unsafe_allow_html=True)

# ── SYSTEM PROMPT RICO ──
SYSTEM_PROMPT = """Você é a Dra. Sofia, educadora em saúde preventiva do Saúde Preventiva IA.

REGRAS ABSOLUTAS:
- NUNCA faz diagnósticos médicos nem prescreve medicamentos ou dosagens
- Sempre orienta a consultar um médico para diagnóstico e tratamento
- Foca em PREVENÇÃO, educação em saúde e hábitos saudáveis
- Quando mencionar sinais de alerta sérios, sempre recomenda buscar atendimento médico

SEU ESTILO:
- Responde de forma calorosa, educativa e prática
- Usa linguagem acessível (não técnica demais)
- Organiza as respostas com tópicos e listas quando útil
- Personaliza para o perfil do usuário quando fornecido
- Sempre termina com uma dica de prevenção ou encorajamento

IDIOMA: Português do Brasil."""

def chamar_ia(msgs_hist, pergunta, contexto_extra=""):
    client = Groq(api_key=st.session_state.api_key)
    system = SYSTEM_PROMPT
    if contexto_extra:
        system += f"\n\nCONTEXTO DO USUÁRIO:\n{contexto_extra}"
    messages = [{"role": "system", "content": system}]
    for m in msgs_hist[-10:]:
        messages.append(m)
    messages.append({"role": "user", "content": pergunta})
    resp = client.chat.completions.create(messages=messages, model="openai/gpt-oss-120b", max_tokens=2048)
    return resp.choices[0].message.content

def contexto_perfil():
    p = st.session_state
    partes = []
    if p.get("perfil_nome"): partes.append(f"Nome: {p['perfil_nome']}")
    if p.get("perfil_idade"): partes.append(f"Idade: {p['perfil_idade']} anos")
    if p.get("perfil_sexo"): partes.append(f"Sexo: {p['perfil_sexo']}")
    if p.get("perfil_peso"): partes.append(f"Peso: {p['perfil_peso']} kg")
    if p.get("perfil_altura"): partes.append(f"Altura: {p['perfil_altura']} cm")
    if p.get("perfil_condicoes"): partes.append(f"Condições de saúde: {p['perfil_condicoes']}")
    if p.get("perfil_medicamentos"): partes.append(f"Medicamentos em uso: {p['perfil_medicamentos']}")
    if p.get("perfil_alergias"): partes.append(f"Alergias: {p['perfil_alergias']}")
    return "\n".join(partes) if partes else ""

def render_chat(hist_key, input_key, btn_key, sugestoes=None, contexto_extra="", placeholder="Digite sua mensagem..."):
    hist = st.session_state.get(hist_key, [])

    # Sugestões rápidas
    if sugestoes:
        st.markdown("**💡 Perguntas rápidas — clique para usar:**")
        cols = st.columns(min(len(sugestoes), 3))
        for i, s in enumerate(sugestoes):
            with cols[i % len(cols)]:
                if st.button(s, key=f"sug_{btn_key}_{i}"):
                    st.session_state[f"_input_{input_key}"] = s

    # Histórico de conversa
    if hist:
        st.markdown("---")
        for msg in hist:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-user'>👤 <b>Você:</b> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ia'>💊 <b>Dra. Sofia:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("---")

    # Input
    val_inicial = st.session_state.pop(f"_input_{input_key}", "")
    pergunta = st.text_area(
        "💬 Sua mensagem:",
        value=val_inicial,
        height=90,
        key=input_key,
        placeholder=placeholder
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        enviar = st.button("📤 ENVIAR MENSAGEM", key=btn_key, use_container_width=True)
    with col2:
        if hist and st.button("🗑️ Limpar", key=f"clear_{btn_key}", use_container_width=True):
            st.session_state[hist_key] = []
            st.rerun()

    if enviar and pergunta.strip():
        with st.spinner("Dra. Sofia está respondendo..."):
            try:
                resposta = chamar_ia(hist, pergunta.strip(), contexto_extra)
                hist.append({"role": "user", "content": pergunta.strip()})
                hist.append({"role": "assistant", "content": resposta})
                st.session_state[hist_key] = hist
                st.session_state.historico_saude_preventiva.append({
                    "data": datetime.now().strftime("%d/%m %H:%M"),
                    "aba": hist_key,
                    "resumo": pergunta[:60],
                    "conteudo": resposta
                })
                st.rerun()
            except Exception as e:
                st.error(f"Erro na API: {e}")
    elif enviar:
        st.warning("Digite uma mensagem antes de enviar.")

# ── DEFAULTS ──
defaults = {
    "etapa": "Login", "usuario": "", "api_key": "",
    "historico_saude_preventiva": [],
    "perfil_nome": "", "perfil_idade": "", "perfil_sexo": "",
    "perfil_peso": "", "perfil_altura": "", "perfil_condicoes": "",
    "perfil_medicamentos": "", "perfil_alergias": "",
    "hist_sintomas": [], "hist_exames": [], "hist_riscos": [],
    "hist_suplementos": [], "hist_alimentacao": [], "hist_mental": [],
    "hist_checkup": [], "hist_diario": [], "hist_evolucao": [],
    "perfil_completo": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 💊 Saúde Preventiva IA")
    st.markdown("<div class='card'><b>🔒 ACESSO RESTRITO A CLIENTES DO MEUSAGENTESIA.COM.BR</b><br>🔗 <a href='https://meusagentesia.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>meusagentesia.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** Pela complexidade dos agentes, no computador a experiência é mais agradável.")
    nome  = st.text_input("Seu Nome:", key="nome_login")
    chave = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_login")
    arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
    if st.button("✨ ENTRAR", key="btn_entrar_login"):
        if len(nome.strip()) < 2:
            st.warning("Digite um nome com pelo menos 2 caracteres.")
        elif chave.strip():
            st.session_state.usuario = nome.strip()
            st.session_state.api_key = chave
            if arq_j:
                try:
                    dados = json.load(arq_j)
                    bloq = {'api_key','etapa'}
                    for k, v in dados.items():
                        if k not in bloq:
                            st.session_state[k] = v
                except:
                    pass
            st.session_state.etapa = "App"
            st.rerun()
        else:
            st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":

    # ── SALVAR / CARREGAR ──
    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            _dsv = {k: st.session_state.get(k) for k in st.session_state.keys() if not k.startswith('_') and k != 'api_key'}
            st.download_button("💾 Baixar meus dados (.json)",
                data=json.dumps(_dsv, ensure_ascii=False, indent=2, default=str),
                file_name=f"saude_preventiva_{st.session_state.usuario}.json",
                mime="application/json", key="dl_barra_sp")
        with c2:
            _fup = st.file_uploader("📂 Carregar dados:", type=["json"], key="ul_barra_sp", label_visibility="collapsed")
            if _fup:
                try:
                    for k, v in json.loads(_fup.read().decode()).items():
                        if k not in ('api_key', 'etapa'):
                            st.session_state[k] = v
                    st.success("✅ Dados restaurados!"); st.rerun()
                except: st.error("Arquivo inválido.")

    tabs = st.tabs([
        '🏠 Home', '👤 Meu Perfil', '🔍 Sintomas', '🧪 Exames',
        '🏃 Hábitos de Risco', '💊 Suplementação', '🥗 Alimentação',
        '🧘 Saúde Mental', '📊 Check-up Digital', '📓 Diário', '📈 Evolução'
    ])
    _tab_home, _tab_perfil, _tab_sint, _tab_exam, _tab_risco, _tab_suple, _tab_alim, _tab_mental, _tab_check, _tab_diario, _tab_evolucao = tabs

    ctx = contexto_perfil()

    # ═══════════════════════════════════════════════════
    # 🏠 HOME
    # ═══════════════════════════════════════════════════
    with _tab_home:
        st.title(f"💊 Olá, {st.session_state.usuario}!")
        st.markdown("*Sua parceira de educação em saúde preventiva — guiada por IA.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        if not st.session_state.perfil_completo:
            st.markdown("<div class='card-yellow'>⚠️ <b>Comece pelo Meu Perfil!</b> Quanto mais informações você preencher, mais personalizadas serão as orientações da Dra. Sofia para você.</div>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        qtd = len(st.session_state.historico_saude_preventiva)
        chats = sum(1 for k in ['hist_sintomas','hist_exames','hist_riscos','hist_suplementos','hist_alimentacao','hist_mental','hist_checkup','hist_diario','hist_evolucao'] if st.session_state.get(k))
        with col1: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>💬</div><div style='font-size:1.4em;font-weight:700;'>{qtd}</div><div style='font-size:0.75em;'>Consultas</div></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🗂️</div><div style='font-size:1.4em;font-weight:700;'>{chats}</div><div style='font-size:0.75em;'>Módulos usados</div></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>👤</div><div style='font-size:1.4em;font-weight:700;'>{'✅' if st.session_state.perfil_completo else '⚠️'}</div><div style='font-size:0.75em;'>Perfil</div></div>", unsafe_allow_html=True)
        with col4: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🤖</div><div style='font-size:1.4em;font-weight:700;'>IA</div><div style='font-size:0.75em;'>Dra. Sofia</div></div>", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("### 🗺️ Como usar cada módulo")
        modulos = [
            ("👤 Meu Perfil", "Cadastre seus dados de saúde para orientações personalizadas"),
            ("🔍 Sintomas", "Descreva sintomas e receba orientação educativa sobre o que podem indicar"),
            ("🧪 Exames", "Saiba quais exames preventivos fazer pela sua faixa etária"),
            ("🏃 Hábitos de Risco", "Avalie seus hábitos e receba orientações para mudá-los"),
            ("💊 Suplementação", "Entenda suplementos e quando podem ser indicados"),
            ("🥗 Alimentação", "Orientações nutricionais e planos alimentares educativos"),
            ("🧘 Saúde Mental", "Apoio e técnicas para bem-estar emocional e mental"),
            ("📊 Check-up Digital", "Questionário guiado para avaliar sua saúde geral"),
            ("📓 Diário", "Registre seu bem-estar diário e acompanhe tendências"),
            ("📈 Evolução", "Analise seu progresso ao longo do tempo"),
        ]
        for nome_m, desc_m in modulos:
            st.markdown(f"<div class='guia-box'><b>{nome_m}</b> — {desc_m}</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # 👤 MEU PERFIL
    # ═══════════════════════════════════════════════════
    with _tab_perfil:
        st.header("👤 Meu Perfil de Saúde")
        st.markdown("<div class='card-blue'>📋 Preencha seus dados para que a Dra. Sofia personalize todas as orientações para você. <b>Não compartilhamos seus dados.</b></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.perfil_nome = st.text_input("Nome completo:", value=st.session_state.perfil_nome, key="inp_pnome")
            st.session_state.perfil_idade = st.text_input("Idade:", value=st.session_state.perfil_idade, key="inp_pidade", placeholder="Ex: 35")
            st.session_state.perfil_sexo = st.selectbox("Sexo biológico:", ["", "Masculino", "Feminino"], key="inp_psexo",
                index=["", "Masculino", "Feminino"].index(st.session_state.perfil_sexo) if st.session_state.perfil_sexo in ["", "Masculino", "Feminino"] else 0)
        with col2:
            st.session_state.perfil_peso = st.text_input("Peso (kg):", value=st.session_state.perfil_peso, key="inp_ppeso", placeholder="Ex: 70")
            st.session_state.perfil_altura = st.text_input("Altura (cm):", value=st.session_state.perfil_altura, key="inp_paltura", placeholder="Ex: 170")

        st.session_state.perfil_condicoes = st.text_area("Condições de saúde existentes:", value=st.session_state.perfil_condicoes, key="inp_pcond",
            placeholder="Ex: Diabetes tipo 2, hipertensão, hipotireoidismo... (ou 'nenhuma')", height=80)
        st.session_state.perfil_medicamentos = st.text_area("Medicamentos em uso:", value=st.session_state.perfil_medicamentos, key="inp_pmed",
            placeholder="Ex: Metformina 500mg, Losartana 50mg... (ou 'nenhum')", height=80)
        st.session_state.perfil_alergias = st.text_input("Alergias conhecidas:", value=st.session_state.perfil_alergias, key="inp_palerg",
            placeholder="Ex: Penicilina, látex, amendoim... (ou 'nenhuma')")

        if st.button("✅ SALVAR MEU PERFIL", key="btn_salvar_perfil"):
            st.session_state.perfil_completo = bool(st.session_state.perfil_nome and st.session_state.perfil_idade)
            st.success("✅ Perfil salvo! A Dra. Sofia agora vai personalizar todas as suas orientações.")
            st.rerun()

        if st.session_state.perfil_completo and ctx:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("### 🤖 Pergunte sobre seu perfil")
            render_chat("hist_perfil_sp", "inp_chat_perfil", "btn_chat_perfil",
                sugestoes=["Qual meu IMC e o que significa?", "Que cuidados devo ter com minha condição?", "Quais riscos tenho pela minha idade?"],
                contexto_extra=ctx,
                placeholder="Pergunte algo sobre sua saúde baseado no seu perfil...")

    # ═══════════════════════════════════════════════════
    # 🔍 SINTOMAS
    # ═══════════════════════════════════════════════════
    with _tab_sint:
        st.header("🔍 Análise Educativa de Sintomas")
        st.markdown("<div class='card-yellow'>⚠️ <b>Importante:</b> Esta ferramenta é educativa — NÃO faz diagnósticos. Para diagnóstico e tratamento, consulte sempre um médico.</div>", unsafe_allow_html=True)

        with st.expander("📝 Descreva seus sintomas com mais detalhes", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                sint_local = st.selectbox("Onde está o sintoma?", ["", "Cabeça", "Peito/Coração", "Abdômen/Barriga", "Costas", "Pernas/Pés", "Braços/Mãos", "Geral/Todo o corpo", "Pele", "Outro"], key="sint_local")
                sint_inicio = st.selectbox("Há quanto tempo?", ["", "Hoje", "Alguns dias", "1-2 semanas", "1 mês ou mais", "Recorrente"], key="sint_inicio")
            with col2:
                sint_intensidade = st.selectbox("Intensidade (1=leve, 10=muito forte):", ["", "1-3 (leve)", "4-6 (moderado)", "7-9 (forte)", "10 (insuportável)"], key="sint_intens")
                sint_historico = st.text_input("Condições de saúde que já tem:", value=st.session_state.perfil_condicoes, key="sint_hist_c")

            sint_desc = st.text_area("Descreva os sintomas em detalhes:", height=80, key="sint_desc_detalhe",
                placeholder="Ex: Dor de cabeça latejante no lado direito, começa de manhã, melhora com escuro...")

        ctx_sint = ctx
        if sint_local or sint_inicio or sint_intensidade:
            ctx_sint += f"\nSintoma em: {sint_local} | Há: {sint_inicio} | Intensidade: {sint_intensidade}"
            if sint_desc:
                ctx_sint += f" | Descrição: {sint_desc}"

        render_chat("hist_sintomas", "inp_sint", "btn_sint",
            sugestoes=["O que pode ser dor de cabeça frequente?", "Cansaço excessivo — quando me preocupar?", "Dor nas costas: hábitos que pioram?", "Quando este sintoma é sinal de alerta?"],
            contexto_extra=ctx_sint,
            placeholder="Descreva seus sintomas ou faça uma pergunta...")

    # ═══════════════════════════════════════════════════
    # 🧪 EXAMES PREVENTIVOS
    # ═══════════════════════════════════════════════════
    with _tab_exam:
        st.header("🧪 Exames Preventivos")
        st.markdown("<div class='card-green'>✅ A prevenção começa com exames regulares. A Dra. Sofia orienta quais exames são recomendados para o seu perfil.</div>", unsafe_allow_html=True)

        with st.expander("🔧 Filtrar recomendações", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                ex_idade = st.text_input("Idade:", value=st.session_state.perfil_idade, key="ex_idade", placeholder="Ex: 40")
            with col2:
                ex_sexo = st.selectbox("Sexo:", ["", "Masculino", "Feminino"], key="ex_sexo",
                    index=["", "Masculino", "Feminino"].index(st.session_state.perfil_sexo) if st.session_state.perfil_sexo in ["", "Masculino", "Feminino"] else 0)
            with col3:
                ex_ultimo = st.selectbox("Último check-up:", ["", "Nunca fiz", "Há menos de 1 ano", "1-2 anos atrás", "Mais de 3 anos"], key="ex_ultimo")

            ex_cond = st.text_input("Condições de saúde:", value=st.session_state.perfil_condicoes, key="ex_cond", placeholder="Ex: diabetes, hipertensão...")

        ctx_ex = ctx
        if ex_idade or ex_sexo:
            ctx_ex += f"\nIdade para exames: {ex_idade} | Sexo: {ex_sexo} | Último check-up: {ex_ultimo} | Condições: {ex_cond}"

        render_chat("hist_exames", "inp_exam", "btn_exam",
            sugestoes=["Quais exames devo fazer com minha idade?", "Com que frequência fazer exames de sangue?", "Exames para detectar câncer precocemente?", "Exames do coração — quando fazer?"],
            contexto_extra=ctx_ex,
            placeholder="Pergunte sobre exames preventivos...")

    # ═══════════════════════════════════════════════════
    # 🏃 HÁBITOS DE RISCO
    # ═══════════════════════════════════════════════════
    with _tab_risco:
        st.header("🏃 Avaliação de Hábitos de Risco")
        st.markdown("<div class='card'>🎯 Identifique hábitos que podem prejudicar sua saúde e receba orientações para mudá-los gradualmente.</div>", unsafe_allow_html=True)

        with st.expander("📋 Meus hábitos atuais", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                r_fuma = st.selectbox("Tabagismo:", ["", "Não fumo", "Fumante (menos de 10/dia)", "Fumante (10-20/dia)", "Fumante pesado (20+/dia)", "Ex-fumante"], key="r_fuma")
                r_alcool = st.selectbox("Álcool:", ["", "Não bebo", "Raramente", "Fins de semana", "Diariamente (moderado)", "Diariamente (excessivo)"], key="r_alcool")
                r_exercicio = st.selectbox("Exercício físico:", ["", "Sedentário (nenhum)", "Leve (1-2x/semana)", "Moderado (3-4x/semana)", "Intenso (5+/semana)"], key="r_exercicio")
            with col2:
                r_sono = st.selectbox("Qualidade do sono:", ["", "Menos de 5h/noite", "5-6h (irregular)", "7-8h (bom)", "9h+ (muito sono)"], key="r_sono")
                r_estresse = st.selectbox("Nível de estresse:", ["", "Baixo", "Moderado", "Alto", "Muito alto / esgotamento"], key="r_estresse")
                r_alimentacao = st.selectbox("Alimentação:", ["", "Muito ruim", "Ruim", "Regular", "Boa", "Excelente"], key="r_alimentacao_geral")

        ctx_risco = ctx
        habitos = []
        if r_fuma: habitos.append(f"Tabagismo: {r_fuma}")
        if r_alcool: habitos.append(f"Álcool: {r_alcool}")
        if r_exercicio: habitos.append(f"Exercício: {r_exercicio}")
        if r_sono: habitos.append(f"Sono: {r_sono}")
        if r_estresse: habitos.append(f"Estresse: {r_estresse}")
        if r_alimentacao: habitos.append(f"Alimentação: {r_alimentacao}")
        if habitos:
            ctx_risco += "\nHábitos informados: " + " | ".join(habitos)

        render_chat("hist_riscos", "inp_risco", "btn_risco",
            sugestoes=["Qual meu maior risco com esses hábitos?", "Como parar de fumar com menos sofrimento?", "Como começar a me exercitar do zero?", "Estresse alto está me fazendo mal — o que fazer?"],
            contexto_extra=ctx_risco,
            placeholder="Pergunte sobre seus hábitos e como melhorá-los...")

    # ═══════════════════════════════════════════════════
    # 💊 SUPLEMENTAÇÃO
    # ═══════════════════════════════════════════════════
    with _tab_suple:
        st.header("💊 Orientação sobre Suplementação")
        st.markdown("<div class='card-yellow'>⚠️ Suplementos não substituem alimentação balanceada. Dosagem e indicação devem ser definidas por médico ou nutricionista.</div>", unsafe_allow_html=True)

        with st.expander("🔍 O que você quer saber?", expanded=True):
            suple_objetivo = st.selectbox("Seu objetivo:", ["", "Saúde geral", "Imunidade", "Energia e disposição", "Sono melhor", "Saúde óssea", "Saúde cardiovascular", "Performance esportiva", "Emagrecimento", "Saúde mental"], key="suple_obj")
            suple_atual = st.text_input("Suplementos que já usa:", key="suple_atual", placeholder="Ex: Vitamina D, Ômega 3, Magnésio...")
            suple_dieta = st.selectbox("Tipo de alimentação:", ["", "Onívoro (come tudo)", "Vegetariano", "Vegano", "Low carb / Cetogênica", "Outro"], key="suple_dieta")

        ctx_suple = ctx
        if suple_objetivo: ctx_suple += f"\nObjetivo: {suple_objetivo}"
        if suple_atual: ctx_suple += f" | Usa atualmente: {suple_atual}"
        if suple_dieta: ctx_suple += f" | Dieta: {suple_dieta}"

        render_chat("hist_suplementos", "inp_suple", "btn_suple",
            sugestoes=["Vitamina D — quando tomar?", "Ômega 3 — quais benefícios reais?", "Magnésio ajuda no sono?", "Vitaminas que veganos precisam?"],
            contexto_extra=ctx_suple,
            placeholder="Pergunte sobre suplementos e vitaminas...")

    # ═══════════════════════════════════════════════════
    # 🥗 ALIMENTAÇÃO
    # ═══════════════════════════════════════════════════
    with _tab_alim:
        st.header("🥗 Alimentação Saudável")
        st.markdown("<div class='card-green'>🌿 Orientações educativas para uma alimentação mais saudável. Para planos personalizados, consulte um nutricionista.</div>", unsafe_allow_html=True)

        with st.expander("🍽️ Seu contexto alimentar", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                alim_obj = st.selectbox("Objetivo:", ["", "Perder peso", "Ganhar massa", "Manutenção", "Controlar diabetes", "Reduzir colesterol", "Mais energia", "Saúde intestinal"], key="alim_obj")
                alim_restricao = st.text_input("Restrições / intolerâncias:", key="alim_restricao", placeholder="Ex: lactose, glúten, amendoim...")
            with col2:
                alim_refeicoes = st.selectbox("Quantas refeições por dia?", ["", "1-2", "3", "4-5", "6+"], key="alim_refeicoes")
                alim_cozinha = st.selectbox("Você cozinha em casa?", ["", "Sempre", "Às vezes", "Raramente", "Nunca"], key="alim_cozinha")

        ctx_alim = ctx
        if alim_obj: ctx_alim += f"\nObjetivo alimentar: {alim_obj}"
        if alim_restricao: ctx_alim += f" | Restrições: {alim_restricao}"
        if alim_refeicoes: ctx_alim += f" | Refeições/dia: {alim_refeicoes}"
        if alim_cozinha: ctx_alim += f" | Cozinha em casa: {alim_cozinha}"

        render_chat("hist_alimentacao", "inp_alim", "btn_alim",
            sugestoes=["Monte um cardápio saudável para a semana", "O que comer para ter mais energia?", "Como reduzir açúcar sem sofrimento?", "Alimentos que ajudam no colesterol?"],
            contexto_extra=ctx_alim,
            placeholder="Pergunte sobre alimentação saudável...")

    # ═══════════════════════════════════════════════════
    # 🧘 SAÚDE MENTAL
    # ═══════════════════════════════════════════════════
    with _tab_mental:
        st.header("🧘 Saúde Mental e Bem-Estar")
        st.markdown("<div class='card-blue'>💙 Cuidar da mente é tão importante quanto cuidar do corpo. Em crises, busque apoio profissional. <b>CVV: 188 (24h)</b></div>", unsafe_allow_html=True)

        with st.expander("💬 Como você está se sentindo?", expanded=True):
            mental_humor = st.selectbox("Seu humor nos últimos dias:", ["", "Muito bem 😄", "Bem 🙂", "Regular 😐", "Triste / ansioso 😟", "Muito mal 😔"], key="mental_humor")
            mental_sono = st.selectbox("Qualidade do sono:", ["", "Ótimo", "Bom", "Regular", "Ruim", "Péssimo (insônia)"], key="mental_sono_m")
            mental_situacao = st.text_area("O que está te preocupando? (opcional):", height=70, key="mental_situacao",
                placeholder="Pode ser breve — ex: estresse no trabalho, ansiedade, tristeza sem motivo...")

        ctx_mental = ctx
        if mental_humor: ctx_mental += f"\nHumor: {mental_humor}"
        if mental_sono: ctx_mental += f" | Sono: {mental_sono}"
        if mental_situacao: ctx_mental += f" | Situação: {mental_situacao}"

        render_chat("hist_mental", "inp_mental", "btn_mental",
            sugestoes=["Técnicas para reduzir ansiedade agora", "Como melhorar a qualidade do sono?", "Estou me sentindo esgotado — o que fazer?", "Mindfulness: como começar do zero?"],
            contexto_extra=ctx_mental,
            placeholder="Fale sobre o que está sentindo ou faça uma pergunta...")

    # ═══════════════════════════════════════════════════
    # 📊 CHECK-UP DIGITAL
    # ═══════════════════════════════════════════════════
    with _tab_check:
        st.header("📊 Check-up Digital de Saúde")
        st.markdown("<div class='card'>📋 Responda ao questionário abaixo e a Dra. Sofia vai gerar uma avaliação educativa completa do seu estado de saúde atual.</div>", unsafe_allow_html=True)

        with st.form("form_checkup"):
            st.markdown("#### 1. Dados básicos")
            col1, col2, col3 = st.columns(3)
            with col1: ck_idade = st.text_input("Idade:", value=st.session_state.perfil_idade, key="ck_idade")
            with col2: ck_sexo = st.selectbox("Sexo:", ["", "Masculino", "Feminino"], key="ck_sexo")
            with col3: ck_peso_alt = st.text_input("Peso/Altura:", key="ck_peso_alt", placeholder="70kg / 170cm")

            st.markdown("#### 2. Sintomas recentes")
            ck_sint = st.multiselect("Algum destes sintomas nas últimas semanas?", [
                "Cansaço excessivo", "Dor de cabeça frequente", "Dificuldade para dormir",
                "Dor no peito", "Falta de ar", "Tontura", "Perda de peso sem motivo",
                "Ansiedade / estresse intenso", "Dores musculares", "Problemas digestivos", "Nenhum"
            ], key="ck_sint_list")

            st.markdown("#### 3. Estilo de vida")
            col1, col2 = st.columns(2)
            with col1:
                ck_exercicio = st.selectbox("Exercício:", ["Sedentário", "1-2x/semana", "3-4x/semana", "5+/semana"], key="ck_ex")
                ck_alcool = st.selectbox("Álcool:", ["Não bebo", "Raramente", "Fim de semana", "Diário"], key="ck_alc")
            with col2:
                ck_sono_h = st.selectbox("Horas de sono:", ["Menos de 5h", "5-6h", "7-8h", "9h+"], key="ck_sono_h")
                ck_fuma = st.selectbox("Tabaco:", ["Não fumo", "Ex-fumante", "Fumante"], key="ck_fuma")

            st.markdown("#### 4. Histórico")
            ck_familia = st.text_area("Doenças na família:", height=60, key="ck_familia",
                placeholder="Ex: pai com diabetes, mãe com hipertensão, avô com infarto...")
            ck_ultima_consulta = st.selectbox("Última consulta médica:", ["Há menos de 6 meses", "6-12 meses", "1-2 anos", "Mais de 3 anos", "Nunca fui"], key="ck_ultima")

            enviado = st.form_submit_button("📊 GERAR MEU CHECK-UP COMPLETO", use_container_width=True)

        if enviado:
            resumo_checkup = f"""
Paciente: {ck_idade} anos, {ck_sexo}, {ck_peso_alt}
Sintomas: {', '.join(ck_sint) if ck_sint else 'Nenhum'}
Exercício: {ck_exercicio} | Sono: {ck_sono_h} | Álcool: {ck_alcool} | Tabaco: {ck_fuma}
Histórico familiar: {ck_familia}
Última consulta: {ck_ultima_consulta}
Por favor, faça uma avaliação educativa completa do meu estado de saúde com base nesses dados, identificando áreas de atenção, hábitos positivos e recomendações preventivas prioritárias.
"""
            with st.spinner("Dra. Sofia está analisando seu check-up..."):
                try:
                    resposta_ck = chamar_ia([], resumo_checkup, ctx)
                    st.session_state["res_checkup_final"] = resposta_ck
                    st.session_state.historico_saude_preventiva.append({
                        "data": datetime.now().strftime("%d/%m %H:%M"),
                        "aba": "Check-up Digital",
                        "resumo": f"Check-up completo — {ck_idade} anos",
                        "conteudo": resposta_ck
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        if st.session_state.get("res_checkup_final"):
            st.markdown("### 📋 Seu Check-up Digital")
            st.markdown(f"<div class='card'>{st.session_state['res_checkup_final']}</div>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("**💬 Tem dúvidas sobre o resultado?**")
            render_chat("hist_checkup", "inp_check_followup", "btn_check_followup",
                contexto_extra=ctx + "\n\nResultado do check-up:\n" + st.session_state.get("res_checkup_final", ""),
                placeholder="Pergunte sobre seu check-up...")

    # ═══════════════════════════════════════════════════
    # 📓 DIÁRIO DE SAÚDE
    # ═══════════════════════════════════════════════════
    with _tab_diario:
        st.header("📓 Diário de Saúde")
        st.markdown("<div class='card-green'>📅 Registre como você está se sentindo diariamente. A IA analisa seus registros e identifica padrões.</div>", unsafe_allow_html=True)

        with st.form("form_diario"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: d_humor = st.slider("😊 Humor (1-10):", 1, 10, 7, key="d_humor")
            with col2: d_energia = st.slider("⚡ Energia (1-10):", 1, 10, 7, key="d_energia")
            with col3: d_sono = st.slider("😴 Sono (1-10):", 1, 10, 7, key="d_sono")
            with col4: d_dor = st.slider("🩹 Dor (0=sem dor):", 0, 10, 0, key="d_dor")

            d_atividade = st.selectbox("🏃 Atividade física hoje:", ["Nenhuma", "Caminhada leve", "Exercício moderado", "Exercício intenso"], key="d_ativ")
            d_agua = st.selectbox("💧 Água ingerida:", ["Menos de 1L", "1-1,5L", "1,5-2L", "Mais de 2L"], key="d_agua")
            d_obs = st.text_area("📝 Observações do dia:", height=80, key="d_obs_diario",
                placeholder="Como foi seu dia de saúde? Sintomas, conquistas, dificuldades...")

            salvar_dia = st.form_submit_button("💾 REGISTRAR DIA + ANÁLISE DA IA", use_container_width=True)

        if salvar_dia:
            diarios = st.session_state.get("registros_diario", [])
            novo = {
                "data": datetime.now().strftime("%d/%m/%Y"),
                "humor": d_humor, "energia": d_energia,
                "sono": d_sono, "dor": d_dor,
                "atividade": d_atividade, "agua": d_agua,
                "obs": d_obs
            }
            diarios.append(novo)
            st.session_state.registros_diario = diarios

            msg_diario = f"Hoje ({novo['data']}): Humor {d_humor}/10, Energia {d_energia}/10, Sono {d_sono}/10, Dor {d_dor}/10. Atividade: {d_atividade}. Água: {d_agua}. {d_obs if d_obs else ''}\nO que observa sobre meu dia? Tem alguma dica ou alerta?"
            with st.spinner("Analisando seu dia..."):
                try:
                    resp_diario = chamar_ia(st.session_state.get("hist_diario", []), msg_diario, ctx)
                    hist_d = st.session_state.get("hist_diario", [])
                    hist_d.append({"role": "user", "content": msg_diario})
                    hist_d.append({"role": "assistant", "content": resp_diario})
                    st.session_state.hist_diario = hist_d
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        # Histórico de registros
        registros = st.session_state.get("registros_diario", [])
        if registros:
            st.markdown("### 📊 Seus últimos registros")
            for r in reversed(registros[-5:]):
                st.markdown(f"<div class='guia-box'><b>{r['data']}</b> — 😊{r['humor']} ⚡{r['energia']} 😴{r['sono']} 🩹{r['dor']} | {r['atividade']} | {r['agua']}{' | ' + r['obs'] if r.get('obs') else ''}</div>", unsafe_allow_html=True)

        if st.session_state.get("hist_diario"):
            st.markdown("---")
            render_chat("hist_diario", "inp_diario_extra", "btn_diario_extra",
                contexto_extra=ctx,
                placeholder="Pergunte sobre seus registros ou o que melhorar...")

    # ═══════════════════════════════════════════════════
    # 📈 EVOLUÇÃO
    # ═══════════════════════════════════════════════════
    with _tab_evolucao:
        st.header("📈 Evolução e Progresso")

        qtd_total = len(st.session_state.historico_saude_preventiva)
        registros_d = st.session_state.get("registros_diario", [])

        if qtd_total == 0 and not registros_d:
            st.markdown("<div class='card-yellow'>📊 Você ainda não tem dados suficientes. Use os outros módulos e volte aqui para ver sua evolução.</div>", unsafe_allow_html=True)
        else:
            col1, col2, col3 = st.columns(3)
            with col1: st.markdown(f"<div class='stat-box'><div style='font-size:1.6em;'>💬</div><div style='font-size:1.8em;font-weight:700;color:#DC2626;'>{qtd_total}</div><div style='font-size:0.75em;'>Consultas</div></div>", unsafe_allow_html=True)
            with col2: st.markdown(f"<div class='stat-box'><div style='font-size:1.6em;'>📓</div><div style='font-size:1.8em;font-weight:700;color:#DC2626;'>{len(registros_d)}</div><div style='font-size:0.75em;'>Dias no diário</div></div>", unsafe_allow_html=True)
            with col3:
                med_humor = round(sum(r['humor'] for r in registros_d) / len(registros_d), 1) if registros_d else "-"
                st.markdown(f"<div class='stat-box'><div style='font-size:1.6em;'>😊</div><div style='font-size:1.8em;font-weight:700;color:#DC2626;'>{med_humor}</div><div style='font-size:0.75em;'>Humor médio</div></div>", unsafe_allow_html=True)

            if st.session_state.historico_saude_preventiva:
                st.markdown("### 📋 Histórico de consultas")
                for item in reversed(st.session_state.historico_saude_preventiva[-10:]):
                    st.markdown(f"<div class='hist-item' style='background:#fff;border-radius:10px;padding:12px 16px;margin-bottom:8px;border-left:4px solid #FECACA;'><span class='badge-verde' style='background:#059669;color:white;padding:3px 8px;border-radius:8px;font-size:0.75em;'>{item['data']}</span> <b>{item['aba']}</b><br><span style='color:#64748B;font-size:0.85em;'>{item['resumo']}</span></div>", unsafe_allow_html=True)

        render_chat("hist_evolucao", "inp_evolucao", "btn_evolucao",
            sugestoes=["Analise meu progresso geral", "O que devo priorizar para melhorar minha saúde?", "Quais mudanças de hábito têm mais impacto?"],
            contexto_extra=ctx + (f"\nRegistros no diário: {len(registros_d)}" if registros_d else "") + (f"\nConsultas realizadas: {qtd_total}" if qtd_total else ""),
            placeholder="Pergunte sobre sua evolução e próximos passos...")

# ── RODAPÉ ──
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Saúde Preventiva IA · MeusAgentesIA.com.br</div>", unsafe_allow_html=True)
