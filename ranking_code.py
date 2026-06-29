import pandas as pd
import numpy as np
import plotly.graph_objects as go
from IPython.core.display import display, HTML

# ==========================================
# 1. KONFIGURACJA LINKU DO PLIKU EXCEL (.XLSX)
# ==========================================

# KROK A: Wklej tutaj oryginalny link do udostępniania Twojego pliku Excel z Dysku Google
# Link powinien wyglądać mniej więcej tak: https://drive.google.com/file/d/XYZ_ID_PLIKU_XYZ/view?usp=sharing
link_do_udostepnienia = "https://docs.google.com/spreadsheets/d/17qgzEkRRJBSlOcsvYyOs5AFYQ2Wyjfsi/edit?usp=sharing&ouid=112239134874349160222&rtpof=true&sd=true"

# KROK B: Automatyczna konwersja linku na format bezpośredniego pobierania binarnego dla Excela
file_id = link_do_udostepnienia.split('/d/')[1].split('/')[0]
direct_download_url = f"https://docs.google.com/uc?export=download&id={file_id}"

# KROK C: Pobranie i wczytanie pliku Excel bezpośrednio do pamięci
# Jeśli dane masz w konkretnej zakładce, dopisz parametr: sheet_name="NazwaTwojejZakladki"
df_raw = pd.read_excel(direct_download_url, sheet_name='Faza grupowa')
df_raw_2 = pd.read_excel(direct_download_url, sheet_name='Faza playoff')

nowa_lista = [f'Kolejka_1_{element}' for element in list(df_raw.iloc[2, 2:50])]
columny = ['Obstawiacz']+nowa_lista
df_1 = df_raw.iloc[27:39, 1:50]
df_1.columns = columny

nowa_lista_2 = [f'Kolejka_2_{element}' for element in list(df_raw.iloc[2, 2:50])]
columny_2 = ['Obstawiacz']+nowa_lista_2
df_2 = df_raw.iloc[69:81, 1:50]
df_2.columns = columny_2

nowa_lista_3 = [f'Kolejka_3_{element}' for element in list(df_raw.iloc[2, 2:50])]
columny_3 = ['Obstawiacz']+nowa_lista_3
df_3 = df_raw.iloc[110:122, 1:50]
df_3.columns = columny_3

nowa_lista_4 = [f'1/16_{element}' for element in list(df_raw_2.iloc[2, 2:50])]
columny_4 = ['Obstawiacz']+nowa_lista_4
df_4 = df_raw_2.iloc[27:39, 1:50]
df_4.columns = columny_4

wynik_cols = [col for col in df_4.columns if col.startswith('1/16')]

ostatnia_wazna_col = None
for col in reversed(wynik_cols):
    if (df_4[col] != 0).any():
        ostatnia_wazna_col = col
        break

if ostatnia_wazna_col:
    idx = df_4.columns.get_loc(ostatnia_wazna_col)
    df_4 = df_4.iloc[:, :idx + 1]  # +1, żeby zachować tę ważną kolumnę
else:

    df_4 = df_4[['Obstawiacz']]

df_raw = df_1.set_index('Obstawiacz').join(df_2.set_index('Obstawiacz'), how='outer').join(df_3.set_index('Obstawiacz'), how='outer').join(df_4.set_index('Obstawiacz'), how='outer').reset_index()
df_raw.fillna(0, inplace=True)

# ==========================================
# 2. PRZELICZANIE SUMY SKUMULOWANEJ
# ==========================================
kolumny_zdarzen = [col for col in df_raw.columns if col != 'Obstawiacz']

df_cumulative = pd.DataFrame()
df_cumulative['Obstawiacz'] = df_raw['Obstawiacz']
df_cumulative[kolumny_zdarzen] = df_raw[kolumny_zdarzen].cumsum(axis=1)

# ==========================================
# 3. GENEROWANIE WYKRESU I KROKÓW SUWAKA
# ==========================================
fig = go.Figure()

