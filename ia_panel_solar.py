from flask import Flask, render_template
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation
#from matplotlib.dates import DateFormatter
from pvlib import solarposition, tracking
from datetime import datetime, timedelta
import pytz
import matplotlib.dates as mdates

app = Flask(__name__)

def index():
    # Obtener la zona horaria local automáticamente
    local_tz = pytz.timezone('America/Mexico_City')  # MX para México

    # Obtener la fecha y hora actual
    current_datetime = datetime.now(local_tz)
    current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

    # Calcular el inicio y el final del período de interés
    start_time = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = current_datetime.replace(hour=23, minute=45, second=0, microsecond=0)

    # Generar el índice de tiempo
    times = pd.date_range(start_time, end_time, freq='15min', tz=local_tz)
    
    # Calcular la posición solar
    solpos = solarposition.get_solarposition(times, lat=40, lon=-80)

    # Inicialización del gráfico
    truetracking = tracking.singleaxis(
        apparent_zenith=solpos['apparent_zenith'],
        solar_azimuth=solpos['azimuth'],
        axis_tilt=0, axis_azimuth=180, max_angle=90, backtrack=False, gcr=0.5)  
     
    # Extraer las posiciones de seguimiento
    position = truetracking['tracker_theta'].fillna(0)

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(5.5, 4))

    # Graficar la curva de seguimiento
    ax.plot(position.index, position.values, label='Curva de Seguimiento', color='black')
    ax.set_ylim(truetracking_position.min() - 5, truetracking_position.max() + 5)

        # Encontrar y marcar los puntos Mínimo y Máximo
    best_min = position.idxmin()
    best_max = position.idxmax()
    ax.plot(best_min, position[best_min], color='#08968F', marker='o', label='Mejor Hora Mañana')
    ax.plot(best_max, position[best_max], color='#0652EA', marker='o', label='Mejor Hora Tarde')

    # Estilos y Protección del Texto de Abajo
    plt.title(f'Irradiación Solar ({current_datetime.strftime("%Y-%m-%d")})', fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    
    # Mostrar solo algunas etiquetas de hora para que no se amontonen
    x_labels = [dt.strftime('%I:%M %p') if i % 8 == 0 else '' for i, dt in enumerate(position.index)]
    ax.set_xticks(position.index)
    ax.set_xticklabels(x_labels)
    ax.legend(fontsize=8)
    
    fig.tight_layout()

    # Guardar la Imagen como PNG (Más ligero que un GIF)
    os.makedirs('static', exist_ok=True)
    graph_filename = 'static/panelsolar.png'
    plt.savefig(graph_filename)
    plt.close(fig) # Cierra la imagen para liberar memoria del servidor

    # Enviar los Datos Listos al HTML
    return render_template(
        'index.html', 
        animation_filename=graph_filename, 
        mejor_hora_min=best_min.strftime("%I:%M %p"), 
        mejor_hora_max=best_max.strftime("%I:%M %p")
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

