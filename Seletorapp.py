import streamlit as st
import pandas as pd
import numpy as np
import re
from urllib.parse import quote
import base64
from pathlib import Path

# ===================================================================
# CONFIGURAÇÕES INICIAIS E CONSTANTES
# ===================================================================

# Configuração de estado da sessão
if 'mostrar_lista_pecas' not in st.session_state: st.session_state.mostrar_lista_pecas = False
if 'mostrar_desenho' not in st.session_state: st.session_state.mostrar_desenho = False
if 'mostrar_desenho_visualizacao' not in st.session_state: st.session_state.mostrar_desenho_visualizacao = False
if 'mostrar_lista_visualizacao' not in st.session_state: st.session_state.mostrar_lista_visualizacao = False
if 'mostrar_buscador_modelo' not in st.session_state: st.session_state.mostrar_buscador_modelo = False
if 'mostrar_grafico' not in st.session_state: st.session_state.mostrar_grafico = False
if 'lang' not in st.session_state: st.session_state.lang = 'pt'
if 'resultado_busca' not in st.session_state: st.session_state.resultado_busca = None
if 'mailto_link' not in st.session_state: st.session_state.mailto_link = None
if 'iniciar_orcamento' not in st.session_state: st.session_state.iniciar_orcamento = False
if 'opcionais_selecionados' not in st.session_state: st.session_state.opcionais_selecionados = None

# Configurações do aplicativo
st.set_page_config(
    layout="wide", 
    page_title="Higra Mining Selector",
    page_icon="💧",
    initial_sidebar_state="collapsed"
)

# ===================================================================
# CONSTANTES E CONFIGURAÇÕES DE DESIGN
# ===================================================================

CORES = {
    'primaria': "#134883",
    'secundaria': "#F8AC2E",
    'fundo': "#F0F5FF",
    'texto': "#333333",
    'sucesso': "#2ECC71",
    'alerta': "#F39C12",
    'erro': "#E74C3C",
    'destaque': "#3498DB"
}

EMAIL_DESTINO = "seu.email@higra.com.br"
ARQUIVOS_DADOS = { "60Hz": "60Hz.xlsx", "50Hz": "50Hz.xlsx" }
FATORES_VAZAO = { "m³/h": 1.0, "gpm (US)": 0.2271247, "l/s": 3.6 }
FATORES_PRESSAO = { "mca": 1.0, "ftH₂O": 0.3048, "bar": 10.197, "kgf/cm²": 10.0 }
ATIVAR_ORCAMENTO = False

# ===================================================================
# ESTILOS CSS PROFISSIONAIS
# ===================================================================