gracze = df_cumulative["Obstawiacz"].unique()
kolory = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
    "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#4B0082", "#FFD700"
]

avatars_dict = {
    "Krzysiek": "https://i.postimg.cc/5jcthcsD/Krzysztof.jpg",
    "Devid": "https://i.postimg.cc/t70gK0Bm/Devid.jpg",
    "Bartek": "https://i.postimg.cc/CdyK3ycX/Bartek.jpg",
    "Adam": "https://i.postimg.cc/HjGLqG6v/Adam.jpg",
    "Przemek": "https://i.postimg.cc/t70gK0Bf/Przemek-Bak.jpg",
    "Pops": "https://i.postimg.cc/hjNBZLjv/Pops.jpg",
    "Wojtas":"https://i.postimg.cc/bvX1PMBD/wb-ryjec.png"
}

# Tworzymy główne linie wykresu (pełna historia jako punkt wyjścia)
lista_obrazkow = []
for idx, gracz in enumerate(gracze):
    row_cumulative = df_cumulative[df_cumulative["Obstawiacz"] == gracz].iloc[0]
    x_data = kolumny_zdarzen
    y_data = row_cumulative[kolumny_zdarzen].values

    kolor_gracza = kolory[idx % len(kolory)]
    pierwsza_litera = str(gracz)[0].upper()

    if gracz in avatars_dict:
        awatar_url = avatars_dict[gracz]
    else:
        awatar_url = (
            f"data:image/svg+xml;utf8,"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'>"
            f"  <circle cx='30' cy='30' r='28' fill='{kolor_gracza.replace('#', '%23')}' stroke='white' stroke-width='3'/>"
            f"  <text x='50%' y='55%' dominant-baseline='middle' text-anchor='middle' "
            f"        fill='white' font-family='Arial, sans-serif' font-size='24' font-weight='bold'>{pierwsza_litera}</text>"
            f"</svg>"
        )

    hover_tekst = (
        f"<b>{gracz}</b><br>"
        f"Zdarzenie: %{{x}}<br>"
        f"Suma punktów: %{{y}} pkt<extra></extra>"
    )

    fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode="lines+markers",
            name=gracz,
            line=dict(color=kolor_gracza, width=3),
            hovertemplate=hover_tekst  # <-- Podmieniamy na nowy, czysty tekst
        ))

    # Początkowa pozycja awatara (na samym końcu, dla ostatniego zdarzenia)
    lista_obrazkow.append(dict(
        source=awatar_url, xref="x", yref="y",
        x=x_data[-1], y=y_data[-1],
        sizex=0.9, sizey=16,
        xanchor="left", yanchor="middle"
    ))

fig.update_layout(images=lista_obrazkow)

# ==========================================
# 4. BUDOWANIE DYNAMICZNYCH KROKÓW DLA SUWAKA
# ==========================================
steps = []
# Przechodzimy przez każde zdarzenie po kolei (każdy krok suwaka)
for i, punkt_stopu in enumerate(kolumny_zdarzen):
    widoczne_kolumny = kolumny_zdarzen[:i+1]

    # Przygotowujemy zmiany wartości linii (obcinamy dane do aktualnego kroku suwaka)
    zmiana_serii = []
    obrazy_kroku = []

    for idx, gracz in enumerate(gracze):
        row_cumulative = df_cumulative[df_cumulative["Obstawiacz"] == gracz].iloc[0]
        y_aktualne = row_cumulative[widoczne_kolumny].values

        # Aktualizacja punktów linii
        zmiana_serii.append(dict(
            x=widoczne_kolumny,
            y=y_aktualne
        ))

        # Przesunięcie pozycji awatara na koniec aktualnie wybranej osi czasu
        obrazy_kroku.append(dict(
            x=widoczne_kolumny[-1],
            y=y_aktualne[-1]
        ))

    # Tworzymy definicję zachowania dla danego kroku suwaka
    krok = dict(
        method="update",
        label=str(punkt_stopu),
        args=[
            # Słownik 1: co zmienić w seriach danych (nasze ucięte linie x i y)
            {
                "x": [s['x'] for s in zmiana_serii],
                "y": [s['y'] for s in zmiana_serii]
            },
            # Słownik 2: co zmienić w wyglądzie layoutu (nowe pozycje awatarów)
            {
                "images": [
                    {**lista_obrazkow[idx], "x": img['x'], "y": img['y']}
                    for idx, img in enumerate(obrazy_kroku)
                ]
            }
        ]
    )
    steps.append(krok)

