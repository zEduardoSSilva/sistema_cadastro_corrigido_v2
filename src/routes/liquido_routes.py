from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
import pyodbc
import os
import json
from datetime import datetime

liquido_bp = Blueprint('liquido_bp', __name__)

def get_connection():
    db_path = session.get('db_path')
    if not db_path:
        return None
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
    )
    return pyodbc.connect(conn_str)

@liquido_bp.route('/')
def index():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        flash('Por favor, configure o banco de dados primeiro.', 'warning')
        return redirect(url_for('select_database'))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT TIPO, ESTADO, CD, DATA, [R$], TONS, [R$ / TON], FATURAMENTO, FAT_DEV_C_MOT, FAT_DEV_S_MOT FROM Faturamento_Liquido')
        rows = cursor.fetchall()
        colunas = [column[0] for column in cursor.description]

        #Ele vai gerar um id incremental fictício para cada item. 
        #Isso só serve para exibir e não deve ser usado para editar ou excluir de verdade, pois não há ligação com o banco.
        dados = [dict({'id': i + 1}, **dict(zip(colunas, row))) for i, row in enumerate(rows)]

        # Mapeia os campos para o que o template espera
        dados_mapeados = []
        for i, item in enumerate(dados):
            dados_mapeados.append({
                'id': i + 1,  # usa índice fictício visível
                'data': item.get('DATA') or '',
                'regiao': item.get('ESTADO') or '',
                'valor': item.get('FATURAMENTO') or 0,
                'observacoes': item.get('TIPO') or ''
            })

        return render_template('liquido/index.html', dados=dados_mapeados, connection_status={'status': True, 'message': 'Conectado'})
    
    except Exception as e:
        flash(f"Erro ao buscar dados: {str(e)}", "danger")
        return render_template('liquido/index.html', dados=[], connection_status={'status': False, 'message': 'Erro na leitura'})

@liquido_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        # Processar dados do formulário
        dados = request.form.to_dict()
        
        # Adicionar ID e data de criação
        dados['id'] = len(dados_liquido) + 1
        dados['data_criacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Em produção, salvaríamos no banco Access
        # Para desenvolvimento, adicionamos à lista simulada
        dados_liquido.append(dados)
        
        flash('Registro adicionado com sucesso!', 'success')
        return redirect(url_for('liquido_bp.index'))
    
    return render_template('liquido/form.html',
                          registro={},
                          connection_status={'status': True, 'message': 'Conectado (simulado)'})

@liquido_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    # Buscar registro pelo ID
    registro = next((item for item in dados_liquido if item['id'] == id), None)
    
    if not registro:
        flash('Registro não encontrado.', 'danger')
        return redirect(url_for('liquido_bp.index'))
    
    if request.method == 'POST':
        # Atualizar dados do registro
        dados = request.form.to_dict()
        dados['id'] = id
        
        # Em produção, atualizaríamos no banco Access
        # Para desenvolvimento, atualizamos na lista simulada
        for i, item in enumerate(dados_liquido):
            if item['id'] == id:
                dados_liquido[i] = dados
                break
        
        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('liquido_bp.index'))
    
    return render_template('liquido/form.html',
                          registro=registro,
                          connection_status={'status': True, 'message': 'Conectado (simulado)'})

@liquido_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    # Em produção, excluiríamos do banco Access
    # Para desenvolvimento, removemos da lista simulada
    global dados_liquido
    dados_liquido = [item for item in dados_liquido if item['id'] != id]
    
    flash('Registro excluído com sucesso!', 'success')
    return redirect(url_for('liquido_bp.index'))
