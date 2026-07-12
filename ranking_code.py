import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

link_do_udostepnienia = "https://docs.google.com/spreadsheets/d/17qgzEkRRJBSlOcsvYyOs5AFYQ2Wyjfsi/edit?usp=sharing&ouid=112239134874349160222&rtpof=true&sd=true"

file_id = link_do_udostepnienia.split('/d/')[1].split('/')[0]
direct_download_url = f"https://docs.google.com/uc?export=download&id={file_id}"

df_raw = pd.read_excel(direct_download_url, sheet_name='Faza grupowa')
df_raw_2 = pd.read_excel(direct_download_url, sheet_name='Faza playoff')
df_raw_3 = pd.read_excel(direct_download_url, sheet_name='Turniej')

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
    df_4 = df_4.iloc[:, :idx + 1]  
else:
    df_4 = df_4[['Obstawiacz']]

nowa_lista_5 = [f'1/8_{element}' for element in list(df_raw_2.iloc[2, 2:26])]
columny_5 = ['Obstawiacz']+nowa_lista_5
df_5 = df_raw_2.iloc[69:81, 1:26]
df_5.columns = columny_5

wynik_cols = [col for col in df_5.columns if col.startswith('1/8')]

ostatnia_wazna_col = None
for col in reversed(wynik_cols):
    if (df_5[col] != 0).any():
        ostatnia_wazna_col = col
        break

if ostatnia_wazna_col:
    idx = df_5.columns.get_loc(ostatnia_wazna_col)
    df_5 = df_5.iloc[:, :idx + 1]  
else:
    df_5 = df_5[['Obstawiacz']]

nowa_lista_6 = [f'1/4_{element}' for element in list(df_raw_2.iloc[2, 2:14])]
columny_6 = ['Obstawiacz']+nowa_lista_6
df_6 = df_raw_2.iloc[111:123, 1:14]
df_6.columns = columny_6

wynik_cols = [col for col in df_6.columns if col.startswith('1/4')]

ostatnia_wazna_col = None
for col in reversed(wynik_cols):
    if (df_6[col] != 0).any():
        ostatnia_wazna_col = col
        break

if ostatnia_wazna_col:
    idx = df_6.columns.get_loc(ostatnia_wazna_col)
    df_6 = df_6.iloc[:, :idx + 1]  
else:
    df_6 = df_6[['Obstawiacz']]

df_raw = df_1.set_index('Obstawiacz').join(df_2.set_index('Obstawiacz'), how='outer').join(df_3.set_index('Obstawiacz'), how='outer').join(df_4.set_index('Obstawiacz'), how='outer').join(df_5.set_index('Obstawiacz'), how='outer').join(df_6.set_index('Obstawiacz'), how='outer').reset_index()
df_raw.fillna(0, inplace=True)

df_raw_3_temp = df_raw_3.iloc[5:17,[0, 8]]
df_raw_3_temp.columns=['Obstawiacz', 'Predykcja_turniej']

df_raw = df_raw.set_index('Obstawiacz').join(df_raw_3_temp.set_index('Obstawiacz'), how='outer').reset_index()
df_raw.fillna(0, inplace=True)
kolumny_zdarzen = [col for col in df_raw.columns if col != 'Obstawiacz']

df_cumulative = pd.DataFrame()
df_cumulative['Obstawiacz'] = df_raw['Obstawiacz']
df_cumulative[kolumny_zdarzen] = df_raw[kolumny_zdarzen].cumsum(axis=1)

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

lista_obrazkow = []

# Rysujemy dwie serie na gracza: główną (ciągłą) oraz odcinek predykcji (kropkowany)
for idx, gracz in enumerate(gracze):
    row_cumulative = df_cumulative[df_cumulative["Obstawiacz"] == gracz].iloc[0]
    kolor_gracza = kolory[idx % len(kolory)]
    pierwsza_litera = str(gracz)[0].upper()

    x_main = kolumny_zdarzen[:-1]
    y_main = row_cumulative[x_main].values
    
    x_pred = kolumny_zdarzen[-2:]
    y_pred = row_cumulative[x_pred].values

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

    # 1. Linia główna (ciągła)
    fig.add_trace(go.Scatter(
        x=x_main,
        y=y_main,
        mode="lines+markers",
        name=gracz,
        line=dict(color=kolor_gracza, width=3, dash="solid"),
        hovertemplate=hover_tekst
    ))

    # 2. Ostatnie zdarzenie (kropkowane)
    fig.add_trace(go.Scatter(
        x=x_pred,
        y=y_pred,
        mode="lines+markers",
        name=gracz,
        line=dict(color=kolor_gracza, width=3, dash="dot"),
        hovertemplate=hover_tekst,
        showlegend=False
    ))

    lista_obrazkow.append(dict(
        source=awatar_url, xref="x", yref="y",
        x=kolumny_zdarzen[-1], y=row_cumulative[kolumny_zdarzen[-1]],
        sizex=0.9, sizey=16,
        xanchor="left", yanchor="middle"
    ))