# Dodajemy suwak do konfiguracji wykresu
sliders = [dict(
    active=len(kolumny_zdarzen) - 1, # domyślnie suwak ustawiony na ostatnim meczu
    currentvalue={"prefix": "Przeglądasz historię do: ", "font": {"size": 14, "color": "#666"}},
    pad={"t": 60}, # odstęp od wykresu
    steps=steps
)]

# ==========================================
# 5. PERSONALIZACJA I SCRIPT INTERAKCJI (Slider + Legenda)
# ==========================================
fig.update_layout(
    title=dict(text="<b>Ranking</b>", font=dict(size=20, family="Arial")),
    xaxis=dict(title="Zdarzenia", gridcolor="#EBF0F5", showline=True, linecolor="#999"),
    yaxis=dict(title="Suma punktów", gridcolor="#EBF0F5", showline=True, linecolor="#999"),
    plot_bgcolor="white",
    hovermode="closest",
    margin=dict(r=120, b=100), # powiększony dolny margines na suwak
    legend=dict(title="<b>Typerzy:</b><br>(kliknij aby schować)", font=dict(size=11)),
    sliders=sliders
)

wykres_html = fig.to_html(include_plotlyjs='cdn', full_html=False)

# Rozbudowany skrypt JS, który pilnuje ukrywania awatarów z legendy,
# nawet jeśli w międzyczasie szalejesz suwakiem.
custom_js_script = """
<script>
var polaczonyWykres = document.getElementsByClassName('plotly-graph-div')[0];

// Tablica pamiętająca, których graczy ręcznie wyłączyliśmy w legendzie
var stanUkrytych = {};

polaczonyWykres.on('plotly_legendclick', function(data) {
    var indeksGracza = data.curveNumber;
    var aktualnyLayout = polaczonyWykres.layout;

    if (aktualnyLayout.images && aktualnyLayout.images[indeksGracza]) {
        var obecnaWidocznosc = aktualnyLayout.images[indeksGracza].opacity;
        var nowaOpacity = (obecnaWidocznosc === 0) ? 1 : 0;

        // Zapisujemy stan, żeby suwak wiedział, że ten gracz ma być niewidoczny
        stanUkrytych[indeksGracza] = nowaOpacity;

        var update = {};
        update['images[' + indeksGracza + '].opacity'] = nowaOpacity;
        Plotly.relayout(polaczonyWykres, update);
    }
    return true;
});

// Nasłuchujemy ruchów suwaka, żeby po przesunięciu czasu natychmiast nałożyć filtry z legendy
polaczonyWykres.on('plotly_sliderchange', function(data) {
    var aktualnyLayout = polaczonyWykres.layout;
    var update = {};

    // Iterujemy po obrazkach i aplikujemy z powrotem ukrycie, jeśli gracz jest wygaszony w legendzie
    if (aktualnyLayout.images) {
        for (var idx in stanUkrytych) {
            if (stanUkrytych[idx] === 0) {
                update['images[' + idx + '].opacity'] = 0;
            }
        }
        if (Object.keys(update).length > 0) {
            Plotly.relayout(polaczonyWykres, update);
        }
    }
});
</script>
"""


# from google.colab import drive
# import os

# # Montujemy Dysk Google w środowisku Colab
# drive.mount('/content/drive')

# pelny_kod_strony = wykres_html + custom_js_script


