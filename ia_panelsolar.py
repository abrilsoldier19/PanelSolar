import pandas as pd
import matplotlib.pyplot as plt

# Crear un DataFrame de ejemplo con datos de radiación solar a lo largo del día
data = {'Hora': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
        'RadiacionSolar': [100, 200, 400, 600, 800, 1000, 800, 600, 400, 200]}

df = pd.DataFrame(data)

# Visualizar los datos
plt.plot(df['Hora'], df['RadiacionSolar'], marker='o')
plt.xlabel('Hora del día')
plt.ylabel('Radiación Solar')
plt.title('Radiación Solar a lo largo del día')
plt.grid(True)
plt.show()

# Encontrar la hora con la radiación solar máxima
mejor_hora = df.loc[df['RadiacionSolar'].idxmax(), 'Hora']

print(f"La mejor hora para conectar el panel solar es a las {mejor_hora}:00")