st.markdown(f"""
<style>
    /* Configurações gerais */
    .stApp {{
        background: linear-gradient(135deg, {CORES['fundo']} 0%, #ffffff 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Container principal */
    .main-container {{
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }}
    
    /* Cabeçalhos */
    h1, h2, h3 {{
        color: {CORES['primaria']};
        font-weight: 700;
        margin-bottom: 1rem;
    }}
    
    h1 {{
        border-bottom: 3px solid {CORES['secundaria']};
        padding-bottom: 10px;
    }}
    
    /* Cards e containers */
    .card {{
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid {CORES['primaria']};
    }}
    
    .card-highlight {{
        border-left: 4px solid {CORES['secundaria']};
        background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
    }}
    
    /* Botões principais */
    .stButton>button {{
        background: linear-gradient(135deg, {CORES['primaria']} 0%, #1a5ba3 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(19, 72, 131, 0.3);
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(19, 72, 131, 0.4);
        background: linear-gradient(135deg, #1a5ba3 0%, {CORES['primaria']} 100%);
    }}
    
    /* Botões secundários */
    .secondary-button {{
        background: white !important;
        color: {CORES['primaria']} !important;
        border: 2px solid {CORES['primaria']} !important;
    }}
    
    .secondary-button:hover {{
        background: {CORES['primaria']} !important;
        color: white !important;
    }}
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: #e8f0fe;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {CORES['primaria']};
        color: white;
    }}
    
    /* Input fields */
    .stNumberInput, .stSelectbox, .stTextInput {{
        background: white;
        border-radius: 6px;
    }}
    
    /* Alertas personalizados */
    .stAlert {{
        border-radius: 10px;
        border-left: 5px solid;
    }}
    
    .stAlert [data-testid="stMarkdownContainer"] {{
        font-weight: 500;
    }}
    
    /* Bandeiras de idioma */
    .language-flags {{
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        margin-bottom: 20px;
    }}
    
    .flag-item {{
        cursor: pointer;
        padding: 8px;
        border-radius: 6px;
        transition: all 0.3s ease;
    }}
    
    .flag-item.active {{
        background: {CORES['secundaria']};
        transform: scale(1.1);
    }}
    
    .flag-item:hover {{
        transform: scale(1.05);
    }}
    
    /* Resultados tabela */
    .dataframe {{
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Divider personalizado */
    .custom-divider {{
        height: 3px;
        background: linear-gradient(90deg, {CORES['primaria']}, {CORES['secundaria']});
        margin: 30px 0;
        border-radius: 2px;
    }}
    
    /* Ícones e emojis */
    .icon {{
        font-size: 1.2em;
        margin-right: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# ===================================================================
# DICIONÁRIO DE TRADUÇÕES (MANTIDO IDÊNTICO)
# ===================================================================

TRADUCOES = {
    'pt': {
        'page_title': "Seletor Higra Mining",
        'main_title': "Seletor de Bombas Hidráulicas Higra Mining",
        'welcome_message': "Bem-vindo! Entre com os dados do seu ponto de trabalho para encontrar a melhor solução.",
        'input_header': "Parâmetros de Entrada",
        'eletric_freq_title': "Frequência Elétrica",
        'freq_header': "Frequência",
        'flow_header': "**Vazão Desejada**",
        'graph_header': "📊 Gráfico de Performance",
        'drawing_header': "📐 Desenho Dimensional",
        'selector_tab_label': "Seletor por Ponto de Trabalho",
        'finder_tab_label': "Buscador por Modelo",
        'parts_list_header': "📋 Lista de Peças",
        'view_graph_button': "Visualizar Gráfico",
        'close_graph_button': "Fechar Gráfico",
        'pressure_header': "**Pressão Desejada**",
        'flow_value_label': "Valor da Vazão",
        'pressure_value_label': "Valor da Pressão",
        'view_drawing_button': "Visualizar Desenho",
        'show_finder_button': "🔎 Buscar por Modelo da Bomba",
        'view_parts_list_button': "Visualizar Lista de Peças",
        'close_view_button': "Fechar Visualização",
        'flow_unit_label': "Unidade Vazão",
        'finder_header': "Busque diretamente pelo modelo da bomba",
        'model_select_label': "1. Selecione o Modelo",
        'motor_select_label': "2. Selecione o Motor (CV)",
        'find_pump_button': "Buscar Bomba",
        'pressure_unit_label': "Unidade Pressão",
        'converted_values_info': "Valores convertidos para a busca: **Vazão: {vazao} m³/h** | **Pressão: {pressao} mca**",
        'search_button': "Buscar Melhor Opção",
        'dimensional_drawing_button': "Desenho Dimensional",
        'dimensional_drawing_warning': "Atenção: O Desenho Dimensional é um documento de referência e pode conter variações. Em caso de dúvida ou para confirmação mais detalhada, por favor, entre em contato.",
        'parts_list_button': "Lista de Peças",
        'parts_list_warning': "Atenção: A lista de peças é um documento de referência e pode conter variações. Em caso de dúvida ou para confirmação mais detalhada, por favor, entre em contato.",
        'download_parts_list_button': "Baixar Lista de Peças",
        'parts_list_unavailable': "Lista de peças indisponível. Por favor, entre em contato para receber.",
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
        'download_drawing_button': "Baixar Desenho Dimensional",
        'performance_note': "Nota: Nossos cálculos avançados para encontrar a bomba ideal podem levar alguns segundos. Agradecemos a sua paciência!",
        'drawing_unavailable': "Desenho dimensional indisponível. Entre em contato para receber.",
        'contact_button': "Contato",
        'show_unique_button': "🔍 Mostrar Bombas Únicas",
        'show_systems_button': "🔄 Mostrar Sistemas Múltiplos",
        'view_mode_unique': "Modo de visualização: Bombas Únicas",
        'view_mode_systems': "Modo de visualização: Sistemas Múltiplos",
        'no_unique_pumps': "❌ Nenhuma bomba única encontrada para estes parâmetros.",
        'no_systems_found': "❌ Nenhum sistema com múltiplas bombas encontrado para estes parâmetros.",
        'system_type_single': "Única",
        'system_type_parallel': "{} em Paralelo",
        'system_type_series': "2 em Série",
        'system_type_combined': "{} Bombas ({}x2)",
        'system_type_header': "Tipo de Sistema",
        'pressure_error_header': "Erro de Pressão",
        'relative_error_header': "Erro Relativo",
        'no_solution_found': "❌ Nenhuma bomba ou sistema de bombas foi encontrado para este ponto de trabalho. Tente outros valores ou entre em contato com nosso suporte.",
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
        'finder_header': "Search directly by pump model",
        'model_select_label': "1. Select Model",
        'motor_select_label': "2. Select Motor (CV)",
        'find_pump_button': "Find Pump",
        'pressure_value_label': "Head Value",
        'selector_tab_label': "Selector by Duty Point",
        'finder_tab_label': "Search by Model",
        'flow_unit_label': "Flow Unit",
        'graph_header': "📊 Performance Chart",
        'drawing_header': "📐 Dimensional Drawing",
        'parts_list_header': "📋 Parts List",
        'view_graph_button': "View Chart",
        'show_finder_button': "🔎 Search by Pump Model",
        'close_graph_button': "Close Chart",
        'pressure_unit_label': "Head Unit",
        'view_drawing_button': "View Drawing",
        'view_parts_list_button': "View Parts List",
        'close_view_button': "Close View",
        'parts_list_button': "Parts List",
        'parts_list_warning': "Attention: The parts list is a reference document and may contain variations. If in doubt or for more detailed confirmation, please contact us.",
        'download_parts_list_button': "Download Parts List",
        'parts_list_unavailable': "Parts list unavailable. Please contact us to receive it.",
        'converted_values_info': "Converted values for search: **Flow: {vazao} m³/h** | **Head: {pressao} mca**",
        'search_button': "Find Best Option",
        'spinner_text': "Calculating the best options for {freq}...",
        'results_header': "Search Results",
        'dimensional_drawing_button': "Dimensional Drawing",
        'dimensional_drawing_warning': "Attention: The Dimensional Drawing is a reference document and may contain variations. If in doubt or for more detailed confirmation, please contact us.",
        'solution_unique': "✅ Solution found with a **SINGLE PUMP**:",
        'solution_parallel': "⚠️ No single pump with good efficiency. Alternative: **TWO PUMPS IN PARALELO**:",
        'solution_parallel_info': "Flow and power below are PER PUMP. Total flow = 2x.",
        'solution_series': "⚠️ No single or parallel option. Alternative: **TWO PUMPS IN SERIES**:",
        'solution_series_info': "Head below is PER PUMP. Total head = 2x.",
        'no_solution_error': "❌ No pump found. Try other values.",
        'quote_button_start': "Request a Quote",
        'quote_options_header': "Step 1: Select Pump Options",
        'quote_continue_button': "Continue to Next Step",
        'quote_contact_header': "Step 2: Your Contact Information",
        'quote_form_name': "Your Name *",
        'download_drawing_button': "Download Dimensional Drawing",
        'drawing_unavailable': "Dimensional drawing unavailable. Please contact us to receive it.",
        'contact_button': "Contact",
        'pressure_error_header': "Pressure Error",
        'relative_error_header': "Relative Error",
        'system_type_header': "System Type",
        'no_solution_found': "❌ No pump or pump system was found for this duty point. Try other values or contact our support.",
        'performance_note': "Note: Our advanced calculations to find the ideal pump may take a few seconds. We appreciate your patience!",
        'quote_form_email': "Your Email *",
        'system_type_single': "Single",
        'show_unique_button': "🔍 Show Single Pumps",
        'show_systems_button': "🔄 Show Multiple Systems",
        'view_mode_unique': "Viewing mode: Single Pumps",
        'view_mode_systems': "Viewing mode: Multiple Systems",
        'no_unique_pumps': "❌ No single pump found for these parameters.",
        'no_systems_found': "❌ No multiple pump system found for these parameters.",
        'system_type_parallel': "{} in Parallel",
        'system_type_series': "2 in Series",
        'system_type_combined': "{} Pumps ({}x2)",
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
        'show_finder_button': "🔎 Buscar por Modelo de Bomba",
        'flow_value_label': "Valor del Caudal",
        'graph_header': "📊 Gráfico de Rendimiento",
        'drawing_header': "📐 Dibujo Dimensional",
        'selector_tab_label': "Selector por Punto de Trabajo",
        'finder_tab_label': "Buscador por Modelo",
        'parts_list_header': "📋 Lista de Repuestos",
        'view_graph_button': "Visualizar Gráfico",
        'close_graph_button': "Cerrar Gráfico",
        'view_drawing_button': "Visualizar Dibujo",
        'view_parts_list_button': "Visualizar Lista de Repuestos",
        'close_view_button': "Cerrar Visualización",
        'pressure_value_label': "Valor de la Altura",
        'finder_header': "Busque directamente por el modelo de la bomba",
        'model_select_label': "1. Seleccione el Modelo",
        'motor_select_label': "2. Seleccione el Motor (CV)",
        'find_pump_button': "Buscar Bomba",
        'flow_unit_label': "Unidad Caudal",
        'parts_list_button': "Lista de Repuestos",
        'parts_list_warning': "Atención: La lista de repuestos es un documento de referencia y puede contener variaciones. En caso de duda o para una confirmación más detallada, póngase en contacto.",
        'download_parts_list_button': "Descargar Lista de Repuestos",
        'parts_list_unavailable': "Lista de repuestos no disponible. Por favor, póngase en contacto para recibirla.",
        'pressure_unit_label': "Unidad Altura",
        'converted_values_info': "Valores convertidos para la búsqueda: **Caudal: {vazao} m³/h** | **Altura: {pressao} mca**",
        'search_button': "Buscar Mejor Opción",
        'dimensional_drawing_button': "Dibujo Dimensional",
        'dimensional_drawing_warning': "Atención: El Dibujo Dimensional es un documento de referencia y puede contener variaciones. En caso de duda o para una confirmación más detallada, por favor, póngase en contacto.",
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
        'download_drawing_button': "Descargar Dibujo Dimensional",
        'drawing_unavailable': "Dibujo dimensional no disponible. Contáctenos para recibirlo.",
        'contact_button': "Contacto",
        'system_type_single': "Única",
        'show_unique_button': "🔍 Mostrar Bombas Únicas",
        'show_systems_button': "🔄 Mostrar Sistemas Múltiples",
        'view_mode_unique': "Modo de visualización: Bombas Únicas",
        'view_mode_systems': "Modo de visualización: Sistemas Múltiples",
        'no_unique_pumps': "❌ No se encontraron bombas únicas para estos parámetros.",
        'no_systems_found': "❌ No se encontraron sistemas de bombas múltiples para estos parámetros.",
        'pressure_error_header': "Error de Presión",
        'relative_error_header': "Error Relativo",
        'system_type_parallel': "{} en Paralelo",
        'system_type_series': "2 en Serie",
        'system_type_combined': "{} Bombas ({}x2)",
        'system_type_header': "Tipo de Sistema",
        'no_solution_found': "❌ No se encontró ninguna bomba o sistema de bombas para este punto de trabajo. Intente otros valores o póngase en contacto con nuestro soporte.",
        'performance_note': "Nota: Nuestros cálculos avanzados para encontrar la bomba ideal pueden tardar unos segundos. ¡Agradecemos su paciencia!",
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
# FUNÇÕES AUXILIARES (MANTIDAS IDÊNTICAS)
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
def image_to_base64(img_path):
    """Converte um arquivo de imagem para string base64."""
    try:
        path = Path(img_path)
        with path.open("rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def mostrar_pdf(caminho_arquivo, legenda="Visualização do Documento"):
    """Exibe a primeira página de um PDF como imagem diretamente no Streamlit."""
    try:
        import fitz
        from PIL import Image
        import io
        
        doc = fitz.open(caminho_arquivo)
        page = doc.load_page(0)
        zoom = 3.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        st.image(image, caption=legenda, use_container_width=True)
        
    except FileNotFoundError:
        st.warning(f"Arquivo não encontrado para este modelo.")
    except Exception as e:
        st.error(f"Não foi possível exibir o PDF: {e}")

@st.cache_data
def carregar_e_processar_dados(caminho_arquivo):
    try:
        df = pd.read_excel(caminho_arquivo)
        df.columns = df.columns.str.strip().str.upper()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o Excel: {e}")
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

def buscar_por_modelo_e_motor(df, modelo, motor):
    if df is None or df.empty:
        return pd.DataFrame()

    df_filtrado = df[
        (df['MODELO'] == modelo) &
        (df['MOTOR PADRÃO (CV)'] == motor)
    ]
    
    if df_filtrado.empty:
        return pd.DataFrame()
        
    melhor_opcao = df_filtrado.loc[df_filtrado['RENDIMENTO (%)'].idxmax()]
    resultado_df = pd.DataFrame([melhor_opcao])
    resultado_df["TIPO_SISTEMA_CODE"] = "single"
    resultado_df["N_TOTAL_BOMBAS"] = 1
    
    colunas_finais = [
       'MODELO', 'ROTOR', 'VAZÃO (M³/H)', 'PRESSÃO (MCA)', 'ERRO_PRESSAO', 'ERRO_RELATIVO',
       'RENDIMENTO (%)', 'POTÊNCIA (HP)', 'MOTOR FINAL (CV)', 
       'TIPO_SISTEMA_CODE', 'N_TOTAL_BOMBAS',
       'ERRO_PRESSAO_ABS', 'ABS_ERRO_RELATIVO' 
    ]
    
    resultado_df = resultado_df.rename(columns={'MOTOR PADRÃO (CV)': 'MOTOR FINAL (CV)'})
    if 'ROTOR' in resultado_df.columns:
        resultado_df = resultado_df.drop(columns=['ROTOR'])
    resultado_df = resultado_df.rename(columns={'ROTORNUM': 'ROTOR'})
    
    colunas_presentes = [col for col in colunas_finais if col in resultado_df.columns]
    return resultado_df[colunas_presentes]

def filtrar_e_classificar(df, vazao, pressao, top_n=5, limite_desempate_rendimento=3):
    if df is None or df.empty: 
        return pd.DataFrame()

    mask_vazao = df["VAZÃO (M³/H)"] == vazao
    if not mask_vazao.any():
        return pd.DataFrame()

    df_vazao = df.loc[mask_vazao].copy()
    min_max = df_vazao.groupby('MODELO')['PRESSÃO (MCA)'].agg(['min', 'max']).reset_index()
    min_max.columns = ['MODELO', 'PRESSAO_DO_ROTOR_MIN', 'PRESSAO_DO_ROTOR_MAX']
    df_vazao = df_vazao.merge(min_max, on='MODELO', how='left')
    
    limite_inferior = df_vazao['PRESSAO_DO_ROTOR_MIN'] * 0.99
    limite_superior = df_vazao['PRESSAO_DO_ROTOR_MAX'] * 1.01
    mask_limites = (pressao >= limite_inferior) & (pressao <= limite_superior)
    df_filtrado = df_vazao.loc[mask_limites].copy()
    
    if df_filtrado.empty:
        return pd.DataFrame()

    df_filtrado["ERRO_PRESSAO"] = df_filtrado["PRESSÃO (MCA)"] - pressao
    df_filtrado["MOTOR FINAL (CV)"] = df_filtrado["POTÊNCIA (HP)"].apply(encontrar_motor_final)
    df_filtrado["ERRO_PRESSAO_ABS"] = df_filtrado["ERRO_PRESSAO"].abs()

    df_grupo_controle = df_filtrado.loc[df_filtrado.groupby('MODELO')['ERRO_PRESSAO_ABS'].idxmin()].copy()
    if df_grupo_controle.empty: return pd.DataFrame()

    min_erro_rel = df_grupo_controle["ABS_ERRO_RELATIVO"].min()
    df_grupo_controle["DIF_ERRO_REL"] = df_grupo_controle["ABS_ERRO_RELATIVO"] - min_erro_rel
    
    grupo_A = df_grupo_controle[df_grupo_controle["DIF_ERRO_REL"] <= 10].copy()
    grupo_B = df_grupo_controle[df_grupo_controle["DIF_ERRO_REL"] > 10].copy()
    
    grupo_A = grupo_A.sort_values(by="RENDIMENTO (%)", ascending=False)
    
    if not grupo_A.empty:
        max_rend = grupo_A["RENDIMENTO (%)"].max()
        grupo_A["DIF_REND"] = max_rend - grupo_A["RENDIMENTO (%)"]
        subgrupo_A1 = grupo_A[grupo_A["DIF_REND"] <= limite_desempate_rendimento].copy()
        subgrupo_A2 = grupo_A[grupo_A["DIF_REND"] > limite_desempate_rendimento].copy()
        subgrupo_A1 = subgrupo_A1.sort_values(by="ERRO_PRESSAO_ABS", ascending=True)
        grupo_A = pd.concat([subgrupo_A1, subgrupo_A2])
    
    grupo_B = grupo_B.sort_values(by="ABS_ERRO_RELATIVO", ascending=True)
    df_resultado = pd.concat([grupo_A, grupo_B])
    df_resultado = df_resultado.head(top_n)
    df_resultado = df_resultado.drop(columns=["DIF_ERRO_REL", "DIF_REND"], errors="ignore")
    
    colunas_finais = [
        'MODELO', 'ROTOR', 'VAZÃO (M³/H)', 'PRESSÃO (MCA)', 'ERRO_PRESSAO', 'ERRO_RELATIVO',
        'RENDIMENTO (%)', 'POTÊNCIA (HP)', 'MOTOR FINAL (CV)', 'ERRO_PRESSAO_ABS', 'ABS_ERRO_RELATIVO'
    ]
    
    if 'ROTOR' in df_resultado.columns:
        df_resultado = df_resultado.drop(columns=['ROTOR'])
    df_resultado = df_resultado.rename(columns={'ROTORNUM': 'ROTOR'})
    colunas_presentes = [col for col in colunas_finais if col in df_resultado.columns]
    return df_resultado[colunas_presentes]

def selecionar_bombas(df, vazao_desejada, pressao_desejada):
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    top_n_unicas = 3
    top_n_multiplas = 5
    
    todas_opcoes = []
    resultado_unico = filtrar_e_classificar(df, vazao_desejada, pressao_desejada, top_n=10)
    if not resultado_unico.empty:
        resultado_unico["TIPO_SISTEMA_CODE"] = "single"
        resultado_unico["N_TOTAL_BOMBAS"] = 1
        resultado_unico["PRIORIDADE_TIPO"] = 1
        todas_opcoes.append(resultado_unico)
    
    sistemas_multiplos = []
    for num_paralelo in range(2, 16):
        vazao_paralelo = vazao_desejada / num_paralelo
        resultado_paralelo = filtrar_e_classificar(df, vazao_paralelo, pressao_desejada, top_n=top_n_multiplas)
        if not resultado_paralelo.empty:
            resultado_paralelo["TIPO_SISTEMA_CODE"] = "parallel"
            resultado_paralelo["N_TOTAL_BOMBAS"] = num_paralelo
            resultado_paralelo["PRIORIDADE_TIPO"] = 2
            sistemas_multiplos.append(resultado_paralelo)
    
    pressao_serie = pressao_desejada / 2
    resultado_serie = filtrar_e_classificar(df, vazao_desejada, pressao_serie, top_n=top_n_multiplas)
    if not resultado_serie.empty:
        resultado_serie["TIPO_SISTEMA_CODE"] = "series"
        resultado_serie["N_TOTAL_BOMBAS"] = 2
        resultado_serie["PRIORIDADE_TIPO"] = 3
        sistemas_multiplos.append(resultado_serie)
    
    for num_conjuntos in range(2, 6):
        vazao_misto = vazao_desejada / num_conjuntos
        pressao_misto = pressao_desejada / 2
        resultado_misto = filtrar_e_classificar(df, vazao_misto, pressao_misto, top_n=top_n_multiplas)
        if not resultado_misto.empty:
            total_bombas = num_conjuntos * 2
            resultado_misto["TIPO_SISTEMA_CODE"] = "combined"
            resultado_misto["N_TOTAL_BOMBAS"] = total_bombas
            resultado_misto["N_PARALELO"] = num_conjuntos
            resultado_misto["PRIORIDADE_TIPO"] = 4
            sistemas_multiplos.append(resultado_misto)
    
    if todas_opcoes:
        df_unicas = pd.concat(todas_opcoes, ignore_index=True)
    else:
        df_unicas = pd.DataFrame()
        
    if sistemas_multiplos:
        df_multiplas = pd.concat(sistemas_multiplos, ignore_index=True)
        df_multiplas = df_multiplas.sort_values(
            by=["MODELO", "N_TOTAL_BOMBAS", "RENDIMENTO (%)"], 
            ascending=[True, True, False]
        ).drop_duplicates(subset=["MODELO"], keep="first")
    else:
        df_multiplas = pd.DataFrame()
    
    resultados_unicas_finais = []
    if not df_unicas.empty:
        candidatas_unicas = df_unicas.copy()
        for _ in range(top_n_unicas):
            if candidatas_unicas.empty:
                break
            candidatas_unicas = candidatas_unicas.sort_values(
                by=["RENDIMENTO (%)", "ERRO_PRESSAO_ABS", "ABS_ERRO_RELATIVO"],
                ascending=[False, True, True]
            )
            melhor_unica = candidatas_unicas.head(1)
            resultados_unicas_finais.append(melhor_unica)
            modelo_remover = melhor_unica["MODELO"].iloc[0]
            candidatas_unicas = candidatas_unicas[candidatas_unicas["MODELO"] != modelo_remover]
    
    resultados_multiplos_finais = []
    if not df_multiplas.empty:
        candidatas_multiplas = df_multiplas.copy()
        for _ in range(top_n_multiplas):
            if candidatas_multiplas.empty:
                break
            candidatas_multiplas = candidatas_multiplas.sort_values(
                by=["N_TOTAL_BOMBAS", "PRIORIDADE_TIPO", "RENDIMENTO (%)", "ERRO_PRESSAO_ABS", "ABS_ERRO_RELATIVO"],
                ascending=[True, True, False, True, True]
            )
            melhor_multipla = candidatas_multiplas.head(1)
            resultados_multiplos_finais.append(melhor_multipla)
            modelo_remover = melhor_multipla["MODELO"].iloc[0]
            candidatas_multiplas = candidatas_multiplas[candidatas_multiplas["MODELO"] != modelo_remover]
    
    if resultados_unicas_finais:
        df_unicas_final = pd.concat(resultados_unicas_finais, ignore_index=True)
        df_unicas_final = df_unicas_final.drop(columns=['ERRO_PRESSAO_ABS', 'ABS_ERRO_RELATIVO', 'PRIORIDADE_TIPO'], errors='ignore')
    else:
        df_unicas_final = pd.DataFrame()
    
    if resultados_multiplos_finais:
        df_multiplas_final = pd.concat(resultados_multiplos_finais, ignore_index=True)
        df_multiplas_final = df_multiplas_final.drop(columns=['ERRO_PRESSAO_ABS', 'ABS_ERRO_RELATIVO', 'PRIORIDADE_TIPO'], errors='ignore')
    else:
        df_multiplas_final = pd.DataFrame()
        
    return df_unicas_final, df_multiplas_final

# ===================================================================
# LAYOUT PRINCIPAL - CABEÇALHO
# ===================================================================

def render_header():
    """Renderiza o cabeçalho com logo e seleção de idioma"""
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            try:
                st.image("logo.png", width=400)
            except:
                st.markdown(f"<h1 style='color: {CORES['primaria']};'>💧 Higra Mining</h1>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='language-flags'>", unsafe_allow_html=True)
            col_pt, col_en, col_es = st.columns(3)
            
            with col_pt:
                active = "active" if st.session_state.lang == 'pt' else ""
                if st.button("🇧🇷", key="lang_pt", use_container_width=True):
                    st.session_state.lang = 'pt'
                    st.rerun()
            
            with col_en:
                active = "active" if st.session_state.lang == 'en' else ""
                if st.button("🇺🇸", key="lang_en", use_container_width=True):
                    st.session_state.lang = 'en'
                    st.rerun()
            
            with col_es:
                active = "active" if st.session_state.lang == 'es' else ""
                if st.button("🇪🇸", key="lang_es", use_container_width=True):
                    st.session_state.lang = 'es'
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

# ===================================================================
# LAYOUT PRINCIPAL - SEÇÃO DE ENTRADA
# ===================================================================

def render_input_section():
    """Renderiza a seção de entrada de dados"""
    T = TRADUCOES[st.session_state.lang]
    
    with st.container():
        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### 🔧 {T['input_header']}")
        
        tab_seletor, tab_buscador = st.tabs([T['selector_tab_label'], T['finder_tab_label']])
        
        with tab_seletor:
            render_selector_tab(T)
        
        with tab_buscador:
            render_finder_tab(T)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_selector_tab(T):
    """Renderiza a aba do seletor por ponto de trabalho"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"**{T['eletric_freq_title']}**")
        frequencia_selecionada = st.radio(
            T['freq_header'], 
            list(ARQUIVOS_DADOS.keys()), 
            horizontal=True, 
            label_visibility="collapsed",
            key='freq_seletor'
        )
    
    caminho_arquivo_selecionado = ARQUIVOS_DADOS[frequencia_selecionada]
    df_processado = carregar_e_processar_dados(caminho_arquivo_selecionado)
    
    col_vazao, col_pressao = st.columns(2)
    
    with col_vazao:
        st.markdown(f"**{T['flow_header']}**")
        col_v1, col_v2 = st.columns([3, 1])
        with col_v1:
            vazao_bruta = st.number_input(
                T['flow_value_label'], 
                min_value=0.1, 
                value=100.0, 
                step=10.0, 
                label_visibility="collapsed"
            )
        with col_v2:
            unidade_vazao = st.selectbox(
                T['flow_unit_label'], 
                list(FATORES_VAZAO.keys()), 
                label_visibility="collapsed"
            )
    
    with col_pressao:
        st.markdown(f"**{T['pressure_header']}**")
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            pressao_bruta = st.number_input(
                T['pressure_value_label'], 
                min_value=0.1, 
                value=100.0, 
                step=5.0, 
                label_visibility="collapsed"
            )
        with col_p2:
            unidade_pressao = st.selectbox(
                T['pressure_unit_label'], 
                list(FATORES_PRESSAO.keys()), 
                label_visibility="collapsed"
            )
    
    vazao_para_busca = round(vazao_bruta * FATORES_VAZAO[unidade_vazao])
    pressao_para_busca = round(pressao_bruta * FATORES_PRESSAO[unidade_pressao])
    
    st.info(T['converted_values_info'].format(vazao=vazao_para_busca, pressao=pressao_para_busca))
    
    if st.button(T['search_button'], use_container_width=True, type="primary"):
        perform_search(df_processado, frequencia_selecionada, vazao_para_busca, pressao_para_busca)

def render_finder_tab(T):
    """Renderiza a aba do buscador por modelo"""
    col_freq, col_modelo, col_motor = st.columns(3)
    
    with col_freq:
        st.markdown(f"**{T['eletric_freq_title']}**")
        frequencia_buscador = st.radio(
            T['freq_header'], 
            list(ARQUIVOS_DADOS.keys()), 
            horizontal=True, 
            key='freq_buscador'
        )
    
    caminho_buscador = ARQUIVOS_DADOS[frequencia_buscador]
    df_buscador = carregar_e_processar_dados(caminho_buscador)
    
    if df_buscador is not None:
        with col_modelo:
            lista_modelos = ["-"] + sorted(df_buscador['MODELO'].unique())
            modelo_selecionado_buscador = st.selectbox(
                T['model_select_label'],
                lista_modelos,
                key='modelo_buscador'
            )
        
        with col_motor:
            motor_selecionado_buscador = None
            if modelo_selecionado_buscador and modelo_selecionado_buscador != "-":
                motores_unicos = df_buscador[df_buscador['MODELO'] == modelo_selecionado_buscador]['MOTOR PADRÃO (CV)'].unique()
                motores_disponiveis = sorted([motor for motor in motores_unicos if pd.notna(motor)])
                
                if motores_disponiveis:
                    motor_selecionado_buscador = st.selectbox(
                        T['motor_select_label'],
                        motores_disponiveis,
                        key='motor_buscador'
                    )
                else:
                    st.selectbox(T['motor_select_label'], ["-"], disabled=True)
            else:
                st.selectbox(T['motor_select_label'], ["-"], disabled=True)
        
        if modelo_selecionado_buscador and modelo_selecionado_buscador != "-" and motor_selecionado_buscador:
            if st.button(T['find_pump_button'], use_container_width=True, type="primary"):
                perform_model_search(df_buscador, frequencia_buscador, modelo_selecionado_buscador, motor_selecionado_buscador)

def perform_search(df, frequencia, vazao, pressao):
    """Executa a busca por ponto de trabalho"""
    T = TRADUCOES[st.session_state.lang]
    
    st.session_state.last_used_freq = frequencia
    st.session_state.resultado_busca = None
    st.session_state.mostrar_grafico = False
    st.session_state.mostrar_desenho = False
    st.session_state.mostrar_lista_pecas = False
    st.session_state.mostrar_desenho_visualizacao = False
    st.session_state.mostrar_lista_visualizacao = False
    
    with st.spinner(T['spinner_text'].format(freq=frequencia)):
        bombas_unicas, sistemas_multiplos = selecionar_bombas(df, vazao, pressao)
        
        st.session_state.resultado_bombas_unicas = bombas_unicas
        st.session_state.resultado_sistemas_multiplos = sistemas_multiplos
        
        if not bombas_unicas.empty:
            st.session_state.modo_visualizacao = 'unicas'
            st.session_state.resultado_busca = {"resultado": bombas_unicas}
        elif not sistemas_multiplos.empty:
            st.session_state.modo_visualizacao = 'multiplas'
            st.session_state.resultado_busca = {"resultado": sistemas_multiplos}
        else:
            st.session_state.modo_visualizacao = 'unicas'
            st.session_state.resultado_busca = {"resultado": pd.DataFrame()}
    
    st.rerun()

def perform_model_search(df, frequencia, modelo, motor):
    """Executa a busca por modelo específico"""
    T = TRADUCOES[st.session_state.lang]
    
    st.session_state.last_used_freq = frequencia
    st.session_state.resultado_bombas_unicas = None
    st.session_state.resultado_sistemas_multiplos = None
    st.session_state.resultado_busca = None
    st.session_state.mostrar_grafico = False
    st.session_state.mostrar_desenho = False
    st.session_state.mostrar_lista_pecas = False
    st.session_state.mostrar_desenho_visualizacao = False
    st.session_state.mostrar_lista_visualizacao = False

    resultado = buscar_por_modelo_e_motor(df, modelo, motor)
    
    if not resultado.empty:
        st.session_state.resultado_bombas_unicas = resultado
        st.session_state.resultado_sistemas_multiplos = pd.DataFrame()
        st.session_state.modo_visualizacao = 'unicas'
        st.session_state.resultado_busca = {"resultado": resultado}
    else:
        st.session_state.resultado_busca = None
        st.error(T['no_solution_error'])
    
    st.rerun()

# ===================================================================
# LAYOUT PRINCIPAL - SEÇÃO DE RESULTADOS
# ===================================================================

def render_results_section():
    """Renderiza a seção de resultados"""
    if st.session_state.resultado_busca is None:
        return
    
    T = TRADUCOES[st.session_state.lang]
    
    if st.session_state.get('modo_visualizacao') == 'multiplas':
        resultado = st.session_state.get('resultado_sistemas_multiplos', pd.DataFrame())
    else:
        resultado = st.session_state.get('resultado_bombas_unicas', pd.DataFrame())

    with st.container():
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card card-highlight'>", unsafe_allow_html=True)
        st.markdown(f"## 📊 {T['results_header']}")
        
        if st.session_state.get('modo_visualizacao') == 'unicas':
            st.success(T['view_mode_unique'])
        else:
            st.warning(T['view_mode_systems'])
        
        render_results_controls(T, resultado)
        st.markdown("</div>", unsafe_allow_html=True)

def render_results_controls(T, resultado):
    """Renderiza os controles e visualização dos resultados"""
    tem_unicas = st.session_state.get('resultado_bombas_unicas') is not None and not st.session_state.resultado_bombas_unicas.empty
    tem_multiplas = st.session_state.get('resultado_sistemas_multiplos') is not None and not st.session_state.resultado_sistemas_multiplos.empty
    
    if tem_unicas or tem_multiplas:
        col1, col2 = st.columns(2)
        with col1:
            disabled = not tem_unicas or st.session_state.modo_visualizacao == 'unicas'
            if st.button(T['show_unique_button'], use_container_width=True, disabled=disabled):
                st.session_state.modo_visualizacao = 'unicas'
                st.rerun()
        with col2:
            disabled = not tem_multiplas or st.session_state.modo_visualizacao == 'multiplas'
            if st.button(T['show_systems_button'], use_container_width=True, disabled=disabled):
                st.session_state.modo_visualizacao = 'multiplas'
                st.rerun()
    
    if resultado.empty:
        if st.session_state.get('modo_visualizacao') == 'unicas':
            st.error(T['no_unique_pumps'])
        else:
            st.error(T['no_systems_found'])
        return
    
    render_results_table(T, resultado)
    render_documentation_sections(T, resultado)

def render_results_table(T, resultado):
    """Renderiza a tabela de resultados"""
    resultado_exibicao = resultado.copy()

    def traduzir_tipo_sistema(row):
        code = row.get('TIPO_SISTEMA_CODE', 'single')
        if code == "single": return T['system_type_single']
        if code == "parallel": return T['system_type_parallel'].format(int(row.get('N_TOTAL_BOMBAS', 2)))
        if code == "series": return T['system_type_series']
        if code == "combined": return T['system_type_combined'].format(int(row.get('N_TOTAL_BOMBAS', 4)), int(row.get('N_PARALELO', 2)))
        return ""
        
    resultado_exibicao[T['system_type_header']] = resultado_exibicao.apply(traduzir_tipo_sistema, axis=1)
    resultado_exibicao = resultado_exibicao.drop(columns=['TIPO_SISTEMA_CODE', 'N_TOTAL_BOMBAS', 'N_PARALELO'], errors='ignore')
    resultado_exibicao = resultado_exibicao.rename(columns={
        "RENDIMENTO (%)": "RENDIMENTO", 
        "POTÊNCIA (HP)": "POTÊNCIA", 
        "MOTOR FINAL (CV)": "MOTOR FINAL", 
        "ERRO_PRESSAO": T['pressure_error_header'], 
        "ERRO_RELATIVO": T['relative_error_header']
    })
    
    resultado_exibicao.insert(0, "Ranking", [f"{i+1}º" for i in range(len(resultado_exibicao))])
    opcoes_ranking = [f"{i+1}º" for i in range(len(resultado_exibicao))]
    
    selecao_ranking = st.radio(
        "Selecione a bomba:", 
        options=opcoes_ranking, 
        index=0, 
        horizontal=True, 
        label_visibility="collapsed",
        key=f'radio_selecao_{st.session_state.modo_visualizacao}'
    )
    
    for col in ['RENDIMENTO', 'POTÊNCIA', 'MOTOR FINAL', T['pressure_error_header'], T['relative_error_header']]:
        if col in resultado_exibicao.columns:
            resultado_exibicao[col] = resultado_exibicao[col].map('{:,.2f}'.format)
    
    st.dataframe(
        resultado_exibicao, 
        hide_index=True, 
        use_container_width=True, 
        column_order=['Ranking', T['system_type_header'], 'MODELO', 'ROTOR', 'RENDIMENTO', 'POTÊNCIA', 'MOTOR FINAL']
    )

def render_documentation_sections(T, resultado):
    """Renderiza as seções de documentação (gráficos, desenhos, lista de peças)"""
    opcoes_ranking = [f"{i+1}º" for i in range(len(resultado))]
    selecao_ranking = st.radio(
        "Selecione a bomba para visualizar documentos:", 
        options=opcoes_ranking, 
        index=0, 
        horizontal=True,
        key=f'doc_selecao_{st.session_state.modo_visualizacao}'
    )
    
    indice_selecionado = opcoes_ranking.index(selecao_ranking)
    melhor_bomba = resultado.iloc[indice_selecionado]
    modelo_selecionado = melhor_bomba['MODELO']
    
    try:
        motor_alvo = int(melhor_bomba['MOTOR FINAL (CV)'])
    except (ValueError, TypeError):
        motor_alvo = 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_performance_chart(T, modelo_selecionado)
    
    with col2:
        render_dimensional_drawing(T, modelo_selecionado, motor_alvo)
    
    with col3:
        render_parts_list(T, modelo_selecionado)

def render_performance_chart(T, modelo_selecionado):
    """Renderiza a seção de gráfico de performance"""
    with st.container():
        st.markdown(f"#### {T['graph_header']}")
        
        frequencia_str = st.session_state.get('last_used_freq', '60Hz')
        caminho_pdf = f"pdfs/{frequencia_str}/{modelo_selecionado}.pdf"
        
        if st.button(T['view_graph_button'], use_container_width=True):
            st.session_state.mostrar_grafico = True
        
        if st.session_state.get('mostrar_grafico', False):
            with st.container(border=True):
                st.subheader(f"Modelo: {modelo_selecionado}")
                mostrar_pdf(caminho_pdf, legenda="Gráfico de Performance")
                if st.button(T['close_graph_button'], use_container_width=True):
                    st.session_state.mostrar_grafico = False
                    st.rerun()

def render_dimensional_drawing(T, modelo_selecionado, motor_alvo):
    """Renderiza a seção de desenho dimensional"""
    with st.container():
        st.markdown(f"#### {T['drawing_header']}")
        
        if st.button(T['dimensional_drawing_button'], use_container_width=True):
            st.session_state.mostrar_desenho = not st.session_state.get('mostrar_desenho', False)

        if st.session_state.get('mostrar_desenho', False):
            with st.container(border=True):
                st.info(T['dimensional_drawing_warning'])
                desenho_base_path = Path("Desenhos")
                caminho_desenho_final = None
                
                if desenho_base_path.exists():
                    desenhos_candidatos = {}
                    for path_arquivo in desenho_base_path.glob(f"{modelo_selecionado}*.pdf"):
                        nome_sem_ext = path_arquivo.stem
                        partes = nome_sem_ext.split('_')
                        if len(partes) == 2:
                            try:
                                motor_no_arquivo = int(partes[1])
                                desenhos_candidatos[motor_no_arquivo] = path_arquivo
                            except ValueError:
                                continue
                    
                    if desenhos_candidatos:
                        motor_mais_proximo = min(
                            desenhos_candidatos.keys(),
                            key=lambda motor: abs(motor - motor_alvo)
                        )
                        caminho_desenho_final = desenhos_candidatos[motor_mais_proximo]
                
                if not caminho_desenho_final:
                    caminho_geral = desenho_base_path / f"{modelo_selecionado}.pdf"
                    if caminho_geral.exists():
                        caminho_desenho_final = caminho_geral
                
                if caminho_desenho_final:
                    if st.button(T['view_drawing_button'], use_container_width=True, type="secondary"):
                        st.session_state.mostrar_desenho_visualizacao = not st.session_state.get('mostrar_desenho_visualizacao', False)

                    if st.session_state.get('mostrar_desenho_visualizacao', False):
                        mostrar_pdf(caminho_desenho_final, legenda="Desenho Dimensional")
                        if st.button(T['close_view_button'], use_container_width=True, key='fechar_desenho'):
                            st.session_state.mostrar_desenho_visualizacao = False
                            st.rerun()
                    
                    with open(caminho_desenho_final, "rb") as pdf_file:
                        st.download_button(
                            label=T['download_drawing_button'],
                            data=pdf_file,
                            file_name=caminho_desenho_final.name,
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.warning(T['drawing_unavailable'])
                
                render_contact_button(T['contact_button'])

def render_parts_list(T, modelo_selecionado):
    """Renderiza a seção de lista de peças"""
    with st.container():
        st.markdown(f"#### {T['parts_list_header']}")
        
        if st.button(T['parts_list_button'], use_container_width=True):
            st.session_state.mostrar_lista_pecas = not st.session_state.get('mostrar_lista_pecas', False)

        if st.session_state.get('mostrar_lista_pecas', False):
            with st.container(border=True):
                caminho_lista_pecas = Path(f"Lista/{modelo_selecionado}.pdf")
                
                if caminho_lista_pecas.exists():
                    st.info(T['parts_list_warning'])
                    if st.button(T['view_parts_list_button'], use_container_width=True, type="secondary"):
                        st.session_state.mostrar_lista_visualizacao = not st.session_state.get('mostrar_lista_visualizacao', False)

                    if st.session_state.get('mostrar_lista_visualizacao', False):
                        mostrar_pdf(caminho_lista_pecas, legenda="Lista de Peças")
                        if st.button(T['close_view_button'], use_container_width=True, key='fechar_lista'):
                            st.session_state.mostrar_lista_visualizacao = False
                            st.rerun()

                    with open(caminho_lista_pecas, "rb") as pdf_file:
                        st.download_button(
                            label=T['download_parts_list_button'],
                            data=pdf_file,
                            file_name=caminho_lista_pecas.name,
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.warning(T['parts_list_unavailable'])
                
                render_contact_button(T['contact_button'])

def render_contact_button(button_text):
    """Renderiza botão de contato padronizado"""
    link_contato = "https://wa.me/5551991808303?text=Ol%C3%A1!%20Preciso%20de%20ajuda%20com%20uma%20bomba%20Higra%20Mining."
    st.markdown(f'''
    <a href="{link_contato}" target="_blank" style="
        display: block;
        padding: 0.5rem 1rem;
        background-color: {CORES['primaria']};
        color: white;
        font-weight: bold;
        text-align: center;
        text-decoration: none;
        border-radius: 8px;
        border: 2px solid {CORES['primaria']};
        box-sizing: border-box;
        margin-top: 10px;
    ">
        {button_text}
    </a>
    ''', unsafe_allow_html=True)

# ===================================================================
# FUNÇÃO PRINCIPAL
# ===================================================================

def main():
    """Função principal do aplicativo"""
    
    # Configuração de query parameters para idioma
    query_params = st.query_params
    if 'lang' in query_params:
        lang_from_url = query_params['lang']
        if lang_from_url in ['pt', 'en', 'es']:
            st.session_state.lang = lang_from_url
    
    T = TRADUCOES[st.session_state.lang]
    
    # Layout principal
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Renderiza componentes
    render_header()
    
    st.title(T['main_title'])
    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
    st.write(T['welcome_message'])
    st.info(T['performance_note'])
    st.markdown("</div>", unsafe_allow_html=True)
    
    render_input_section()
    render_results_section()
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
