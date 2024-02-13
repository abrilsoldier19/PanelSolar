from flask import Flask, render_template, request
import subprocess


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('output.html')

@app.route('/compilar', methods=['POST'])
def compilar():
    # Lógica para compilar el software
    # Puedes utilizar el módulo subprocess para ejecutar el archivo Python
    
    # Ejemplo:
    output = subprocess.check_output(['python', 'D:/ITS Sistemas/8 Semestre/Ingeniería De Software/Unidad 3 Desarrollo/proyecto pagina web/software simulador completo/Software_Final.py'])


    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to a different port if needed


