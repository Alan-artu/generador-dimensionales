import streamlit as st
import ezdxf
from ezdxf.enums import TextEntityAlignment
import os
import datetime
import math
import io

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y VARIABLES
# ==========================================
st.set_page_config(page_title="Generador Dimensionales Industronic", layout="wide")

GAP_GABINETES = 20  
FACTOR_ESCALA = 10  
CARPETA_BLOQUES = "bloques"

# --- PANEL DE CONTROL DE DISTANCIAS (AJUSTE FINO) ---
POS_X_TABLA = 0       
POS_Y_TABLA = -330    
GAP_FILAS_PARALELO = 220  
GAP_Y_VISTAS = 100           
GAP_X_LATERAL = 600          
OFFSET_Y_TITULO = -150       
OFFSET_Y_MARCO_GRANDE = -200 
OFFSET_Y_MARCO_CHICO = -100  

# --- COORDENADAS DEL MARCO BASE ---
MARCO_DIBUJO_X, MARCO_DIBUJO_Y = 980.55, 27.71
MARCO_PROYECTO_X, MARCO_PROYECTO_Y = 980.55, 65.0
# --- CONFIGURACIÓN DE MARCOS ESTÁNDAR (MEDIDAS EN MM) ---
MARCOS_DISPONIBLES = {
    "C": {"ancho": 560, "alto": 432},
    "D": {"ancho": 864, "alto": 560},
    "E": {"ancho": 1120, "alto": 864}
}
MARGEN_MARCO = 100  # Margen de seguridad en mm para que el dibujo no toque el borde

# ==========================================
# 2. BASE DE DATOS MAESTRA
# ==========================================
TABLA_PLOMO_AUTOMATICA = {
    "10-44": {"sap": "262702", "cant": 1, "peso": 420}, "10-60": {"sap": "262702", "cant": 1, "peso": 480}, "10-120": {"sap": "262702", "cant": 1, "peso": 710},
    "15-20": {"sap": "262702", "cant": 1, "peso": 370}, "15-30": {"sap": "264340", "cant": 1, "peso": 520}, "15-45": {"sap": "330904", "cant": 1, "peso": 600}, "15-60": {"sap": "262702", "cant": 1, "peso": 620},
    "20-15": {"sap": "262702", "cant": 1, "peso": 400}, "20-20": {"sap": "262702", "cant": 1, "peso": 420}, "20-30": {"sap": "262702", "cant": 1, "peso": 520}, "20-44": {"sap": "262730", "cant": 1, "peso": 720},
    "30-15": {"sap": "262702", "cant": 1, "peso": 520}, "30-30": {"sap": "264340", "cant": 1, "peso": 770}, "30-60": {"sap": "262730", "cant": 1, "peso": 1110},
    "40-10": {"sap": "262702", "cant": 1, "peso": 570}, "40-15": {"sap": "330904", "cant": 1, "peso": 690}, "40-30": {"sap": "264303", "cant": 1, "peso": 1080}, "40-60": {"sap": "330904", "cant": 2, "peso": 870}, "40-90": {"sap": "265023", "cant": 2, "peso": 1200},
    "60-05": {"sap": "262702", "cant": 1, "peso": 630}, "60-10": {"sap": "262730", "cant": 1, "peso": 900}, "60-15": {"sap": "264303", "cant": 1, "peso": 965}, "60-30": {"sap": "265023", "cant": 1, "peso": 1620}, "60-60": {"sap": "264303", "cant": 2, "peso": 1165}, "60-90": {"sap": "264303", "cant": 2, "peso": 1360},
    "80-05": {"sap": "264303", "cant": 1, "peso": 790}, "80-10": {"sap": "264303", "cant": 1, "peso": 1090}, "80-15": {"sap": "264303", "cant": 1, "peso": 1200}, "80-30": {"sap": "265023", "cant": 1, "peso": 1960}, "80-60": {"sap": "265023", "cant": 2, "peso": 1610},
    "100-05": {"sap": "265023", "cant": 1, "peso": 1210}, "100-10": {"sap": "265023", "cant": 1, "peso": 1500}, "100-15": {"sap": "265023", "cant": 1, "peso": 1640}, "100-30": {"sap": "264303", "cant": 2, "peso": 1250}, "100-60": {"sap": "265023", "cant": 2, "peso": 1810},
    "120-05": {"sap": "264303", "cant": 1, "peso": 1220}, "120-10": {"sap": "265023", "cant": 1, "peso": 1680}, "120-15": {"sap": "265023", "cant": 1, "peso": 1970}, "120-30": {"sap": "264303", "cant": 2, "peso": 1370}, "120-60": {"sap": "265023", "cant": 2, "peso": 2220},
    "160-05": {"sap": "265023", "cant": 1, "peso": 1640}, "160-10": {"sap": "265023", "cant": 2, "peso": 2090}, "160-15": {"sap": "264303", "cant": 2, "peso": 1200}, "160-30": {"sap": "265023", "cant": 2, "peso": 2100}, "160-60": {"sap": "265023", "cant": 3, "peso": 2020},
    "200-05": {"sap": "265023", "cant": 1, "peso": 2000}, "200-10": {"sap": "265023", "cant": 2, "peso": 1450}, "200-15": {"sap": "264270", "cant": 2, "peso": 1470}, "200-30": {"sap": "265023", "cant": 2, "peso": 2180}, "200-60": {"sap": "265023", "cant": 3, "peso": 2040},
    "300-05": {"sap": "265023", "cant": 2, "peso": 1640}, "300-10": {"sap": "265025", "cant": 2, "peso": 1780}, "300-15": {"sap": "265025", "cant": 2, "peso": 2260}, "300-30": {"sap": "265026", "cant": 3, "peso": 2320},
    "400-05": {"sap": "265023", "cant": 3, "peso": 1465}, "400-10": {"sap": "265023", "cant": 3, "peso": 1790}, "400-15": {"sap": "265023", "cant": 3, "peso": 1940},
    "500-05": {"sap": "265023", "cant": 3, "peso": 1670}, "500-10": {"sap": "265023", "cant": 3, "peso": 1830}, "500-15": {"sap": "265023", "cant": 3, "peso": 2070},
    "600-05": {"sap": "265023", "cant": 3, "peso": 1980}, "600-10": {"sap": "265023", "cant": 3, "peso": 2160},
    "800-05": {"sap": "265023", "cant": 3, "peso": 2320},
    "1000-05": {"sap": "265023", "cant": 4, "peso": 2200}
}

TABLA_LITIO_AUTOMATICA = {
    "60-10": {"cant": 1, "peso": 440}, "60-15": {"cant": 1, "peso": 445}, "60-30": {"cant": 1, "peso": 630}, "60-60": {"cant": 1, "peso": 756},
    "80-10": {"cant": 1, "peso": 510}, "80-15": {"cant": 1, "peso": 519}, "80-30": {"cant": 1, "peso": 741}, "80-60": {"cant": 2, "peso": 600},
    "100-10": {"cant": 1, "peso": 545}, "100-15": {"cant": 1, "peso": 556}, "100-20": {"cant": 1, "peso": 667}, "100-30": {"cant": 1, "peso": 852}, "100-60": {"cant": 2, "peso": 652},
    "120-10": {"cant": 1, "peso": 580}, "120-15": {"cant": 1, "peso": 630}, "120-30": {"cant": 1, "peso": 1000}, "120-60": {"cant": 2, "peso": 756},
    "160-10": {"cant": 1, "peso": 685}, "160-15": {"cant": 1, "peso": 741}, "160-20": {"cant": 1, "peso": 889}, "160-30": {"cant": 2, "peso": 741}, "160-60": {"cant": 3, "peso": 704},
    "200-10": {"cant": 1, "peso": 790}, "200-15": {"cant": 1, "peso": 852}, "200-20": {"cant": 2, "peso": 667}, "200-30": {"cant": 2, "peso": 852}, "200-60": {"cant": 3, "peso": 808},
    "300-10": {"cant": 2, "peso": 650}, "300-15": {"cant": 2, "peso": 704}, "300-20": {"cant": 2, "peso": 852}, "300-30": {"cant": 3, "peso": 852}, "300-60": {"cant": 4, "peso": 1068}, "300-120": {"cant": 8, "peso": 860}, "300-180": {"cant": 12, "peso": 860}, "300-224": {"cant": 15, "peso": 860},
    "400-10": {"cant": 2, "peso": 790}, "400-15": {"cant": 2, "peso": 852}, "400-30": {"cant": 4, "peso": 852}, "400-60": {"cant": 6, "peso": 808}, "400-120": {"cant": 11, "peso": 860}, "400-168": {"cant": 18, "peso": 756},
    "500-10": {"cant": 2, "peso": 825}, "500-15": {"cant": 2, "peso": 1000}, "500-30": {"cant": 4, "peso": 1000}, "500-60": {"cant": 7, "peso": 860}, "500-120": {"cant": 16, "peso": 756}, "500-134": {"cant": 18, "peso": 756},
    "600-10": {"cant": 3, "peso": 790}, "600-15": {"cant": 3, "peso": 852}, "600-30": {"cant": 5, "peso": 963}, "600-60": {"cant": 10, "peso": 756}, "600-112": {"cant": 18, "peso": 756},
    "800-10": {"cant": 3, "peso": 965}, "800-15": {"cant": 4, "peso": 852}, "800-30": {"cant": 7, "peso": 963}, "800-60": {"cant": 11, "peso": 860}, "800-84": {"cant": 18, "peso": 756},
    "1000-10": {"cant": 4, "peso": 895}, "1000-15": {"cant": 4, "peso": 1000}, "1000-30": {"cant": 8, "peso": 1000}, "1000-60": {"cant": 16, "peso": 756},
    "1200-10": {"cant": 5, "peso": 895}, "1200-15": {"cant": 5, "peso": 1000}, "1200-20": {"cant": 7, "peso": 963}, "1200-30": {"cant": 10, "peso": 963}, "1200-46": {"cant": 15, "peso": 1000}
}

BASE_DATOS_UPS = {
    "1310": {"alto": 1100, "ancho": 358, "fondo": 883, "peso": 93, "dxf": "ups_1310"}, "1315": {"alto": 1100, "ancho": 358, "fondo": 883, "peso": 109, "dxf": "ups_1315"},
    "1320": {"alto": 1100, "ancho": 358, "fondo": 883, "peso": 109, "dxf": "ups_1320"}, "1330": {"alto": 1250, "ancho": 378, "fondo": 883, "peso": 117, "dxf": "ups_1330"},
    "1340": {"alto": 1250, "ancho": 358, "fondo": 835, "peso": 89, "dxf": "ups_1340"}, "1360 127V": {"alto": 1800, "ancho": 600, "fondo": 1000, "peso": 230, "dxf": "ups_1360_127"},
    "1360 230-400V": {"alto": 1200, "ancho": 400, "fondo": 960, "peso": 145, "dxf": "ups_1360_230"}, "1380": {"alto": 1800, "ancho": 600, "fondo": 1000, "peso": 230, "dxf": "ups_1380"},
    "13100": {"alto": 1800, "ancho": 600, "fondo": 1000, "peso": 230, "dxf": "ups_13100"}, "13120": {"alto": 1800, "ancho": 600, "fondo": 1000, "peso": 230, "dxf": "ups_13120"},
    "13160": {"alto": 1800, "ancho": 600, "fondo": 1000, "peso": 320, "dxf": "ups_13160"}, "13200": {"alto": 1800, "ancho": 600, "fondo": 1000, "peso": 320, "dxf": "ups_13200"},
    "13300 230V": {"alto": 1950, "ancho": 1000, "fondo": 900, "peso": 750, "dxf": "ups_13300_230"}, "13300 277V": {"alto": 1950, "ancho": 1000, "fondo": 900, "peso": 750, "dxf": "ups_13300_277"},
    "13400 230V": {"alto": 1950, "ancho": 1000, "fondo": 900, "peso": 750, "dxf": "ups_13400_230"}, "13400 277V": {"alto": 1950, "ancho": 1000, "fondo": 900, "peso": 750, "dxf": "ups_13400_277"},
    "13500 230V": {"alto": 1950, "ancho": 1400, "fondo": 900, "peso": 1100, "dxf": "ups_13500_230"}, "13500 277V": {"alto": 1950, "ancho": 1400, "fondo": 900, "peso": 1100, "dxf": "ups_13500_277"},
    "13600 230V": {"alto": 1950, "ancho": 1400, "fondo": 900, "peso": 1100, "dxf": "ups_13600_230"}, "13600 277V": {"alto": 1950, "ancho": 1400, "fondo": 900, "peso": 1100, "dxf": "ups_13600_277"},
    "13800 230V": {"alto": 1950, "ancho": 1900, "fondo": 900, "peso": 1450, "dxf": "ups_13800_230"}, "13800 277V": {"alto": 1950, "ancho": 1900, "fondo": 900, "peso": 1450, "dxf": "ups_13800_277"},
    "131000 230V": {"alto": 1950, "ancho": 3000, "fondo": 900, "peso": 2400, "dxf": "ups_131000_230"}, "131000 277V": {"alto": 1950, "ancho": 3000, "fondo": 900, "peso": 2400, "dxf": "ups_131000_277"},
    "131200 230V": {"alto": 1950, "ancho": 3000, "fondo": 900, "peso": 2400, "dxf": "ups_131200_230"}, "131200 277V": {"alto": 1950, "ancho": 3000, "fondo": 900, "peso": 2400, "dxf": "ups_131200_277"}
}

BASE_DATOS_MODULOS = {
    "Ninguno": {"alto": 0, "ancho": 0, "fondo": 0, "dxf": None},
    "263361": {"alto": 1100, "ancho": 447, "fondo": 901, "dxf": "mod_263361"}, "264145": {"alto": 1200, "ancho": 600, "fondo": 900, "dxf": "mod_264145"},
    "264172": {"alto": 1250, "ancho": 600, "fondo": 900, "dxf": "mod_264172"}, "264175": {"alto": 1950, "ancho": 1136, "fondo": 1200, "dxf": "mod_264175"},
    "264450": {"alto": 1800, "ancho": 715, "fondo": 1000, "dxf": "mod_264450"}, "264600": {"alto": 440, "ancho": 260, "fondo": 680, "dxf": "mod_264600"}
}

BASE_DATOS_GABPAR = {
    "265233": {"alto": 1020, "ancho": 855, "fondo": 300, "peso": "", "dxf": "gabpar_265233"},
    "265191": {"alto": 1860, "ancho": 1575, "fondo": 1270, "peso": "", "dxf": "gabpar_265191"},
    "265400": {"alto": 1950, "ancho": 1136, "fondo": 1200, "peso": "", "dxf": "gabpar_265400"},
    "264885": {"alto": 842, "ancho": 635, "fondo": 247, "peso": "", "dxf": "gabpar_264885"},
    "264840": {"alto": 596, "ancho": 445, "fondo": 123, "peso": "", "dxf": "gabpar_264840"}
}

