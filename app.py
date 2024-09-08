from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from models import db, Professor

app = Flask(__name__)
#app = Flask(__name__, template_folder='.')

app.secret_key = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

with app.app_context():
    db.create_all()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aluno', methods=['GET', 'POST'])
def aluno():
    if request.method == 'POST':
        codigo = request.form['codigo']
        conn = get_db_connection()
        aluno = conn.execute('SELECT * FROM alunos WHERE codigo = ?', (codigo,)).fetchone()
        aluno_retiradas = conn.execute('SELECT * FROM retiradas WHERE codigo = ?', (codigo,)).fetchone()
        aluno_adicoes = conn.execute('SELECT * FROM adicoes WHERE codigo = ?', (codigo,)).fetchone()

        conn.close()
        if aluno:
            return render_template('aluno.html', aluno=aluno, aluno_retiradas=aluno_retiradas, aluno_adicoes=aluno_adicoes)
        else:
            flash('Código não encontrado', 'error')
            return redirect(url_for('aluno'))
    return render_template('aluno.html')

@app.route('/professor_login', methods=['GET', 'POST'])
def professor_login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        conn = get_db_connection()
        professor = conn.execute('SELECT * FROM professores WHERE login = ? AND senha = ?', (login, senha)).fetchone()
        conn.close()
        if professor:
            session['professor_id'] = professor['id']
            return redirect(url_for('professor_dashboard'))
        else:
            flash('Login ou senha incorretos', 'error')
            return redirect(url_for('professor_login'))
    return render_template('professor_login.html')

@app.route('/professor_dashboard', methods=['GET', 'POST'])
def professor_dashboard():
    if 'professor_id' not in session:
        return redirect(url_for('professor_login'))

    conn = get_db_connection()

    # Obter o nome do professor baseado no ID da sessão
    professor = conn.execute('SELECT nome FROM professores WHERE id = ?', (session['professor_id'],)).fetchone()
    professor_nome = professor['nome'] if professor else None

    turmas = conn.execute('SELECT DISTINCT turma FROM alunos').fetchall()
    alunos = []
    alunos_a = []
    alunos_r = []
    alunos_completos = []

    if request.method == 'POST':
        turma = request.form.get('turma')
        if professor_nome:
            # Selecionar alunos e a coluna correspondente ao nome do professor
            alunos = conn.execute(f'SELECT id, nome, "{professor_nome}" FROM alunos WHERE turma = ?', (turma,)).fetchall()
            alunos_a = conn.execute(f'SELECT id, nome, "{professor_nome}" FROM adicoes WHERE turma = ?', (turma,)).fetchall()
            alunos_r = conn.execute(f'SELECT id, nome, "{professor_nome}" FROM retiradas WHERE turma = ?', (turma,)).fetchall()
            alunos_completos = [(aluno, aluno_a, aluno_r) for aluno, aluno_a, aluno_r in zip(alunos, alunos_a, alunos_r)]

    conn.close()
    return render_template('professor_dashboard.html', turmas=turmas, alunos_completos=alunos_completos, alunos=alunos, professor_nome=professor_nome, alunos_a=alunos_a,alunos_r=alunos_r)

@app.route('/admin_saldos', methods=['GET', 'POST'])
def admin_saldos():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    turmas = conn.execute('SELECT DISTINCT turma FROM alunos').fetchall()
    saldos = []

    if request.method == 'POST':
        turma = request.form.get('turma')
        saldos = conn.execute('''
            SELECT nome, saldo, "Amanda", "Daniella Amaral Pinto", "Elizete", "Fátima",
                              "Heryco Lemos Queirós", "João Pedro Mendes de Siqueira", "Luciano", "Maria Aparecida", "Nayara Cristina de Jesus Ferreira",
                              "Pedro Henrique Pereira Dos Santos", "Rodrigo Prado", "Stael Batista Schenkel de Morais", "Tiago", "Suely"
            FROM alunos
            WHERE turma = ?
        ''', (turma,)).fetchall()

    conn.close()
    return render_template('admin_saldos.html', turmas=turmas, saldos=saldos)

