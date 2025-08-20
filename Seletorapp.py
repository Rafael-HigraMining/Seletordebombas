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
# NOVA FUNÇÃO PARA EXIBIR PDF
# ===================================================================
def mostrar_pdf(caminho_arquivo, legenda="Visualização do Documento"):
    """Exibe a primeira página de um PDF como imagem diretamente no Streamlit."""
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        import io
        
        # Abre o arquivo PDF
        doc = fitz.open(caminho_arquivo)
        
        # Seleciona a primeira página
        page = doc.load_page(0)
        
        # Renderiza a página como imagem (aumentando a resolução)
        zoom = 3.0  # Aumenta a qualidade
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Converte para formato PIL Image
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        
        # CORREÇÃO: Usa a legenda que foi passada como parâmetro
        st.image(image, caption=legenda, use_container_width=True)
        
    except FileNotFoundError:
        st.warning(f"Arquivo não encontrado para este modelo.")
    except Exception as e:
        st.error(f"Não foi possível exibir o PDF: {e}")

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
        'performance_note': "Note: Our advanced calculations to find the ideal pump may take a few seconds. We appreciate your patience!",
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
        # st.error(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except Exception as e:
        # st.error(f"Ocorreu um erro ao ler o Excel: {e}")
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
    # Adicionado + 1e-9 para evitar divisão por zero se min == max
    df["ERRO_RELATIVO"] = ((df["VAZÃO (M³/H)"] - df["VAZAO_CENTRO"]) / (df["max"] - df["min"] + 1e-9)) * 100
    df["ABS_ERRO_RELATIVO"] = df["ERRO_RELATIVO"].abs()
    return df
