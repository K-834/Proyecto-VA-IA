from flask import Flask, render_template
import backendFace as faceVAIA


app = Flask(__name__)

@app.route('/VA-IA/')
def index():
    return render_template('index.html')

@app.route('/sections/live.html', methods=['POST'])
def ejecutar_proyecto():
    faceVAIA.run3(0)                #verificación de rostros
    return "Proyecto ejecutado"

if __name__ == '__main__':
    app.run(debug=True)
