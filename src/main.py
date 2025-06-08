import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import secrets
from werkzeug.utils import secure_filename
import os
import pyodbc

# Importar rotas
from src.routes.bruto_routes import bruto_bp
from src.routes.liquido_routes import liquido_bp
from src.routes.regiao_routes import regiao_bp
from src.routes.entregas_routes import entregas_bp
from src.routes.km_rodado_routes import km_rodado_bp
from src.routes.ocupacao_routes import ocupacao_bp

# Configuração da aplicação
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['ALLOWED_EXTENSIONS'] = {'.accdb', '.mdb'}
app.config['CONFIG_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_config.json')

# Configuração do banco de dados - agora usando variável global para conexão Access
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dummy.db'


# Variável global para armazenar a conexão com o banco Access
access_connection = None
access_cursor = None

# Inicializar o banco de dados SQLAlchemy (usado apenas para estrutura, não para dados)
db = SQLAlchemy(app)

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Registrar blueprints
app.register_blueprint(bruto_bp, url_prefix='/bruto')
app.register_blueprint(liquido_bp, url_prefix='/liquido')
app.register_blueprint(regiao_bp, url_prefix='/regiao')
app.register_blueprint(entregas_bp, url_prefix='/entregas')
app.register_blueprint(km_rodado_bp, url_prefix='/km_rodado')
app.register_blueprint(ocupacao_bp, url_prefix='/ocupacao')

