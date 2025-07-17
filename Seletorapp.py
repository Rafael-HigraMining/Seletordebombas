import streamlit as st
import pandas as pd
import numpy as np
import re
from urllib.parse import quote
import base64
from pathlib import Path

# ===================================================================
# FUNÇÃO AUXILIAR PARA IMAGENS
# ===================================================================
# Esta função garante que as imagens sejam carregadas de forma segura.
@st.cache_data
def image_to_base64(img_path):
    """Converte um arquivo de imagem para string base64."""
    try:
        path = Path(img_path)
        with path.open("rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        # Retorna um pixel transparente se a imagem não for encontrada
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# ===================================================================
# 1. DICIONÁRIO DE TRADUÇÕES (IDÊNTICO AO SEU ORIGINAL)
# ===================================================================
ATIVAR_ORCAMENTO = False # Mude para False se quiser desativar

TRADUCOES = {
    'pt': {
        'page_title': "Seletor Higra Mining",
        'main_title': "Seletor de Bombas Hidráulicas Higra Mining",
        'welcome_message': "Bem-vindo! Entre com os dados do seu ponto de trabalho para encontrar a melhor solução.",
        'input_header': "Parâmetros de Entrada",
        'eletric_freq_title': "Frequência Elétrica",
        'freq_header': "Frequência",
        'flow_header': "**Vazão Desejada**",
        'pressure_header': "**Pressão Desejada**",
        'flow_value_label': "Valor da Vazão",
        'pressure_value_label': "Valor da Pressão",
        'flow_unit_label': "Unidade Vazão",
        'pressure_unit_label': "Unidade Pressão",
        'converted_values_info': "Valores convertidos para a busca: **Vazão: {vazao} m³/h** | **Pressão: {pressao} mca**",
        'search_button': "Buscar Melhor Opção",
        'spinner_text': "Calculando as melhores opções para {freq}...",
        'results_header': "Resultados da Busca",
        'solution_unique': "✅ Solução encontrada com **BOMBA ÚNICA**:",
        'solution_parallel': "⚠️ Nenhuma bomba única com bom rendimento. Alternativa: **DUAS BOMBAS EM PARALELO**:",
        'solution_parallel_info': "A vazão e potência abaixo são POR BOMBA. Vazão total = 2x.",
        'solution_series': "⚠️ Nenhuma opção única ou paralela. Alternativa: **DUAS BOMBAS EM SÉRIE**:",
        'solution_series_info': "A pressão abaixo é POR BOMBA. Pressão total = 2x.",
        'no_solution_error': "❌ Nenhuma bomba encontrada. Tente outros valores.",
        'quote_button_start': "Fazer Orçamento",
        'quote_options_header': "Passo 1: Selecione os Opcionais da Bomba",
        'quote_continue_button': "Continuar para o Próximo Passo",
        'quote_contact_header': "Passo 2: Seus Dados de Contato",
        'quote_form_name': "Seu Nome *",
        'quote_form_email': "Seu E-mail *",
        'quote_form_message': "Mensagem (opcional)",
        'quote_form_button': "Enviar Pedido de Orçamento",
        'quote_form_warning': "Por favor, preencha seu nome e e-mail.",
        'quote_form_success': "Pedido pronto para ser enviado!",
        'quote_form_click_here': "Clique aqui para abrir e enviar o e-mail",
        'quote_form_info': "Seu programa de e-mail padrão será aberto com todas as informações preenchidas.",
        'email_subject': "Pedido de Orçamento via Seletor de Bombas - {nome}",
        'email_body': """Olá,\n\nUm novo pedido de orçamento foi gerado através do Seletor de Bombas.\n\nDADOS DO CLIENTE:\n- Nome: {nome}\n- E-mail: {email}\n\nMENSAGEM:\n{mensagem}\n\n---------------------------------\nPARÂMETROS DA BUSCA:\n- Frequência: {freq}\n- Vazão: {vazao} m³/h\n- Pressão: {pressao} mca\n\n---------------------------------\nRESULTADOS ENCONTRADOS:\n{tabela_resultados}"""
    },
    'en': {
        'page_title': "Higra Mining Selector",
        'main_title': "Higra Mining Hydraulic Pump Selector",
        'welcome_message': "Welcome! Enter your duty point data to find the best solution.",
        'input_header': "Input Parameters",
        'eletric_freq_title': "Electrical Frequency",
        'freq_header': "Frequency",
        'flow_header': "**Desired Flow**",
        'pressure_header': "**Desired Head**",
        'flow_value_label': "Flow Value",
        'pressure_value_label': "Head Value",
        'flow_unit_label': "Flow Unit",
        'pressure_unit_label': "Head Unit",
        'converted_values_info': "Converted values for search: **Flow: {vazao} m³/h** | **Head: {pressao} mca**",
        'search_button': "Find Best Option",
        'spinner_text': "Calculating the best options for {freq}...",
        'results_header': "Search Results",
        'solution_unique': "✅ Solution found with a **SINGLE PUMP**:",
        'solution_parallel': "⚠️ No single pump with good efficiency. Alternative: **TWO PUMPS IN PARALLEL**:",
        'solution_parallel_info': "Flow and power below are PER PUMP. Total flow = 2x.",
        'solution_series': "⚠️ No single or parallel option. Alternative: **TWO PUMPS IN SERIES**:",
        'solution_series_info': "Head below is PER PUMP. Total head = 2x.",
        'no_solution_error': "❌ No pump found. Try other values.",
        'quote_button_start': "Request a Quote",
        'quote_options_header': "Step 1: Select Pump Options",
        'quote_continue_button': "Continue to Next Step",
        'quote_contact_header': "Step 2: Your Contact Information",
        'quote_form_name': "Your Name *",
        'quote_form_email': "Your Email *",
        'quote_form_message': "Message (optional)",
        'quote_form_button': "Send Quote Request",
        'quote_form_warning': "Please fill in your name and email.",
        'quote_form_success': "Request ready to be sent!",
        'quote_form_click_here': "Click here to open and send the email",
        'quote_form_info': "Your default email client will open with all the information pre-filled.",
        'email_subject': "Quote Request via Pump Selector - {nome}",
        'email_body': """Hello,\n\nA new quote request has been generated through the Pump Selector.\n\nCUSTOMER DATA:\n- Name: {nome}\n- Email: {email}\n\nMESSAGE:\n{mensagem}\n\n---------------------------------\nSEARCH PARAMETERS:\n- Frequency: {freq}\n- Flow: {vazao} m³/h\n- Head: {pressao} mca\n\n---------------------------------\nRESULTS FOUND:\n{tabela_resultados}"""
    },
    'es': {
        'page_title': "Selector Higra Mining",
        'main_title': "Selector de Bombas Hidráulicas Higra Mining",
        'welcome_message': "¡Bienvenido! Ingrese los datos de su punto de trabajo para encontrar la mejor solución.",
        'input_header': "Parámetros de Entrada",
        'eletric_freq_title': "Frecuencia Eléctrica",
        'freq_header': "Frecuencia",
        'flow_header': "**Caudal Deseado**",
        'pressure_header': "**Altura Deseada**",
        'flow_value_label': "Valor del Caudal",
        'pressure_value_label': "Valor de la Altura",
        'flow_unit_label': "Unidad Caudal",
        'pressure_unit_label': "Unidad Altura",
        'converted_values_info': "Valores convertidos para la búsqueda: **Caudal: {vazao} m³/h** | **Altura: {pressao} mca**",
        'search_button': "Buscar Mejor Opción",
        'spinner_text': "Calculando las mejores opciones para {freq}...",
        'results_header': "Resultados de la Búsqueda",
        'solution_unique': "✅ Solución encontrada con **BOMBA ÚNICA**:",
        'solution_parallel': "⚠️ Ninguna bomba única con buen rendimiento. Alternativa: **DOS BOMBAS EN PARALELO**:",
        'solution_parallel_info': "El caudal y la potencia a continuación son POR BOMBA. Caudal total = 2x.",
        'solution_series': "⚠️ Ninguna opción única o en paralelo. Alternativa: **DOS BOMBAS EN SERIE**:",
        'solution_series_info': "La altura a continuación es POR BOMBA. Altura total = 2x.",
        'no_solution_error': "❌ No se encontró ninguna bomba. Pruebe con otros valores.",
        'quote_button_start': "Solicitar Cotización",
        'quote_options_header': "Paso 1: Seleccione Opcionales de la Bomba",
        'quote_continue_button': "Continuar al Siguiente Paso",
        'quote_contact_header': "Paso 2: Sus Datos de Contacto",
        'quote_form_name': "Su Nombre *",
        'quote_form_email': "Su Correo Electrónico *",
        'quote_form_message': "Mensaje (opcional)",
        'quote_form_button': "Enviar Solicitud de Cotización",
        'quote_form_warning': "Por favor, complete su nombre y correo electrónico.",
        'quote_form_success': "¡Solicitud lista para ser enviada!",
        'quote_form_click_here': "Haga clic aquí para abrir y enviar el correo",
        'quote_form_info': "Su cliente de correo electrónico predeterminado se abrirá con toda la información completada.",
        'email_subject': "Solicitud de Cotización vía Selector de Bombas - {nome}",
        'email_body': """Hola,\n\nSe ha generado una nueva solicitud de cotización a través del Selector de Bombas.\n\nDATOS DEL CLIENTE:\n- Nombre: {nome}\n- Correo Electrónico: {email}\n\nMENSAJE:\n{mensagem}\n\n---------------------------------\nPARÁMETROS DE BÚSQUEDA:\n- Frecuencia: {freq}\n- Caudal: {vazao} m³/h\n- Altura: {pressao} mca\n\n---------------------------------\nRESULTADOS ENCONTRADOS:\n{tabela_resultados}"""
    }
}

# ===================================================================
# FUNÇÕES GLOBAIS E CONSTANTES (IDÊNTICAS AO SEU ORIGINAL)
# ===================================================================
MOTORES_PADRAO = np.array([
    15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 175, 200, 250, 300,
    350, 400, 450, 500, 550, 600
])

def encontrar_motor_final(potencia_real):
    if pd.isna(potencia_real): return np.nan
    candidatos = MOTORES_PADRAO[MOTORES_PADRAO >= potencia_real]
    return candidatos.min() if len(candidatos) > 0 else np.nan

@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
    try:
        df = pd.read_excel(caminho_arquivo)
        df.columns = df.columns.str.strip().str.upper()
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o Excel: {e}")
        return None
    df["MOTOR PADRÃO (CV)"] = df["POTÊNCIA (HP)"].apply(encontrar_motor_final)
    def extrair_rotor_num(rotor_str):
        match = re.match(r"(\d+)(?:\s*\((\d+)°\))?", str(rotor_str))
        if match:
            base = int(match.group(1)); grau = int(match.group(2)) if match.group(2) else 0
            return base + grau / 100
        return np.nan
    df["ROTORNUM"] = df["ROTOR"].apply(extrair_rotor_num)
    df["ROTOR_MIN_MODELO"] = df.groupby("MODELO")["ROTORNUM"].transform("min")
    df["ROTOR_MAX_MODELO"] = df.groupby("MODELO")["ROTORNUM"].transform("max")
    df["PRESSAO_MAX_MODELO"] = df.groupby("MODELO")["PRESSÃO (MCA)"].transform("max")
    df['POTENCIA_MAX_FAMILIA'] = df.groupby('MODELO')['POTÊNCIA (HP)'].transform('max')
    intervalos_vazao = df.groupby(["MODELO", "ROTOR"])["VAZÃO (M³/H)"].agg(["min", "max"]).reset_index()
    df = pd.merge(df, intervalos_vazao, on=["MODELO", "ROTOR"], how="left", suffixes=("", "_range"))
    df["VAZAO_CENTRO"] = (df["min"] + df["max"]) / 2
    df["ERRO_RELATIVO"] = ((df["VAZÃO (M³/H)"] - df["VAZAO_CENTRO"]) / (df["max"] - df["min"] + 1e-9)) * 100
    df["ABS_ERRO_RELATIVO"] = df["ERRO_RELATIVO"].abs()
    return df

def filtrar_e_classificar(df, vazao, pressao, top_n=5, fator_limitador=0.025, limite_desempate_rendimento=3):
    if df is None: return pd.DataFrame()
    cond_max = df['ROTORNUM'] == df['ROTOR_MAX_MODELO']
    cond_min = df['ROTORNUM'] == df['ROTOR_MIN_MODELO']
    df['margem_cima'] = np.select([cond_max, cond_min], [df['PRESSAO_MAX_MODELO'] * 0.03, df['PRESSAO_MAX_MODELO'] * 0.1], default=df['PRESSAO_MAX_MODELO'] * 0.1)
    df['margem_baixo'] = np.select([cond_max, cond_min], [df['PRESSAO_MAX_MODELO'] * 0.1, df['PRESSAO_MAX_MODELO'] * 0.03], default=df['PRESSAO_MAX_MODELO'] * 0.1)
    pressao_min_aceita = pressao - df['margem_baixo']
    pressao_max_aceita = pressao + df['margem_cima']
    df_filtrado = df[(df["VAZÃO (M³/H)"] == vazao) & (df["PRESSÃO (MCA)"] >= pressao_min_aceita) & (df["PRESSÃO (MCA)"] <= pressao_max_aceita)].copy()
    if not df_filtrado.empty:
        df_filtrado = df_filtrado[~((df_filtrado['ROTORNUM'] == df_filtrado['ROTOR_MIN_MODELO']) & (pressao < df_filtrado["PRESSÃO (MCA)"] - df_filtrado['PRESSAO_MAX_MODELO'] * 0.03)) & ~((df_filtrado['ROTORNUM'] == df_filtrado['ROTOR_MAX_MODELO']) & (pressao > df_filtrado["PRESSÃO (MCA)"] + df_filtrado['PRESSAO_MAX_MODELO'] * 0.03))]
    if df_filtrado.empty: return pd.DataFrame()
    df_filtrado["ERRO_PRESSAO"] = df_filtrado["PRESSÃO (MCA)"] - pressao
    if pressao > 0:
        df_filtrado["PERC_ERRO_PRESSAO"] = df_filtrado["ERRO_PRESSAO"] / pressao
    else:
        df_filtrado["PERC_ERRO_PRESSAO"] = 0
    ajuste_bruto = df_filtrado["POTÊNCIA (HP)"] * df_filtrado["PERC_ERRO_PRESSAO"]
    limite_seguranca = df_filtrado['POTENCIA_MAX_FAMILIA'] * fator_limitador
    ajuste_final = np.clip(ajuste_bruto, -limite_seguranca, limite_seguranca)
    df_filtrado["POTÊNCIA CORRIGIDA (HP)"] = df_filtrado["POTÊNCIA (HP)"] - ajuste_final
    df_filtrado["MOTOR FINAL (CV)"] = df_filtrado["POTÊNCIA CORRIGIDA (HP)"].apply(encontrar_motor_final)
    df_filtrado["ERRO_PRESSAO_ABS"] = df_filtrado["ERRO_PRESSAO"].abs()
    df_filtrado = df_filtrado.sort_values(by=["MOTOR FINAL (CV)", "RENDIMENTO (%)"], ascending=[True, False])
    df_filtrado['DIFF_CONSECUTIVO'] = df_filtrado.groupby('MOTOR FINAL (CV)')['RENDIMENTO (%)'].diff(-1).abs()
    df_filtrado['CHAVE_DESEMPATE'] = np.where(df_filtrado['DIFF_CONSECUTIVO'].fillna(np.inf) <= limite_desempate_rendimento, df_filtrado['ABS_ERRO_RELATIVO'], np.inf)
    df_resultado = df_filtrado.sort_values(
        by=["MOTOR FINAL (CV)", "CHAVE_DESEMPATE", "RENDIMENTO (%)", "POTÊNCIA CORRIGIDA (HP)"],
        ascending=[True, True, False, True]
    )
    colunas_finais = ['MODELO', 'ROTOR', 'VAZÃO (M³/H)', 'PRESSÃO (MCA)', 'ERRO_PRESSAO', 'ERRO_RELATIVO', 'RENDIMENTO (%)', 'POTÊNCIA (HP)', 'POTÊNCIA CORRIGIDA (HP)', 'MOTOR FINAL (CV)']
    return df_resultado[colunas_finais].head(top_n)

def selecionar_bombas(df, vazao_desejada, pressao_desejada, top_n=5):
    resultado_unico = filtrar_e_classificar(df, vazao_desejada, pressao_desejada, top_n)
    if not resultado_unico.empty and resultado_unico.iloc[0]["RENDIMENTO (%)"] > 50:
        return resultado_unico, "unica"
    resultado_paralelo = filtrar_e_classificar(df, vazao_desejada / 2, pressao_desejada, top_n)
    if not resultado_paralelo.empty:
        return resultado_paralelo, "paralelo"
    resultado_serie = filtrar_e_classificar(df, vazao_desejada, pressao_desejada / 2, top_n)
    if not resultado_serie.empty:
        return resultado_serie, "serie"
    return pd.DataFrame(), "nenhuma"

# ===================================================================
# INTERFACE STREAMLIT (VERSÃO ESTÁVEL COM NOVO DESIGN)
# ===================================================================

# --- CONFIGURAÇÕES INICIAIS ---
if 'lang' not in st.session_state: st.session_state.lang = 'pt'
if 'resultado_busca' not in st.session_state: st.session_state.resultado_busca = None
if 'mailto_link' not in st.session_state: st.session_state.mailto_link = None
if 'iniciar_orcamento' not in st.session_state: st.session_state.iniciar_orcamento = False
if 'opcionais_selecionados' not in st.session_state: st.session_state.opcionais_selecionados = None

st.set_page_config(layout="wide", page_title=TRADUCOES[st.session_state.lang]['page_title'])

# --- ESTILOS CSS APRIMORADOS ---
COR_PRIMARIA = "#134883"
COR_SECUNDARIA = "#F8AC2E"
COR_FUNDO = "#F0F5FF"
COR_TEXTO = "#333333"

st.markdown(f"""
<style>
    /* Configurações gerais */
    .stApp {{
        background-color: {COR_FUNDO};
        color: {COR_TEXTO};
    }}
    
    /* Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {{
        color: {COR_PRIMARIA};
    }}
    
    /* Botões Principais (CORRIGIDO) */
    .stButton>button {{
        border: 2px solid {COR_PRIMARIA} !important;
        background-color: {COR_PRIMARIA} !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }}
    .stButton>button:hover {{
        background-color: white !important;
        color: {COR_PRIMARIA} !important;
    }}
    
    /* Alertas */
    .stAlert > div {{ border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); padding: 15px 20px; }}
    .stAlert-success {{ background-color: #e0f2f1; color: {COR_PRIMARIA}; border-left: 5px solid #2ECC71; }}
    .stAlert-warning {{ background-color: #fff8e1; color: #c08b2c; border-left: 5px solid {COR_SECUNDARIA}; }}
    .stAlert-info {{ background-color: #e3f2fd; color: {COR_PRIMARIA}; border-left: 5px solid {COR_PRIMARIA}; }}
    .stAlert-error {{ background-color: #ffebee; color: #b71c1c; border-left: 5px solid #E74C3C; }}

    /* Container de bandeiras */
    .bandeira-container {{ cursor: pointer; transition: all 0.2s ease-in-out; border-radius: 8px; padding: 5px; margin-top: 10px; border: 2px solid transparent; }}
    .bandeira-container:hover {{ transform: scale(1.1); background-color: rgba(19, 72, 131, 0.1); }}
    .bandeira-container.selecionada {{ border: 2px solid {COR_SECUNDARIA}; box-shadow: 0 0 10px rgba(248, 172, 46, 0.5); }}
    .bandeira-img {{ width: 45px; height: 30px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}

    /* Dataframe estilizado */
    .stDataFrame {{ border: 1px solid #d0d7de; border-radius: 8px; }}

    /* Botões de Rádio da Frequência (NOVO) */
    div[data-baseweb="radio"] label > div:first-child {{
        background-color: {COR_SECUNDARIA} !important; /* Cor Amarela */
        border: 2px solid {COR_SECUNDARIA} !important;
</style>
""", unsafe_allow_html=True)


# ===================================================================
# CABEÇALHO COM LOGO E SELEÇÃO DE IDIOMA
# ===================================================================

# Mapeamento das bandeiras para idiomas
bandeiras = {
    "pt": {"nome": "PT", "img": "brasil.png"},
    "en": {"nome": "EN", "img": "uk.png"},
    "es": {"nome": "ES", "img": "espanha.png"}
}

col_logo, col_vazia, col_bandeiras = st.columns([4, 4, 2])

with col_logo:
    try:
        st.image("logo.png", width=500)
    except Exception:
        st.warning("Logo não encontrada.")

with col_bandeiras:
    # Cria colunas para cada bandeira ficarem lado a lado
    flag_cols = st.columns(len(bandeiras))
    for i, (lang_code, info) in enumerate(bandeiras.items()):
        with flag_cols[i]:
            # Lógica do botão invisível sobre a imagem
            if st.button(label=info['nome'], key=f"btn_lang_{lang_code}"):
                st.session_state.lang = lang_code
                st.rerun()
            
            # Adiciona efeito visual para a bandeira selecionada usando o container de markdown
            classe_css = "selecionada" if st.session_state.lang == lang_code else ""
            img_base64 = image_to_base64(info["img"])
            st.markdown(
                f'<div class="bandeira-container {classe_css}">'
                f'<img src="data:image/png;base64,{img_base64}" class="bandeira-img" title="{info["nome"]}">'
                f'</div>',
                unsafe_allow_html=True
            )
            # Para simplificar, o clique é no botão de texto e a imagem é o feedback visual
            # Se quiser a imagem clicável, a complexidade aumenta um pouco (componente customizado)


# Atualiza a variável de tradução APÓS a possível troca de idioma
T = TRADUCOES[st.session_state.lang]

# Título e Mensagem de Boas-vindas
st.title(T['main_title'])
st.write(T['welcome_message'])
st.divider()


# ===================================================================
# RESTANTE DO SCRIPT ORIGINAL (IDÊNTICO)
# ===================================================================

EMAIL_DESTINO = "seu.email@higra.com.br"
ARQUIVOS_DADOS = { "60Hz": "60Hz.xlsx", "50Hz": "50Hz.xlsx" }
FATORES_VAZAO = { "m³/h": 1.0, "gpm (US)": 0.2271247, "l/s": 3.6 }
FATORES_PRESSAO = { "mca": 1.0, "ftH₂O": 0.3048, "bar": 10.197, "kgf/cm²": 10.0 }

st.header(T['input_header'])

# Novo subtítulo acima da seleção de frequência
st.markdown(f"#### {T['eletric_freq_title']}")

col_freq, col_vazio = st.columns([1, 3])
with col_freq:
    frequencia_selecionada = st.radio(T['freq_header'], list(ARQUIVOS_DADOS.keys()), horizontal=True, label_visibility="collapsed")

col_vazao, col_pressao = st.columns(2)
with col_vazao:
    st.markdown(T['flow_header'])
    sub_col_v1, sub_col_v2 = st.columns([2,1])
    with sub_col_v1: vazao_bruta = st.number_input(T['flow_value_label'], min_value=0.1, value=100.0, step=10.0, label_visibility="collapsed")
    with sub_col_v2: unidade_vazao = st.selectbox(T['flow_unit_label'], list(FATORES_VAZAO.keys()), label_visibility="collapsed")
with col_pressao:
    st.markdown(T['pressure_header'])
    sub_col_p1, sub_col_p2 = st.columns([2,1])
    with sub_col_p1: pressao_bruta = st.number_input(T['pressure_value_label'], min_value=0.1, value=100.0, step=5.0, label_visibility="collapsed")
    with sub_col_p2: unidade_pressao = st.selectbox(T['pressure_unit_label'], list(FATORES_PRESSAO.keys()), label_visibility="collapsed")

vazao_para_busca = round(vazao_bruta * FATORES_VAZAO[unidade_vazao])
pressao_para_busca = round(pressao_bruta * FATORES_PRESSAO[unidade_pressao])
st.info(T['converted_values_info'].format(vazao=vazao_para_busca, pressao=pressao_para_busca))

caminho_arquivo_selecionado = ARQUIVOS_DADOS[frequencia_selecionada]
df_processado = carregar_e_processar_dados(caminho_arquivo_selecionado)

if df_processado is not None:
    if st.button(T['search_button'], use_container_width=True):
        st.session_state.mailto_link = None
        st.session_state.iniciar_orcamento = False
        st.session_state.opcionais_selecionados = None
        with st.spinner(T['spinner_text'].format(freq=frequencia_selecionada)):
            resultado, tipo = selecionar_bombas(df_processado, vazao_para_busca, pressao_para_busca, top_n=5)
            if not resultado.empty:
                st.session_state.resultado_busca = {"resultado": resultado, "tipo": tipo}
            else:
                st.session_state.resultado_busca = None
                st.error(T['no_solution_error'])

    if st.session_state.resultado_busca:
        st.divider()
        st.header(T['results_header'])
        resultado_data = st.session_state.resultado_busca
        resultado = resultado_data["resultado"]
        tipo = resultado_data["tipo"]
        if tipo == "unica": st.success(T['solution_unique'])
        elif tipo == "paralelo": st.warning(T['solution_parallel']); st.info(T['solution_parallel_info'])
        elif tipo == "serie": st.warning(T['solution_series']); st.info(T['solution_series_info'])
        
        resultado_formatado = resultado.copy()
        for col in ['ERRO_PRESSAO', 'ERRO_RELATIVO', 'RENDIMENTO (%)', 'POTÊNCIA (HP)', 'POTÊNCIA CORRIGIDA (HP)']:
            if col in resultado_formatado.columns:
                    resultado_formatado[col] = resultado_formatado[col].map('{:,.2f}'.format)
        st.dataframe(resultado_formatado, hide_index=True, use_container_width=True)
        st.divider()
        
        # Módulo de Orçamento
        if ATIVAR_ORCAMENTO:
            if st.button(T['quote_button_start'], use_container_width=True):
                st.session_state.iniciar_orcamento = not st.session_state.iniciar_orcamento
                st.session_state.mailto_link = None
                st.session_state.opcionais_selecionados = None

            if st.session_state.iniciar_orcamento:
                with st.form("opcionais_form"):
                    st.subheader(T['quote_options_header'])
                    col_op1, col_op2 = st.columns(2)
                    with col_op1:
                        rotor_orc = st.selectbox("Material do Rotor", ["FOFO", "CA40", "INOX34"])
                        difusor_orc = st.selectbox("Material do Difusor", ["FOFO", "CA40", "INOX34"])
                        equalizador_orc = st.selectbox("Equalizador de Pressão", ["FILTRO EQUALIZADOR", "PISTÃO EQUALIZADOR"])
                    with col_op2:
                        sensor_motor_orc = st.selectbox("Sensor Temperatura do Motor", ["1 SENSOR", "3 SENSORES"])
                        sensor_nivel_orc = st.selectbox("Sensor de Nível", ["NÃO", "SIM"])
                        crivo_orc = st.selectbox("Crivo", ["SIM", "NÃO"])
                    continuar_orcamento = st.form_submit_button(T['quote_continue_button'])
                    if continuar_orcamento:
                        st.session_state.opcionais_selecionados = {
                            "Material do Rotor": rotor_orc,
                            "Material do Difusor": difusor_orc,
                            "Equalizador de Pressão": equalizador_orc,
                            "Sensor Temperatura do Motor": sensor_motor_orc,
                            "Sensor de Nível": sensor_nivel_orc,
                            "Crivo": crivo_orc
                        }

                if st.session_state.opcionais_selecionados:
                    with st.form("contato_form"):
                        st.subheader(T['quote_contact_header'])
                        nome_cliente = st.text_input(T['quote_form_name'])
                        email_cliente = st.text_input(T['quote_form_email'])
                        mensagem_cliente = st.text_area(T['quote_form_message'])
                        enviar_orcamento = st.form_submit_button(T['quote_form_button'])
                        if enviar_orcamento:
                            if not nome_cliente or not email_cliente:
                                st.warning(T['quote_form_warning'])
                            else:
                                opcionais_texto = "\n\nOPCIONAIS SELECIONADOS PARA O ORÇAMENTO:\n"
                                for chave, valor in st.session_state.opcionais_selecionados.items():
                                    opcionais_texto += f"- {chave}: {valor}\n"
                                tabela_resultados_texto = resultado.to_string()
                                corpo_email = T['email_body'].format(
                                    nome=nome_cliente,
                                    email=email_cliente,
                                    mensagem=mensagem_cliente,
                                    freq=frequencia_selecionada,
                                    vazao=vazao_para_busca,
                                    pressao=pressao_para_busca,
                                    tabela_resultados=tabela_resultados_texto
                                ) + opcionais_texto
                                corpo_email_codificado = quote(corpo_email)
                                assunto = quote(T['email_subject'].format(nome=nome_cliente))
                                st.session_state.mailto_link = f"mailto:{EMAIL_DESTINO}?subject={assunto}&body={corpo_email_codificado}"

                if st.session_state.mailto_link:
                    st.success(T['quote_form_success'])
                    st.markdown(f'''
                        <a href="{st.session_state.mailto_link}" target="_blank" style="
                            display: inline-block; padding: 12px 20px; background-color: {COR_SECUNDARIA};
                            color: {COR_PRIMARIA}; font-weight: bold; text-align: center;
                            text-decoration: none; border-radius: 8px; border: 2px solid {COR_PRIMARIA};
                        ">
                            {T['quote_form_click_here']}
                        </a>
                    ''', unsafe_allow_html=True)
                    st.info(T['quote_form_info'])