# ===================================================================
# NOVA FUNÇÃO OTIMIZADA PARA O BUSCADOR POR MODELO
# ===================================================================
def buscar_por_modelo_e_motor(df, modelo, motor):
    """
    Função rápida e simples para buscar a melhor bomba quando o modelo e o motor já são conhecidos.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Filtro direto e rápido no DataFrame
    df_filtrado = df[
        (df['MODELO'] == modelo) &
        (df['MOTOR PADRÃO (CV)'] == motor)
    ]
    
    if df_filtrado.empty:
        return pd.DataFrame()
        
    # Pega a melhor opção baseada no maior rendimento
    melhor_opcao = df_filtrado.loc[df_filtrado['RENDIMENTO (%)'].idxmax()]
    
    # Formata o resultado para ser compatível com o resto da interface
    resultado_df = pd.DataFrame([melhor_opcao])
    
    # Prepara as colunas finais
    colunas_finais = [
       'MODELO', 'ROTOR', 'VAZÃO (M³/H)', 'PRESSÃO (MCA)', 'ERRO_PRESSAO', 'ERRO_RELATIVO',
       'RENDIMENTO (%)', 'POTÊNCIA (HP)', 'MOTOR FINAL (CV)'
    ]
    
    # Renomeia 'MOTOR PADRÃO (CV)' para 'MOTOR FINAL (CV)' para consistência
    resultado_df = resultado_df.rename(columns={'MOTOR PADRÃO (CV)': 'MOTOR FINAL (CV)'})

    # Remove a coluna de texto 'ROTOR' e renomeia 'ROTORNUM'
    if 'ROTOR' in resultado_df.columns:
        resultado_df = resultado_df.drop(columns=['ROTOR'])
    resultado_df = resultado_df.rename(columns={'ROTORNUM': 'ROTOR'})
    
    # Garante que apenas colunas existentes sejam retornadas
    colunas_presentes = [col for col in colunas_finais if col in resultado_df.columns]
    
    return resultado_df[colunas_presentes]
# ===================================================================
# FUNÇÃO PRINCIPAL COM A LÓGICA DE FILTRAGEM CORRIGIDA
# ===================================================================
def filtrar_e_classificar(df, vazao, pressao, top_n=5, limite_desempate_rendimento=3):
    if df is None or df.empty: 
        return pd.DataFrame()

    # 1. Filtro inicial por vazão (mais eficiente)
    mask_vazao = df["VAZÃO (M³/H)"] == vazao
    if not mask_vazao.any():
        return pd.DataFrame()

    df_vazao = df.loc[mask_vazao].copy()
    
    # 2. Calcular pressões min/max por modelo sem múltiplos merges
    min_max = df_vazao.groupby('MODELO')['PRESSÃO (MCA)'].agg(['min', 'max']).reset_index()
    min_max.columns = ['MODELO', 'PRESSAO_DO_ROTOR_MIN', 'PRESSAO_DO_ROTOR_MAX']
    
    df_vazao = df_vazao.merge(min_max, on='MODELO', how='left')
    
    # 3. Calcular limites e filtrar de forma vetorizada
    limite_inferior = df_vazao['PRESSAO_DO_ROTOR_MIN'] * 0.99
    limite_superior = df_vazao['PRESSAO_DO_ROTOR_MAX'] * 1.01
    
    mask_limites = (pressao >= limite_inferior) & (pressao <= limite_superior)
    df_filtrado = df_vazao.loc[mask_limites].copy()
    
    if df_filtrado.empty:
        return pd.DataFrame()

    # Restante do seu código (preservado)
    df_filtrado["ERRO_PRESSAO"] = df_filtrado["PRESSÃO (MCA)"] - pressao
    df_filtrado["MOTOR FINAL (CV)"] = df_filtrado["POTÊNCIA (HP)"].apply(encontrar_motor_final)
    df_filtrado["ERRO_PRESSAO_ABS"] = df_filtrado["ERRO_PRESSAO"].abs()
    

    # ===================================================================
    # A PARTIR DAQUI, O SEU CÓDIGO ORIGINAL É PRESERVADO
    # ===================================================================

    # ETAPA 2: CÁLCULOS BÁSICOS
    df_filtrado["ERRO_PRESSAO"] = df_filtrado["PRESSÃO (MCA)"] - pressao
    df_filtrado["MOTOR FINAL (CV)"] = df_filtrado["POTÊNCIA (HP)"].apply(encontrar_motor_final)
    df_filtrado["ERRO_PRESSAO_ABS"] = df_filtrado["ERRO_PRESSAO"].abs()
    
    if df_filtrado.empty: return pd.DataFrame()
    
    # ETAPA 3: LÓGICA DE ORDENAÇÃO
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
       'RENDIMENTO (%)', 'POTÊNCIA (HP)', 'MOTOR FINAL (CV)'
    ]
    
    # CORREÇÃO: Para evitar o erro de coluna duplicada, removemos a coluna 'ROTOR' original (texto)
    # antes de renomear a coluna numérica 'ROTORNUM' para 'ROTOR'.
    if 'ROTOR' in df_resultado.columns:
        df_resultado = df_resultado.drop(columns=['ROTOR'])
        
    # Renomeando ROTORNUM para ROTOR para corresponder à sua saída desejada
    df_resultado = df_resultado.rename(columns={'ROTORNUM': 'ROTOR'})
    
    colunas_presentes = [col for col in colunas_finais if col in df_resultado.columns]
    
    return df_resultado[colunas_presentes]

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
# CABEÇALHO COM LOGO E SELEÇÃO DE IDIOMA (VERSÃO ATUALIZADA)
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
        st.image("logo.png", width=900)
    except Exception:
        st.warning("Logo não encontrada.")

with col_bandeiras:
    # Cria colunas para cada bandeira ficarem lado a lado
    flag_cols = st.columns(len(bandeiras))
    for i, (lang_code, info) in enumerate(bandeiras.items()):
        with flag_cols[i]:
            classe_css = "selecionada" if st.session_state.lang == lang_code else ""
            img_base64 = image_to_base64(info["img"])

            # Unimos o texto e a imagem dentro de um único link (tag <a>).
            # O href="?lang=..." instrui o Streamlit a recarregar a página com o novo idioma.
            # O target="_self" garante que a página recarregue na mesma aba.
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




# Atualiza a variável de tradução APÓS a possível troca de idioma
T = TRADUCOES[st.session_state.lang]

# Título e Mensagem de Boas-vindas
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
# SEÇÃO DE ENTRADAS (VERSÃO CORRIGIDA E REESTRUTURADA)
# ===================================================================

# --- Parte 1: Seletor por Ponto de Trabalho (VERSÃO CORRIGIDA) ---
# ===================================================================
# SEÇÃO DE ENTRADAS REESTRUTURADA COM ABAS (VERSÃO CORRIGIDA)
# ===================================================================

# Cria as duas abas para separar as formas de busca
tab_seletor, tab_buscador = st.tabs([T['selector_tab_label'], T['finder_tab_label']])

# --- Aba 1: Seletor por Ponto de Trabalho ---
with tab_seletor:
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

    # Carrega os dados para o SELETOR
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

    # Botão do SELETOR, agora dentro de sua própria aba
    if df_processado is not None:
        if st.button(T['search_button'], use_container_width=True, key='btn_seletor'):
            # Reseta todos os estados ao iniciar uma nova busca
            st.session_state.resultado_busca = None
            st.session_state.mostrar_grafico = False
            st.session_state.mostrar_desenho = False
            st.session_state.mostrar_lista_pecas = False
            st.session_state.mostrar_desenho_visualizacao = False
            st.session_state.mostrar_lista_visualizacao = False
            
            with st.spinner(T['spinner_text'].format(freq=frequencia_selecionada)):
                resultado, tipo = selecionar_bombas(df_processado, vazao_para_busca, pressao_para_busca, top_n=3)
                if not resultado.empty:
                    st.session_state.resultado_busca = {"resultado": resultado, "tipo": tipo}
                else:
                    st.error(T['no_solution_error'])
            
            st.rerun()

# --- Aba 2: Buscador por Modelo ---
with tab_buscador:
    col_freq_busca, col_modelo_busca, col_motor_busca = st.columns(3)
    
    with col_freq_busca:
        frequencia_buscador = st.radio(
            T['freq_header'], 
            list(ARQUIVOS_DADOS.keys()), 
            horizontal=True, 
            key='freq_buscador'
        )

    # Graças ao cache, esta linha agora é instantânea após a primeira execução
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
            motor_selecionado_buscador = None # Inicializa a variável para evitar erros
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

        # A lógica do botão agora chama a nova função rápida 'buscar_por_modelo_e_motor'
        if modelo_selecionado_buscador and modelo_selecionado_buscador != "-" and motor_selecionado_buscador:
            if st.button(T['find_pump_button'], use_container_width=True, key='btn_find_pump'):
                # Reseta o estado da interface
                st.session_state.resultado_busca = None
                st.session_state.mostrar_grafico = False
                st.session_state.mostrar_desenho = False
                st.session_state.mostrar_lista_pecas = False
                st.session_state.mostrar_desenho_visualizacao = False
                st.session_state.mostrar_lista_visualizacao = False

                # Chama a nova função rápida, que não causa lentidão
                resultado = buscar_por_modelo_e_motor(df_buscador, modelo_selecionado_buscador, motor_selecionado_buscador)
                
                if not resultado.empty:
                    st.session_state.resultado_busca = {"resultado": resultado, "tipo": "unica"}
                else:
                    st.session_state.resultado_busca = None # Limpa o resultado se nada for encontrado
                    st.error(T['no_solution_error'])
                
                st.rerun()
                
# O bloco de exibição de resultados abaixo desta linha permanece o mesmo.
# --- Parte 3: Exibição dos Resultados (o código abaixo permanece o mesmo) ---
# A linha 'if st.session_state.resultado_busca:' já existe no seu código,
# então a substituição termina antes dela.

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
        
        # ===================================================================
        # SEÇÃO DE EXIBIÇÃO DO GRÁFICO (DENTRO DO BLOCO COM RESULTADOS)
        # ===================================================================
    st.divider()
        # Corrigido para usar a tradução
    st.header(T['graph_header']) 
        
        # Obtém o modelo selecionado
    modelo_selecionado = resultado.iloc[0]['MODELO']
    frequencia_str = frequencia_selecionada
    caminho_pdf = f"pdfs/{frequencia_str}/{modelo_selecionado}.pdf"
        
        # Botão estilizado para visualizar o gráfico
    if st.button(
        T['view_graph_button'],
        key="btn_visualizar_grafico",
        use_container_width=True,
        type="primary",
    ):
        st.session_state.mostrar_grafico = True
            
    st.divider()

 # ===================================================================
        # SEÇÃO DE DOWNLOAD DO DESENHO DIMENSIONAL (COM CAIXA EXPANSÍVEL)
        # ===================================================================
# ADICIONE AS 2 LINHAS ABAIXO
        
    st.header(T['drawing_header'])
        
        # 1. Botão principal que abre/fecha a seção do desenho
    if st.button(T['dimensional_drawing_button'], use_container_width=True):
        st.session_state.mostrar_desenho = not st.session_state.get('mostrar_desenho', False)

        # 2. Container que só aparece quando o botão acima é clicado
    if st.session_state.get('mostrar_desenho', False):
        with st.container(border=True):
                # Mensagem de aviso padrão
            st.info(T['dimensional_drawing_warning'])

                # A lógica de busca do arquivo (que já tínhamos) agora fica DENTRO do container
                # -------------------------------------------------------------------------
                
                # a. Obter dados da bomba selecionada (top 1)
            melhor_bomba = resultado.iloc[0]
            modelo_selecionado = melhor_bomba['MODELO']
            motor_alvo = int(melhor_bomba['MOTOR FINAL (CV)'])

                # b. Preparar para a busca na pasta "Desenhos"
            desenho_base_path = Path("Desenhos")
            caminho_desenho_final = None
                
                # c. Lógica de busca por motor mais próximo
            if desenho_base_path.exists():
                desenhos_candidatos = {} # Dicionário para guardar {motor_disponivel: caminho_completo}
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
                
                # d. Fallback para o nome geral
            if not caminho_desenho_final:
                caminho_geral = desenho_base_path / f"{modelo_selecionado}.pdf"
                if caminho_geral.exists():
                    caminho_desenho_final = caminho_geral

# e. Exibe os botões e a visualização condicional
            if caminho_desenho_final:
                    # Botão para pré-visualizar o PDF como imagem
                if st.button(T['view_drawing_button'], use_container_width=True, type="secondary"):
                    st.session_state.mostrar_desenho_visualizacao = not st.session_state.get('mostrar_desenho_visualizacao', False)

                    # Se o botão de visualizar foi clicado, mostra a imagem e o botão de fechar
                if st.session_state.get('mostrar_desenho_visualizacao', False):
                    mostrar_pdf(caminho_desenho_final, legenda="Desenho Dimensional")
                    if st.button(T['close_view_button'], use_container_width=True, key='fechar_desenho'):
                        st.session_state.mostrar_desenho_visualizacao = False
                        st.rerun()
                    
                    # Botão para fazer o download do arquivo
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
                    
                # f. Exibe o botão de Contato em ambos os casos (arquivo encontrado ou não)
            link_contato = "https://wa.me/5551991808303?text=Ol%C3%A1!%20Preciso%20do%20desenho%20dimensional%20de%20uma%20bomba%20Higra%20Mining."
            st.markdown(f'''
            <a href="{link_contato}" target="_blank" style="
                display: block; 
                padding: 0.5rem 1rem; 
                background-color: {COR_PRIMARIA};
                color: white; 
                font-weight: bold; 
                text-align: center;
                text-decoration: none; 
                border-radius: 8px; 
                border: 2px solid {COR_PRIMARIA};
                box-sizing: border-box;
                margin-top: 10px;
            ">
                {T['contact_button']}
            </a>
            ''', unsafe_allow_html=True)
                
    st.divider()

# Adiciona uma linha para separar as seções

        # ===================================================================
        # SEÇÃO LISTA DE PEÇAS
        # ===================================================================
        
    st.header(T['parts_list_header'])
        
        # 1. Botão principal que abre/fecha a seção da lista de peças
    if st.button(T['parts_list_button'], use_container_width=True):
            # Inverte o estado atual (se era False, vira True, e vice-versa)
        st.session_state.mostrar_lista_pecas = not st.session_state.get('mostrar_lista_pecas', False)

        # 2. Container que só aparece quando o botão acima for clicado
    if st.session_state.get('mostrar_lista_pecas', False):
        with st.container(border=True):
                # Lógica de busca do arquivo (simples, só por modelo, na pasta "Lista")
            caminho_lista_pecas = Path(f"Lista/{modelo_selecionado}.pdf")
                
                # Link de contato para o WhatsApp
            link_contato_pecas = "https://wa.me/5551991808303?text=Ol%C3%A1!%20Preciso%20de%20ajuda%20com%20uma%20lista%20de%20pe%C3%A7as%20para%20uma%20bomba%20Higra%20Mining."
            botao_contato_html = f'''
            <a href="{link_contato_pecas}" target="_blank" style="
                display: block; 
                padding: 0.5rem 1rem; 
                background-color: {COR_PRIMARIA};
                color: white; 
                font-weight: bold; 
                text-align: center;
                text-decoration: none; 
                border-radius: 8px; 
                border: 2px solid {COR_PRIMARIA};
                box-sizing: border-box;
                margin-top: 10px;
            ">
                {T['contact_button']}
            </a>
            '''

# CASO A: O arquivo da lista de peças EXISTE
            if caminho_lista_pecas.exists():
                st.info(T['parts_list_warning']) # Mensagem de aviso
                    
                    # Botão para pré-visualizar a lista de peças
                if st.button(T['view_parts_list_button'], use_container_width=True, type="secondary"):
                    st.session_state.mostrar_lista_visualizacao = not st.session_state.get('mostrar_lista_visualizacao', False)

                    # Se o botão de visualizar foi clicado, mostra a imagem e o botão de fechar
                if st.session_state.get('mostrar_lista_visualizacao', False):
                    mostrar_pdf(caminho_lista_pecas, legenda="Lista de Peças")
                    if st.button(T['close_view_button'], use_container_width=True, key='fechar_lista'):
                        st.session_state.mostrar_lista_visualizacao = False
                        st.rerun()

                    # Botão para fazer o download do arquivo
                with open(caminho_lista_pecas, "rb") as pdf_file:
                    st.download_button(
                        label=T['download_parts_list_button'],
                        data=pdf_file,
                        file_name=caminho_lista_pecas.name,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Exibe o botão de contato logo abaixo
                st.markdown(botao_contato_html, unsafe_allow_html=True)

                # CASO B: O arquivo da lista de peças NÃO existe
            else:
                st.warning(T['parts_list_unavailable'])
                    
                    # Exibe apenas o botão de contato
                st.markdown(botao_contato_html, unsafe_allow_html=True)
                    
        # Verifica se devemos mostrar o gráfico
    if st.session_state.get('mostrar_grafico', False):
            # O container e tudo dentro dele precisa estar INDENTADO (com mais espaços)
            # para pertencer ao 'if' acima.
        with st.container(border=True):
            st.subheader(f"Modelo: {modelo_selecionado}")
            mostrar_pdf(caminho_pdf, legenda="Gráfico de Performance")

                # O botão de fechar também deve aparecer junto com o gráfico
            if st.button(T['close_graph_button'], key="btn_fechar_grafico", use_container_width=True):
                st.session_state.mostrar_grafico = False
                st.rerun() # Adicionado para fechar o gráfico instantaneamente
                
        # O código do formulário de orçamento que já existe continua depois daqui....
                
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
                    

