
from pvlib import solarposition, tracking
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates


# Obtener la zona horaria local automáticamente
local_tz = pytz.timezone(pytz.country_timezones['MX'][0])  # MX para México

lat, lon = 40, -80

# Obtener la fecha y hora actual
current_datetime = datetime.now(local_tz)
current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Calcular el inicio y el final del período de interés (15:00 horas del día actual hasta 15:00 horas del siguiente día)
start_time = current_datetime.replace(hour=12, minute=0, second=0, microsecond=0)
if current_datetime.hour < 12:
    start_time -= timedelta(days=1)  # Retroceder un día si la hora actual es antes de las 15:00 horas
end_time = start_time + timedelta(days=1)

# Generar el índice de tiempo desde las 15:00 horas del día actual hasta las 15:00 horas del siguiente día, de 3 en 3 horas
times = pd.date_range(start_time, end_time, freq='3H', tz=local_tz)



# Calcular la posición solar
solpos = solarposition.get_solarposition(times, lat, lon)

# Crear la figura y el eje
fig, ax = plt.subplots(figsize=(10, 6))

# Inicialización del gráfico
truetracking_angles = tracking.singleaxis(
    apparent_zenith=solpos['apparent_zenith'],
    apparent_azimuth=solpos['azimuth'],
    axis_tilt=0,
    axis_azimuth=180,
    max_angle=90,
    backtrack=False,  # for true-tracking
    gcr=0.5)  # irrelevant for true-tracking

# Extraer las posiciones de seguimiento
truetracking_position = truetracking_angles['tracker_theta'].fillna(0)

# Graficar la curva de seguimiento
curve, = ax.plot(truetracking_position.index, truetracking_position.values, label='Curva de Seguimiento')
ax.set_ylim(truetracking_position.min() - 5, truetracking_position.max() + 5)

# Marcar las mejores horas en el gráfico
best_hours_min = truetracking_position.idxmin()
best_hours_max = truetracking_position.idxmax()
min_point, = ax.plot(best_hours_min, truetracking_position[best_hours_min], 'go', label=f'Mejor Hora (Mínimo): {best_hours_min}')
max_point, = ax.plot(best_hours_max, truetracking_position[best_hours_max], 'ro', label=f'Mejor Hora (Máximo): {best_hours_max}')

# Mostrar leyenda
ax.legend()

# Función de actualización
# Función de actualización
def update(frame):
    if frame < len(times):
        truetracking_angles = tracking.singleaxis(
            apparent_zenith=solpos['apparent_zenith'],
            apparent_azimuth=solpos['azimuth'],
            axis_tilt=0,
            axis_azimuth=180,
            max_angle=90,
            backtrack=False,  # for true-tracking
            gcr=0.5)  # irrelevant for true-tracking

        # Actualizar datos
        truetracking_position = truetracking_angles['tracker_theta'].fillna(0)
        plt.title(label=f'Mejoras para conectar panel solar ({current_datetime_str})')
        curve.set_data(truetracking_position.index[:frame], truetracking_position.values[:frame])

        # Actualizar mejor hora (mínimo)
        best_hours_min = truetracking_position.idxmin()
        min_point.set_data([best_hours_min], [truetracking_position[best_hours_min]])

        # Actualizar mejor hora (máximo)
        best_hours_max = truetracking_position.idxmax()
        max_point.set_data([best_hours_max], [truetracking_position[best_hours_max]])

        # Actualizar etiquetas del eje x
        ax.set_xticks(truetracking_position.index)
        x_labels = [dt.strftime('%I:%M %p') for dt in truetracking_position.index]
        ax.set_xticklabels(x_labels)


        # Actualizar límites del eje x
        ax.set_xlim(start_time, end_time)

    return curve, min_point, max_point


# Crear la animación
ani = FuncAnimation(fig, update, frames=len(times), blit=True, interval=300)

plt.xticks(rotation=360)

plt.show()
