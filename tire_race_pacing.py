import streamlit as st
import numpy as np
from scipy.optimize import minimize
import plotly.graph_objects as go
from weasyprint import HTML

# --- HELPER FUNCTIONS ---
def format_pace(decimal_pace):
    """Converte i minuti decimali (es. 4.75) nel formato stringa MM:SS/km."""
    minutes = int(decimal_pace)
    seconds = int(round((decimal_pace - minutes) * 60))
    if seconds == 60:
        minutes += 1
        seconds = 0
    return f"{minutes}:{seconds:02d}/km"

def parse_pace_to_decimal(min_val, sec_val):
    """Converte minuti e secondi in un valore decimale per l'ottimizzatore."""
    return min_val + (sec_val / 60.0)

def generate_pdf_report(paces, speeds, total_time_str, params, station_time, station_ranks, stations):
    """Genera un file PDF strutturato e professionale usando WeasyPrint."""
    
    # Costruzione delle righe della tabella dei segmenti
    table_rows = ""
    for i, p in enumerate(paces):
        table_rows += f"""
        <tr>
            <td><strong>Chilometro {i+1}</strong></td>
            <td>Prima di: {stations[i].replace('_', ' ').title()}</td>
            <td class="pace">{format_pace(p)}</td>
            <td>{speeds[i]:.2f} km/h</td>
        </tr>
        """

    # Costruzione dei dettagli dei parametri
    param_rows = f"""
    <tr><td><strong>Focus Obiettivo Gara (α):</strong></td><td>{params['alpha']:.2f} (0=Comfort, 1=Velocità)</td></tr>
    <tr><td><strong>Margine di Sicurezza:</strong></td><td>{params['safety_margin']:.2f} (Inizio conservativo)</td></tr>
    <tr><td><strong>Tasso di Affaticamento:</strong></td><td>{params['stamina_decay']:.2f} (Perdita di stamina)</td></tr>
    <tr><td><strong>Impatto Temperatura:</strong></td><td>{params['heat_factor']:.2f} (Stress termico)</td></tr>
    <tr><td><strong>Tempo Medio alle Stazioni:</strong></td><td>{station_time} minuti per stazione</td></tr>
    """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm 15mm;
                background-color: #fafbfc;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2c3e50;
                margin: 0;
                padding: 0;
                line-height: 1.5;
            }}
            .header {{
                background-color: #1f3a52;
                color: white;
                padding: 30px;
                margin: -20mm -15mm 25px -15mm;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24pt;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                font-size: 11pt;
                color: #cbd5e1;
            }}
            .section {{
                margin-bottom: 25px;
                background: white;
                padding: 20px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
            }}
            h2 {{
                color: #1f3a52;
                font-size: 14pt;
                margin-top: 0;
                margin-bottom: 15px;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }}
            th, td {{
                padding: 10px 12px;
                text-align: left;
                font-size: 10pt;
                border-bottom: 1px solid #edf2f7;
            }}
            th {{
                background-color: #f8fafc;
                color: #475569;
                font-weight: bold;
            }}
            .pace {{
                font-family: 'Courier New', Courier, monospace;
                font-weight: bold;
                color: #0f172a;
            }}
            .summary-box {{
                background-color: #f0fdf4;
                border: 2px solid #bbf7d0;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
                margin-top: 20px;
            }}
            .summary-box h3 {{
                margin: 0;
                color: #166534;
                font-size: 12pt;
            }}
            .summary-box .time {{
                font-size: 28pt;
                font-weight: bold;
                color: #15803d;
                margin: 5px 0;
            }}
            .footer {{
                text-align: center;
                font-size: 8pt;
                color: #94a3b8;
                position: absolute;
                bottom: 0;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Report Strategia di Gara 5km</h1>
            <p>Pianificazione personalizzata del ritmo e gestione dello sforzo</p>
        </div>

        <div class="section">
            <h2>🏆 Tempo Totale Stimato di Gara</h2>
            <div class="summary-box">
                <h3>TEMPO TOTALE PREVISTO</h3>
                <div class="time">{total_time_str}</div>
                <p style="margin: 0; font-size: 9pt; color: #166534;">Include 5 km di corsa + soste stimate alle stazioni fitness</p>
            </div>
        </div>

        <div class="section">
            <h2>🏃‍♂️ Tabella dei Ritmi per Chilometro</h2>
            <table>
                <thead>
                    <tr>
                        <th>Frazione</th>
                        <th>Dettaglio Segmento</th>
                        <th>Ritmo Target</th>
                        <th>Velocità Media</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>⚙️ Configurazione Parametri Strategia</h2>
            <table>
                <tbody>
                    {param_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Generato automaticamente dal Race Pacing Strategy Calculator • 5km Fitness Race Edition
        </div>
    </body>
    </html>
    """
    # Converte l'HTML direttamente in un PDF in formato bytes
    return HTML(string=html_content).write_pdf()

# --- PAGE SETUP ---
st.set_page_config(page_title="Race Pacing Calculator", layout="wide")
st.title("🏃‍♂️ 5km Race Pacing Strategy Calculator")
st.write(
    "**Flusso di Gara:** Corsa 1 → Stazione 1 (Tire Flip) → Corsa 2 → Stazione 2 (Tire Pull) → "
    "Corsa 3 → Stazione 3 (Lunges) → Corsa 4 → Stazione 4 (Tire Carry) → Corsa 5 → **Stazione 5 (Burpees & Traguardo) 🏁**"
)

# --- STATION LIST ---
STATIONS = ["tire_flip", "tire_pull", "lunges", "tire_carry", "burpees"]

# --- SIDEBAR: CONTROLLI FLUIDI CON LABEL AGGIORNATE ---
st.sidebar.header("1. Strategia & Profilo Atleta")

# 1. Focus Obiettivo Gara
alpha = st.sidebar.slider(
    "Race Goal Focus (α)",
    min_value=0.0, max_value=1.0, value=0.5, step=0.01
)
st.sidebar.caption("🟢 **0.0:** Finire comodamente | 🟡 **0.5:** Approccio bilanciato | 🔴 **1.0:** Spingi alla massima velocità")
st.sidebar.write("") 

# 2. Margine di Sicurezza
safety_margin = st.sidebar.slider(
    "Margine di Sicurezza (Inizio Calmo)",
    min_value=0.0, max_value=1.0, value=0.4, step=0.01
)
st.sidebar.caption("🟢 **0.0:** Partenza aggressiva | 🟡 **0.5:** Moderata cautela | 🔴 **1.0:** Molto conservativo (Salva gambe all'inizio)")
st.sidebar.write("") 

# 3. Tasso di Affaticamento delle Gambe
stamina_decay = st.sidebar.slider(
    "Tasso di Affaticamento / Perdita Stamina",
    min_value=0.0, max_value=1.0, value=0.3, step=0.01
)
st.sidebar.caption("🟢 **0.0:** Corritore d'élite / Grande endurance | 🟡 **0.5:** Fitness regolare | 🔴 **1.0:** Principiante (Fatica rapida)")
st.sidebar.write("") 

# 4. Impatto della Temperatura
heat_factor = st.sidebar.slider(
    "Effetto Temperatura (Stress Termico)",
    min_value=0.0, max_value=1.0, value=0.15, step=0.01
)
st.sidebar.caption("🟢 **0.0:** Fresco e Perfetto (<15°C) | 🟡 **0.5:** Caldo e Umido | 🔴 **1.0:** Caldo torrido ed estremo")
st.sidebar.write("---")

# 5. LIMITI RESTRITTIVI DI PASSO (BOUNDARIES)
st.sidebar.subheader("Limiti Rigidi di Passo Corsa")
st.sidebar.write("La strategia sarà matematicamente bloccata entro questi confini esatti.")

col_min_m, col_min_s = st.sidebar.columns(2)
with col_min_m:
    min_m = st.number_input("Passo Più Lento (Min)", min_value=1, max_value=20, value=5, step=1)
with col_min_s:
    min_s = st.number_input("Passo Più Lento (Sec)", min_value=0, max_value=59, value=0, step=5)

col_max_m, col_max_s = st.sidebar.columns(2)
with col_max_m:
    max_m = st.number_input("Passo Più Rapido (Min)", min_value=1, max_value=20, value=4, step=1)
with col_max_s:
    max_s = st.number_input("Passo Più Rapido (Sec)", min_value=0, max_value=59, value=30, step=5)

# Converti input in decimali
upper_pace_bound = parse_pace_to_decimal(min_m, min_s)  
lower_pace_bound = parse_pace_to_decimal(max_m, max_s)  

# Controllo di sicurezza dei limiti
if lower_pace_bound >= upper_pace_bound:
    st.sidebar.error("❌ Il tuo 'Passo più rapido' deve essere più veloce del tuo 'Passo più lento'!")
    st.stop()

st.sidebar.write("---")
st.sidebar.subheader("Dettagli Stazioni")
station_time = st.sidebar.number_input("Minuti medi spesi in ogni stazione", min_value=0.5, value=3.0, step=0.5)

# --- MAIN PAGE: CLASSIFICAZIONE STAZIONI ---
st.header("2. Quanto pesano queste stazioni sulle tue gambe?")
st.write("Vota ogni stazione da **1 (Leggerissima sulle gambe)** a **5 (Brutale / Gambe di piombo)**.")

col1, col2, col3, col4, col5 = st.columns(5)
station_ranks = {}

with col1: station_ranks["tire_flip"] = st.selectbox(f"1. {STATIONS[0].replace('_', ' ').title()}", [1, 2, 3, 4, 5], index=2)
with col2: station_ranks["tire_pull"] = st.selectbox(f"2. {STATIONS[1].replace('_', ' ').title()}", [1, 2, 3, 4, 5], index=1)
with col3: station_ranks["lunges"] = st.selectbox(f"3. {STATIONS[2].replace('_', ' ').title()}", [1, 2, 3, 4, 5], index=4)
with col4: station_ranks["tire_carry"] = st.selectbox(f"4. {STATIONS[3].replace('_', ' ').title()}", [1, 2, 3, 4, 5], index=3)
with col5: station_ranks["burpees"] = st.selectbox(f"5. {STATIONS[4].replace('_', ' ').title()}", [1, 2, 3, 4, 5], index=0)

# --- ENGINE DI OTTIMIZZAZIONE ---
def objective_function(paces):
    total_time = 0
    total_fatigue = 0
    pace_range = upper_pace_bound - lower_pace_bound
    
    for i in range(5):
        p = paces[i] 
        speed_effort = (upper_pace_bound - p) / pace_range
        
        st_next = station_ranks[STATIONS[i]]
        st_prev = station_ranks[STATIONS[i-1]] if i > 0 else 1 
        
        segment_total_time = p + station_time
        total_time += segment_total_time
        
        station_stress = ((st_prev * 0.6) + (st_next * 0.4)) / 5.0
        fatigue_i = station_stress * speed_effort + (i * stamina_decay * 0.5 + heat_factor * 0.5) * (speed_effort ** 2)
        
        if i < 2:
            fatigue_i += safety_margin * speed_effort * 1.5
            
        total_fatigue += fatigue_i
        
    return alpha * total_time + (1 - alpha) * total_fatigue * pace_range

bounds = [(lower_pace_bound, upper_pace_bound) for _ in range(5)]
initial_paces = [(lower_pace_bound + upper_pace_bound) / 2] * 5

result = minimize(objective_function, initial_paces, bounds=bounds, method='SLSQP')

# --- DISPLAY RISULTATI ---
st.header("3. La Tua Strategia di Passo Personalizzata")

if result.success:
    optimized_paces = result.x
    optimized_speeds = [60 / p for p in optimized_paces]
    
    pace_range = upper_pace_bound - lower_pace_bound
    efforts = [(upper_pace_bound - p) / pace_range for p in optimized_paces]
    
    res_col1, res_col2 = st.columns([1, 2])
    
    # Calcolo del tempo complessivo di gara
    total_race_time_decimal = sum(optimized_paces) + (station_time * 5)
    total_minutes = int(total_race_time_decimal)
    total_seconds = int(round((total_race_time_decimal - total_minutes) * 60))
    if total_seconds == 60:
        total_minutes += 1
        total_seconds = 0
    race_time_string = f"{total_minutes}m {total_seconds:02d}s"
    
    with res_col1:
        st.subheader("Target di Passo al Chilometro")
        for i in range(5):
            formatted_p = format_pace(optimized_paces[i])
            st.metric(
                label=f"Corsa {i+1} (1 km prima di {STATIONS[i].replace('_', ' ').title()})", 
                value=formatted_p, 
                delta=f"{optimized_speeds[i]:.2f} km/h"
            )
            
        st.markdown("---")
        st.subheader("🏆 Riepilogo Gara Stimato")
        st.metric(label="Tempo Totale Previsto", value=race_time_string)
        
        # Dizionario contenente i parametri correnti scelti dall'utente da stampare nel report
        current_params = {
            'alpha': alpha,
            'safety_margin': safety_margin,
            'stamina_decay': stamina_decay,
            'heat_factor': heat_factor
        }
        
        # Generazione e Pulsante di Download del PDF
        pdf_data = generate_pdf_report(
            optimized_paces, optimized_speeds, race_time_string, 
            current_params, station_time, station_ranks, STATIONS
        )
        
        st.write("")
        st.download_button(
            label="📥 Scarica Report Strategia (PDF)",
            data=pdf_data,
            file_name="Strategia_Gara_5km.pdf",
            mime="application/pdf",
            help="Scarica un documento PDF formattato con i dettagli di questa configurazione."
        )

    with res_col2:
        st.subheader("Visualizzazione Strategia d'Intensità")
        
        x_labels = [f"Corsa {i+1} (1 km)\n➔ {STATIONS[i].replace('_', ' ').title()}" for i in range(5)]
        hover_text = [f"Velocità: {s:.2f} km/h<br>Passo: {format_pace(p)}" for s, p in zip(optimized_speeds, optimized_paces)]
        
        custom_colorscale = [
            [0.0, '#2ca02c'],   # Verde (Passo più tranquillo / Gestione)
            [0.5, '#fec44f'],   # Giallo (Sforzo Intermedio)
            [1.0, '#d62728']    # Rosso (Massima Velocità / Livello Pro)
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_labels, y=optimized_speeds, mode='lines',
            line=dict(color='rgba(150,150,150,0.4)', width=3), hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=x_labels, y=optimized_speeds, mode='markers+text',
            text=[format_pace(p) for p in optimized_paces],
            textposition="top center", hoverinfo="text", hovertext=hover_text,
            marker=dict(
                size=14, color=efforts, colorscale=custom_colorscale,
                cmin=0.0, cmax=1.0, showscale=True,           
                colorbar=dict(
                    title="Livello Sforzo",
                    tickvals=[0.0, 0.5, 1.0],
                    ticktext=["Passo Calmo", "Intermedio", "Massima Velocità"],
                    thickness=15
                ),
                line=dict(color='white', width=2)
            )
        ))
        
        max_speed_view = 60 / lower_pace_bound
        min_speed_view = 60 / upper_pace_bound
        
        fig.update_layout(
            xaxis_title="Segmenti di Gara",
            yaxis_title="Velocità Target Corrente (km/h)",
            yaxis=dict(range=[min_speed_view - 0.4, max_speed_view + 0.4]), 
            margin=dict(l=20, r=20, t=30, b=20), height=430, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("I parametri o i limiti di passo inseriti sono in conflitto. Prova ad allargare leggermente i limiti di passo corsa.")