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
if 'mostrar_lista_pecas' not in st.session_state: st.session_state.mostrar_lista_pecas = False
if 'mostrar_desenho' not in st.session_state: st.session_state.mostrar_desenho = False
if 'mostrar_desenho_visualizacao' not in st.session_state: st.session_state.mostrar_desenho_visualizacao = False
if 'mostrar_lista_visualizacao' not in st.session_state: st.session_state.mostrar_lista_visualizacao = False
if 'mostrar_buscador_modelo' not in st.session_state: st.session_state.mostrar_buscador_modelo = False

if 'mostrar_grafico' not in st.session_state:
    st.session_state.mostrar_grafico = False

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

def mostrar_pdf(caminho_arquivo, legenda="Visualização do Documento"):
    """Exibe a primeira página de um PDF como imagem diretamente no Streamlit."""
    try:
        import fitz  # PyMuPDF
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

# ===================================================================
# DICIONÁRIO DE TRADUÇÕES E VARIÁVEIS DE COR (COMBINADOS E LIMPOS)
# ===================================================================
ATIVAR_ORCAMENTO = False

COR_PRIMARIA = "#134883"
COR_SECUNDARIA = "#F8AC2E"
COR_FUNDO = "#F0F5FF"
COR_TEXTO = "#333333"

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
        'email_body': """Olá,\n\nUm novo pedido de orçamento foi gerado através do Seletor de Bombas.\n\nDADOS DO CLIENTE:\n- Nome: {nome}\n- E-mail: {email}\n\nMENSAGEM:\n{mensagem}\n\n---------------------------------\nPARÂMETROS DA BUSCA:\n- Frequência: {freq}\n- Vazão: {vazao} m³/h\n- Pressão: {pressao} mca\n\n---------------------------------\nRESULTS ENCONTRADOS:\n{tabela_resultados}"""
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
        'email_subject': "Quote Request via Pump Selector - {nome}",
        'email_body': """Hello,\n\nA new quote request has been generated through the Pump Selector.\n\nCUSTOMER DATA:\n- Nome: {nome}\n- Email: {email}\n\nMESSAGE:\n{mensagem}\n\n---------------------------------\nSEARCH PARAMETERS:\n- Frequency: {freq}\n- Flow: {vazao} m³/h\n- Head: {pressao} mca\n\n---------------------------------\nRESULTS FOUND:\n{tabela_resultados}"""
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
        'dimensional_drawing_warning': "Atención: El Dibujo Dimensional es um documento de referencia y puede contener variaciones. En caso de duda o para una confirmación más detallada, por favor, póngase en contacto.",
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
        'view_mode_unique': "Modo de visualização: Bombas Únicas",
        'view_mode_systems': "Modo de visualização: Sistemas Múltiples",
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
        'email_subject': "Solicitud de Cotización vía Selector de Bombas - {nome}",
        'email_body': """Hola,\n\nSe ha generado una nueva solicitud de cotización a través del Selector de Bombas.\n\nDATOS DEL CLIENTE:\n- Nombre: {nome}\n- Correo Electrónico: {email}\n\nMENSAJE:\n{mensagem}\n\n---------------------------------\nPARÁMETROS DE BÚSQUEDA:\n- Frecuencia: {freq}\n- Caudal: {vazao} m³/h\n- Altura: {pressao} mca\n\n---------------------------------\nRESULTS ENCONTRADOS:\n{tabela_resultados}"""
    }
}

# ===================================================================
# FUNÇÕES GLOBAIS E CONSTANTES (DO SEU CÓDIGO ORIGINAL)
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
    """
    Função rápida e simples para buscar a melhor bomba quando o modelo e o motor já são conhecidos.
    """
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
    
    if df_filtrado.empty: return pd.DataFrame()
    
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
# INTERFACE STREAMLIT (VERSÃO ESTÁVEL COM NOVO DESIGN)
# ===================================================================
st.set_page_config(layout="wide", page_title="Seletor Higra Mining")

