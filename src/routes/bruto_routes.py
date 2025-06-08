from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
import pyodbc
import os
import json
from datetime import datetime

bruto_bp = Blueprint('bruto_bp', __name__)

def get_connection():
    db_path = session.get('db_path')
    if not db_path:
        return None
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
    )
    return pyodbc.connect(conn_str)

@bruto_bp.route('/')
def index():
    db_path = session.get('db_path')
    if not db_path:
        flash('Por favor, configure o banco de dados primeiro.', 'warning')
        return redirect(url_for('select_database'))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Filtros recebidos
        filtro_data = request.args.get('filtroData')
        filtro_tipo = request.args.get('filtroTipo')
        filtro_cd = request.args.get('filtroCD')

        # Parâmetro de página (padrão: 1)
        pagina = int(request.args.get('pagina', 1))
        limite = 100
        offset = (pagina - 1) * limite

        # Construção da cláusula WHERE
        where_clauses = []
        params = []
        if filtro_data:
            where_clauses.append('DATA = ?')
            params.append(filtro_data or '')
        if filtro_tipo:
            where_clauses.append('TIPO LIKE ?')
            params.append(f'%{filtro_tipo or ""}%')
        if filtro_cd:
            where_clauses.append('CD = ?')
            params.append(filtro_cd or "")

        where_sql = 'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''

        # Contagem total de registros com filtros
        count_query = f'SELECT COUNT(*) FROM Faturamento_Bruto {where_sql}'
        cursor.execute(count_query, params)
        total_registros = cursor.fetchone()[0]
        total_paginas = (total_registros + limite - 1) // limite

        # Consulta paginada com filtros
        select_query = f'''
            SELECT ID, TIPO, CD, DATA, [R$], TONS, [R$ / TON], FATURAMENTO, FAT_DEV_C_MOT, FAT_DEV_S_MOT
            FROM Faturamento_Bruto
            {where_sql}
            ORDER BY ID
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        '''
        cursor.execute(select_query, params + [offset, limite])
        rows = cursor.fetchall()
        colunas = [column[0] for column in cursor.description]
        dados = [dict(zip(colunas, row)) for row in rows]

        return render_template('bruto/index.html',
                               dados=dados,
                               pagina=pagina,
                               total_paginas=total_paginas,
                               filtros={'filtroData': filtro_data or '', 'filtroTipo': filtro_tipo or '', 'filtroCD': filtro_cd or ''},
                               connection_status={'status': True, 'message': 'Conectado'})

    except Exception as e:
        flash(f"Erro ao buscar dados: {str(e)}", "danger")
        return render_template('bruto/index.html', dados=[], pagina=1, total_paginas=1, filtros={}, connection_status={'status': False, 'message': 'Erro na leitura'})
    
@bruto_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        dados = request.form.to_dict()
        dados['data_criacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Faturamento_Bruto (TIPO, ESTADO, CD, DATA, [R$], TONS, [R$ / TON], FATURAMENTO, FAT_DEV_C_MOT, FAT_DEV_S_MOT)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('TIPO'),
            dados.get('ESTADO'),
            dados.get('CD'),
            dados.get('DATA'),
            float(dados.get('R$', 0)),
            float(dados.get('TONS', 0)),
            float(dados.get('R$ / TON', 0)),
            float(dados.get('FATURAMENTO', 0)),
            float(dados.get('FAT_DEV_C_MOT', 0)),
            float(dados.get('FAT_DEV_S_MOT', 0)),
        ))
        conn.commit()
        conn.close()

        flash('Registro adicionado com sucesso!', 'success')
        return redirect(url_for('bruto_bp.index'))

    return render_template('bruto/form.html', registro={}, connection_status={'status': True, 'message': 'Conectado'})

@bruto_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        dados = request.form.to_dict()
        cursor.execute('''
            UPDATE Faturamento_Bruto SET TIPO=?, ESTADO=?, CD=?, DATA=?, [R$]=?, TONS=?, [R$ / TON]=?, FATURAMENTO=?, FAT_DEV_C_MOT=?, FAT_DEV_S_MOT=? WHERE ID=?
        ''', (
            dados.get('TIPO'),
            dados.get('ESTADO'),
            dados.get('CD'),
            dados.get('DATA'),
            float(dados.get('R$', 0)),
            float(dados.get('TONS', 0)),
            float(dados.get('R$ / TON', 0)),
            float(dados.get('FATURAMENTO', 0)),
            float(dados.get('FAT_DEV_C_MOT', 0)),
            float(dados.get('FAT_DEV_S_MOT', 0)),
            id
        ))
        conn.commit()
        conn.close()

        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('bruto_bp.index'))

    cursor.execute('SELECT * FROM Faturamento_Bruto WHERE ID = ?', (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        flash('Registro não encontrado.', 'danger')
        return redirect(url_for('bruto_bp.index'))

    colunas = [column[0] for column in cursor.description]
    registro = dict(zip(colunas, row))

    return render_template('bruto/form.html', registro=registro, connection_status={'status': True, 'message': 'Conectado'})

@bruto_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Faturamento_Bruto WHERE ID = ?', (id,))
    conn.commit()
    conn.close()

    flash('Registro excluído com sucesso!', 'success')
    return redirect(url_for('bruto_bp.index'))
