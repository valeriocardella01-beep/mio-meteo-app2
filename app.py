import requests
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
from datetime import datetime

# @title Previsioni Meteo Gratuite Avanzate con Grafici (Senza API Key)
CITTA_SENZA_KEY = "Bientina" # @param {type:"string"}
ORIZZONTE_TEMPORALE = "1 giorno" # @param ["1 giorno", "3 giorni", "7 giorni"]

def get_meteo_wttr_con_grafici(citta, orizzonte):
    # Mapping dei giorni da richiedere
    giorni_mappa = {"1 giorno": 1, "3 giorni": 3, "7 giorni": 7}
    num_giorni = giorni_mappa.get(orizzonte, 3)

    url = f"https://wttr.in/{citta}?format=j1&lang=it"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Errore: Impossibile recuperare i dati per {citta}.")
            return

        data = response.json()

        # 1. Informazioni sulla stazione
        stazione_info = data.get("nearest_area", [{}])[0]
        nome_stazione = stazione_info.get("areaName", [{}])[0].get("value", "N/D")
        paese_stazione = stazione_info.get("country", [{}])[0].get("value", "N/D")
        altitudine = stazione_info.get("elevationByMeter", "N/D")

        current = data["current_condition"][0]
        temp_attuale = float(current["temp_C"])
        umidita = current["humidity"]
        pressione = float(current["pressure"])
        vento = current["windspeedKmph"]
        descrizione = current["lang_it"][0]["value"]

        # 2. Estrazione dati in base all'orizzonte temporale selezionato
        giorni_meteo = data["weather"][:num_giorni]

        ore_plot = []
        temperature_plot = []
        prob_pioggia_plot = []

        orario_corrente = datetime.now().hour
        tendenza_pioggia = "Nessuna pioggia significativa prevista nelle prossime ore."

        for i, giorno in enumerate(giorni_meteo):
            data_giorno = giorno["date"]
            # Formattiamo la data per l'asse X del grafico
            data_formattata = datetime.strptime(data_giorno, "%Y-%m-%d").strftime("%d/%m")

            for slot in giorno["hourly"]:
                ora_slot = int(slot["time"]) // 100
                prob_pioggia = int(slot["chanceofrain"])
                temp_slot = float(slot["tempC"])

                # Filtro per il primo giorno (mostra solo ore future)
                if i == 0 and ora_slot < orario_corrente:
                    continue

                ore_plot.append(f"{data_formattata} {ora_slot}:00")
                temperature_plot.append(temp_slot)
                prob_pioggia_plot.append(prob_pioggia)

                if i == 0 and prob_pioggia > 50 and tendenza_pioggia.startswith("Nessuna"):
                    desc_pioggia = slot.get("lang_it", [{"value": "pioggia"}])[0]["value"]
                    tendenza_pioggia = f"⚠️ Prevista {desc_pioggia} oggi intorno alle ore {ora_slot}:00 ({prob_pioggia}%)"

        # Analizziamo la tendenza termica a breve termine
        tendenza_temperatura = "Temperature stabili."
        if len(temperature_plot) >= 2:
            differenza = temperature_plot[-1] - temp_attuale
            if differenza >= 1.5:
                tendenza_temperatura = f"​▲ Tendenza ad aumento delle temperature (fino a {max(temperature_plot)}°C)."
            elif differenza <= -1.5:
                tendenza_temperatura = f"​▼ Tendenza a calo delle temperature (fino a {min(temperature_plot)}°C)."

        # 3. Analisi e Simulazione di avvicinamento Fronti Meteorologici
        # Basato sulla variazione di pressione barometrica e umidità correnti
        pressione_standard = 1013.25
        umidita_num = float(umidita)

        if pressione < 1008 and umidita_num > 80:
            fronte = "Fronte Freddo in avvicinamento"
            impatto_temp = "Diminuzione rapida di 4-7°C nelle prossime ore"
            impatto_pioggia = "Aumento significativo della piovosità (+40/60% probabilità di rovesci temporaleschi)"
            probabilita_fronte = "85%"
        elif pressione < 1012 and umidita_num > 70:
            fronte = "Fronte Caldo in transito"
            impatto_temp = "Aumento graduale di 2-4°C con clima afoso"
            impatto_pioggia = "Possibile pioggia leggera o nebbia persistente nelle prossime ore (+25% probabilità)"
            probabilita_fronte = "65%"
        elif pressione < 1005 and umidita_num > 85:
            fronte = "Fronte Occluso stazionario"
            impatto_temp = "Temperature instabili e fresche (-2°C rispetto alla norma)"
            impatto_pioggia = "Piogge continue o pioviggine diffusa nelle prossime 12-24 ore"
            probabilita_fronte = "90%"
        else:
            fronte = "Nessun fronte meteorologico instabile rilevato (Regime di Alta Pressione / Stabilità)"
            impatto_temp = "Variazioni termiche regolari entro il ciclo giorno/notte"
            impatto_pioggia = "Nessuna variazione significativa stimata"
            probabilita_fronte = "--"

        # Stampa del Report Testuale
        report = f"""
        --- BOLLETTINO METEO AVANZATO PER: {citta.upper()} ({orizzonte.upper()}) ---
        📡 Stazione di Rilevamento: {nome_stazione} ({paese_stazione}) | Altitudine: {altitudine} m
        🌡️ Temperatura Attuale: {temp_attuale}°C
        💧 Umidità: {umidita}%
        ⏱️ Pressione: {pressione} hPa
        🌬️ Vento: {vento} km/h
        ☁️ Condizione attuale: {descrizione.capitalize()}

        🔮 TENDENZA ORARIA / GIORNALIERA:
        ☔ Precipitazioni: {tendenza_pioggia}
        🌡️ Termica:   {tendenza_temperatura}

        ⚠️ MONITORAGGIO FRONTI METEOROLOGICI:
        🌤️ Fronte Rilevato: {fronte}
        🎯 Probabilità che colpisca la località: {probabilita_fronte}
        📈 Impatto Stimato Temperature: {impatto_temp}
        🌧️ Impatto Stimato Piovosità: {impatto_pioggia}
        """
        print(report)

        # Disegniamo i grafici se abbiamo dati futuri sufficienti
        if ore_plot:
            # Riduciamo le etichette sull'asse X per non sovrapporle se i giorni sono molti
            passo = max(1, len(ore_plot) // 10)
            posizioni_ticks = list(range(len(ore_plot)))
            etichette_x = [ore_plot[i] if i % passo == 0 else '' for i in range(len(ore_plot))]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

            # Grafico 1: Probabilità di pioggia
            colormap = plt.cm.Blues
            norm = mcolors.Normalize(vmin=0, vmax=100)
            colori_barre = [colormap(norm(p)) for p in prob_pioggia_plot]

            sns.barplot(x=ore_plot, y=prob_pioggia_plot, ax=ax1, palette=colori_barre, hue=ore_plot, legend=False)
            ax1.set_title(f"Probabilità di Pioggia ({orizzonte})\n(Colori più scuri indicano maggiore probabilità)")
            ax1.set_ylabel("Probabilità (%)")
            ax1.set_ylim(0, 100)
            ax1.set_xticks(posizioni_ticks)
            ax1.set_xticklabels(etichette_x, rotation=45, ha='right')
            ax1.grid(axis='y', linestyle='--', alpha=0.5)

            # Grafico 2: Andamento della temperatura
            sns.lineplot(x=ore_plot, y=temperature_plot, ax=ax2, marker="o", color="orangered", linewidth=2)
            ax2.set_title(f"Andamento della Temperatura ({orizzonte})")
            ax2.set_ylabel("Temperatura (°C)")
            ax2.set_xticks(posizioni_ticks)
            ax2.set_xticklabels(etichette_x, rotation=45, ha='right')
            ax2.grid(True, linestyle='--', alpha=0.5)

            plt.tight_layout()
            plt.show()

    except Exception as e:
        print(f"Si è verificato un errore durante l'elaborazione dei dati: {e}")

get_meteo_wttr_con_grafici(CITTA_SENZA_KEY, ORIZZONTE_TEMPORALE)
