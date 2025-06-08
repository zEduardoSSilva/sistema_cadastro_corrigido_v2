from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
import os
import json
from datetime import datetime

km_rodado_bp = Blueprint('km_rodado_bp', __name__)

# Simulação de dados para desenvolvimento
dados_km_rodado = []

@km_rodado_bp.route('/')
def index():
    # Verificar se há um banco configurado
    db_path = session.get('db_path')
    if not db_path:
        flash('Por favor, configure o banco de dados primeiro.', 'warning')
        return redirect(url_for('select_database'))
    
    # Em produção, aqui buscaríamos os dados do banco Access
    # Para desenvolvimento, usamos dados simulados
    
    return render_template('km_rodado/index.html', 
                          dados=dados_km_rodado,
                          connection_status={'status': True, 'message': 'Conectado (simulado)'})

@km_rodado_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        # Processar dados do formulário
        dados = request.form.to_dict()
        
        # Adicionar ID e data de criação
        dados['id'] = len(dados_km_rodado) + 1
        dados['data_criacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Em produção, salvaríamos no banco Access
        # Para desenvolvimento, adicionamos à lista simulada
        dados_km_rodado.append(dados)
        
        flash('Registro adicionado com sucesso!', 'success')
        return redirect(url_for('km_rodado_bp.index'))
    
    return render_template('km_rodado/form.html',
                          registro={},
                          connection_status={'status': True, 'message': 'Conectado (simulado)'})

@km_rodado_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    # Buscar registro pelo ID
    registro = next((item for item in dados_km_rodado if item['id'] == id), None)
    
    if not registro:
        flash('Registro não encontrado.', 'danger')
        return redirect(url_for('km_rodado_bp.index'))
    
    if request.method == 'POST':
        # Atualizar dados do registro
        dados = request.form.to_dict()
        dados['id'] = id
        
        # Em produção, atualizaríamos no banco Access
        # Para desenvolvimento, atualizamos na lista simulada
        for i, item in enumerate(dados_km_rodado):
            if item['id'] == id:
                dados_km_rodado[i] = dados
                break
        
        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('km_rodado_bp.index'))
    
    return render_template('km_rodado/form.html',
                          registro=registro,
                          connection_status={'status': True, 'message': 'Conectado (simulado)'})

@km_rodado_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    # Em produção, excluiríamos do banco Access
    # Para desenvolvimento, removemos da lista simulada
    global dados_km_rodado
    dados_km_rodado = [item for item in dados_km_rodado if item['id'] != id]
    
    flash('Registro excluído com sucesso!', 'success')
    return redirect(url_for('km_rodado_bp.index'))