BASE_DATOS_GABCONX = {
    "SAP_CONX1": {"alto": 1950, "ancho": 600, "fondo": 900, "dxf": "gabconx_SAP"},
    "SAP_CONX2": {"alto": 1950, "ancho": 800, "fondo": 900, "dxf": "gabconx_SAP2"}
}

BASE_DATOS_PLOMO = {
    "Ninguno": {"alto": 0, "ancho": 0, "fondo": 0, "dxf": None},
    "262702": {"alto": 1600, "ancho": 623, "fondo": 900, "dxf": "bat_262702"}, "262730": {"alto": 1600, "ancho": 1100, "fondo": 900, "dxf": "bat_262730"},
    "263243": {"alto": 2000, "ancho": 800, "fondo": 1100, "dxf": "bat_263243"}, "263530": {"alto": 2100, "ancho": 900, "fondo": 1200, "dxf": "bat_263530"},
    "264270": {"alto": 2110, "ancho": 850, "fondo": 1150, "dxf": "bat_264270"}, "264303": {"alto": 1800, "ancho": 800, "fondo": 1000, "dxf": "bat_264303"},
    "264340": {"alto": 1250, "ancho": 800, "fondo": 1000, "dxf": "bat_264340"}, "265023": {"alto": 2110, "ancho": 813, "fondo": 1245, "dxf": "bat_265023"},
    "265025": {"alto": 2110, "ancho": 813, "fondo": 1245, "dxf": "bat_265025"}, "265026": {"alto": 2110, "ancho": 813, "fondo": 1245, "dxf": "bat_265026"},
    "330900": {"alto": 1800, "ancho": 1120, "fondo": 1000, "dxf": "bat_330900"}, "330904": {"alto": 1600, "ancho": 959, "fondo": 825, "dxf": "bat_330904"}
}

GABINETE_LITIO = {"alto": 2000, "ancho": 600, "fondo": 860, "dxf": "bat_litio"}
GABINETE_DIST_LITIO = {"alto": 2000, "ancho": 600, "fondo": 860, "peso": 150, "dxf": "distrubucion_litio"} 

LISTA_VOLTAJES = ["120/208", "127/220", "220/380", "230/400", "254/440", "266/460", "277/480", "208D", "220D", "380D", "400D", "440D", "460D", "480D"]

def extraer_kva(modelo_str):
    try: return str(int(modelo_str.split()[0][2:]))
    except: return "0"

@st.cache_data
def obtener_imagen(nombre_dxf):
    if not nombre_dxf: return None
    for ext in [".jpg", ".png", ".jpeg"]:
        ruta = os.path.join("imagenes", nombre_dxf + ext)
        if os.path.exists(ruta): return ruta
    return None

# ==========================================
# 3. INTERFAZ WEB STREAMLIT
# ==========================================
encabezado_html = """
<style>
    /* Efecto elegante para todas las listas desplegables */
    div[data-baseweb="select"] > div {
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="select"] > div:hover, div[data-baseweb="select"] > div:focus-within {
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.2) !important;
    }
    
    /* 1. Encerrar ÚNICAMENTE las 4 columnas principales en "Tarjetas" (Cards) */
    /* La regla :has(h3) asegura que solo se formatee la columna si contiene un título h3 */
    div[data-testid="stColumn"]:has(h3) {
        background-color: rgba(23, 27, 36, 0.8) !important; 
        border: 1px solid #374151 !important; 
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important;
    }
    
    /* 2. Ola Blanca translúcida de fondo fijada abajo */
    .stApp {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23ffffff' fill-opacity='0.05' d='M0,160L48,170.7C96,181,192,203,288,197.3C384,192,480,160,576,160C672,160,768,192,864,202.7C960,213,1056,203,1152,176C1248,149,1344,107,1392,85.3L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
        background-position: bottom;
        background-repeat: no-repeat;
        background-size: 100% 350px;
        background-attachment: fixed;
    }
</style>
<div style="padding: 10px 0px 20px 0px; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <div style="width: 55px; height: 55px; background-color: #1d4ed8; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 15px;">
            <div style="display: flex; gap: 4px; align-items: center;">
                <!-- Signo de exclamación (!) -->
                <div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
                    <div style="width: 8px; height: 16px; background-color: white;"></div>
                    <div style="width: 8px; height: 8px; background-color: white;"></div>
                </div>
                <!-- Letra (i) -->
                <div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
                    <div style="width: 8px; height: 8px; background-color: white;"></div>
                    <div style="width: 8px; height: 16px; background-color: white;"></div>
                </div>
            </div>
        </div>
        <span style="font-size: 2.2rem; font-weight: 600; color: white; letter-spacing: 0.5px;">Industronic</span>
    </div>
    <h1 style="font-size: 2.6rem; font-weight: 800; margin: 0 0 10px 0; color: white; text-transform: uppercase; line-height: 1.2; letter-spacing: 0.5px;">CREADOR DE DIAGRAMAS DIMENSIONALES</h1>
    <p style="font-size: 1.1rem; color: #d1d5db; margin: 0;">Plataforma Web para Generación Automática de Diagramas Dimensionales CAD (DXF)</p>
</div>
"""
st.markdown(encabezado_html, unsafe_allow_html=True)
st.markdown("---")

# Configuración en 4 columnas superiores (Dashboard)
col_cfg1, col_cfg2, col_cfg3, col_cfg4 = st.columns(4)