COR_PRIMARIA = "#134883"
COR_SECUNDARIA = "#F8AC2E"
COR_FUNDO = "#F0F5FF"
COR_TEXTO = "#333333"

st.markdown(f"""
<style>
    /* Estilos gerais da app */
    .stApp {{
        background-color: {COR_FUNDO};
        color: {COR_TEXTO};
    }}
    
    /* Estilos de cabeçalhos */
    h1, h2, h3, h4, h5, h6 {{
        color: {COR_PRIMARIA};
    }}
    
    /* Estilos de Botões */
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
    
    /* Estilos de Alertas */
    .stAlert > div {{ border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); padding: 15px 20px; }}
    .stAlert-success {{ background-color: #e0f2f1; color: {COR_PRIMARIA}; border-left: 5px solid #2ECC71; }}
    .stAlert-warning {{ background-color: #fff8e1; color: #c08b2c; border-left: 5px solid {COR_SECUNDARIA}; }}
    .stAlert-info {{ background-color: #e3f2fd; color: {COR_PRIMARIA}; border-left: 5px solid {COR_PRIMARIA}; }}
    .stAlert-error {{ background-color: #ffebee; color: #b71c1c; border-left: 5px solid #E74C3C; }}

    /* Estilos de Bandeiras */
    .bandeira-container {{ cursor: pointer; transition: all 0.2s ease-in-out; border-radius: 8px; padding: 5px; margin-top: 10px; border: 2px solid transparent; }}
    .bandeira-container:hover {{ transform: scale(1.1); background-color: rgba(19, 72, 131, 0.1); }}
    .bandeira-container.selecionada {{ border: 2px solid {COR_SECUNDARIA}; box-shadow: 0 0 10px rgba(248, 172, 46, 0.5); }}
    .bandeira-img {{ width: 45px; height: 30px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}

    /* Dataframe estilizado */
    .stDataFrame {{ border: 1px solid #d0d7de; border-radius: 8px; }}

    /* Estilo de botões de rádio */
    div[data-baseweb="radio"] label > div:first-child {{
        background-color: {COR_SECUNDARIA} !important;
        border: 2px solid {COR_SECUNDARIA} !important;
    }}
    /* Estilo para links como botões */
    .stLinkButton > a {{
        border: 2px solid {COR_PRIMARIA};
        background-color: {COR_PRIMARIA};
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        border-radius: 8px;
        display: inline-block;
        text-align: center;
        padding: 0.5rem 1rem;
        text-decoration: none;
    }}
    .stLinkButton > a:hover {{
        background-color: white;
        color: {COR_PRIMARIA};
    }}
</style>
""", unsafe_allow_html=True)


# --- CONFIGURAÇÕES INICIAIS ---
query_params = st.query_params
if 'lang' in query_params:
    lang_from_url = query_params['lang']
    if lang_from_url in ['pt', 'en', 'es']:
        st.session_state.lang = lang_from_url
if 'lang' not in st.session_state: st.session_state.lang = 'pt'
if 'resultado_busca' not in st.session_state: st.session_state.resultado_busca = None
if 'mailto_link' not in st.session_state: st.session_state.mailto_link = None
if 'iniciar_orcamento' not in st.session_state: st.session_state.iniciar_orcamento = False
if 'opcionais_selecionados' not in st.session_state: st.session_state.opcionais_selecionados = None

T = TRADUCOES[st.session_state.lang]

# ===================================================================
# CABEÇALHO COM LOGO E SELEÇÃO DE IDIOMA
# ===================================================================
col_logo, col_vazia, col_bandeiras = st.columns([4, 4, 2])

with col_logo:
    try:
        st.image("logo.png", width=900)
    except Exception:
        st.warning("Logo não encontrada.")