fig.update_layout(images=lista_obrazkow)

# ==========================================
# 4. BUDOWANIE DYNAMICZNYCH KROKÓW DLA SUWAKA
# ==========================================
steps = []

for i, punkt_stopu in enumerate(kolumny_zdarzen):
    widoczne_kolumny = kolumny_zdarzen[:i+1]

    zmiana_x = []
    zmiana_y = []
    obrazy_kroku = []

    for idx, gracz in enumerate(gracze):
        row_cumulative = df_cumulative[df_cumulative["Obstawiacz"] == gracz].iloc[0]
        
        if punkt_stopu == "Predykcja_turniej":
            x_m = widoczne_kolumny[:-1]
        else:
            x_m = widoczne_kolumny
        y_m = row_cumulative[x_m].values
        
        zmiana_x.append(x_m)
        zmiana_y.append(y_m)

        if punkt_stopu == "Predykcja_turniej":
            x_p = widoczne_kolumny[-2:]
            y_p = row_cumulative[x_p].values
        else:
            x_p = []
            y_p = []
            
        zmiana_x.append(x_p)
        zmiana_y.append(y_p)

        obrazy_kroku.append(dict(
            x=widoczne_kolumny[-1],
            y=row_cumulative[widoczne_kolumny[-1]]
        ))

    krok = dict(
        method="update",
        label=str(punkt_stopu),
        args=[
            {
                "x": zmiana_x,
                "y": zmiana_y
            },
            {
                "images": [
                    {**lista_obrazkow[idx], "x": img['x'], "y": img['y']}
                    for idx, img in enumerate(obrazy_kroku)
                ]
            }
        ]
    )
    steps.append(krok)

sliders = [dict(
    active=len(kolumny_zdarzen) - 1, 
    currentvalue={"prefix": "Przeglądasz historię do: ", "font": {"size": 14, "color": "#666"}},
    pad={"t": 60}, 
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
    margin=dict(r=120, b=100), 
    legend=dict(title="<b>Typerzy:</b><br>(kliknij aby schować)", font=dict(size=11)),
    sliders=sliders
)

wykres_html = fig.to_html(include_plotlyjs='cdn', full_html=False)

custom_js_script = """
<script>
var polaczonyWykres = document.getElementsByClassName('plotly-graph-div')[0];
var stanUkrytych = {};

polaczonyWykres.on('plotly_legendclick', function(data) {
    var indeksGracza = Math.floor(data.curveNumber / 2);
    var aktualnyLayout = polaczonyWykres.layout;

    if (aktualnyLayout.images && aktualnyLayout.images[indeksGracza]) {
        var obecnaWidocznosc = aktualnyLayout.images[indeksGracza].opacity;
        var nowaOpacity = (obecnaWidocznosc === 0) ? 1 : 0;

        stanUkrytych[indeksGracza] = nowaOpacity;

        var update = {};
        update['images[' + indeksGracza + '].opacity'] = nowaOpacity;
        
        var seriaKropkowana = (indeksGracza * 2) + 1;
        Plotly.restyle(polaczonyWykres, {visible: nowaOpacity === 1 ? true : 'legendonly'}, [seriaKropkowana]);
        Plotly.relayout(polaczonyWykres, update);
    }
    return true;
});

polaczonyWykres.on('plotly_sliderchange', function(data) {
    var aktualnyLayout = polaczonyWykres.layout;
    var update = {};

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

GITHUB_TOKEN = os.environ.get("SUPER_SECRET_TOKEN")
GITHUB_USER = "Wator96"
REPO_NAME = "ranking_mundial