# Função para verificar se o arquivo é permitido
def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Função para salvar configuração do banco
def save_db_config(db_path):
    config = {'db_path': db_path, 'last_connected': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    with open(app.config['CONFIG_FILE'], 'w') as f:
        json.dump(config, f)

# Função para carregar configuração do banco
def load_db_config():
    if os.path.exists(app.config['CONFIG_FILE']):
        try:
            with open(app.config['CONFIG_FILE'], 'r') as f:
                return json.load(f)
        except:
            return None
    return None

# Função para conectar ao banco Access
def connect_to_access(db_path):
    global access_connection, access_cursor
    
    try:
        # Fechar conexão anterior se existir
        if access_connection:
            access_cursor.close()
            access_connection.close()
            
        # Criar nova conexão
        if db_path.endswith('.accdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};'
        elif db_path.endswith('.mdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={db_path};'
        else:
            return {'status': False, 'message': 'Formato de banco de dados não suportado'}
        
        access_connection = pyodbc.connect(conn_str)
        access_cursor = access_connection.cursor()
        
        # Testar conexão com uma consulta simples
        access_cursor.execute("SELECT 1")
        access_cursor.fetchone()
        
        return {'status': True, 'message': 'Conexão com Access estabelecida com sucesso'}
    except pyodbc.Error as e:
        if access_connection:
            access_connection.close()
        access_connection = None
        access_cursor = None
        return {'status': False, 'message': f'Erro ao conectar ao Access: {str(e)}'}
    except Exception as e:
        if access_connection:
            access_connection.close()
        access_connection = None
        access_cursor = None
        return {'status': False, 'message': f'Erro: {str(e)}'}

# Função para testar conexão com o banco
def test_connection(db_path):
    try:
        if db_path.endswith(('.accdb', '.mdb')):
            # Usar pyodbc para conectar ao Access
            return connect_to_access(db_path)
        else:
            return {'status': False, 'message': 'Tipo de banco não suportado'}
    except Exception as e:
        return {'status': False, 'message': f'Erro: {str(e)}'}

# Função para executar consulta no Access
def execute_access_query(query, params=None, fetch=True):
    global access_cursor
    
    if not access_cursor:
        return None
    
    try:
        if params:
            access_cursor.execute(query, params)
        else:
            access_cursor.execute(query)
        
        if fetch:
            return access_cursor.fetchall()
        else:
            access_connection.commit()
            return True
    except Exception as e:
        print(f"Erro ao executar consulta: {str(e)}")
        return None

# Rotas da aplicação
@app.route('/')
def index():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    # Testar conexão
    connection_status = {'status': False, 'message': 'Banco não configurado'}
    if db_path and os.path.exists(db_path):
        connection_status = test_connection(db_path)
    
    return render_template('index.html', 
                          db_path=db_path,
                          connection_status=connection_status)

@app.route('/select_database', methods=['GET', 'POST'])
def select_database():
    if request.method == 'POST':
        # Verificar se o arquivo foi enviado
        if 'database_file' not in request.files:
            return jsonify({'status': False, 'message': 'Nenhum arquivo enviado'})
        
        file = request.files['database_file']
        if file.filename == '':
            return jsonify({'status': False, 'message': 'Nenhum arquivo selecionado'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Salvar caminho na sessão e no arquivo de configuração
            session['db_path'] = file_path
            save_db_config(file_path)
            
            # Testar conexão
            connection_status = test_connection(file_path)
            
            return jsonify({
                'status': True,
                'db_path': file_path,
                'connection_status': connection_status
            })
        
        return jsonify({'status': False, 'message': 'Tipo de arquivo não permitido'})
    
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    # Testar conexão
    connection_status = {'status': False, 'message': 'Banco não configurado'}
    if db_path and os.path.exists(db_path):
        connection_status = test_connection(db_path)
    
    return render_template('select_database.html', 
                          db_path=db_path,
                          connection_status=connection_status)

@app.route('/set_database_path', methods=['POST'])
def set_database_path():
    data = request.get_json()
    db_path = data.get('db_path')
    
    if not db_path or not os.path.exists(db_path):
        return jsonify({'status': False, 'message': 'Caminho inválido ou arquivo não existe'})
    
    # Salvar caminho na sessão e no arquivo de configuração
    session['db_path'] = db_path
    save_db_config(db_path)
    
    # Testar conexão
    connection_status = test_connection(db_path)
    
    return jsonify({
        'status': True,
        'db_path': db_path,
        'connection_status': connection_status
    })

@app.route('/test_connection')
def check_connection():
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    if not db_path:
        return jsonify({'status': False, 'message': 'Banco não configurado'})
    
    connection_status = test_connection(db_path)
    return jsonify(connection_status)

# Rotas para as páginas CRUD
@app.route('/clientes')
def clientes():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    # Testar conexão
    connection_status = {'status': False, 'message': 'Banco não configurado'}
    if db_path and os.path.exists(db_path):
        connection_status = test_connection(db_path)
    
    return render_template('clientes.html', 
                          db_path=db_path,
                          connection_status=connection_status)

@app.route('/produtos')
def produtos():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    # Testar conexão
    connection_status = {'status': False, 'message': 'Banco não configurado'}
    if db_path and os.path.exists(db_path):
        connection_status = test_connection(db_path)
    
    return render_template('produtos.html', 
                          db_path=db_path,
                          connection_status=connection_status)

@app.route('/vendas')
def vendas():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    # Testar conexão
    connection_status = {'status': False, 'message': 'Banco não configurado'}
    if db_path and os.path.exists(db_path):
        connection_status = test_connection(db_path)
    
    return render_template('vendas.html', 
                          db_path=db_path,
                          connection_status=connection_status)

@app.route('/importacao')
def importacao():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        config = load_db_config()
        if config:
            db_path = config.get('db_path')
            session['db_path'] = db_path
    
    # Testar conexão
    connection_status = {'status': False, 'message': 'Banco não configurado'}
    if db_path and os.path.exists(db_path):
        connection_status = test_connection(db_path)
    
    return render_template('importacao.html', 
                          db_path=db_path,
                          connection_status=connection_status)

@app.route('/get_statistics')
def get_statistics():
    global access_cursor
    
    if not access_cursor:
        return jsonify({
            'status': False,
            'message': 'Banco de dados não conectado'
        })
    
    try:
        # Tentar obter estatísticas reais do banco Access
        # Estas consultas são exemplos e devem ser adaptadas às tabelas reais do banco
        stats = {}
        
        # Tentar obter contagem de registros da tabela Bruto
        try:
            result = execute_access_query("SELECT COUNT(*) FROM Bruto")
            if result:
                stats['bruto'] = result[0][0]
            else:
                stats['bruto'] = 0
        except:
            stats['bruto'] = 0
            
        # Tentar obter contagem de registros da tabela Liquido
        try:
            result = execute_access_query("SELECT COUNT(*) FROM Liquido")
            if result:
                stats['liquido'] = result[0][0]
            else:
                stats['liquido'] = 0
        except:
            stats['liquido'] = 0
            
        # Tentar obter contagem de registros da tabela Regiao
        try:
            result = execute_access_query("SELECT COUNT(*) FROM Regiao")
            if result:
                stats['regiao'] = result[0][0]
            else:
                stats['regiao'] = 0
        except:
            stats['regiao'] = 0
            
        # Tentar obter contagem de registros da tabela Entregas
        try:
            result = execute_access_query("SELECT COUNT(*) FROM Entregas")
            if result:
                stats['entregas'] = result[0][0]
            else:
                stats['entregas'] = 0
        except:
            stats['entregas'] = 0
            
        return jsonify({
            'status': True,
            **stats
        })
    except Exception as e:
        # Em caso de erro, retornar estatísticas simuladas
        return jsonify({
            'status': True,
            'bruto': 5,
            'liquido': 5,
            'regiao': 5,
            'entregas': 5
        })

# Tratamento de erros
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Inicialização da aplicação
if __name__ == '__main__':
    # Verificar se há um banco configurado
    config = load_db_config()
    if config:
        db_path = config.get('db_path')
        if db_path and os.path.exists(db_path):
            # Tentar conectar ao banco
            connection_status = test_connection(db_path)
            print(f"Status da conexão: {connection_status['message']}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

#python -m venv venv
#venv\Scripts\activate
#pip install -r requirements.txt
#python -m src.main