import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider
import mplcursors  # Import mplcursors
from shapely.geometry import Point

# dadesgeojson
fitxer_json = "divisions-administratives-v2r1-comarques-100000-20230928.json"
comarques = gpd.read_file(fitxer_json)

# Dades dels accidents
fitxer = "morts.csv"
gdf = pd.read_csv(fitxer)

# Colors
colors = {
    'yellow': '#ffffb2',
    'orange': '#fecc5c',
    'darkorange': '#fd8d3c',
    'red': '#e31a1c',
    'lightgrey': '#cccccc'
}

legend_labels = {
    'yellow': '0-4 morts',
    'orange': '5-9 morts',
    'darkorange': '10-14 morts',
    'red': '15 o més morts',
    'lightgrey': 'sense dades'
}

# Crear el gràfoc
fig, ax = plt.subplots(figsize=(12, 8))

# Función que calcula las datos y hace el plot
def update(val):
    # Dades del 2011
    gdf_2011 = gdf[gdf['Any'] == val]

    # Es fusionen les dades per tal de tenir els valor
    comarques_merged = comarques.merge(gdf_2011, left_on='NOMCOMAR', right_on='nomCom', how='left')

    # Asignació del color
    comarques_merged['color'] = pd.cut(comarques_merged['F_MORTS'],
                                       bins=[-1, 4, 9, 14, float('inf')],
                                       labels=['yellow', 'orange', 'darkorange', 'red'])

    comarques_merged['color'] = comarques_merged['color'].astype('object')
    # Asigna el color gris als valors NaN
    comarques_merged['color'].fillna('lightgrey', inplace=True)

    ax.clear()

    # Visualización
    for color, label in legend_labels.items():
        comarques_merged[comarques_merged['color'] == color].plot(ax=ax, color=colors[color], edgecolor="black",
                                                                  label=label)

    # Posicionem la legenda, s'ha de jugar amb bbox per tal de trobar la posició optima
    handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[color], markersize=10, label=label)
               for color, label in legend_labels.items()]

    ax.legend(handles=handles, title='Nombre de morts', loc='upper center', bbox_to_anchor=(0.7, 0.3))

    ax.set_title(f"Morts en accidents en les comarques catalanes ({val})")
    ax.axis("off")

    # cursor
    mplcursors.cursor(hover=True).connect("add", lambda sel: show_cursor_info(sel, comarques_merged))

# Funció del cursor
def show_cursor_info(sel, comarques_merged):
    x, y = sel.target
    # Verificar si el cursor está en la zona del slider
    if ax_slider.contains_point((x, y)):
        sel.annotation.set_text("Slider")
        return
    
    point = Point(x, y)
    comarque_info = comarques_merged[comarques_merged.geometry.contains(point)]
    if not comarque_info.empty:
        comarque_name = comarque_info.iloc[0]['NOMCOMAR']
        morts_value = int(comarque_info.iloc[0]['F_MORTS'])
        sel.annotation.set_text(f"Comarca: {comarque_name}\nMorts: {morts_value}")
    else:
        sel.annotation.set_text("No data")

# Slider per seleccionar l'any
ax_slider = plt.axes([0.31, 0.02, 0.5, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Any', 2010, 2021, valinit=2010, valstep=1)

# Funció d'actualització del mapa en canviar el valor del slider
slider.on_changed(update)

# Creació inicial del mapa
update(2010)

plt.show()