# # 2. Definiujemy ścieżkę zapisu bezpośrednio na Twoim Dysku Google
# sciezka_na_dysku = '/content/drive/MyDrive/ranking_mundial26.html'

# # 3. Zapisujemy/nadpisujemy plik (zawsze pod tą samą nazwą)
# with open(sciezka_na_dysku, "w", encoding="utf-8") as f:
#     f.write(pelny_kod_strony)

# print("Sukces! Wykres został zaktualizowany bezpośrednio na Twoim Dysku Google.")


# ==============================================================================
# DANE DO TWOJEGO GITHUBA (Uzupełnij przed uruchomieniem)
# ==============================================================================
import os

# Zamiast wpisywać token tekstowo, pobieramy go bezpiecznie z systemu:
GITHUB_TOKEN = os.environ.get("SUPER_SECRET_TOKEN") 
GITHUB_USER = "Wator96"
REPO_NAME = "ranking_mundial"  
FILENAME = "index.html"

# ==============================================================================
# DANE DO TWOJEGO GITHUBA (Sprawdź wielkość liter!)
# ==============================================================================
# GITHUB_TOKEN = "TUTAJ_WKLEJ_KOD_TOKENU_Z_KROKU_2"
# GITHUB_USER = "TWÓJ_NICK_Z_GITHUBAS"
# REPO_NAME = "ranking"
# FILENAME = "index.html"

# ==============================================================================
# AUTOMATYCZNE WYSYŁANIE Z DIAGNOSTYKĄ
# ==============================================================================
import requests
import base64

pelny_kod_strony = wykres_html + custom_js_script

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# --- TEST 1: Sprawdzenie połączenia z Twoim profilem ---
test_user_url = "https://api.github.com/user"
user_res = requests.get(test_user_url, headers=headers)

if user_res.status_code != 200:
    print("❌ BŁĄD TOKENU: Twój token jest niepoprawny lub wygasł. GitHub go odrzuca.")
    print("Wygeneruj nowy Token (classic) i upewnij się, że zaznaczyłeś ptaszek przy 'repo'.")
else:
    zalogowany_jako = user_res.json().get('login')
    print(f"✅ Token działa! Zalogowano pomyślnie jako: {zalogowany_jako}")

    # --- TEST 2: Sprawdzenie widoczności repozytorium ---
    repo_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}"
    repo_res = requests.get(repo_url, headers=headers)

    if repo_res.status_code == 404:
        print(f"❌ BŁĄD REPOZYTORIUM: GitHub twierdzi, że repozytorium '{REPO_NAME}' nie istnieje na koncie '{GITHUB_USER}'.")
        print(" -> Sprawdź, czy nie ma literówki w nazwie repozytorium lub użytkownika (małe/duże litery!).")
        print(" -> Jeśli repozytorium jest prywatne, Twój token NIE MA uprawnień 'repo' (musisz wygenerować nowy token z tym ptaszkiem).")
    else:
        print(f"✅ Repozytorium '{REPO_NAME}' zostało znalezione!")

        # --- KROK WŁAŚCIWY: Wysyłanie pliku ---
        contents_url = f"{repo_url}/contents/{FILENAME}"

        # Sprawdzamy czy plik istnieje
        file_res = requests.get(contents_url, headers=headers)
        sha = file_res.json().get("sha") if file_res.status_code == 200 else None

        content_encoded = base64.b64encode(pelny_kod_strony.encode("utf-8")).decode("utf-8")

        data = {
            "message": "Aktualizacja rankingu (automatyczna z Colaba)",
            "content": content_encoded
        }
        if sha:
            data["sha"] = sha

        put_response = requests.put(contents_url, headers=headers, json=data)

        if put_response.status_code in [200, 201]:
            print("\n🚀 SUKCES! Plik został wysłany.")
            print(f"Strona zaktualizuje się za chwilę pod adresem: https://{GITHUB_USER}.github.io/{REPO_NAME}/")
        else:
            print("\n❌ Błąd podczas zapisu pliku:")
            print(put_response.json())