with col_cfg1:
    # --- SECCIÓN 1: CONFIGURACIÓN ---
    with st.container():
        st.markdown("""<div style="background-color: #3b82f6; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"><h3 style="margin:0; font-size: 1.2rem; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">⚙️ Configuración</h3></div>""", unsafe_allow_html=True)
        
        col_fam, col_ups = st.columns(2)
        with col_fam: var_sufijo_ups = st.selectbox("Familia UPS:", ["M1", "N1", "HF", "R1", "MR1"], index=0)

        lista_ups_filtrada = []
        for modelo in BASE_DATOS_UPS.keys():
            kva = int(extraer_kva(modelo))
            es_gigante = modelo.startswith("13") and kva >= 300
            
            if var_sufijo_ups == "N1":
                if es_gigante and "277V" in modelo: lista_ups_filtrada.append(modelo)
            elif var_sufijo_ups == "HF":
                if es_gigante and "230V" in modelo: lista_ups_filtrada.append(modelo)
            else:
                if not es_gigante: lista_ups_filtrada.append(modelo)

        idx_ups_default = lista_ups_filtrada.index("1310") if "1310" in lista_ups_filtrada else 0
        # Muestra visualmente solo el modelo base (ej. "1310", "1360") sin medidas ni voltajes
        with col_ups: var_ups = st.selectbox("Modelo UPS:", lista_ups_filtrada, index=idx_ups_default, format_func=lambda x: x.split()[0])

        # Inicialización forzada por defecto en "Ninguno" para el estandar de la empresa
        var_cant_mods = st.selectbox("Cantidad de Módulos de Potencia:", ["Ninguno", "1", "2"], index=0)
        
        alto_ups = BASE_DATOS_UPS[var_ups]["alto"]
        modulo_detectado = "Ninguno"
        
        if var_ups.startswith("13"):
            for sap, datos in BASE_DATOS_MODULOS.items():
                if sap != "Ninguno" and datos["alto"] == alto_ups:
                    modulo_detectado = sap
                    break

        lista_mods = list(BASE_DATOS_MODULOS.keys())
        idx_ninguno = lista_mods.index("Ninguno")
        idx_detectado = lista_mods.index(modulo_detectado) if modulo_detectado in lista_mods else idx_ninguno
        
        if var_cant_mods == "Ninguno":
            idx_mod1 = idx_ninguno
            idx_mod2 = idx_ninguno
        elif var_cant_mods == "1":
            idx_mod1 = idx_detectado
            idx_mod2 = idx_ninguno
        else:
            idx_mod1 = idx_detectado
            idx_mod2 = idx_detectado

        # SE AÑADIÓ FORMAT_FUNC
        col_mod1, col_mod2 = st.columns(2)
        fmt_mod = lambda x: f"{x}  ({BASE_DATOS_MODULOS[x]['alto']}x{BASE_DATOS_MODULOS[x]['ancho']}x{BASE_DATOS_MODULOS[x]['fondo']} mm)" if x != "Ninguno" else "Ninguno"
        
        with col_mod1: 
            var_mod1 = st.selectbox("Módulo de Potencia 1 (SAP):", lista_mods, index=idx_mod1, format_func=fmt_mod)
            img_m1 = obtener_imagen(BASE_DATOS_MODULOS[var_mod1].get("dxf")) if var_mod1 != "Ninguno" else None
            if img_m1: st.image(img_m1, caption=f"SAP: {var_mod1}", width=120)
            
        with col_mod2: 
            var_mod2 = st.selectbox("Módulo de Potencia 2 (SAP):", lista_mods, index=idx_mod2, format_func=fmt_mod)
            img_m2 = obtener_imagen(BASE_DATOS_MODULOS[var_mod2].get("dxf")) if var_mod2 != "Ninguno" else None
            if img_m2: st.image(img_m2, caption=f"SAP: {var_mod2}", width=120)

    with col_cfg2:
    # --- SECCIÓN 2: SISTEMA PARALELO ---
        with st.container():
            st.markdown("""<div style="background-color: #a855f7; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"><h3 style="margin:0; font-size: 1.2rem; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">🔄 Sistema Paralelo</h3></div>""", unsafe_allow_html=True)
        
        var_es_paralelo = st.selectbox("Sistema Paralelo:", ["Unitario", "Paralelo"])
        
        var_cant_ups_paralelo = "2"
        var_gabpar = list(BASE_DATOS_GABPAR.keys())[0]
        var_lleva_gabconx = "No"
        var_gabconx = list(BASE_DATOS_GABCONX.keys())[0]
        var_tipo_paralelo = "Capacidad" # Valor por defecto seguro

        if var_es_paralelo == "Paralelo":
            col_p1, col_p2 = st.columns(2)
            with col_p1: var_cant_ups_paralelo = st.selectbox("Cantidad UPS:", ["2", "3", "4", "5"])
            with col_p2: var_tipo_paralelo = st.selectbox("Tipo de Paralelo:", ["Capacidad", "Redundante"])
            
            var_gabpar = st.selectbox("Modelo GABPAR:", list(BASE_DATOS_GABPAR.keys()), format_func=lambda x: f"{x}  ({BASE_DATOS_GABPAR[x]['alto']}x{BASE_DATOS_GABPAR[x]['ancho']}x{BASE_DATOS_GABPAR[x]['fondo']} mm)")
            img_gp = obtener_imagen(BASE_DATOS_GABPAR[var_gabpar].get("dxf"))
            if img_gp: st.image(img_gp, caption=f"GABPAR: {var_gabpar}", width=120)
            
            col_c1, col_c2 = st.columns(2)
            with col_c1: var_lleva_gabconx = st.selectbox("¿Lleva GABCONX?", ["No", "Sí"])
            with col_c2:
                if var_lleva_gabconx == "Sí": 
                    var_gabconx = st.selectbox("Modelo GABCONX:", list(BASE_DATOS_GABCONX.keys()), format_func=lambda x: f"{x}  ({BASE_DATOS_GABCONX[x]['alto']}x{BASE_DATOS_GABCONX[x]['ancho']}x{BASE_DATOS_GABCONX[x]['fondo']} mm)")
                    img_gc = obtener_imagen(BASE_DATOS_GABCONX[var_gabconx].get("dxf"))
                    if img_gc: st.image(img_gc, caption=f"GABCONX: {var_gabconx}", width=120)

    with col_cfg3:
    # --- SECCIÓN 3: BATERÍAS ---
        with st.container():
            st.markdown("""<div style="background-color: #10b981; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"><h3 style="margin:0; font-size: 1.2rem; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">🔋 Baterías</h3></div>""", unsafe_allow_html=True)
        
        # EXTRACCIÓN TEMPRANA PARA FILTRADO INTELIGENTE
        kva = extraer_kva(var_ups)
        
        # --- NUEVA LÓGICA: RESTRICCIÓN DE LITIO PARA 1360 127V ---
        opciones_bateria = ["Ninguno", "Plomo"] if var_ups == "1360 127V" else ["Ninguno", "Plomo", "Litio"]
        
        col_bat1, col_bat2 = st.columns(2)
        with col_bat1: 
            var_tipo_bat = st.selectbox("Tipo de Batería:", opciones_bateria, index=1)
            if var_ups == "1360 127V":
                st.caption("⚠️ Baterías de Litio no compatibles con UPS 1360 nativo en 127V.")
        
        minutos_disponibles = []
        if var_tipo_bat == "Plomo":
            minutos_disponibles = sorted(list(set([int(k.split("-")[1]) for k in TABLA_PLOMO_AUTOMATICA.keys() if k.startswith(f"{kva}-")])))
        elif var_tipo_bat == "Litio":
            minutos_disponibles = sorted(list(set([int(k.split("-")[1]) for k in TABLA_LITIO_AUTOMATICA.keys() if k.startswith(f"{kva}-")])))
            
        opciones_minutos = [str(m) for m in minutos_disponibles] if minutos_disponibles else ["5"]
        
        with col_bat2:
            if var_tipo_bat != "Ninguno": var_tiempo_respaldo = st.selectbox("Respaldo (Minutos):", opciones_minutos)
            else: var_tiempo_respaldo = "0"

        var_manual_bat = False
        var_plomo = "Ninguno"
        var_cant_baterias = "1"
        var_peso_manual = ""

        # SE AÑADIÓ ZFILL PARA AUTO-CORRECCIÓN DE DÍGITOS
        minutos = var_tiempo_respaldo.strip().zfill(2)
        llave_busqueda = f"{kva}-{minutos}"
        cant_final_bat, sap_final_bat = 0, "Ninguno"

        if var_tipo_bat != "Ninguno":
            var_manual_bat = st.checkbox("Configuración Especial (Manual)")
            
            if not var_manual_bat:
                if var_tipo_bat == "Plomo":
                    if llave_busqueda in TABLA_PLOMO_AUTOMATICA:
                        datos = TABLA_PLOMO_AUTOMATICA[llave_busqueda]
                        cant_final_bat, sap_final_bat = datos['cant'], datos['sap']
                        st.success(f"✓ {cant_final_bat} x {sap_final_bat} ({datos['peso']} Kg)")
                    else: st.error(f"⚠ Sin datos para {kva}kVA a {minutos} min. Activa Configuración Especial.")
                elif var_tipo_bat == "Litio":
                    if llave_busqueda in TABLA_LITIO_AUTOMATICA:
                        datos = TABLA_LITIO_AUTOMATICA[llave_busqueda]
                        cant_final_bat, sap_final_bat = datos['cant'], "Litio"
                        st.success(f"✓ {cant_final_bat} x LITIO ({datos['peso']} Kg)")
                    else: st.error(f"⚠ Sin datos para {kva}kVA a {minutos} min. Activa Configuración Especial.")
            else:
                if var_tipo_bat == "Plomo":
                    fmt_bat = lambda x: f"{x}  ({BASE_DATOS_PLOMO[x]['alto']}x{BASE_DATOS_PLOMO[x]['ancho']}x{BASE_DATOS_PLOMO[x]['fondo']} mm)"
                    var_plomo = st.selectbox("Modelo Plomo (SAP):", [k for k in BASE_DATOS_PLOMO.keys() if k != "Ninguno"], format_func=fmt_bat)
                    sap_final_bat = var_plomo
                    img_bat = obtener_imagen(BASE_DATOS_PLOMO[var_plomo].get("dxf"))
                    if img_bat: st.image(img_bat, caption=f"SAP: {var_plomo}", width=120)
                else: sap_final_bat = "Litio"
                
                c1, c2 = st.columns(2)
                with c1: var_cant_baterias = st.selectbox("Cantidad:", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
                with c2: var_peso_manual = st.text_input("Peso Manual (Kg):", "")
                cant_final_bat = int(var_cant_baterias)

    with col_cfg4:
    # --- SECCIÓN 4: DATOS DEL CAJETÍN ---
        with st.container():
            st.markdown("""<div style="background-color: #f59e0b; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"><h3 style="margin:0; font-size: 1.2rem; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">📝 Datos del Cajetín</h3></div>""", unsafe_allow_html=True)
        
        var_num_orden = st.text_input("No. de Diagrama:", "000000")
        
        idx_v = 4 
        if var_cant_mods == "Ninguno":
            if "127" in var_ups or var_ups in ["1310", "1320", "1330", "1380", "13100"]: idx_v = 1 
            elif "230" in var_ups or var_ups in ["1340", "13120", "13160", "13200"]: idx_v = 3 
            elif "277" in var_ups: idx_v = 6 
            
        col_v1, col_v2 = st.columns(2)
        with col_v1: var_volt_entrada = st.selectbox("Voltaje de Entrada:", LISTA_VOLTAJES, index=idx_v)
        with col_v2: var_volt_salida = st.selectbox("Voltaje de Salida:", LISTA_VOLTAJES, index=idx_v)
        
        modelo_base_ups = var_ups.split()[0] 
        minutos_str = var_tiempo_respaldo.zfill(2) 
        sufijo_ups = "" if var_sufijo_ups == "HF" else var_sufijo_ups.strip()
        kva_ups = extraer_kva(modelo_base_ups)
        
        # Generación del título para la interfaz
        v_in = var_volt_entrada if "V" in var_volt_entrada or "D" in var_volt_entrada else f"{var_volt_entrada}V"
        v_out = var_volt_salida if "V" in var_volt_salida or "D" in var_volt_salida else f"{var_volt_salida}V"
        str_voltaje_oficial = f" VN: {v_in}" if var_volt_entrada == var_volt_salida else f" VE: {v_in} VS: {v_out}"
        
        str_bat_oficial = ""
        if var_tipo_bat == "Litio" and cant_final_bat > 0:
            str_bat_oficial = f" + BBIL-IND HF {modelo_base_ups}-{var_tiempo_respaldo}"
        elif var_tipo_bat == "Plomo" and cant_final_bat > 0:
            str_bat_oficial = f" + BAT-IND HF {modelo_base_ups}-{var_tiempo_respaldo}"
            
        str_paralelo_oficial = ""
        cant_sistemas_titulo = int(var_cant_ups_paralelo) if var_es_paralelo == "Paralelo" else 1
        if var_es_paralelo == "Paralelo":
            if var_tipo_paralelo == "Redundante":
                capacidad_total = int(kva_ups) 
                txt_sufijo_paralelo = " REDUNDANTE"
            else:
                capacidad_total = int(kva_ups) * cant_sistemas_titulo 
                txt_sufijo_paralelo = " POR CAPACIDAD"
                
            modelo_gabinetes = f"13{capacidad_total}"
            if var_lleva_gabconx == "Sí": str_paralelo_oficial += f" + GABCONX {modelo_gabinetes}"
            str_paralelo_oficial += f" + GABPAR {modelo_gabinetes}{txt_sufijo_paralelo}"
        
        sufijo_espacio = f" {sufijo_ups}" if sufijo_ups and sufijo_ups.strip() != "" and sufijo_ups != "Ninguno" else ""
        titulo_documento = f"DIAGRAMA DIMENSIONAL UPS-IND HF {modelo_base_ups}{sufijo_espacio} {kva_ups}KVA{str_voltaje_oficial}{str_bat_oficial}{str_paralelo_oficial}".strip()
        titulo_documento = " ".join(titulo_documento.split())

        col_f1, col_f2 = st.columns(2)
        with col_f1: 
            var_dibujo = st.selectbox("Dibujó:", ["AACR", "IMC", "JCTF", "YGHG", "Nuevo/Otro..."])
            var_dibujo_otro = st.text_input("Iniciales Dibujo:", "") if var_dibujo == "Nuevo/Otro..." else ""
        with col_f2: 
            var_reviso = st.selectbox("Revisó:", ["JAAB", "Nuevo/Otro..."])
            var_reviso_otro = st.text_input("Iniciales Revisó:", "") if var_reviso == "Nuevo/Otro..." else ""

# --- CATÁLOGO VISUAL DE GABINETES (OCULTO/EXPANDER) ---
with st.expander("📖 VER CATÁLOGO"):
    tab_mod, tab_par, tab_bat = st.tabs(["Módulos de Potencia", "Gabinetes Externos (Paralelo y Conexión)", "Baterías"])
    
    import base64
    
    def generar_tabla_catalogo(diccionario):
        html = """<table style="width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.95rem; text-align: left; background-color: rgba(255, 255, 255, 0.05); color: white;">
        <tr style="background-color: rgba(255, 255, 255, 0.1); border-bottom: 2px solid #4b5563;">
        <th style="padding: 12px; width: 150px; text-align: center;">Visualización</th>
        <th style="padding: 12px;">Código SAP</th>
        <th style="padding: 12px;">Dimensiones (Al x An x Fo) mm</th>
        </tr>"""
        
        for sap, datos in diccionario.items():
            if sap == "Ninguno": continue
            ruta_img = obtener_imagen(datos.get("dxf"))
            if ruta_img:
                # Convertimos la imagen a Base64 para incrustarla en el HTML
                with open(ruta_img, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                ext = ruta_img.split('.')[-1]
                img_tag = f'<img src="data:image/{ext};base64,{b64}" style="max-height: 80px; object-fit: contain; border-radius: 4px;">'
                
                html += f"""<tr style="border-bottom: 1px solid #374151;">
                <td style="padding: 12px; text-align: center;">{img_tag}</td>
                <td style="padding: 12px; font-weight: bold; color: #60a5fa; vertical-align: middle;">{sap}</td>
                <td style="padding: 12px; vertical-align: middle;">{datos['alto']} x {datos['ancho']} x {datos['fondo']}</td>
                </tr>"""
        html += "</table>"
        return html

    with tab_mod:
        st.markdown(generar_tabla_catalogo(BASE_DATOS_MODULOS), unsafe_allow_html=True)
                
    with tab_par:
        gab_ext = {**BASE_DATOS_GABPAR, **BASE_DATOS_GABCONX}
        st.markdown(generar_tabla_catalogo(gab_ext), unsafe_allow_html=True)
                
    with tab_bat:
        st.markdown(generar_tabla_catalogo(BASE_DATOS_PLOMO), unsafe_allow_html=True)

st.markdown("---") # Línea divisoria limpia
with st.container():
    # Declarar contenedores en el orden visual deseado: Plano -> Selector -> Tabla
    contenedor_plano = st.container()
    contenedor_selector = st.container()
    contenedor_tabla = st.container()
            
    # Inyectamos el selector en el contenedor intermedio (Centrado)
    with contenedor_selector:
        # Se crean 3 columnas (Espacio izq, Centro, Espacio der) para forzar el centrado
        col_izq, col_centro, col_der = st.columns([3, 4, 3])
        with col_centro:
            var_seleccion_marco = st.selectbox(
                "Tamaño de Marco (Formato):", 
                ["Automático", "Marco C (560x432)", "Marco D (864x560)", "Marco E (1120x864)"]
            )
        st.markdown("---") # Movimos la línea divisoria aquí abajo del selector
            
    # Escribimos el título en el contenedor de hasta arriba
    with contenedor_plano:
        st.subheader("Plano Dimensional (Proporción y Ensamble)")
            
    # 1. Recopilar equipos base y externos para la vista previa
    equipos_base = []
    if var_mod1 != "Ninguno": equipos_base.append(("Mpot", BASE_DATOS_MODULOS[var_mod1], "#e91e63"))
    if var_mod2 != "Ninguno": equipos_base.append(("Mpot", BASE_DATOS_MODULOS[var_mod2], "#e91e63"))
    equipos_base.append((f"UPS\n{modelo_base_ups}", BASE_DATOS_UPS[var_ups], "#f1c40f"))
    
    if var_tipo_bat == "Plomo" and sap_final_bat != "Ninguno" and sap_final_bat in BASE_DATOS_PLOMO:
        for i in range(cant_final_bat):
            if sap_final_bat == "265023" and i > 0: equipos_base.append(("BANCO\nCOMPL.", BASE_DATOS_PLOMO[sap_final_bat], "#3498db"))
            else: equipos_base.append(("BANCO\nPLOMO", BASE_DATOS_PLOMO[sap_final_bat], "#2980b9"))
    elif var_tipo_bat == "Litio":
        for i in range(cant_final_bat):
            if cant_final_bat >= 4 and i % 4 == 0: equipos_base.append(("DIST.\nLITIO", GABINETE_DIST_LITIO, "#e67e22"))
            equipos_base.append(("BANCO\nLITIO", GABINETE_LITIO, "#3498db"))
            
    equipos_externos = []
    cant_sistemas = int(var_cant_ups_paralelo) if var_es_paralelo == "Paralelo" else 1
    if var_es_paralelo == "Paralelo":
        if var_lleva_gabconx == "Sí": equipos_externos.append(("GAB.\nCONEX.", BASE_DATOS_GABCONX[var_gabconx], "#27ae60"))
        equipos_externos.append(("GAB.\nPARALELO", BASE_DATOS_GABPAR[var_gabpar], "#2ecc71"))
        
    # 2. Cálculos de espacio físico (mm) - BASADO EN VISTA SUPERIOR (HOJA 2)
    ancho_base_real = sum([eq[1]["ancho"] for eq in equipos_base]) + (GAP_GABINETES * (len(equipos_base) - 1)) if equipos_base else 0
    
    gabconx_eq = next((eq for eq in equipos_externos if "CONEX." in eq[0]), None)
    gabpar_eq = next((eq for eq in equipos_externos if "PARALELO" in eq[0]), None)
    
    w_gabconx = gabconx_eq[1]["ancho"] if gabconx_eq else 0
    w_gabpar = gabpar_eq[1]["ancho"] if gabpar_eq else 0
    
    # Holguras perimetrales exactas de Hoja 2
    offset_izq = 500 + (1500 + w_gabconx if gabconx_eq else 0)
    offset_der = 500 + (1500 + w_gabpar if gabpar_eq else 0)
    
    ancho_estimado_dibujo = offset_izq + ancho_base_real + offset_der
    
    fondos_equipos = [eq[1]["fondo"] for eq in equipos_base + equipos_externos]
    max_fondo = max(fondos_equipos) if fondos_equipos else 0
    
    # Altura en planta: 500 + (Sistemas * Fondo) + Pasillos (1000) + 500
    alto_estimado_dibujo = 1000 + (max_fondo * cant_sistemas) + (1000 * (cant_sistemas - 1))
    
    # 3. Selección del Marco y Auto-Escalado
    MARGEN_HOLGADO = 350 # Margen perimetral mínimo para respirar
    
    marco_sugerido = "E" 
    for letra in ["C", "D", "E"]:
        if (ancho_estimado_dibujo + (MARGEN_HOLGADO * 2)) <= MARCOS_DISPONIBLES[letra]["ancho"] * 10 and \
           (alto_estimado_dibujo + (MARGEN_HOLGADO * 2)) <= MARCOS_DISPONIBLES[letra]["alto"] * 10:
            marco_sugerido = letra
            break
            
    if var_seleccion_marco == "Automático": 
        marco_final = marco_sugerido
    else: 
        marco_final = var_seleccion_marco.split(" ")[1] 
        
    # --- CÁLCULO MATEMÁTICO DE ESCALA DINÁMICA ---
    limite_ancho_E = (MARCOS_DISPONIBLES["E"]["ancho"] * 10) - (MARGEN_HOLGADO * 2)
    limite_alto_E = (MARCOS_DISPONIBLES["E"]["alto"] * 10) - (MARGEN_HOLGADO * 2)
    
    FACTOR_ESCALA_BLOQUES = FACTOR_ESCALA 
    
    if ancho_estimado_dibujo > limite_ancho_E or alto_estimado_dibujo > limite_alto_E:
        proporcion_ancho = ancho_estimado_dibujo / limite_ancho_E
        proporcion_alto = alto_estimado_dibujo / limite_alto_E
        peor_proporcion = max(proporcion_ancho, proporcion_alto)
        FACTOR_ESCALA_BLOQUES = FACTOR_ESCALA * peor_proporcion
        
    # 4. Dimensiones para Canvas SVG
    marco_w = MARCOS_DISPONIBLES[marco_final]["ancho"]
    marco_h = MARCOS_DISPONIBLES[marco_final]["alto"]
    escala_preview = 600 / MARCOS_DISPONIBLES["E"]["ancho"] 
    escala_dibujo = (1 / 10) * escala_preview
    
    pw = marco_w * escala_preview
    ph = marco_h * escala_preview

    # =======================================================
    # CONSTRUCCIÓN SVG 1: HOJA 1 (VISTA FRONTAL)
    # =======================================================
    w_externos_h1 = w_gabconx + w_gabpar + (3000 if (gabconx_eq and gabpar_eq) else 0)
    w_total_h1 = max(ancho_base_real, w_externos_h1)
    
    alto_max_base = max([eq[1]["alto"] for eq in equipos_base]) if equipos_base else 0
    alto_max_ext = max([eq[1]["alto"] for eq in equipos_externos]) if equipos_externos else 0
    h_total_h1 = alto_max_base + (1000 if equipos_externos else 0) + alto_max_ext
    
    sys_w_h1 = (w_total_h1 / 10) * escala_preview
    sys_h_h1 = (h_total_h1 / 10) * escala_preview
    
    canvas_w_h1 = max(pw, sys_w_h1) + 40
    canvas_h_h1 = max(ph, sys_h_h1) + 40
    cx_h1, cy_h1 = canvas_w_h1 / 2, canvas_h_h1 / 2
    
    marco_x_h1 = cx_h1 - (pw / 2)
    marco_y_h1 = cy_h1 - (ph / 2)
    sistema_x_h1 = cx_h1 - (sys_w_h1 / 2)
    sistema_y_h1 = cy_h1 - (sys_h_h1 / 2)
    
    svg_h1 = []
    svg_h1.append(f'<rect x="{marco_x_h1}" y="{marco_y_h1}" width="{pw}" height="{ph}" fill="none" stroke="white" stroke-width="2"/>')
    svg_h1.append(f'<text x="{marco_x_h1 + 5}" y="{marco_y_h1 + 15}" fill="white" font-size="12px" font-family="sans-serif">Marco {marco_final} ({marco_w}x{marco_h}) - Hoja 1 (Vista Frontal)</text>')
    
    x_offset_base = sistema_x_h1 + (((w_total_h1 - ancho_base_real) / 2) / 10 * escala_preview)
    current_x = x_offset_base
    y_base_bottom = sistema_y_h1 + (alto_max_base / 10 * escala_preview)
    
    for label, eq, color in equipos_base:
        w = eq["ancho"] * escala_dibujo
        h = eq["alto"] * escala_dibujo
        current_y = y_base_bottom - h
        
        svg_h1.append(f'<rect x="{current_x}" y="{current_y}" width="{w}" height="{h}" fill="{color}" stroke="#ecf0f1" stroke-width="1"/>')
        lineas = label.split('\n')
        start_text_y = current_y + (h / 2) - ((len(lineas) * 9) / 2) + 4
        for i, linea in enumerate(lineas):
            svg_h1.append(f'<text x="{current_x + w/2}" y="{start_text_y + (i * 9)}" fill="black" font-size="7px" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{linea}</text>')
        current_x += w + (GAP_GABINETES * escala_dibujo)
        
    if equipos_externos:
        x_offset_ext = sistema_x_h1 + (((w_total_h1 - w_externos_h1) / 2) / 10 * escala_preview)
        current_x = x_offset_ext
        y_ext_bottom = y_base_bottom + (1000 / 10 * escala_preview) + (alto_max_ext / 10 * escala_preview)
        
        if gabconx_eq:
            w = gabconx_eq[1]["ancho"] * escala_dibujo
            h = gabconx_eq[1]["alto"] * escala_dibujo
            current_y = y_ext_bottom - h
            svg_h1.append(f'<rect x="{current_x}" y="{current_y}" width="{w}" height="{h}" fill="{gabconx_eq[2]}" stroke="#ecf0f1" stroke-width="1"/>')
            lineas = gabconx_eq[0].split('\n')
            start_text_y = current_y + (h / 2) - ((len(lineas) * 9) / 2) + 4
            for i, linea in enumerate(lineas):
                svg_h1.append(f'<text x="{current_x + w/2}" y="{start_text_y + (i * 9)}" fill="black" font-size="7px" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{linea}</text>')
            current_x += w + (3000 * escala_dibujo)
            
        if gabpar_eq:
            w = gabpar_eq[1]["ancho"] * escala_dibujo
            h = gabpar_eq[1]["alto"] * escala_dibujo
            current_y = y_ext_bottom - h
            svg_h1.append(f'<rect x="{current_x}" y="{current_y}" width="{w}" height="{h}" fill="{gabpar_eq[2]}" stroke="#ecf0f1" stroke-width="1"/>')
            lineas = gabpar_eq[0].split('\n')
            start_text_y = current_y + (h / 2) - ((len(lineas) * 9) / 2) + 4
            for i, linea in enumerate(lineas):
                svg_h1.append(f'<text x="{current_x + w/2}" y="{start_text_y + (i * 9)}" fill="black" font-size="7px" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{linea}</text>')

    svg_code_h1 = f'<div style="display:flex; justify-content:center; margin-bottom: 0px;"><svg width="100%" viewBox="0 0 {canvas_w_h1} {canvas_h_h1}" style="max-height: 400px; background-color: transparent;">{"".join(svg_h1)}</svg></div>'

    # =======================================================
    # CONSTRUCCIÓN SVG 2: HOJA 2 (VISTA SUPERIOR)
    # =======================================================
    sys_w = (ancho_estimado_dibujo / 10) * escala_preview
    sys_h = (alto_estimado_dibujo / 10) * escala_preview
    
    canvas_w = max(pw, sys_w) + 40
    canvas_h = max(ph, sys_h) + 40
    cx, cy = canvas_w / 2, canvas_h / 2
    
    marco_x = cx - (pw / 2)
    marco_y = cy - (ph / 2)
    sistema_x = cx - (sys_w / 2)
    sistema_y = cy - (sys_h / 2)
    
    start_x_base = sistema_x + (offset_izq * escala_dibujo)
    start_y_base = sistema_y + (500 * escala_dibujo)
    
    svg_h2 = []
    svg_h2.append(f'<rect x="{marco_x}" y="{marco_y}" width="{pw}" height="{ph}" fill="none" stroke="white" stroke-width="2"/>')
    svg_h2.append(f'<text x="{marco_x + 5}" y="{marco_y + 15}" fill="white" font-size="12px" font-family="sans-serif">Marco {marco_final} ({marco_w}x{marco_h}) - Hoja 2 (Vista Superior)</text>')
    svg_h2.append(f'<rect x="{sistema_x}" y="{sistema_y}" width="{sys_w}" height="{sys_h}" fill="none" stroke="#2ecc71" stroke-width="1.5" stroke-dasharray="4"/>')
    
    for fila in range(cant_sistemas):
        current_x = start_x_base
        current_y = start_y_base + (fila * (max_fondo + 1000) * escala_dibujo)
        
        for label, eq, color in equipos_base:
            w = eq["ancho"] * escala_dibujo
            h = eq["fondo"] * escala_dibujo 
            
            if fila == 0: 
                svg_h2.append(f'<line x1="{current_x}" y1="{current_y - 10}" x2="{current_x + w}" y2="{current_y - 10}" stroke="#bdc3c7" stroke-width="1"/>')
                svg_h2.append(f'<line x1="{current_x}" y1="{current_y - 13}" x2="{current_x}" y2="{current_y - 7}" stroke="#bdc3c7" stroke-width="1"/>')
                svg_h2.append(f'<line x1="{current_x + w}" y1="{current_y - 13}" x2="{current_x + w}" y2="{current_y - 7}" stroke="#bdc3c7" stroke-width="1"/>')
                svg_h2.append(f'<text x="{current_x + w/2}" y="{current_y - 15}" fill="#bdc3c7" font-size="8px" font-family="sans-serif" text-anchor="middle">{int(eq["ancho"])}</text>')
            
            svg_h2.append(f'<rect x="{current_x}" y="{current_y}" width="{w}" height="{h}" fill="{color}" stroke="#ecf0f1" stroke-width="1"/>')
            lineas = label.split('\n')
            start_text_y = current_y + (h / 2) - ((len(lineas) * 9) / 2) + 4
            for i, linea in enumerate(lineas):
                svg_h2.append(f'<text x="{current_x + w/2}" y="{start_text_y + (i * 9)}" fill="black" font-size="7px" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{linea}</text>')
            current_x += w + (GAP_GABINETES * escala_dibujo)

    center_y_sistemas = start_y_base + (((cant_sistemas * max_fondo) + ((cant_sistemas - 1) * 1000)) / 2 * escala_dibujo)
    if gabconx_eq:
        w = gabconx_eq[1]["ancho"] * escala_dibujo
        h = gabconx_eq[1]["fondo"] * escala_dibujo
        current_x = start_x_base - w - (1500 * escala_dibujo)
        current_y = center_y_sistemas - (h / 2)
        svg_h2.append(f'<rect x="{current_x}" y="{current_y}" width="{w}" height="{h}" fill="{gabconx_eq[2]}" stroke="#ecf0f1" stroke-width="1"/>')
        lineas = gabconx_eq[0].split('\n')
        start_text_y = current_y + (h / 2) - ((len(lineas) * 9) / 2) + 4
        for i, linea in enumerate(lineas):
            svg_h2.append(f'<text x="{current_x + w/2}" y="{start_text_y + (i * 9)}" fill="black" font-size="7px" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{linea}</text>')

    if gabpar_eq:
        w = gabpar_eq[1]["ancho"] * escala_dibujo
        h = gabpar_eq[1]["fondo"] * escala_dibujo
        current_x = start_x_base + (ancho_base_real * escala_dibujo) + (1500 * escala_dibujo)
        current_y = center_y_sistemas - (h / 2)
        svg_h2.append(f'<rect x="{current_x}" y="{current_y}" width="{w}" height="{h}" fill="{gabpar_eq[2]}" stroke="#ecf0f1" stroke-width="1"/>')
        lineas = gabpar_eq[0].split('\n')
        start_text_y = current_y + (h / 2) - ((len(lineas) * 9) / 2) + 4
        for i, linea in enumerate(lineas):
            svg_h2.append(f'<text x="{current_x + w/2}" y="{start_text_y + (i * 9)}" fill="black" font-size="7px" font-family="sans-serif" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{linea}</text>')

    ancho_cuarto_mm = int(ancho_estimado_dibujo)
    fondo_cuarto_mm = int(alto_estimado_dibujo)
    ancho_cuarto_m = ancho_cuarto_mm / 1000
    fondo_cuarto_m = fondo_cuarto_mm / 1000
    
    y_cota_w = sistema_y - 15
    svg_h2.append(f'<line x1="{sistema_x}" y1="{y_cota_w}" x2="{sistema_x + sys_w}" y2="{y_cota_w}" stroke="#06b6d4" stroke-width="1"/>')
    svg_h2.append(f'<line x1="{sistema_x}" y1="{y_cota_w - 3}" x2="{sistema_x}" y2="{y_cota_w + 3}" stroke="#06b6d4" stroke-width="1"/>')
    svg_h2.append(f'<line x1="{sistema_x + sys_w}" y1="{y_cota_w - 3}" x2="{sistema_x + sys_w}" y2="{y_cota_w + 3}" stroke="#06b6d4" stroke-width="1"/>')
    svg_h2.append(f'<text x="{sistema_x + sys_w/2}" y="{y_cota_w - 6}" fill="#06b6d4" font-size="9px" font-family="sans-serif" font-weight="bold" text-anchor="middle">{ancho_cuarto_mm} mm ({ancho_cuarto_m:.2f} m)</text>')

    x_cota_h = sistema_x + sys_w + 15
    svg_h2.append(f'<line x1="{x_cota_h}" y1="{sistema_y}" x2="{x_cota_h}" y2="{sistema_y + sys_h}" stroke="#06b6d4" stroke-width="1"/>')
    svg_h2.append(f'<line x1="{x_cota_h - 3}" y1="{sistema_y}" x2="{x_cota_h + 3}" y2="{sistema_y}" stroke="#06b6d4" stroke-width="1"/>')
    svg_h2.append(f'<line x1="{x_cota_h - 3}" y1="{sistema_y + sys_h}" x2="{x_cota_h + 3}" y2="{sistema_y + sys_h}" stroke="#06b6d4" stroke-width="1"/>')
    svg_h2.append(f'<text x="{x_cota_h + 14}" y="{sistema_y + sys_h/2}" fill="#06b6d4" font-size="9px" font-family="sans-serif" font-weight="bold" text-anchor="middle" transform="rotate(-90 {x_cota_h + 14} {sistema_y + sys_h/2})">{fondo_cuarto_mm} mm ({fondo_cuarto_m:.2f} m)</text>')

    svg_code_h2 = f'<div style="display:flex; justify-content:center; margin-bottom: 0px;"><svg width="100%" viewBox="0 0 {canvas_w} {canvas_h}" style="max-height: 400px; background-color: transparent;">{"".join(svg_h2)}</svg></div>'

    # RENDERIZAR AMBOS SVGs EN DOS COLUMNAS
    col_plano1, col_plano2 = contenedor_plano.columns(2)
    with col_plano1:
        st.markdown(svg_code_h1, unsafe_allow_html=True)
    with col_plano2:
        st.markdown(svg_code_h2, unsafe_allow_html=True)
    
    # --- TABLA DE RESUMEN EN INTERFAZ (Se envía al contenedor de en medio) ---
    contenedor_tabla.markdown("<h4 style='color: white; margin-bottom: 5px;'>📋 Resumen de Equipos</h4>", unsafe_allow_html=True)
    
    # CSS para convertir el bloque de código nativo en nuestra caja azul estilizada
    contenedor_tabla.markdown("""
    <style>
        div[data-testid="stCodeBlock"] {
            background-color: rgba(96, 165, 250, 0.1) !important;
            border-left: 4px solid #3b82f6 !important;
            border-radius: 4px !important;
            margin-bottom: 15px !important;
        }
        div[data-testid="stCodeBlock"] code {
            color: #93c5fd !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # st.code agrega automáticamente el botón de "Copiar al portapapeles" en la esquina superior derecha
    contenedor_tabla.code(titulo_documento, language="text")
    
    tabla_html = """<table style="width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.95rem; background-color: rgba(255, 255, 255, 0.05);">
<tr style="background-color: rgba(255, 255, 255, 0.1); text-align: left;">
<th style="padding: 12px; color: white; border-bottom: 2px solid #4b5563;">Tipo de Equipo</th>
<th style="padding: 12px; color: white; border-bottom: 2px solid #4b5563;">Num. Gabinetes</th>
<th style="padding: 12px; color: white; border-bottom: 2px solid #4b5563;">Dimensiones (Al x An x Fo) mm</th>
<th style="padding: 12px; color: #93c5fd; border-bottom: 2px solid #4b5563;">Peso (Kg) ✎ Editable</th>
</tr>"""
    
    def add_fila(equipo, cantidad, dim, peso):
        if peso == "" or peso is None: peso = "-"
        return f"""<tr style="border-bottom: 1px solid #374151;">
<td style="padding: 12px; color: #eab308; font-weight: bold;">{equipo}</td>
<td style="padding: 12px; color: white; font-weight: bold; text-align: center;">{cantidad}</td>
<td style="padding: 12px; color: white;">{dim}</td>
<td style="padding: 12px; color: white; background-color: rgba(255, 255, 255, 0.1); border-left: 1px solid #4b5563;" contenteditable="true" title="Clic para editar">{peso}</td>
</tr>"""
        
    # Bloque de Módulos
    if var_mod1 != "Ninguno" and var_mod2 != "Ninguno":
        tabla_html += add_fila("MÓDULO DE ENTRADA", cant_sistemas, f"{BASE_DATOS_MODULOS[var_mod1]['alto']} x {BASE_DATOS_MODULOS[var_mod1]['ancho']} x {BASE_DATOS_MODULOS[var_mod1]['fondo']}", BASE_DATOS_MODULOS[var_mod1].get("peso", "-"))
        tabla_html += add_fila("MÓDULO DE SALIDA", cant_sistemas, f"{BASE_DATOS_MODULOS[var_mod2]['alto']} x {BASE_DATOS_MODULOS[var_mod2]['ancho']} x {BASE_DATOS_MODULOS[var_mod2]['fondo']}", BASE_DATOS_MODULOS[var_mod2].get("peso", "-"))
    else:
        if var_mod1 != "Ninguno": tabla_html += add_fila("MÓDULO DE POTENCIA", cant_sistemas, f"{BASE_DATOS_MODULOS[var_mod1]['alto']} x {BASE_DATOS_MODULOS[var_mod1]['ancho']} x {BASE_DATOS_MODULOS[var_mod1]['fondo']}", BASE_DATOS_MODULOS[var_mod1].get("peso", "-"))
        if var_mod2 != "Ninguno": tabla_html += add_fila("MÓDULO DE POTENCIA", cant_sistemas, f"{BASE_DATOS_MODULOS[var_mod2]['alto']} x {BASE_DATOS_MODULOS[var_mod2]['ancho']} x {BASE_DATOS_MODULOS[var_mod2]['fondo']}", BASE_DATOS_MODULOS[var_mod2].get("peso", "-"))

    # Bloque UPS
    str_ups_oficial = f"UPS-IND HF {modelo_base_ups} {sufijo_ups}".strip()
    tabla_html += add_fila(str_ups_oficial, cant_sistemas, f"{BASE_DATOS_UPS[var_ups]['alto']} x {BASE_DATOS_UPS[var_ups]['ancho']} x {BASE_DATOS_UPS[var_ups]['fondo']}", BASE_DATOS_UPS[var_ups].get("peso", "-"))

    # Bloque Baterías
    if var_tipo_bat == "Plomo" and sap_final_bat != "Ninguno" and cant_final_bat > 0:
        peso_plomo = var_peso_manual if var_manual_bat else TABLA_PLOMO_AUTOMATICA.get(llave_busqueda, {}).get("peso", "-")
        cant_total_plomo = cant_final_bat * cant_sistemas
        str_bat_plomo = f"BAT-IND HF {modelo_base_ups}-{var_tiempo_respaldo}".strip()
        tabla_html += add_fila(str_bat_plomo, cant_total_plomo, f"{BASE_DATOS_PLOMO[sap_final_bat]['alto']} x {BASE_DATOS_PLOMO[sap_final_bat]['ancho']} x {BASE_DATOS_PLOMO[sap_final_bat]['fondo']}", f"{peso_plomo} c/u")
        
    elif var_tipo_bat == "Litio" and cant_final_bat > 0:
        peso_litio = var_peso_manual if var_manual_bat else TABLA_LITIO_AUTOMATICA.get(llave_busqueda, {}).get("peso", "-")
        cant_dist = cant_final_bat // 4  
        cant_total_dist = cant_dist * cant_sistemas
        cant_total_litio = cant_final_bat * cant_sistemas
        str_bat_litio = f"BBIL-IND HF {modelo_base_ups}-{var_tiempo_respaldo}".strip()
        
        if cant_total_dist > 0:
            tabla_html += add_fila("GABINETE DE DISTRIBUCIÓN", cant_total_dist, f"{GABINETE_DIST_LITIO['alto']} x {GABINETE_DIST_LITIO['ancho']} x {GABINETE_DIST_LITIO['fondo']}", GABINETE_DIST_LITIO.get("peso", "-"))
        tabla_html += add_fila(str_bat_litio, cant_total_litio, f"{GABINETE_LITIO['alto']} x {GABINETE_LITIO['ancho']} x {GABINETE_LITIO['fondo']}", f"{peso_litio} c/u")

    # Bloque Paralelo
    if var_es_paralelo == "Paralelo":
        if var_lleva_gabconx == "Sí":
            tabla_html += add_fila("GABINETE DE CONEXIÓN", 1, f"{BASE_DATOS_GABCONX[var_gabconx]['alto']} x {BASE_DATOS_GABCONX[var_gabconx]['ancho']} x {BASE_DATOS_GABCONX[var_gabconx]['fondo']}", BASE_DATOS_GABCONX[var_gabconx].get("peso", "-"))
        tabla_html += add_fila("GABINETE PARALELO", 1, f"{BASE_DATOS_GABPAR[var_gabpar]['alto']} x {BASE_DATOS_GABPAR[var_gabpar]['ancho']} x {BASE_DATOS_GABPAR[var_gabpar]['fondo']}", BASE_DATOS_GABPAR[var_gabpar].get("peso", "-"))

    tabla_html += "</table>"
    
    if var_tipo_bat in ["Plomo", "Litio"]:
        tabla_html += f'<p style="font-size: 0.85rem; color: #9ca3af; margin-top: 8px; text-align: right;">* Tiempo de Respaldo del Sistema: <b>{var_tiempo_respaldo} Minutos</b></p>'
    contenedor_tabla.markdown(tabla_html, unsafe_allow_html=True)
    contenedor_tabla.markdown("---")

    # ==========================================================
    # 4. FUNCIÓN MAESTRA DE INCRUSTACIÓN VECTORIAL
    # ==========================================================
    def registrar_bloque(doc, archivo_dxf, nombre_bloque):
        ruta = os.path.join(CARPETA_BLOQUES, archivo_dxf)
        if nombre_bloque in doc.blocks: return True
        if not os.path.exists(ruta): return False
        try:
            doc_origen = ezdxf.readfile(ruta)
            nuevo_bloque = doc.blocks.new(nombre_bloque)
            
            entidades_peligrosas = ['SOLID', 'HATCH', 'LEADER', 'MULTILEADER', 'WIPEOUT']
            
            for entity in doc_origen.modelspace():
                if entity.dxftype() not in entidades_peligrosas:
                    # --- PARCHE INTELIGENTE PARA COTAS (DIMENSIONS) ---
                    if entity.dxftype() == 'DIMENSION':
                        estilo_cota = entity.dxf.get('dimstyle', 'Standard')
                        if estilo_cota not in doc.dimstyles:
                            doc.dimstyles.new(estilo_cota)
                    # --------------------------------------------------
                    copia = entity.copy()
                    if copia.dxftype() in ['TEXT', 'MTEXT']: copia.dxf.style = 'Standard'
                    nuevo_bloque.add_entity(copia)
            return True
        except Exception as e:
            st.error(f"Error registrando {nombre_bloque}: {e}")
            return False

    def crear_dxf():
        sistema_base = []
        modelo_base_ups = var_ups.split()[0] 
        minutos = var_tiempo_respaldo.zfill(2) 
        sufijo_ups = "" if var_sufijo_ups == "HF" else var_sufijo_ups.strip()
        kva_ups = extraer_kva(modelo_base_ups)
        
        # --- NUEVA LÓGICA DE NOMENCLATURA OFICIAL PARA EL TÍTULO ---
        v_in = var_volt_entrada if "V" in var_volt_entrada or "D" in var_volt_entrada else f"{var_volt_entrada}V"
        v_out = var_volt_salida if "V" in var_volt_salida or "D" in var_volt_salida else f"{var_volt_salida}V"
        str_voltaje_oficial = f" VN: {v_in}" if var_volt_entrada == var_volt_salida else f" VE: {v_in} VS: {v_out}"
        
        str_bat_oficial = ""
        if var_tipo_bat == "Litio" and cant_final_bat > 0:
            str_bat_oficial = f" + BBIL-IND HF {modelo_base_ups}-{var_tiempo_respaldo}"
        elif var_tipo_bat == "Plomo" and cant_final_bat > 0:
            str_bat_oficial = f" + BAT-IND HF {modelo_base_ups}-{var_tiempo_respaldo}"
            
        str_paralelo_oficial = ""
        cant_sistemas_titulo = int(var_cant_ups_paralelo) if var_es_paralelo == "Paralelo" else 1
        if var_es_paralelo == "Paralelo":
            capacidad_total = int(kva_ups) * cant_sistemas_titulo
            modelo_gabinetes = f"13{capacidad_total}"
            if var_lleva_gabconx == "Sí": str_paralelo_oficial += f" + GABCONX {modelo_gabinetes}"
            str_paralelo_oficial += f" + GABPAR {modelo_gabinetes}"
        
        sufijo_espacio = f" {sufijo_ups}" if sufijo_ups and sufijo_ups.strip() != "" and sufijo_ups != "Ninguna" else ""
        titulo_documento = f"DIAGRAMA DIMENSIONAL UPS-IND HF {modelo_base_ups}{sufijo_espacio} {kva_ups}KVA{str_voltaje_oficial}{str_bat_oficial}{str_paralelo_oficial}".strip()
        titulo_documento = " ".join(titulo_documento.split())
        nombre_diagrama_completo = f"{var_num_orden.strip()} {titulo_documento}"

        if var_mod1 != "Ninguno" and var_mod2 != "Ninguno":
            sistema_base.append(("MÓDULO DE ENTRADA", var_mod1, BASE_DATOS_MODULOS[var_mod1]))
            sistema_base.append(("MÓDULO DE SALIDA", var_mod2, BASE_DATOS_MODULOS[var_mod2]))
        else:
            if var_mod1 != "Ninguno": sistema_base.append(("MÓDULOS DE POTENCIA", var_mod1, BASE_DATOS_MODULOS[var_mod1]))
            if var_mod2 != "Ninguno": sistema_base.append(("MÓDULOS DE POTENCIA", var_mod2, BASE_DATOS_MODULOS[var_mod2]))
        
        sistema_base.append((f"UPS-IND-HF {modelo_base_ups} {sufijo_ups}".strip(), var_ups, BASE_DATOS_UPS[var_ups]))
        
        if var_tipo_bat == "Plomo" and sap_final_bat != "Ninguno" and cant_final_bat > 0:
            datos_bat = BASE_DATOS_PLOMO[sap_final_bat].copy()
            peso = str(TABLA_PLOMO_AUTOMATICA.get(llave_busqueda, {}).get("peso", ""))
            if peso: datos_bat["peso"] = f"{peso} c/u" if cant_final_bat > 1 else f"{peso}"
            
            for i in range(cant_final_bat):
                if sap_final_bat == "265023" and i > 0:
                    datos_bat_comp = datos_bat.copy()
                    datos_bat_comp["dxf"] = "bat_265023_complemento" 
                    sistema_base.append((f"BAT-IND-HF {modelo_base_ups}-{minutos}", "265023_Complemento", datos_bat_comp))
                else:
                    sistema_base.append((f"BAT-IND-HF {modelo_base_ups}-{minutos}", sap_final_bat, datos_bat))
                    
        elif var_tipo_bat == "Litio" and cant_final_bat > 0:
            datos_litio = GABINETE_LITIO.copy()
            peso = str(TABLA_LITIO_AUTOMATICA.get(llave_busqueda, {}).get("peso", ""))
            if peso: datos_litio["peso"] = f"{peso} c/u" if cant_final_bat > 1 else f"{peso}"
            for i in range(cant_final_bat):
                if cant_final_bat >= 4 and i % 4 == 0: sistema_base.append(("GABINETE DE DISTRIBUCIÓN", "Estándar", GABINETE_DIST_LITIO))
                sistema_base.append((f"BBIL-IND HF {modelo_base_ups}-{minutos}", "Estándar", datos_litio))

        sistema_externo = []
        if var_es_paralelo == "Paralelo":
            if var_lleva_gabconx == "Sí": sistema_externo.append(("GABINETE DE CONEXIÓN", var_gabconx, BASE_DATOS_GABCONX[var_gabconx]))
            sistema_externo.append(("GABINETE PARALELO", var_gabpar, BASE_DATOS_GABPAR[var_gabpar]))

        lista_para_tabla = sistema_base + sistema_externo

        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        cant_sistemas = int(var_cant_ups_paralelo) if var_es_paralelo == "Paralelo" else 1
        
        # --- CÁLCULO DE ESCALA DINÁMICA HOJA 1 (VISTA FRONTAL 1 SISTEMA) ---
        # --- CÁLCULO DE ESCALA DINÁMICA HOJA 1 (SISTEMA ARRIBA, EXTERNOS ABAJO) ---
        escala_b = FACTOR_ESCALA_BLOQUES
        
        real_w_base_h1 = sum([eq[2]["ancho"] for eq in sistema_base]) + (GAP_GABINETES * (len(sistema_base) - 1))
        gabconx_data_tmp = next((eq for eq in sistema_externo if "CONEXIÓN" in eq[0]), None)
        gabpar_data_tmp = next((eq for eq in sistema_externo if "PARALELO" in eq[0]), None)
        gabconx_w_h1 = gabconx_data_tmp[2]["ancho"] if gabconx_data_tmp else 0
        gabpar_w_h1 = gabpar_data_tmp[2]["ancho"] if gabpar_data_tmp else 0
        
        # Ancho H1: Se compara la fila superior vs la fila inferior (si existe)
        w_externos_h1 = gabconx_w_h1 + gabpar_w_h1 + (3000 if (gabconx_data_tmp and gabpar_data_tmp) else 0) # Separación calculada a 3 metros
        total_real_x_h1 = max(real_w_base_h1, w_externos_h1)
        
        alto_max_base = max([eq[2]["alto"] for eq in sistema_base])
        alto_max_ext = max([eq[2]["alto"] for eq in sistema_externo]) if sistema_externo else 0
        
        # Apilado vertical: Base + Margen (600mm) + Externos
        total_real_y_h1 = alto_max_base + (600 if sistema_externo else 0) + alto_max_ext + 1000 
        
        escala_h1_x = total_real_x_h1 / (MARCOS_DISPONIBLES[marco_final]["ancho"] * 0.95) # Escala ampliada al 95% para maximizar el área
        escala_h1_y = total_real_y_h1 / (MARCOS_DISPONIBLES[marco_final]["alto"] * 0.70)
        
        escala_b_h1 = max(FACTOR_ESCALA_BLOQUES, escala_h1_x, escala_h1_y)
        escala_dinamica_h1 = FACTOR_ESCALA / escala_b_h1
        
        # Coordenadas centradas por fila
        x_base_start = (total_real_x_h1 - real_w_base_h1) / (2 * escala_b_h1)
        x_ext_start = (total_real_x_h1 - w_externos_h1) / (2 * escala_b_h1)
        y_base_start = (alto_max_ext + 600) / escala_b_h1 if sistema_externo else 0
        y_ext_start = 0
        
        # Compatibilidad matemática con Hoja 2
        max_x_base = (real_w_base_h1 + GAP_GABINETES) / escala_b
        
        # --- DIBUJAR HOJA 1 ---
        inicio_baterias_x, fin_baterias_x, cotas_distribucion = None, None, []
        inicio_modulos_x, fin_modulos_x = None, None
        inicio_ups_x, fin_ups_x = None, None
        inicio_gabconx_x, fin_gabconx_x = None, None
        inicio_gabpar_x, fin_gabpar_x = None, None
        nombre_cota_bat, nombre_cota_ups = "", ""
        
        max_y_dibujado = y_base_start + (alto_max_base / escala_b_h1)
        coordenada_x_actual = x_base_start
        
        # 1. SISTEMA BASE (Fila Superior)
        for tipo, modelo, datos_eq in sistema_base:
            ancho_cad = datos_eq["ancho"] / escala_b_h1
            alto_cad = datos_eq["alto"] / escala_b_h1
            gap_cad = GAP_GABINETES / escala_b_h1
            nombre_dxf = datos_eq["dxf"]
            
            if "BAT-IND" in tipo or "BBIL-IND" in tipo or "DISTRIBUCIÓN" in tipo:
                if inicio_baterias_x is None: inicio_baterias_x = coordenada_x_actual  
                fin_baterias_x = coordenada_x_actual + ancho_cad 
                if "BAT-IND" in tipo or "BBIL-IND" in tipo: nombre_cota_bat = tipo
                if "DISTRIBUCIÓN" in tipo: cotas_distribucion.append((coordenada_x_actual, coordenada_x_actual + ancho_cad))
            elif "MÓDULO" in tipo or "MODULO" in tipo:
                if inicio_modulos_x is None: inicio_modulos_x = coordenada_x_actual
                fin_modulos_x = coordenada_x_actual + ancho_cad
            elif "UPS-IND" in tipo:
                if inicio_ups_x is None: inicio_ups_x = coordenada_x_actual
                fin_ups_x, nombre_cota_ups = coordenada_x_actual + ancho_cad, tipo 
            
            if registrar_bloque(doc, f"{nombre_dxf}.dxf", nombre_dxf):
                blk = msp.add_blockref(name=nombre_dxf, insert=(coordenada_x_actual, y_base_start))
                blk.dxf.xscale = escala_dinamica_h1
                blk.dxf.yscale = escala_dinamica_h1
            else:
                p1, p2, p3, p4 = (coordenada_x_actual, y_base_start), (coordenada_x_actual + ancho_cad, y_base_start), (coordenada_x_actual + ancho_cad, y_base_start + alto_cad), (coordenada_x_actual, y_base_start + alto_cad)
                msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 3})
                
            coordenada_x_actual += (ancho_cad + gap_cad)
            
        # 2. EXTERNOS (Fila Inferior Centrada)
        coordenada_x_ext = x_ext_start
        if gabconx_data_tmp:
            ancho_cad = gabconx_w_h1 / escala_b_h1
            alto_cad = gabconx_data_tmp[2]["alto"] / escala_b_h1
            nombre_dxf = gabconx_data_tmp[2]["dxf"]
            inicio_gabconx_x = coordenada_x_ext
            fin_gabconx_x = coordenada_x_ext + ancho_cad
            
            if registrar_bloque(doc, f"{nombre_dxf}.dxf", nombre_dxf):
                blk = msp.add_blockref(name=nombre_dxf, insert=(coordenada_x_ext, y_ext_start))
                blk.dxf.xscale = escala_dinamica_h1
                blk.dxf.yscale = escala_dinamica_h1
            else:
                p1, p2, p3, p4 = (coordenada_x_ext, y_ext_start), (coordenada_x_ext + ancho_cad, y_ext_start), (coordenada_x_ext + ancho_cad, y_ext_start + alto_cad), (coordenada_x_ext, y_ext_start + alto_cad)
                msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 3})
            
            coordenada_x_ext += ancho_cad + (3000 / escala_b_h1) # Aplica la separación física de 3 metros
            
        if gabpar_data_tmp:
            ancho_cad = gabpar_w_h1 / escala_b_h1
            alto_cad = gabpar_data_tmp[2]["alto"] / escala_b_h1
            nombre_dxf = gabpar_data_tmp[2]["dxf"]
            inicio_gabpar_x = coordenada_x_ext
            fin_gabpar_x = coordenada_x_ext + ancho_cad
            
            if registrar_bloque(doc, f"{nombre_dxf}.dxf", nombre_dxf):
                blk = msp.add_blockref(name=nombre_dxf, insert=(coordenada_x_ext, y_ext_start))
                blk.dxf.xscale = escala_dinamica_h1
                blk.dxf.yscale = escala_dinamica_h1
            else:
                p1, p2, p3, p4 = (coordenada_x_ext, y_ext_start), (coordenada_x_ext + ancho_cad, y_ext_start), (coordenada_x_ext + ancho_cad, y_ext_start + alto_cad), (coordenada_x_ext, y_ext_start + alto_cad)
                msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 3})
        
        ancho_total_ensamble = total_real_x_h1 / escala_b_h1
        y_vista = max_y_dibujado + (GAP_Y_VISTAS / FACTOR_ESCALA)
        centro_ensamble = ancho_total_ensamble / 2
        
        msp.add_text("VISTA FRONTAL", dxfattribs={'height': 50 / FACTOR_ESCALA, 'color': 7}).set_placement((centro_ensamble, y_vista), align=TextEntityAlignment.BOTTOM_CENTER)
        msp.add_lwpolyline([(centro_ensamble - (400/FACTOR_ESCALA), y_vista - (15/FACTOR_ESCALA)), (centro_ensamble + (400/FACTOR_ESCALA), y_vista - (15/FACTOR_ESCALA))], dxfattribs={'color': 7})
        
        # --- COTAS HOJA 1 (Alineadas a sus respectivas filas) ---
        tick = 40 / FACTOR_ESCALA  
        y_cota_base = y_base_start - (150 / FACTOR_ESCALA)
        y_cota_ext = y_ext_start - (150 / FACTOR_ESCALA)
        
        if inicio_modulos_x is not None:
            msp.add_lwpolyline([(inicio_modulos_x, y_cota_base + tick), (inicio_modulos_x, y_cota_base), (fin_modulos_x, y_cota_base), (fin_modulos_x, y_cota_base + tick)], dxfattribs={'color': 7})
            msp.add_text("MÓDULOS DE POTENCIA", dxfattribs={'height': 25 / FACTOR_ESCALA, 'color': 7}).set_placement(((inicio_modulos_x + fin_modulos_x) / 2, y_cota_base - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        for i_d, f_d in cotas_distribucion:
            msp.add_lwpolyline([(i_d, y_cota_base + tick), (i_d, y_cota_base), (f_d, y_cota_base), (f_d, y_cota_base + tick)], dxfattribs={'color': 7})
            msp.add_text("GAB. DE DIST.", dxfattribs={'height': 25 / FACTOR_ESCALA, 'color': 7}).set_placement(((i_d + f_d) / 2, y_cota_base - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if inicio_baterias_x is not None:
            offset_y_cota = (120 / FACTOR_ESCALA) if cotas_distribucion else 0
            y_cota_global = y_cota_base - offset_y_cota
            msp.add_lwpolyline([(inicio_baterias_x, y_cota_global + tick), (inicio_baterias_x, y_cota_global), (fin_baterias_x, y_cota_global), (fin_baterias_x, y_cota_global + tick)], dxfattribs={'color': 7})
            msp.add_text(nombre_cota_bat, dxfattribs={'height': 25 / FACTOR_ESCALA, 'color': 7}).set_placement(((inicio_baterias_x + fin_baterias_x) / 2, y_cota_global - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if inicio_ups_x is not None:
            msp.add_lwpolyline([(inicio_ups_x, y_cota_base + tick), (inicio_ups_x, y_cota_base), (fin_ups_x, y_cota_base), (fin_ups_x, y_cota_base + tick)], dxfattribs={'color': 7})
            msp.add_text(nombre_cota_ups, dxfattribs={'height': 25 / FACTOR_ESCALA, 'color': 7}).set_placement(((inicio_ups_x + fin_ups_x) / 2, y_cota_base - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if inicio_gabconx_x is not None:
            msp.add_lwpolyline([(inicio_gabconx_x, y_cota_ext + tick), (inicio_gabconx_x, y_cota_ext), (fin_gabconx_x, y_cota_ext), (fin_gabconx_x, y_cota_ext + tick)], dxfattribs={'color': 7})
            msp.add_text("GABINETE DE CONEXIÓN", dxfattribs={'height': 25 / FACTOR_ESCALA, 'color': 7}).set_placement(((inicio_gabconx_x + fin_gabconx_x) / 2, y_cota_ext - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if inicio_gabpar_x is not None:
            msp.add_lwpolyline([(inicio_gabpar_x, y_cota_ext + tick), (inicio_gabpar_x, y_cota_ext), (fin_gabpar_x, y_cota_ext), (fin_gabpar_x, y_cota_ext + tick)], dxfattribs={'color': 7})
            msp.add_text("GABINETE PARALELO", dxfattribs={'height': 25 / FACTOR_ESCALA, 'color': 7}).set_placement(((inicio_gabpar_x + fin_gabpar_x) / 2, y_cota_ext - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)

        archivo_marco = f"marco_{marco_final.lower()}.dxf" 
        marco_w = MARCOS_DISPONIBLES[marco_final]["ancho"]
        marco_h = MARCOS_DISPONIBLES[marco_final]["alto"]
        escala = 1.0  
        
        if marco_final == "C": h_tit_base = 5.0
        elif marco_final == "D": h_tit_base = 9.0
        else: h_tit_base = 12.0
            
        inter_base = h_tit_base * 1.4 

        def estampar_cajetin(x_m, y_m, titulo_vista):
            if registrar_bloque(doc, archivo_marco, f"bloque_{archivo_marco}"):
                msp.add_blockref(name=f"bloque_{archivo_marco}", insert=(x_m, y_m))
            else:
                p1, p2, p3, p4 = (x_m, y_m), (x_m + marco_w, y_m), (x_m + marco_w, y_m + marco_h), (x_m, y_m + marco_h)
                msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 3})
                
            c_marco_x = x_m + (marco_w / 2)
            ajuste_y = (h_tit_base - 5.0)
            y_titulo_principal = y_m + marco_h + ((OFFSET_Y_TITULO / FACTOR_ESCALA) * escala) - ajuste_y
            
            txt_bus = "BUS DE VOLTAJE: +/- 240VCD" if var_tipo_bat == "Litio" and int(kva_ups) < 300 else "BUS DE VOLTAJE 480VCD" if var_tipo_bat == "Litio" else "BUS DE VOLTAJE VCD AJUSTABLE"
            h_tit = h_tit_base * escala
            inter = inter_base * escala
            
            # Títulos Divididos (Proyecto a la Izquierda, Voltajes a la Derecha)
            y_titulos = y_m + marco_h - (30 * escala)
            x_tit_izq = x_m + (40 * escala)
            x_tit_der = x_m + marco_w - (40 * escala)
            
            # Tamaños de fuente dinámicos según el marco
            w_tit_izq = 1.0
            if marco_final == "C":
                h_tit_izq = 6.0 * escala
                w_tit_izq = 0.9
                h_tit_der = 4.0 * escala
                inter_der = 4.0 * 2.2 * escala
                h_nota = 4.0 * escala
            elif marco_final == "D":
                h_tit_izq = 7.0 * escala
                h_tit_der = 5.0 * escala
                inter_der = 5.0 * 2.2 * escala
                h_nota = 5.0 * escala
            else:
                h_tit_izq = 10.0 * escala
                h_tit_der = 7.5 * escala
                inter_der = 7.5 * 2.2 * escala  
                h_nota = 7.0 * escala
            
            msp.add_text(f"UPS-IND HF {modelo_base_ups} {sufijo_ups} - {titulo_vista}".strip(), dxfattribs={'height': h_tit_izq, 'width': w_tit_izq, 'color': 7}).set_placement((x_tit_izq, y_titulos), align=TextEntityAlignment.TOP_LEFT)
            
            # --- NUEVA NOTA REPRESENTATIVA (SOLO EN HOJA 1 SI HAY VARIOS SISTEMAS) ---
            if "FRONTAL" in titulo_vista and cant_sistemas > 1:
                y_nota = y_titulos - (18 * escala) 
                nota_l1 = "NOTA: VISTA FRONTAL REPRESENTATIVA DE UN SISTEMA. PARA CANTIDAD TOTAL DE ARREGLOS Y DISTRIBUCION"
                nota_l2 = "REFERIRSE A HOJA 2 (VISTA SUPERIOR) Y TABLA DE EQUIPOS."
                msp.add_text(nota_l1, dxfattribs={'height': h_nota, 'width': 0.9, 'color': 7}).set_placement((x_tit_izq, y_nota), align=TextEntityAlignment.TOP_LEFT)
                msp.add_text(nota_l2, dxfattribs={'height': h_nota, 'width': 0.9, 'color': 7}).set_placement((x_tit_izq, y_nota - (15 * escala)), align=TextEntityAlignment.TOP_LEFT) 

            # Imprimir voltajes SOLO si NO es la Hoja 2
            if "HOJA 2" not in titulo_vista:
                msp.add_text(f"VOLTAJE ENTRADA: {var_volt_entrada} VCA", dxfattribs={'height': h_tit_der, 'color': 7}).set_placement((x_tit_der, y_titulos), align=TextEntityAlignment.TOP_RIGHT)
                msp.add_text(f"VOLTAJE SALIDA: {var_volt_salida} VCA", dxfattribs={'height': h_tit_der, 'color': 7}).set_placement((x_tit_der, y_titulos - inter_der), align=TextEntityAlignment.TOP_RIGHT)
                msp.add_text(txt_bus, dxfattribs={'height': h_tit_der, 'color': 7}).set_placement((x_tit_der, y_titulos - 2*inter_der), align=TextEntityAlignment.TOP_RIGHT)

            fecha_hoy = datetime.datetime.now().strftime("%m/%y")
            txt_d = var_dibujo_otro if var_dibujo == "Nuevo/Otro..." else var_dibujo
            txt_r = var_reviso_otro if var_reviso == "Nuevo/Otro..." else var_reviso
            tam_letra = 1.5 * escala
            m_dib_y, m_dib_x = 27.71 * escala, 420.55 * escala
            m_proy_y, m_proy_x = 65.0 * escala, 420.55 * escala
            pos_y_firmas = y_m + m_dib_y - (13.94 * escala)
            
            msp.add_text(txt_d, dxfattribs={'height': tam_letra, 'color': 2}).set_placement((x_m + m_dib_x - (99.01 * escala), pos_y_firmas), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text(fecha_hoy, dxfattribs={'height': tam_letra, 'color': 6}).set_placement((x_m + m_dib_x - (87.09 * escala), pos_y_firmas), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text(txt_r, dxfattribs={'height': tam_letra, 'color': 2}).set_placement((x_m + m_dib_x - (76.05 * escala), pos_y_firmas), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text(fecha_hoy, dxfattribs={'height': tam_letra, 'color': 6}).set_placement((x_m + m_dib_x - (63.65 * escala), pos_y_firmas), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text(titulo_documento, dxfattribs={'height': 3.5 * escala, 'color': 7}).set_placement((x_m + m_proy_x - (30.0 * escala), y_m + m_proy_y), align=TextEntityAlignment.MIDDLE_LEFT)

        min_x_dibujo, max_x_dibujo = 0, ancho_total_ensamble
        min_y_dibujo, max_y_dibujo = 0, y_vista + (100/FACTOR_ESCALA) 
        c_x, c_y = (min_x_dibujo + max_x_dibujo) / 2, (min_y_dibujo + max_y_dibujo) / 2

        x_insert_marco1 = c_x - (marco_w / 2)
        y_insert_marco1 = c_y - (marco_h / 2) + (-150 / FACTOR_ESCALA)
        
        conteo_equipos = {}
        elementos_unicos_tabla = []
        for tipo, modelo, datos_eq in lista_para_tabla:
            if tipo not in conteo_equipos:
                conteo_equipos[tipo] = 1
                elementos_unicos_tabla.append((tipo, datos_eq))
            else:
                conteo_equipos[tipo] += 1
                
        OFFSET_X_MARCO_C = 343.77
        OFFSET_Y_MARCO_C = 46.0
        OFFSET_X_MARCO_D = 586.27
        OFFSET_Y_MARCO_D = 46
        OFFSET_X_MARCO_E = 760.27
        OFFSET_Y_MARCO_E = 46.0
        
        if marco_final == "C": 
            factor_tabla = 1.0
            offset_x = OFFSET_X_MARCO_C
            offset_y = OFFSET_Y_MARCO_C
        elif marco_final == "D": 
            factor_tabla = 1.3
            offset_x = OFFSET_X_MARCO_D
            offset_y = OFFSET_Y_MARCO_D
        else: 
            factor_tabla = 1.7
            offset_x = OFFSET_X_MARCO_E
            offset_y = OFFSET_Y_MARCO_E
        
        w_box = (300 / FACTOR_ESCALA) * factor_tabla
        w_tipo = (650 / FACTOR_ESCALA) * factor_tabla
        w_cant = (300 / FACTOR_ESCALA) * factor_tabla
        w_dim = (850 / FACTOR_ESCALA) * factor_tabla
        w_peso = (250 / FACTOR_ESCALA) * factor_tabla
        h_fila = (100 / FACTOR_ESCALA) * factor_tabla
        
        ancho_total_tabla = w_tipo + w_cant + w_dim + w_peso
        
        def estampar_tabla_equipos(x_marco, y_marco):
            x_t = x_marco + offset_x
            y_t = y_marco + offset_y + ((len(elementos_unicos_tabla) + 1) * h_fila)
            p_cols = [x_t + (w_tipo/2), x_t + w_tipo + (w_cant/2), x_t + w_tipo + w_cant + (w_dim/2), x_t + w_tipo + w_cant + w_dim + (w_peso/2)]
            
            if var_tipo_bat != "Ninguno":
                x_box = x_t - w_box
                msp.add_lwpolyline([(x_box, y_t), (x_box + w_box, y_t), (x_box + w_box, y_t - 2*h_fila), (x_box, y_t - 2*h_fila), (x_box, y_t)], dxfattribs={'color': 3})
                msp.add_lwpolyline([(x_box, y_t - h_fila), (x_box + w_box, y_t - h_fila)], dxfattribs={'color': 3})
                h_h, h_d, off = (20/FACTOR_ESCALA)*factor_tabla, (25/FACTOR_ESCALA)*factor_tabla, (17/FACTOR_ESCALA)*factor_tabla
                msp.add_text("TIEMPO DE", dxfattribs={'height': h_h, 'color': 3}).set_placement((x_box + w_box/2, y_t - h_fila/2 + off), align=TextEntityAlignment.MIDDLE_CENTER)
                msp.add_text("RESPALDO", dxfattribs={'height': h_h, 'color': 3}).set_placement((x_box + w_box/2, y_t - h_fila/2 - off), align=TextEntityAlignment.MIDDLE_CENTER)
                msp.add_text(f"{var_tiempo_respaldo.zfill(2)} MINUTOS", dxfattribs={'height': h_d, 'color': 3}).set_placement((x_box + w_box/2, y_t - h_fila*1.5), align=TextEntityAlignment.MIDDLE_CENTER)
                
            def fila(y, textos, es_encabezado=False):
                msp.add_lwpolyline([(x_t, y - h_fila), (x_t + ancho_total_tabla, y - h_fila)], dxfattribs={'color': 7})
                for i, txt in enumerate(textos):
                    c, h = (3, (20/FACTOR_ESCALA)*factor_tabla) if es_encabezado else (7, (25/FACTOR_ESCALA)*factor_tabla)
                    if "\n" in txt:
                        lins = txt.split("\n")
                        msp.add_text(lins[0], dxfattribs={'height': h, 'color': c}).set_placement((p_cols[i], y - h_fila/2 + off), align=TextEntityAlignment.MIDDLE_CENTER)
                        msp.add_text(lins[1], dxfattribs={'height': h, 'color': c}).set_placement((p_cols[i], y - h_fila/2 - off), align=TextEntityAlignment.MIDDLE_CENTER)
                    else:
                        msp.add_text(txt, dxfattribs={'height': h, 'color': c}).set_placement((p_cols[i], y - h_fila/2), align=TextEntityAlignment.MIDDLE_CENTER)

            msp.add_lwpolyline([(x_t, y_t), (x_t + ancho_total_tabla, y_t)], dxfattribs={'color': 7})
            fila(y_t, ["TIPO DE EQUIPO", "NUM.\nGABINETES", "DIMENSIONES\n(Alto x Ancho x Fondo) mm", "PESO (Kg)"], True)
            y_act = y_t - h_fila
            for tipo, datos_eq in elementos_unicos_tabla:
                fila(y_act, [tipo, str(conteo_equipos[tipo]), f"{datos_eq['alto']} x {datos_eq['ancho']} x {datos_eq['fondo']}", str(datos_eq.get('peso', ''))])
                y_act -= h_fila
            for x_v in [x_t, x_t + w_tipo, x_t + w_tipo + w_cant, x_t + w_tipo + w_cant + w_dim, x_t + ancho_total_tabla]: 
                msp.add_lwpolyline([(x_v, y_t), (x_v, y_act)], dxfattribs={'color': 7})

        # Estampar tabla en Hoja 1
        estampar_tabla_equipos(x_insert_marco1, y_insert_marco1)

        estampar_cajetin(x_insert_marco1, y_insert_marco1, "HOJA 1 DE 2 (VISTA FRONTAL)")

        # --- CENTRADO E INSERCIÓN MARCO 2 (HOJA PLANTA) ---
        x_insert_marco2 = x_insert_marco1 + marco_w + (1000 / FACTOR_ESCALA)
        y_insert_marco2 = y_insert_marco1
        
        # Título dinámico para Hoja 2 (Tabla removida a petición para limpiar la vista)
        estampar_cajetin(x_insert_marco2, y_insert_marco2, "HOJA 2 DE 2 (DIMENSIONAMIENTO DE CUARTO ELECTRICO)")

        # Centro del área de dibujo ajustado perfectamente a la mitad (ya no hay tabla abajo)
        c_m2_x = x_insert_marco2 + (marco_w / 2)
        c_m2_y = y_insert_marco2 + (marco_h * 0.50)
        
        # --- NUEVA LÓGICA ARQUITECTÓNICA VISTA SUPERIOR (HOJA 2) ---
        gabconx_data_tmp = next((eq for eq in sistema_externo if "CONEXIÓN" in eq[0]), None)
        gabpar_data_tmp = next((eq for eq in sistema_externo if "PARALELO" in eq[0]), None)
        
        # 1. Calculamos las medidas reales del cuarto para escalar y centrar proporcionalmente
        real_w_base = (max_x_base * escala_b) - GAP_GABINETES
        gabconx_w = gabconx_data_tmp[2]["ancho"] if gabconx_data_tmp else 0
        gabpar_w = gabpar_data_tmp[2]["ancho"] if gabpar_data_tmp else 0
        max_fondo_val = max([eq["fondo"] for _, _, eq in lista_para_tabla])
        
        offset_izq = 500 + (1500 + gabconx_w if gabconx_data_tmp else 0)
        offset_der = 500 + (1500 + gabpar_w if gabpar_data_tmp else 0)
        offset_frontal = 500
        offset_trasero = 500
        
        total_real_x = offset_izq + real_w_base + offset_der
        total_real_y = offset_frontal + (cant_sistemas * max_fondo_val) + ((cant_sistemas - 1) * 1000) + offset_trasero
        
        # 2. Re-calculamos escala independiente para Hoja 2 (Dejando buen margen)
        escala_h2_x = total_real_x / (marco_w * 0.85)
        escala_h2_y = total_real_y / (marco_h * 0.70)
        
        escala_b = max(escala_b, escala_h2_x, escala_h2_y)
        escala_dinamica = FACTOR_ESCALA / escala_b
        
        # 3. Cálculo de Coordenadas para Centrado Perfecto del Cuarto
        room_w_scaled = total_real_x / escala_b
        room_h_scaled = total_real_y / escala_b
        
        pared_izq_ideal = c_m2_x - (room_w_scaled / 2)
        pared_frontal_ideal = c_m2_y - (room_h_scaled / 2)
        
        start_x_top = pared_izq_ideal + (offset_izq / escala_b)
        start_y_top = pared_frontal_ideal + (offset_frontal / escala_b)
        
        gap_y_hoja2 = 1000 / escala_b
        alto_total_planta_h2 = (cant_sistemas * (max_fondo_val / escala_b)) + ((cant_sistemas - 1) * gap_y_hoja2)
        ancho_base_total_scaled = real_w_base / escala_b

        # Variables para calcular el límite real de todos los equipos dibujados

        true_min_x = start_x_top
        true_max_x = start_x_top + ancho_base_total_scaled
        true_min_y = start_y_top
        true_max_y = start_y_top + alto_total_planta_h2

        for fila in range(cant_sistemas):
            coord_x_top = start_x_top
            # El pasillo libre entre gabinetes es de 1000mm exactos
            coord_y_top = start_y_top + (fila * ((max_fondo_val / escala_b) + (1000 / escala_b)))
            
            for tipo, modelo, datos_eq in sistema_base:
                ancho_cad = datos_eq["ancho"] / escala_b
                fondo_cad = datos_eq["fondo"] / escala_b
                gap_cad = GAP_GABINETES / escala_b
                nom_bloque_top = f"{datos_eq['dxf']}_top"
                
                if registrar_bloque(doc, f"{nom_bloque_top}.dxf", nom_bloque_top):
                    blk = msp.add_blockref(name=nom_bloque_top, insert=(coord_x_top, coord_y_top))
                    blk.dxf.xscale = escala_dinamica
                    blk.dxf.yscale = escala_dinamica
                else:
                    p1, p2 = (coord_x_top, coord_y_top), (coord_x_top + ancho_cad, coord_y_top)
                    p3, p4 = (coord_x_top + ancho_cad, coord_y_top + fondo_cad), (coord_x_top, coord_y_top + fondo_cad)
                    msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 1})
                    msp.add_text("FALTA", dxfattribs={'height': 15/FACTOR_ESCALA, 'color': 1}).set_placement((coord_x_top + ancho_cad/2, coord_y_top + fondo_cad/2 + (10/FACTOR_ESCALA)), align=TextEntityAlignment.MIDDLE_CENTER)
                    msp.add_text("BLOQUE_TOP", dxfattribs={'height': 15/FACTOR_ESCALA, 'color': 1}).set_placement((coord_x_top + ancho_cad/2, coord_y_top + fondo_cad/2 - (10/FACTOR_ESCALA)), align=TextEntityAlignment.MIDDLE_CENTER)
                
                coord_x_top += (ancho_cad + gap_cad)
                
        c_y_sistemas = start_y_top + (alto_total_planta_h2 / 2)
        distancia_2m = 1500 / escala_b  # Reducido a 1.5m (mantenemos el nombre de variable por seguridad)
        
        gabconx_data = next((eq for eq in sistema_externo if "CONEXIÓN" in eq[0]), None)
        gabpar_data = next((eq for eq in sistema_externo if "PARALELO" in eq[0]), None)
        
        if gabconx_data:
            ancho_cad = gabconx_data[2]["ancho"] / escala_b
            fondo_cad = gabconx_data[2]["fondo"] / escala_b
            x_gconx = start_x_top - ancho_cad - distancia_2m
            y_gconx = c_y_sistemas - (fondo_cad / 2)
            
            nom_bloque_top = f"{gabconx_data[2]['dxf']}_top"
            if registrar_bloque(doc, f"{nom_bloque_top}.dxf", nom_bloque_top):
                blk = msp.add_blockref(name=nom_bloque_top, insert=(x_gconx, y_gconx))
                blk.dxf.xscale = escala_dinamica
                blk.dxf.yscale = escala_dinamica
            else:
                p1, p2 = (x_gconx, y_gconx), (x_gconx + ancho_cad, y_gconx)
                p3, p4 = (x_gconx + ancho_cad, y_gconx + fondo_cad), (x_gconx, y_gconx + fondo_cad)
                msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 1})
            
            true_min_x = min(true_min_x, x_gconx)
            true_min_y = min(true_min_y, y_gconx)
            true_max_y = max(true_max_y, y_gconx + fondo_cad)

        if gabpar_data:
            ancho_cad = gabpar_data[2]["ancho"] / escala_b
            fondo_cad = gabpar_data[2]["fondo"] / escala_b
            x_gpar = start_x_top + ancho_base_total_scaled + distancia_2m
            y_gpar = c_y_sistemas - (fondo_cad / 2)
            
            nom_bloque_top = f"{gabpar_data[2]['dxf']}_top"
            if registrar_bloque(doc, f"{nom_bloque_top}.dxf", nom_bloque_top):
                blk = msp.add_blockref(name=nom_bloque_top, insert=(x_gpar, y_gpar))
                blk.dxf.xscale = escala_dinamica
                blk.dxf.yscale = escala_dinamica
            else:
                p1, p2 = (x_gpar, y_gpar), (x_gpar + ancho_cad, y_gpar)
                p3, p4 = (x_gpar + ancho_cad, y_gpar + fondo_cad), (x_gpar, y_gpar + fondo_cad)
                msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'color': 1})
                
            true_max_x = max(true_max_x, x_gpar + ancho_cad)
            true_min_y = min(true_min_y, y_gpar)
            true_max_y = max(true_max_y, y_gpar + fondo_cad)

        # --- CREACIÓN DE LÍNEA PUNTEADA PARA EL PERÍMETRO DEL CUARTO ---
        if 'DASHED' not in doc.linetypes:
            # Patrón: [longitud de ciclo, trazo sólido, espacio en blanco]
            doc.linetypes.new('DASHED', dxfattribs={'description': 'Punteada _ _ _ _ _ _ _ _ _', 'pattern': [1.0, 0.5, -0.5]})
            
        pared_izq = true_min_x - (500 / escala_b)
        pared_der = true_max_x + (500 / escala_b)
        pared_trasera = true_max_y + (500 / escala_b) 
        pared_frontal = true_min_y - (500 / escala_b) 
        
        p1_r = (pared_izq, pared_frontal)
        p2_r = (pared_der, pared_frontal)
        p3_r = (pared_der, pared_trasera)
        p4_r = (pared_izq, pared_trasera)
        
        # Se dibuja la línea en color verde (3) y estilo punteado
        linea_cuarto = msp.add_lwpolyline([p1_r, p2_r, p3_r, p4_r, p1_r], dxfattribs={'color': 3, 'linetype': 'DASHED'})
        # Compensación del factor de escala para que los guiones sean perfectamente legibles
        linea_cuarto.dxf.ltscale = 100 / escala_b
        
        # --- COTAS DE SEPARACIÓN (A PARED Y PASILLO) ---
        h_text_cota = 45 / FACTOR_ESCALA 
        
        # Cotas de pasillos (Efectivamente adaptativas según el primer equipo del sistema base)
        if cant_sistemas > 1:
            x_pasillo = start_x_top 
            primer_eq_fondo = sistema_base[0][2]["fondo"] / escala_b
            step_y = (max_fondo_val / escala_b) + (1000 / escala_b)
            
            for fila in range(cant_sistemas - 1):
                # Punto final superior del gabinete de la fila actual
                y_pasillo_ini = start_y_top + (fila * step_y) + primer_eq_fondo
                # Punto inicial inferior del gabinete de la siguiente fila
                y_pasillo_fin = start_y_top + ((fila + 1) * step_y)
                
                pts_pasillo = [(x_pasillo + tick, y_pasillo_ini), (x_pasillo, y_pasillo_ini), (x_pasillo, y_pasillo_fin), (x_pasillo + tick, y_pasillo_fin)]
                msp.add_lwpolyline(pts_pasillo, dxfattribs={'color': 2})
                msp.add_text("1000 mm", dxfattribs={'height': h_text_cota, 'color': 2}).set_placement((x_pasillo + (30/FACTOR_ESCALA), (y_pasillo_ini + y_pasillo_fin)/2), align=TextEntityAlignment.MIDDLE_CENTER).dxf.rotation = 90
        
        # Cota Pared Izquierda (500mm)
        y_cota_izq = c_y_sistemas
        pts_izq = [(pared_izq, y_cota_izq + tick), (pared_izq, y_cota_izq), (true_min_x, y_cota_izq), (true_min_x, y_cota_izq + tick)]
        msp.add_lwpolyline(pts_izq, dxfattribs={'color': 2})
        msp.add_text("500 mm", dxfattribs={'height': h_text_cota, 'color': 2}).set_placement(((pared_izq + true_min_x)/2, y_cota_izq - (45/FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        # Cota Pared Derecha (500mm)
        y_cota_der = c_y_sistemas
        pts_der = [(true_max_x, y_cota_der + tick), (true_max_x, y_cota_der), (pared_der, y_cota_der), (pared_der, y_cota_der + tick)]
        msp.add_lwpolyline(pts_der, dxfattribs={'color': 2})
        msp.add_text("500 mm", dxfattribs={'height': h_text_cota, 'color': 2}).set_placement(((true_max_x + pared_der)/2, y_cota_der - (45/FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        # Cota Pared Frontal (500mm) - Alineada a la derecha de las baterías
        x_cota_front = start_x_top + ancho_base_total_scaled
        pts_front = [(x_cota_front - tick, pared_frontal), (x_cota_front, pared_frontal), (x_cota_front, true_min_y), (x_cota_front - tick, true_min_y)]
        msp.add_lwpolyline(pts_front, dxfattribs={'color': 2})
        msp.add_text("500 mm", dxfattribs={'height': h_text_cota, 'color': 2}).set_placement((x_cota_front - (30/FACTOR_ESCALA), (pared_frontal + true_min_y)/2), align=TextEntityAlignment.MIDDLE_CENTER).dxf.rotation = 90
        
        # Cota Pared Trasera (500mm) - Alineada a la derecha de las baterías
        x_cota_tras = start_x_top + ancho_base_total_scaled
        pts_tras = [(x_cota_tras - tick, true_max_y), (x_cota_tras, true_max_y), (x_cota_tras, pared_trasera), (x_cota_tras - tick, pared_trasera)]
        msp.add_lwpolyline(pts_tras, dxfattribs={'color': 2})
        msp.add_text("500 mm", dxfattribs={'height': h_text_cota, 'color': 2}).set_placement((x_cota_tras - (30/FACTOR_ESCALA), (true_max_y + pared_trasera)/2), align=TextEntityAlignment.MIDDLE_CENTER).dxf.rotation = 90

        # Cotas Generales (Ancho y Fondo) - Cambiadas a Color 4 (Cyan)
        ancho_cuarto_real = (pared_der - pared_izq) * escala_b
        fondo_cuarto_real = (pared_trasera - pared_frontal) * escala_b
        
        ancho_m = ancho_cuarto_real / 1000
        fondo_m = fondo_cuarto_real / 1000
        
        # Tamaño dinámico: 5 si marco C, 6 si marco D, 9 si es E
        if marco_final == "C":
            h_text_cuarto_grande = 50 / FACTOR_ESCALA
        elif marco_final == "D":
            h_text_cuarto_grande = 60 / FACTOR_ESCALA
        else:
            h_text_cuarto_grande = 90 / FACTOR_ESCALA
        
        # Cotas Generales (Línea súper pegada a 50 del cuarto verde, texto a 100)
        
        # Cotas Generales (Línea pegada a 150 del cuarto verde, manteniendo el texto legible a 120 de la línea)
        y_cota_cuarto_x = pared_trasera + (150 / FACTOR_ESCALA)
        msp.add_lwpolyline([(pared_izq, y_cota_cuarto_x), (pared_der, y_cota_cuarto_x)], dxfattribs={'color': 4})
        msp.add_lwpolyline([(pared_izq, y_cota_cuarto_x - tick), (pared_izq, y_cota_cuarto_x + tick)], dxfattribs={'color': 4})
        msp.add_lwpolyline([(pared_der, y_cota_cuarto_x - tick), (pared_der, y_cota_cuarto_x + tick)], dxfattribs={'color': 4})
        msp.add_text(f"ANCHO MIN. CUARTO: {int(ancho_cuarto_real)} mm ({ancho_m:.2f} m)", dxfattribs={'height': h_text_cuarto_grande, 'color': 4}).set_placement(((pared_izq + pared_der)/2, y_cota_cuarto_x + (120/FACTOR_ESCALA)), align=TextEntityAlignment.BOTTOM_CENTER)

        x_cota_cuarto_y = pared_der + (150 / FACTOR_ESCALA)
        msp.add_lwpolyline([(x_cota_cuarto_y, pared_frontal), (x_cota_cuarto_y, pared_trasera)], dxfattribs={'color': 4})
        msp.add_lwpolyline([(x_cota_cuarto_y - tick, pared_frontal), (x_cota_cuarto_y + tick, pared_frontal)], dxfattribs={'color': 4})
        msp.add_lwpolyline([(x_cota_cuarto_y - tick, pared_trasera), (x_cota_cuarto_y + tick, pared_trasera)], dxfattribs={'color': 4})
        msp.add_text(f"FONDO MIN. CUARTO: {int(fondo_cuarto_real)} mm ({fondo_m:.2f} m)", dxfattribs={'height': h_text_cuarto_grande, 'color': 4}).set_placement((x_cota_cuarto_y + (120/FACTOR_ESCALA), (pared_frontal + pared_trasera)/2), align=TextEntityAlignment.MIDDLE_CENTER).dxf.rotation = 90

        # (Se omite el texto de INDICACIONES a petición para un diseño más limpio)

        # --- NOMBRES Y COTAS DE ANCHO EN VISTA SUPERIOR ---
        factor_conv = FACTOR_ESCALA_BLOQUES / escala_b  # Convierte medidas de Hoja 1 a la nueva escala de Hoja 2
        y_cota_top = start_y_top - (250 / escala_b)     # Coloca la cota matemáticamente a medio camino de la pared verde
        h_text_eq = 35 / FACTOR_ESCALA
        
        if inicio_modulos_x is not None:
            i_x, f_x = start_x_top + (inicio_modulos_x * factor_conv), start_x_top + (fin_modulos_x * factor_conv)
            pts = [(i_x, y_cota_top + tick), (i_x, y_cota_top), (f_x, y_cota_top), (f_x, y_cota_top + tick)]
            msp.add_lwpolyline(pts, dxfattribs={'color': 7})
            msp.add_text("MÓDULOS DE POTENCIA", dxfattribs={'height': h_text_eq, 'color': 7}).set_placement(((i_x + f_x) / 2, y_cota_top - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        for i_d, f_d in cotas_distribucion:
            i_x, f_x = start_x_top + (i_d * factor_conv), start_x_top + (f_d * factor_conv)
            pts = [(i_x, y_cota_top + tick), (i_x, y_cota_top), (f_x, y_cota_top), (f_x, y_cota_top + tick)]
            msp.add_lwpolyline(pts, dxfattribs={'color': 7})
            msp.add_text("GAB. DE DIST.", dxfattribs={'height': h_text_eq, 'color': 7}).set_placement(((i_x + f_x) / 2, y_cota_top - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if inicio_baterias_x is not None:
            offset_y_cota = (150 / escala_b) if cotas_distribucion else 0
            y_cota_global_top = y_cota_top - offset_y_cota
            i_x, f_x = start_x_top + (inicio_baterias_x * factor_conv), start_x_top + (fin_baterias_x * factor_conv)
            pts = [(i_x, y_cota_global_top + tick), (i_x, y_cota_global_top), (f_x, y_cota_global_top), (f_x, y_cota_global_top + tick)]
            msp.add_lwpolyline(pts, dxfattribs={'color': 7})
            msp.add_text(nombre_cota_bat, dxfattribs={'height': h_text_eq, 'color': 7}).set_placement(((i_x + f_x) / 2, y_cota_global_top - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if inicio_ups_x is not None:
            i_x, f_x = start_x_top + (inicio_ups_x * factor_conv), start_x_top + (fin_ups_x * factor_conv)
            pts = [(i_x, y_cota_top + tick), (i_x, y_cota_top), (f_x, y_cota_top), (f_x, y_cota_top + tick)]
            msp.add_lwpolyline(pts, dxfattribs={'color': 7})
            msp.add_text(nombre_cota_ups, dxfattribs={'height': h_text_eq, 'color': 7}).set_placement(((i_x + f_x) / 2, y_cota_top - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)
        
        if gabconx_data:
            i_x, f_x = x_gconx, x_gconx + (gabconx_data[2]["ancho"]/escala_b)
            y_gconx_cota = y_gconx - (250 / escala_b)
            pts = [(i_x, y_gconx_cota + tick), (i_x, y_gconx_cota), (f_x, y_gconx_cota), (f_x, y_gconx_cota + tick)]
            msp.add_lwpolyline(pts, dxfattribs={'color': 7})
            msp.add_text("GABINETE DE CONEXIÓN", dxfattribs={'height': h_text_eq, 'color': 7}).set_placement(((i_x + f_x) / 2, y_gconx_cota - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)

        if gabpar_data:
            i_x, f_x = x_gpar, x_gpar + (gabpar_data[2]["ancho"]/escala_b)
            y_gpar_cota = y_gpar - (250 / escala_b)
            pts = [(i_x, y_gpar_cota + tick), (i_x, y_gpar_cota), (f_x, y_gpar_cota), (f_x, y_gpar_cota + tick)]
            msp.add_lwpolyline(pts, dxfattribs={'color': 7})
            msp.add_text("GABINETE PARALELO", dxfattribs={'height': h_text_eq, 'color': 7}).set_placement(((i_x + f_x) / 2, y_gpar_cota - (40 / FACTOR_ESCALA)), align=TextEntityAlignment.TOP_CENTER)

        # (Se omite el título "VISTA SUPERIOR" a petición)

        memoria_dxf = io.StringIO()
        doc.write(memoria_dxf)
        datos_descarga = memoria_dxf.getvalue()
        return datos_descarga, nombre_diagrama_completo.replace("/", "-").replace(":", "") + ".dxf"

    # --- CONTROL DE ACCIÓN Y ESTILOS DE BOTONES ---
    st.markdown("""
    <style>
        /* Botón de Generar (Azul cielo brillante) */
        div[data-testid="stButton"] > button {
            background-color: #0ea5e9 !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            height: 46px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stButton"] > button:hover {
            box-shadow: 0 0 15px #0ea5e9 !important;
            background-color: #38bdf8 !important;
            color: white !important;
        }
        
        /* Botón de Descargar (Amarillo brillante) */
        div[data-testid="stDownloadButton"] > button {
            background-color: #eab308 !important;
            color: #1c1917 !important;
            border: none !important;
            font-weight: 700 !important;
            height: 46px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            box-shadow: 0 0 15px #eab308 !important;
            background-color: #facc15 !important;
            color: black !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Creamos 3 columnas
    col_btn, col_msg, col_dl = st.columns(3)

    with col_btn:
        btn_generar = st.button("🛠️ GENERAR PLANO CAD (DXF)", use_container_width=True)

    if btn_generar:
        try:
            dxf_data, file_name = crear_dxf()
            
            with col_msg:
                # Mensaje renderizado como HTML flexible para alinear perfecto con botones de 46px
                st.markdown(
                    '<div style="display: flex; align-items: center; justify-content: center; height: 46px; background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; color: #34d399; font-weight: bold; font-size: 1.05rem;">'
                    '✓ ¡Plano generado!'
                    '</div>', 
                    unsafe_allow_html=True
                )
                
            with col_dl:
                st.download_button(
                    label="📥 DESCARGAR PLANO", 
                    data=dxf_data, 
                    file_name=file_name, 
                    mime="application/dxf", 
                    use_container_width=True
                )
        except Exception as e:
            import traceback
            with col_msg:
                st.markdown(
                    f'<div style="display: flex; align-items: center; justify-content: center; height: 46px; background-color: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; color: #f87171; font-weight: bold; font-size: 0.9rem;">'
                    f'❌ Error al generar'
                    f'</div>', 
                    unsafe_allow_html=True
                )
            st.error(f"**Detalle técnico del error:** {str(e)}")
            st.code(traceback.format_exc(), language="python")