with col_bandeiras:
    bandeiras = {
        "pt": {"nome": "PT", "img": "brasil.png"},
        "en": {"nome": "EN", "img": "uk.png"},
        "es": {"nome": "ES", "img": "espanha.png"}
    }
    flag_cols = st.columns(len(bandeiras))
    for i, (lang_code, info) in enumerate(bandeiras.items()):
        with flag_cols[i]:
            classe_css = "selecionada" if st.session_state.lang == lang_code else ""
            img_base64 = image_to_base64(info["img"])
            st.markdown(f"""
            <a href="?lang={lang_code}" target="_self" style="text-decoration: none;">
                <div style="display: flex; flex-direction: column; align-items: center; font-family: 'Source Sans Pro', sans-serif; font-weight: bold; color: {COR_PRIMARIA};">
                    <span>{info['nome']}</span>
                    <div class="bandeira-container {classe_css}">
                        <img src="data:image/png;base64,{img_base64}" class="bandeira-img">
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)

st.title(T['main_title'])
st.write(T['welcome_message'])
st.info(T['performance_note'])
st.divider()

# ===================================================================
# RESTANTE DO SCRIPT ORIGINAL (IDÊNTICO)
# ===================================================================

EMAIL_DESTINO = "seu.email@higra.com.br"
ARQUIVOS_DADOS = { "60Hz": "60Hz.xlsx", "50Hz": "50Hz.xlsx" }
FATORES_VAZAO = { "m³/h": 1.0, "gpm (US)": 0.2271247, "l/s": 3.6 }
FATORES_PRESSAO = { "mca": 1.0, "ftH₂O": 0.3048, "bar": 10.197, "kgf/cm²": 10.0 }

# ===================================================================
# SEÇÃO DE ENTRADAS (REESTRUTURADA COM LAYOUT EM BLOCOS)
# ===================================================================

tab_seletor, tab_buscador = st.tabs([T['selector_tab_label'], T['finder_tab_label']])

with tab_seletor:
    with st.container(border=True): # NOVO BLOCO VISUAL
        st.markdown(f"#### {T['eletric_freq_title']}")
        col_freq, col_vazio = st.columns([1, 3])
        with col_freq:
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
            st.markdown(T['flow_header'])
            sub_col_v1, sub_col_v2 = st.columns([2,1])
            with sub_col_v1: vazao_bruta = st.number_input(T['flow_value_label'], min_value=0.1, value=100.0, step=10.0, label_visibility="collapsed", key='vazao_bruta')
            with sub_col_v2: unidade_vazao = st.selectbox(T['flow_unit_label'], list(FATORES_VAZAO.keys()), label_visibility="collapsed", key='unidade_vazao')
        with col_pressao:
            st.markdown(T['pressure_header'])
            sub_col_p1, sub_col_p2 = st.columns([2,1])
            with sub_col_p1: pressao_bruta = st.number_input(T['pressure_value_label'], min_value=0.1, value=100.0, step=5.0, label_visibility="collapsed", key='pressao_bruta')
            with sub_col_p2: unidade_pressao = st.selectbox(T['pressure_unit_label'], list(FATORES_PRESSAO.keys()), label_visibility="collapsed", key='unidade_pressao')
        vazao_para_busca = round(vazao_bruta * FATORES_VAZAO[unidade_vazao])
        pressao_para_busca = round(pressao_bruta * FATORES_PRESSAO[unidade_pressao])
        st.info(T['converted_values_info'].format(vazao=vazao_para_busca, pressao=pressao_para_busca))

        if st.button(T['search_button'], use_container_width=True, key='btn_seletor'):
            st.session_state.last_used_freq = frequencia_selecionada
            st.session_state.resultado_busca = None
            st.session_state.mostrar_grafico = False
            st.session_state.mostrar_desenho = False
            st.session_state.mostrar_lista_pecas = False
            st.session_state.mostrar_desenho_visualizacao = False
            st.session_state.mostrar_lista_visualizacao = False
            
            with st.spinner(T['spinner_text'].format(freq=frequencia_selecionada)):
                bombas_unicas, sistemas_multiplos = selecionar_bombas(df_processado, vazao_para_busca, pressao_para_busca)
                
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

with tab_buscador:
    with st.container(border=True): # NOVO BLOCO VISUAL
        st.markdown(f"#### {T['finder_header']}")
        col_freq_busca, col_modelo_busca, col_motor_busca = st.columns(3)
        
        with col_freq_busca:
            frequencia_buscador = st.radio(
                T['freq_header'], 
                list(ARQUIVOS_DADOS.keys()), 
                horizontal=True, 
                key='freq_buscador'
            )

        caminho_buscador = ARQUIVOS_DADOS[frequencia_buscador]
        df_buscador = carregar_e_processar_dados(caminho_buscador)

        if df_buscador is not None:
            with col_modelo_busca:
                lista_modelos = ["-"] + sorted(df_buscador['MODELO'].unique())
                modelo_selecionado_buscador = st.selectbox(
                    T['model_select_label'],
                    lista_modelos,
                    key='modelo_buscador'
                )

            with col_motor_busca:
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
                if st.button(T['find_pump_button'], use_container_width=True, key='btn_find_pump'):
                    st.session_state.last_used_freq = frequencia_buscador
                    st.session_state.resultado_bombas_unicas = None
                    st.session_state.resultado_sistemas_multiplos = None
                    st.session_state.resultado_busca = None
                    st.session_state.mostrar_grafico = False
                    st.session_state.mostrar_desenho = False
                    st.session_state.mostrar_lista_pecas = False
                    st.session_state.mostrar_desenho_visualizacao = False
                    st.session_state.mostrar_lista_visualizacao = False

                    resultado = buscar_por_modelo_e_motor(df_buscador, modelo_selecionado_buscador, motor_selecionado_buscador)
                    
                    if not resultado.empty:
                        st.session_state.resultado_bombas_unicas = resultado
                        st.session_state.resultado_sistemas_multiplos = pd.DataFrame()
                        st.session_state.modo_visualizacao = 'unicas'
                        st.session_state.resultado_busca = {"resultado": resultado}
                    else:
                        st.session_state.resultado_busca = None
                        st.error(T['no_solution_error'])
                    
                    st.rerun()

if st.session_state.resultado_busca is not None:
    with st.container(border=True): # NOVO BLOCO VISUAL para resultados
        if st.session_state.get('modo_visualizacao') == 'multiplas':
            resultado = st.session_state.get('resultado_sistemas_multiplos', pd.DataFrame())
        else:
            resultado = st.session_state.get('resultado_bombas_unicas', pd.DataFrame())

        st.divider()
        st.header(T['results_header'])
        
        if st.session_state.get('modo_visualizacao') == 'unicas':
            st.info(T['view_mode_unique'])
        else:
            st.info(T['view_mode_systems'])

        tem_unicas = st.session_state.get('resultado_bombas_unicas') is not None and not st.session_state.resultado_bombas_unicas.empty
        tem_multiplas = st.session_state.get('resultado_sistemas_multiplos') is not None and not st.session_state.resultado_sistemas_multiplos.empty
        
        if tem_unicas or tem_multiplas:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(T['show_unique_button'], 
                            use_container_width=True,
                            disabled=not tem_unicas or st.session_state.modo_visualizacao == 'unicas',
                            help="Exibir bombas únicas" if tem_unicas else "Nenhuma bomba única disponível"):
                    st.session_state.modo_visualizacao = 'unicas'
                    st.rerun()
            with col2:
                if st.button(T['show_systems_button'], 
                            use_container_width=True,
                            disabled=not tem_multiplas or st.session_state.modo_visualizacao == 'multiplas',
                            help="Exibir sistemas múltiplos" if tem_multiplas else "Nenhum sistema múltiplo disponível"):
                    st.session_state.modo_visualizacao = 'multiplas'
                    st.rerun()

        if resultado.empty:
            if st.session_state.get('modo_visualizacao') == 'unicas':
                st.error(T['no_unique_pumps'])
            else:
                st.error(T['no_systems_found'])
        else:
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
            selecao_ranking = st.radio("Selecione a bomba:", options=opcoes_ranking, index=0, horizontal=True, label_visibility="collapsed", key=f'radio_selecao_{st.session_state.modo_visualizacao}')
            for col in ['RENDIMENTO', 'POTÊNCIA', 'MOTOR FINAL', T['pressure_error_header'], T['relative_error_header']]:
                if col in resultado_exibicao.columns:
                    resultado_exibicao[col] = resultado_exibicao[col].map('{:,.2f}'.format)
            
            st.dataframe(resultado_exibicao, hide_index=True, use_container_width=True, column_order=['Ranking', T['system_type_header'], 'MODELO', 'ROTOR', 'RENDIMENTO', 'POTÊNCIA', 'MOTOR FINAL'])
            
    with st.container(border=True): # NOVO BLOCO VISUAL
        st.header(T['graph_header'])
        frequencia_str = st.session_state.get('last_used_freq', '60Hz')
        caminho_pdf = f"pdfs/{frequencia_str}/{modelo_selecionado}.pdf"
        
        if st.button(
            T['view_graph_button'],
            key="btn_visualizar_grafico",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.mostrar_grafico = True
        
        if st.session_state.get('mostrar_grafico', False):
            with st.container(border=True):
                st.subheader(f"Modelo: {modelo_selecionado}")
                mostrar_pdf(caminho_pdf, legenda="Gráfico de Performance")
                if st.button(T['close_graph_button'], key="btn_fechar_grafico", use_container_width=True):
                    st.session_state.mostrar_grafico = False
                    st.rerun()

    with st.container(border=True): # NOVO BLOCO VISUAL
        st.header(T['drawing_header'])
        
        if st.button(T['dimensional_drawing_button'], use_container_width=True, type="primary"):
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
                        if st.button(T['close_view_button'], use_container_width=True, key='fechar_desenho', type="secondary"):
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
                
                link_contato = "https://wa.me/5551991808303?text=Ol%C3%A1!%20Preciso%20do%20desenho%20dimensional%20de%20uma%20bomba%20Higra%20Mining."
                st.link_button(T['contact_button'], link_contato, use_container_width=True)
    
    with st.container(border=True): # NOVO BLOCO VISUAL
        st.header(T['parts_list_header'])
        
        if st.button(T['parts_list_button'], use_container_width=True, type="primary"):
            st.session_state.mostrar_lista_pecas = not st.session_state.get('mostrar_lista_pecas', False)

        if st.session_state.get('mostrar_lista_pecas', False):
            with st.container(border=True):
                caminho_lista_pecas = Path(f"Lista/{modelo_selecionado}.pdf")
                
                link_contato_pecas = "https://wa.me/5551991808303?text=Ol%C3%A1!%20Preciso%20de%20ajuda%20com%20uma%20lista%20de%C3%A7as%20para%20uma%20bomba%20Higra%20Mining."

                if caminho_lista_pecas.exists():
                    st.info(T['parts_list_warning'])
                    if st.button(T['view_parts_list_button'], use_container_width=True, type="secondary"):
                        st.session_state.mostrar_lista_visualizacao = not st.session_state.get('mostrar_lista_visualizacao', False)

                    if st.session_state.get('mostrar_lista_visualizacao', False):
                        mostrar_pdf(caminho_lista_pecas, legenda="Lista de Peças")
                        if st.button(T['close_view_button'], use_container_width=True, key='fechar_lista', type="secondary"):
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
                    
                    st.link_button(T['contact_button'], link_contato_pecas, use_container_width=True)
                else:
                    st.warning(T['parts_list_unavailable'])
                    st.link_button(T['contact_button'], link_contato_pecas, use_container_width=True)
