import streamlit as st
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
from datetime import datetime

st.set_page_config(page_title="Meteo App", page_icon="🌤️", layout="centered")

st.title("🌤️ Previsioni Meteo Avanzate")

# Input della città direttamente dall'interfaccia web dell'applicazione
citta = st.text_input("Inserisci il nome della città:", value="Bientina")

if citta:
    url = f"https://wttr.in/{citta}?format=j1&lang=it"
    
    with st.spinner("Recupero dei dati meteo in corso..."):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                st.error(f"Errore: Impossibile recuperare i dati per {citta}.")
            else:
                data = response.json()
                current = data["current_condition"][0]
                
                temp_attuale = float(current["temp_C"])
                umidita = current["humidity"]
                pressione = current["pressure"]
                vento = current["windspeedKmph"]
                descrizione = current["lang_it"][0]["value"]
                
                orario_corrente = datetime.now().hour
                fasce_orarie = data["weather"][0["hourly"] # N.B. Qui useremo la sintassi corretta [0]["hourly"]
                fasce_orarie = data["weather"][0]["hourly"]
                
                tendenza_pioggia = "Nessuna pioggia significativa prevista nelle prossime ore."
                ore_plot, temperature_plot, prob_pioggia_plot = [], [], []
                
                for slot in fasce_orarie:
                    ora_slot = int(slot["time"]) // 100
                    prob_pioggia = int(slot["chanceofrain"])
                    temp_slot = float(slot["tempC"])
                    
                    if ora_slot >= orario_corrente:
                        ore_plot.append(f"{ora_slot}:00")
                        temperature_plot.append(temp_slot)
                        prob_pioggia_plot.append(prob_pioggia)
                        
                        if prob_pioggia > 50 and tendenza_pioggia.startswith("Nessuna"):
                            desc_pioggia = slot.get("lang_it", [{"value": "pioggia"}])[0]["value"]
                            tendenza_pioggia = f"⚠️ Prevista {desc_pioggia} intorno alle ore {ora_slot}:00 ({prob_pioggia}%)"
                
                tendenza_temperatura = "Temperature stabili."
                if len(temperature_plot) >= 2:
                    differenza = temperature_plot[-1] - temp_attuale
                    if differenza >= 1.5:
                        tendenza_temperatura = f"📈 Tendenza ad aumento ({temperature_plot[-1]}°C)."
                    elif differenza <= -1.5:
                        tendenza_temperatura = f"📉 Tendenza a calo ({temperature_plot[-1]}°C)."
                
                # Mostriamo il bollettino in modo moderno usando le card di Streamlit
                st.subheader(f"Meteo attuale a {citta.capitalize()}")
                
                col1, col2 = st.columns(2)
                col1.metric("Temperatura", f"{temp_attuale} °C")
                col2.metric("Umidità", f"{umidita} %")
                
                col3, col4 = st.columns(2)
                col3.metric("Pressione", f"{pressione} hPa")
                col4.metric("Vento", f"{vento} km/h")
                
                st.info(f"**Condizione attuale:** {descrizione.capitalize()}\n\n" 
                        f"☔ **Precipitazioni:** {tendenza_pioggia}\n\n" 
                        f"🌡️ **Tendenza termica:** {tendenza_temperatura}")
                
                # Disegniamo i grafici integrati nella pagina web
                if ore_plot:
                    st.subheader("Grafici delle prossime ore")
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
                    
                    colormap = plt.cm.Blues
                    norm = mcolors.Normalize(vmin=0, vmax=100)
                    colori_barre = [colormap(norm(p)) for p in prob_pioggia_plot]
                    
                    sns.barplot(x=ore_plot, y=prob_pioggia_plot, ax=ax1, palette=colori_barre, hue=ore_plot, legend=False)
                    ax1.set_title("Probabilità di Pioggia")
                    ax1.set_ylabel("Probabilità (%)")
                    ax1.set_ylim(0, 100)
                    ax1.grid(axis='y', linestyle='--', alpha=0.5)
                    
                    sns.lineplot(x=ore_plot, y=temperature_plot, ax=ax2, marker="o", color="orangered", linewidth=2.5)
                    ax2.set_title("Andamento della Temperatura")
                    ax2.set_ylabel("Temperatura (°C)")
                    ax2.grid(True, linestyle='--', alpha=0.5)
                    
                    st.pyplot(fig)
                    
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
            st.error(f"Si è verificato un errore: {e}")
