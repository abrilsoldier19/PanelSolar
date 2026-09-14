from flask import Flask, render_template
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#from matplotlib.dates import DateFormatter
from pvlib import solarposition, tracking
from datetime import datetime, timedelta
import pytz
import matplotlib.dates as mdates
import os

app = Flask(__name__)

@app.route("/")

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
    times = pd.date_range(start_time, end_time, freq='h', tz=local_tz)
    
    # Calcular la posición solar
    latitud = 25.65
    longitud = -100.32
    solpos = solarposition.get_solarposition(times, latitud, longitud)

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
    curve, = ax.plot(position.index, position.values, label='Curva de Seguimiento', color='black')
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(position.min() - 5, position.max() + 5)

     # Encontrar y marcar los puntos Mínimo y Máximo
    best_min = position.idxmin()
    best_max = position.idxmax()
    ax.plot(best_min, position[best_min], color='#08968F', marker='o', label='Mejor Hora Mañana')
    ax.plot(best_max, position[best_max], color='#0652EA', marker='o', label='Mejor Hora Tarde')
    

    # Estilos y Protección del Texto de Abajo
    plt.title(f'Irradiación Solar ({current_datetime.strftime("%Y-%m-%d")})', fontsize=10)
    
    # Mostrar solo algunas etiquetas de hora para que no se amontonen
    plt.xticks(rotation=45, fontsize=8)
    x_labels = [dt.strftime('%I:%M %p') if i % 3 == 0 else '' for i, dt in enumerate(position.index)]
    ax.set_xticks(position.index)
    ax.set_xticklabels(x_labels)
    ax.legend(fontsize=8)

    # Función de actualización para la animación cuadro por cuadro
    def update(frame):
        # Va pintando la curva conforme avanza el tiempo
        curve.set_data(position.index[:frame+1], position.values[:frame+1])
        
        # Muestra la fecha y la hora correspondiente a ese cuadro en el título
        timestamp_actual = position.index[frame].strftime('%I:%M %p')
        ax.set_title(f'Irradiación Solar ({current_datetime.strftime("%Y-%m-%d")} {timestamp_actual})', fontsize=10)
        return curve,

    # Crear la animación secuencial
    ani = FuncAnimation(fig, update, frames=len(times), blit=False)
    
    fig.tight_layout()

    # Guardar la Imagen como PNG (Más ligero que un GIF)
    os.makedirs('static', exist_ok=True)
    graph_filename = 'static/panelsolar.png'
    ani.save(graph_filename, writer="pillow", fps=5)
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

