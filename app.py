from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Lista de estudiantes actualizada
estudiantes = [
    {'id': '1', 'nombre': 'Antonio', 'email': '1aaaaa@alumnos.aa'},
    {'id': '2', 'nombre': 'Brigitte', 'email': '2aaaaa@alumnos.aa'},
    {'id': '3', 'nombre': 'Carlos', 'email': '3aaaaa@alumnos.aa'},
    {'id': '4', 'nombre': 'Daniela', 'email': '4aaaaa@alumnos.aa'},
    {'id': '5', 'nombre': 'Eduardo', 'email': '5aaaaa@alumnos.aa'},
    {'id': '6', 'nombre': 'Fernanda', 'email': '6aaaaa@alumnos.aa'},
    {'id': '7', 'nombre': 'Gabriel', 'email': '7aaaaa@alumnos.aa'},
    {'id': '8', 'nombre': 'Hilda', 'email': '8aaaaa@alumnos.aa'},
    {'id': '9', 'nombre': 'Ignacio', 'email': '9aaaaa@alumnos.aa'},
    {'id': '10', 'nombre': 'Julia', 'email': '10aaaaa@alumnos.aa'}
]

# Lista de profesores actualizada
profesores = [
    {'id': '1', 'nombre': 'Prof. Antonio', 'email': '1bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '2', 'nombre': 'Prof. Brigitte', 'email': '2bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '3', 'nombre': 'Prof. Carlos', 'email': '3bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '4', 'nombre': 'Prof. Daniela', 'email': '4bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '5', 'nombre': 'Prof. Eduardo', 'email': '5bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '6', 'nombre': 'Prof. Fernanda', 'email': '6bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '7', 'nombre': 'Prof. Gabriel', 'email': '7bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '8', 'nombre': 'Prof. Hilda', 'email': '8bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '9', 'nombre': 'Prof. Ignacio', 'email': '9bbbbb@profesores.aa', 'disponibilidad': []},
    {'id': '10', 'nombre': 'Prof. Julia', 'email': '10bbbbb@profesores.aa', 'disponibilidad': []}
]

consultas = []

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        if role == 'student':
            student_id = request.form['student_id']
            student = next((s for s in estudiantes if s['id'] == student_id), None)
            if student:
                session['user'] = student
                session['role'] = 'student'
                return redirect(url_for('index'))
        elif role == 'teacher':
            teacher_id = request.form['teacher_id']
            teacher = next((t for t in profesores if t['id'] == teacher_id), None)
            if teacher:
                session['user'] = teacher
                session['role'] = 'teacher'
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/index')
def index():
    if 'role' not in session:
        return redirect(url_for('login'))
    role = session['role']
    if role == 'student':
        estudiante_id = session['user']['id']
        consulta_pendiente = next((c for c in consultas if c['estudiante_id'] == estudiante_id and c['estado'] in ['pendiente', 'confirmada', 'rechazada']), None)
        return render_template('estudiante.html', consulta_pendiente=consulta_pendiente)
    elif role == 'teacher':
        return render_template('maestro.html')

@app.route('/horarios')
def horarios():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    return render_template('horarios.html', profesores=profesores)

@app.route('/solicitar', methods=['POST'])
def solicitar():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    estudiante_id = session['user']['id']
    profesor_id = request.form['profesor_id']
    fecha = request.form['fecha']
    hora = request.form['hora']
    # Verificar si la hora está disponible
    profesor = next((p for p in profesores if p['id'] == profesor_id), None)
    if not profesor:
        return "Profesor no encontrado."
    disponibilidad = next((d for d in profesor['disponibilidad'] if d['dia'] == fecha and d['hora_inicio'] <= hora <= d['hora_fin']), None)
    if not disponibilidad:
        return "Hora no disponible, por favor elige otra."
    # Verificar si la hora ya está ocupada
    for consulta in consultas:
        if consulta['profesor_id'] == profesor_id and consulta['fecha'] == fecha and consulta['hora'] == hora:
            return "Hora no disponible, por favor elige otra."
    consulta = {
        'id': len(consultas) + 1,
        'estudiante_id': estudiante_id,
        'profesor_id': profesor_id,
        'fecha': fecha,
        'hora': hora,
        'estado': 'pendiente'
    }
    consultas.append(consulta)
    return redirect(url_for('index'))

@app.route('/gestionar')
def gestionar():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('solicitudes.html', consultas=consultas)

@app.route('/actualizar', methods=['POST'])
def actualizar():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    consulta_id = request.form['consulta_id']
    estado = request.form['estado']
    for consulta in consultas:
        if consulta['id'] == int(consulta_id):
            consulta['estado'] = estado
            break
    return redirect(url_for('gestionar'))

@app.route('/disponibilidad', methods=['GET', 'POST'])
def disponibilidad():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    if request.method == 'POST':
        profesor_id = session['user']['id']
        dia = request.form['dia']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        disponibilidad = {'dia': dia, 'hora_inicio': hora_inicio, 'hora_fin': hora_fin}
        for profesor in profesores:
            if profesor['id'] == profesor_id:
                profesor['disponibilidad'].append(disponibilidad)
                break
        return redirect(url_for('index'))
    return render_template('disponibilidad.html')

if __name__ == '__main__':
    app.run(debug=True)