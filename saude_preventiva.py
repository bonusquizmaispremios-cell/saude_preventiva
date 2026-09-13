import streamlit as st
from groq import Groq
from datetime import datetime
import json

st.set_page_config(page_title="Saúde Preventiva IA", page_icon="💊", layout="wide")

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
    .card-red { background:linear-gradient(135deg,#FFF5F5,#FEE2E2); padding:20px; border-radius:14px; border:1px solid #FECACA; margin-bottom:14px; }
    .stApp .card-red, .stApp .card-red p, .stApp .card-red div { color:#7F1D1D !important; }
    .card-green { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); padding:20px; border-radius:14px; border:1px solid #86EFAC; margin-bottom:14px; }
    .stApp .card-green, .stApp .card-green p, .stApp .card-green div { color:#14532D !important; }
    .card-yellow { background:linear-gradient(135deg,#FFFBEB,#FEF3C7); padding:18px; border-radius:12px; border:1px solid #FCD34D; margin-bottom:12px; }
    .stApp .card-yellow, .stApp .card-yellow p, .stApp .card-yellow div { color:#78350F !important; }
    .badge { background:#DC2626; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-verde { background:#059669; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-amarelo { background:#B45309; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-roxo { background:#6D28D9; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .divider { border:none; height:1px; background:linear-gradient(to right,transparent,#FECACA,transparent); margin:18px 0; }
    .hist-item { background:#FFFFFF; border-radius:10px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #FECACA; }
    .stApp .hist-item, .stApp .hist-item p, .stApp .hist-item span, .stApp .hist-item div { color:#7F1D1D !important; }
    .stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #FECACA; }
    .stApp .stat-box div, .stApp .stat-box span { color:#7F1D1D !important; }
    .chat-user { background:#FFFFFF; border:1px solid #FECACA; border-radius:12px 12px 4px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-user, .stApp .chat-user p, .stApp .chat-user div { color:#7F1D1D !important; }
    .chat-persona { background:#FEE2E2; border:1px solid #FECACA; border-radius:4px 12px 12px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-persona, .stApp .chat-persona p, .stApp .chat-persona div { color:#7F1D1D !important; }

    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = "Você é um educador em saúde preventiva. NUNCA faz diagnósticos médicos nem prescreve medicamentos. Orienta sobre exames preventivos recomendados por faixa etária, hábitos saudáveis e sinais de alerta para procurar um médico. Sempre recomenda consultar um profissional de saúde. Português do Brasil."

@st.cache_resource
def get_cache_saude_prev():
    return {"perfis": {}}

_cache = get_cache_saude_prev()

CHAVES_SALVAR = ["usuario","historico_saude_preventiva"]

def gerar_json():
    return json.dumps({k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k not in ("api_key",)}, ensure_ascii=False, indent=2, default=str)

def carregar_json_sessao(dados):
    _bloq = {'api_key','etapa','nome_login','chave_login','upload_login','btn_entrar_login'}
    _pref = (
        'btn_','sel_','ul_','dl_','cad_','_sub','_sm','_tab','_bsc',
        'ativo_','rem_','sel_pet_','ev_','prof_','hig_','prev_',
        'vac_','sint_','comp_','trad_','subs_','amb_','viag_','chat_',
        'duvida_','emerg_','peso_','data_','obs_','tipo_','vet_','desc_',
        'local_','prox_','alim','sit_emerg_','tc_','oraf','siau','agmag',
        'lv','mv','pt','pi','sh','wc','rv','rp','rc',
    )
    import re as _re
    for k, v in dados.items():
        if k in _bloq: continue
        if any(k.startswith(p) for p in _pref): continue
        if _re.match(r'.+_\d+$', k): continue
        st.session_state[k] = v

def salvar_perfil_cache(usuario):
    _cache["perfis"][usuario] = {k: st.session_state.get(k) for k in CHAVES_SALVAR}

def perfis_salvos():
    return [p for p in _cache["perfis"].keys() if len(p.strip()) >= 2]

def carregar_perfil_cache(usuario):
    return _cache["perfis"].get(usuario)

defaults = {
    "etapa": "Login", "usuario": "", "api_key": "",
    "historico_saude_preventiva": [],
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 💊 Saúde Preventiva IA")
    st.markdown("<div class=\'card\'><b>🔒 ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</b><br>🔗 <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** Pela complexidade dos agentes, no computador a experiência é mais agradável.")
    with st.container():
        nome  = st.text_input("Seu Nome:", key="nome_login")
        chave = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_login")
        arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
        dados_login = json.load(arq_j) if arq_j else None
        if st.button("✨ ENTRAR", key="btn_entrar_login"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 caracteres.")
            elif chave.strip():
                st.session_state.usuario = nome.strip()
                st.session_state.api_key = chave
                if dados_login: carregar_json_sessao(dados_login)
                st.session_state.etapa = "App"
                st.rerun()
            else:
                st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":
    historico = st.session_state.get("historico_saude_preventiva", [])
    salvar_perfil_cache(st.session_state.usuario)

    _tab_home_sp, _tab_perfil_sp, _tab_sintomas, _tab_exames, _tab_riscos, _tab_suplementos, _tab_alimentacao_sp, _tab_saude_mental_sp, _tab_checkup, _tab_diario_sp, _tab_evolucao_sp = st.tabs(['🏠 Home', '👤 Meu Perfil de Saúde', '🔍 Análise de Sintomas', '🧪 Exames Preventivos', '🏃 Hábitos de Risco', '💊 Suplementação', '🥗 Alimentação Saudável', '🧘 Saúde Mental', '📊 Check-up Digital', '📓 Diário de Saúde', '📈 Evolução'])

    # ── BARRA SALVAR — aparece em todas as abas ──
    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        _bsc1, _bsc2 = st.columns(2)
        with _bsc1:
            import json as _jsv
            _dsv = {k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith('_') and k not in ('api_key',)}
            st.download_button("💾 Baixar meus dados (.json)",
                data=_jsv.dumps(_dsv, ensure_ascii=False, indent=2, default=str),
                file_name=f"dados_{st.session_state.get('usuario','user')}.json",
                mime="application/json", key="dl_barra_sv_saudepre")
        with _bsc2:
            _fupsv = st.file_uploader("📂 Carregar dados salvos:", type=["json"], key="ul_barra_sv_saudepre", label_visibility="collapsed")
            if _fupsv:
                try:
                    import json as _jld
                    for _k2,_v2 in _jld.loads(_fupsv.read().decode()).items():
                        if _k2 not in ('api_key','etapa'): st.session_state[_k2] = _v2
                    st.success("✅ Dados restaurados!"); st.rerun()
                except: st.error("Arquivo inválido.")


    with _tab_home_sp:
        st.title(f"💊 Olá, {st.session_state.usuario}!")
        st.markdown(f"*Cuide da sua saúde antes que ela precise de cuidados.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"### Bem-vindo ao **Saúde Preventiva IA**")
        st.markdown(f"<div class='card'>Use as abas acima para navegar entre as funcionalidades. Cada aba oferece uma ferramenta diferente com IA.</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🏠</div><div style='font-size:0.8em;'>Saúde Preventiva IA</div></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🤖</div><div style='font-size:0.8em;'>Powered by IA</div></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>💾</div><div style='font-size:0.8em;'>Salve seus dados</div></div>", unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_sv, _ = st.columns([1,3])
        with col_sv:
            st.download_button("💾 Salvar dados (.json)", data=json.dumps({k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k not in ("api_key",)}, ensure_ascii=False, indent=2, default=str), file_name=f"saude_preventiva_{st.session_state.usuario}.json", mime="application/json", key="dl_saude__1")

    with _tab_perfil_sp:
        st.header("👤 Meu Perfil de Saúde")
        prompt_perfil_sp = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_perfil_sp", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_perfil_sp", use_container_width=True):
            if prompt_perfil_sp.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_perfil_sp}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_perfil_sp = resp.choices[0].message.content
                        if resultado_perfil_sp: st.session_state['res_perfil_sp_saudep1'] = str(resultado_perfil_sp)
                        st.session_state["res_perfil_sp"] = resultado_perfil_sp
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Meu Perfil de Saúde","resumo":prompt_perfil_sp[:60],"conteudo":resultado_perfil_sp})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_perfil_sp"):
            st.markdown(f"<div class='card'>{st.session_state['res_perfil_sp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_perfil_sp"], file_name="perfil_sp_resultado.txt", mime="text/plain", key="dl_perfil_sp")

    with _tab_sintomas:
        st.header("🔍 Análise de Sintomas")
        prompt_sintomas = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_sintomas", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_sintomas", use_container_width=True):
            if prompt_sintomas.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_sintomas}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_sintomas = resp.choices[0].message.content
                        if resultado_sintomas: st.session_state['res_sintomas_saudep2'] = str(resultado_sintomas)
                        st.session_state["res_sintomas"] = resultado_sintomas
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Análise de Sintomas","resumo":prompt_sintomas[:60],"conteudo":resultado_sintomas})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_sintomas"):
            st.markdown(f"<div class='card'>{st.session_state['res_sintomas']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_sintomas"], file_name="sintomas_resultado.txt", mime="text/plain", key="dl_sintomas")

    with _tab_exames:
        st.header("🧪 Exames Preventivos")
        prompt_exames = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_exames", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_exames", use_container_width=True):
            if prompt_exames.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_exames}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_exames = resp.choices[0].message.content
                        if resultado_exames: st.session_state['res_exames_saudep3'] = str(resultado_exames)
                        st.session_state["res_exames"] = resultado_exames
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Exames Preventivos","resumo":prompt_exames[:60],"conteudo":resultado_exames})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_exames"):
            st.markdown(f"<div class='card'>{st.session_state['res_exames']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_exames"], file_name="exames_resultado.txt", mime="text/plain", key="dl_exames")

    with _tab_riscos:
        st.header("🏃 Hábitos de Risco")
        prompt_riscos = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_riscos", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_riscos", use_container_width=True):
            if prompt_riscos.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_riscos}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_riscos = resp.choices[0].message.content
                        if resultado_riscos: st.session_state['res_riscos_saudep4'] = str(resultado_riscos)
                        st.session_state["res_riscos"] = resultado_riscos
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Hábitos de Risco","resumo":prompt_riscos[:60],"conteudo":resultado_riscos})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_riscos"):
            st.markdown(f"<div class='card'>{st.session_state['res_riscos']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_riscos"], file_name="riscos_resultado.txt", mime="text/plain", key="dl_riscos")

    with _tab_suplementos:
        st.header("💊 Suplementação")
        prompt_suplementos = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_suplementos", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_suplementos", use_container_width=True):
            if prompt_suplementos.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_suplementos}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_suplementos = resp.choices[0].message.content
                        if resultado_suplementos: st.session_state['res_suplementos_saudep5'] = str(resultado_suplementos)
                        st.session_state["res_suplementos"] = resultado_suplementos
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Suplementação","resumo":prompt_suplementos[:60],"conteudo":resultado_suplementos})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_suplementos"):
            st.markdown(f"<div class='card'>{st.session_state['res_suplementos']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_suplementos"], file_name="suplementos_resultado.txt", mime="text/plain", key="dl_suplementos")

    with _tab_alimentacao_sp:
        st.header("🥗 Alimentação Saudável")
        prompt_alimentacao_sp = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_alimentacao_sp", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_alimentacao_sp", use_container_width=True):
            if prompt_alimentacao_sp.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_alimentacao_sp}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_alimentacao_sp = resp.choices[0].message.content
                        if resultado_alimentacao_sp: st.session_state['res_alimentacao__saudep6'] = str(resultado_alimentacao_sp)
                        st.session_state["res_alimentacao_sp"] = resultado_alimentacao_sp
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Alimentação Saudável","resumo":prompt_alimentacao_sp[:60],"conteudo":resultado_alimentacao_sp})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_alimentacao_sp"):
            st.markdown(f"<div class='card'>{st.session_state['res_alimentacao_sp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_alimentacao_sp"], file_name="alimentacao_sp_resultado.txt", mime="text/plain", key="dl_alimentacao_sp")

    with _tab_saude_mental_sp:
        st.header("🧘 Saúde Mental")
        prompt_saude_mental_sp = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_saude_mental_sp", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_saude_mental_sp", use_container_width=True):
            if prompt_saude_mental_sp.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_saude_mental_sp}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_saude_mental_sp = resp.choices[0].message.content
                        if resultado_saude_mental_sp: st.session_state['res_saude_mental_saudep7'] = str(resultado_saude_mental_sp)
                        st.session_state["res_saude_mental_sp"] = resultado_saude_mental_sp
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Saúde Mental","resumo":prompt_saude_mental_sp[:60],"conteudo":resultado_saude_mental_sp})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_saude_mental_sp"):
            st.markdown(f"<div class='card'>{st.session_state['res_saude_mental_sp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_saude_mental_sp"], file_name="saude_mental_sp_resultado.txt", mime="text/plain", key="dl_saude_mental_sp")

    with _tab_checkup:
        st.header("📊 Check-up Digital")
        prompt_checkup = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_checkup", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_checkup", use_container_width=True):
            if prompt_checkup.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_checkup}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_checkup = resp.choices[0].message.content
                        if resultado_checkup: st.session_state['res_checkup_saudep8'] = str(resultado_checkup)
                        st.session_state["res_checkup"] = resultado_checkup
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Check-up Digital","resumo":prompt_checkup[:60],"conteudo":resultado_checkup})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_checkup"):
            st.markdown(f"<div class='card'>{st.session_state['res_checkup']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_checkup"], file_name="checkup_resultado.txt", mime="text/plain", key="dl_checkup")

    with _tab_diario_sp:
        st.header("📓 Diário de Saúde")
        prompt_diario_sp = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_diario_sp", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_diario_sp", use_container_width=True):
            if prompt_diario_sp.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_diario_sp}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_diario_sp = resp.choices[0].message.content
                        if resultado_diario_sp: st.session_state['res_diario_sp_saudep9'] = str(resultado_diario_sp)
                        st.session_state["res_diario_sp"] = resultado_diario_sp
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Diário de Saúde","resumo":prompt_diario_sp[:60],"conteudo":resultado_diario_sp})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_diario_sp"):
            st.markdown(f"<div class='card'>{st.session_state['res_diario_sp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_diario_sp"], file_name="diario_sp_resultado.txt", mime="text/plain", key="dl_diario_sp")

    with _tab_evolucao_sp:
        st.header("📈 Evolução")
        prompt_evolucao_sp = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_evolucao_sp", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_evolucao_sp", use_container_width=True):
            if prompt_evolucao_sp.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_evolucao_sp}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_evolucao_sp = resp.choices[0].message.content
                        if resultado_evolucao_sp: st.session_state['res_evolucao_sp_saudep10'] = str(resultado_evolucao_sp)
                        st.session_state["res_evolucao_sp"] = resultado_evolucao_sp
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Evolução","resumo":prompt_evolucao_sp[:60],"conteudo":resultado_evolucao_sp})
                        st.session_state.historico_saude_preventiva = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_evolucao_sp"):
            st.markdown(f"<div class='card'>{st.session_state['res_evolucao_sp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_evolucao_sp"], file_name="evolucao_sp_resultado.txt", mime="text/plain", key="dl_evolucao_sp")


# --- RODAPÉ ---
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Saúde Preventiva IA · Quiz Com Prêmios</div>", unsafe_allow_html=True)