@app.route('/update_americanos', methods=['POST'])
def update_americanos():
    if 'professor_id' not in session:
        return redirect(url_for('professor_login'))
    
    conn = get_db_connection()
    tipo = request.form['tipo']
    quantidade = int(request.form['quantidade'])
    alunos_selecionados = request.form.getlist('alunos')

    professor = conn.execute('SELECT nome FROM professores WHERE id = ?', (session['professor_id'],)).fetchone()
    professor_nome = professor['nome'] if professor else None

    if not professor_nome:
        return redirect(url_for('professor_dashboard'))
    
    for aluno_id in alunos_selecionados:
        aluno = conn.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,)).fetchone()
        adicionar = conn.execute('SELECT * FROM adicoes WHERE id = ?', (aluno_id,)).fetchone()
        retirar = conn.execute('SELECT * FROM retiradas WHERE id = ?', (aluno_id,)).fetchone()

        if aluno:
            novo_saldo = aluno['saldo'] + quantidade if tipo == 'add' else aluno['saldo'] - quantidade
            nova_quantidade_professor = aluno[professor_nome] + quantidade if tipo == 'add' else aluno[professor_nome] - quantidade

            novo_saldo_add_ou_ret = adicionar['saldo'] + quantidade if tipo == 'add' else retirar['saldo'] + quantidade
            nova_quantidade_add_ou_ret = adicionar[professor_nome] + quantidade if tipo == 'add' else retirar[professor_nome] + quantidade

            conn.execute('UPDATE alunos SET saldo = ? WHERE id = ?', (novo_saldo, aluno_id))
            conn.execute(f'UPDATE alunos SET saldo = ?, "{professor_nome}" = ? WHERE id = ?', 
                         (novo_saldo, nova_quantidade_professor, aluno_id))
            conn.execute('INSERT INTO transacoes (aluno_id, professor_id, tipo, quantidade) VALUES (?, ?, ?, ?)',
                         (aluno_id, session['professor_id'], tipo, quantidade))
            
            # Inserir na tabela 'adicoes' ou 'retiradas' conforme o tipo de transação
            if tipo == 'add':
                novo_saldo_add_ou_ret = adicionar['saldo'] + quantidade
                conn.execute('UPDATE adicoes SET saldo = ? WHERE id = ?', (novo_saldo_add_ou_ret, aluno_id))
                conn.execute(f'UPDATE adicoes SET saldo = ?, "{professor_nome}" = ? WHERE id = ?', 
                         (novo_saldo_add_ou_ret, nova_quantidade_add_ou_ret, aluno_id))
            else:
                novo_saldo_add_ou_ret = retirar['saldo'] + quantidade
                conn.execute('UPDATE retiradas SET saldo = ? WHERE id = ?', (novo_saldo_add_ou_ret, aluno_id))
                conn.execute(f'UPDATE retiradas SET saldo = ?, "{professor_nome}" = ? WHERE id = ?', 
                         (novo_saldo_add_ou_ret, nova_quantidade_add_ou_ret, aluno_id))
    
    conn.commit()
    conn.close()
    return redirect(url_for('professor_dashboard'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        if login == 'adminheryco' and senha == 'KKKofoda':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login ou senha incorretos', 'error')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin_alunos', methods=['GET', 'POST'])
def admin_alunos():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        nome = request.form['nome']
        turma = request.form['turma']
        codigo = request.form['codigo']
        
        # Adiciona o novo aluno na tabela alunos
        conn.execute('INSERT INTO alunos (nome, turma, codigo, saldo) VALUES (?, ?, ?, ?)', (nome, turma, codigo, 0))
        
        # Obtém o ID do aluno recém-adicionado
        aluno_id = conn.execute('SELECT id FROM alunos WHERE nome = ? AND turma = ? AND codigo = ?', (nome, turma, codigo)).fetchone()['id']
        
        # Adiciona o novo aluno nas tabelas adicoes e retiradas
        conn.execute('INSERT INTO adicoes (id, nome, turma, codigo, saldo, "Heryco Lemos Queirós", "Stael Batista Schenkel de Morais", "Nayara Cristina de Jesus Ferreira", "João Pedro Mendes de Siqueira", "Rodrigo Prado", "Daniella Amaral Pinto", "Pedro Henrique Pereira Dos Santos", Tiago, "Maria Aparecida", Elizete, Luciano, Amanda, Fátima, Suely) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (aluno_id, nome, turma, codigo, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        conn.execute('INSERT INTO retiradas (id, nome, turma, codigo, saldo, "Heryco Lemos Queirós", "Stael Batista Schenkel de Morais", "Nayara Cristina de Jesus Ferreira", "João Pedro Mendes de Siqueira", "Rodrigo Prado", "Daniella Amaral Pinto", "Pedro Henrique Pereira Dos Santos", Tiago, "Maria Aparecida", Elizete, Luciano, Amanda, Fátima, Suely) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (aluno_id, nome, turma, codigo, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        
        conn.commit()
    
    # Obtém a turma selecionada (ou todas se não houver seleção)
    turma_filtro = request.args.get('turma', default=None)
    if turma_filtro:
        alunos = conn.execute('SELECT * FROM alunos WHERE turma = ?', (turma_filtro,)).fetchall()
    else:
        alunos = conn.execute('SELECT * FROM alunos').fetchall()
    
    # Obtém a lista de turmas para o filtro
    turmas = conn.execute('SELECT DISTINCT turma FROM alunos').fetchall()
    
    conn.close()
    
    return render_template('admin_alunos.html', alunos=alunos, turmas=turmas)




@app.route('/delete_aluno/<int:id>', methods=['GET'])
def delete_aluno(id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    
    # Excluir o aluno das tabelas alunos, adicoes e retiradas
    conn.execute('DELETE FROM alunos WHERE id = ?', (id,))
    conn.execute('DELETE FROM adicoes WHERE id = ?', (id,))
    conn.execute('DELETE FROM retiradas WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_alunos'))




@app.route('/admin_professores', methods=['GET', 'POST'])
def admin_professores():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form['nome']
        login = request.form['login']
        senha = request.form['senha']
        conn.execute('INSERT INTO professores (nome, login, senha) VALUES (?, ?, ?)', (nome, login, senha))
        conn.execute(f'''
            ALTER TABLE alunos
            ADD COLUMN "{nome}" INTEGER NOT NULL DEFAULT 0;
        ''')
        conn.commit()
    professores = conn.execute('SELECT * FROM professores').fetchall()
    conn.close()
    return render_template('admin_professores.html', professores=professores)

@app.route('/admin_transacoes', methods=['GET', 'POST'])
def admin_transacoes():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()

    # Obtém todos os professores e turmas para os filtros
    professores = conn.execute('SELECT id, nome FROM professores').fetchall()
    turmas = conn.execute('SELECT DISTINCT turma FROM alunos').fetchall()

    transacoes = []
    professor_selecionado = None
    turma_selecionada = None

    if request.method == 'POST':
        professor_id = request.form.get('professor')
        turma = request.form.get('turma')

        # Filtra os registros de acordo com o professor e a turma selecionados
        query = '''
            SELECT t.data, a.nome as aluno_nome, p.nome as professor_nome, t.tipo, t.quantidade
            FROM transacoes t
            JOIN alunos a ON t.aluno_id = a.id
            JOIN professores p ON t.professor_id = p.id
            WHERE 1=1
        '''
        params = []

        if professor_id and professor_id != 'all':
            query += ' AND p.id = ?'
            params.append(professor_id)
            professor_selecionado = conn.execute('SELECT nome FROM professores WHERE id = ?', (professor_id,)).fetchone()

        if turma:
            query += ' AND a.turma = ?'
            params.append(turma)
            turma_selecionada = turma

        query += ' ORDER BY t.data DESC'

        transacoes = conn.execute(query, params).fetchall()

    conn.close()

    return render_template('admin_transacoes.html', transacoes=transacoes, professores=professores, turmas=turmas, professor_selecionado=professor_selecionado, turma_selecionada=turma_selecionada)

  

@app.route('/professor_transacoes', methods=['GET', 'POST'])
def professor_transacoes():
    if 'professor_id' not in session:
        return redirect(url_for('professor_login'))

    conn = get_db_connection()

    # Obtém o nome do professor baseado no ID da sessão
    professor = conn.execute('SELECT nome FROM professores WHERE id = ?', (session['professor_id'],)).fetchone()
    professor_nome = professor['nome'] if professor else None

    turmas = conn.execute('SELECT DISTINCT turma FROM alunos').fetchall()
    transacoes = []
    turma_selecionada = None

    if request.method == 'POST':
        turma = request.form.get('turma')

        # Filtra os registros de acordo com o professor e a turma selecionados
        query = '''
            SELECT t.data, a.nome as aluno_nome, t.tipo, t.quantidade
            FROM transacoes t
            JOIN alunos a ON t.aluno_id = a.id
            WHERE t.professor_id = ? 
        '''
        params = [session['professor_id']]

        if turma:
            query += ' AND a.turma = ?'
            params.append(turma)
            turma_selecionada = turma

        query += ' ORDER BY t.data DESC'

        transacoes = conn.execute(query, params).fetchall()

    conn.close()

    return render_template('professor_transacoes.html', transacoes=transacoes, turmas=turmas, turma_selecionada=turma_selecionada)
 

@app.route('/edit_professor/<int:professor_id>', methods=['GET', 'POST'])
def edit_professor(professor_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    professor = conn.execute('SELECT * FROM professores WHERE id = ?', (professor_id,)).fetchone()
    
    if request.method == 'POST':
        nome = request.form['nome']
        login = request.form['login']
        senha = request.form['senha']
        conn.execute('UPDATE professores SET nome = ?, login = ?, senha = ? WHERE id = ?', 
                     (nome, login, senha, professor_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_professores'))
    
    conn.close()
    return render_template('edit_professor.html', professor=professor)

@app.route('/delete_professor', methods=['POST'])
def delete_professor():
    professor_id = request.form['professor_id']
    conn = get_db_connection()
    conn.execute('DELETE FROM professores WHERE id = ?', (professor_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_professores'))

import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Tenta se conectar a um endereço externo para obter o IP local
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

if __name__ == '__main__':
    local_ip = get_local_ip()
    app.run(host=local_ip, port=5000, debug=True)
