from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Bruto(db.Model):
    __tablename__ = 'bruto'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cd = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False)  # R$
    tons = db.Column(db.Float, nullable=False)  # TONS
    valor_por_ton = db.Column(db.Float)  # R$ / TON (calculado)
    faturamento = db.Column(db.Float)
    fat_dev_c_mot = db.Column(db.Float)
    fat_dev_s_mot = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tipo, estado, cd, data, valor, tons, faturamento=None, 
                 fat_dev_c_mot=None, fat_dev_s_mot=None):
        self.tipo = tipo
        self.estado = estado
        self.cd = cd
        self.data = data
        self.valor = valor
        self.tons = tons
        self.valor_por_ton = valor / tons if tons else 0
        self.faturamento = faturamento
        self.fat_dev_c_mot = fat_dev_c_mot
        self.fat_dev_s_mot = fat_dev_s_mot
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'estado': self.estado,
            'cd': self.cd,
            'data': self.data.strftime('%Y-%m-%d'),
            'valor': self.valor,
            'tons': self.tons,
            'valor_por_ton': self.valor_por_ton,
            'faturamento': self.faturamento,
            'fat_dev_c_mot': self.fat_dev_c_mot,
            'fat_dev_s_mot': self.fat_dev_s_mot
        }


class Liquido(db.Model):
    __tablename__ = 'liquido'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cd = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False)  # R$
    tons = db.Column(db.Float, nullable=False)  # TONS
    valor_por_ton = db.Column(db.Float)  # R$ / TON (calculado)
    faturamento = db.Column(db.Float)
    fat_dev_c_mot = db.Column(db.Float)
    fat_dev_s_mot = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tipo, estado, cd, data, valor, tons, faturamento=None, 
                 fat_dev_c_mot=None, fat_dev_s_mot=None):
        self.tipo = tipo
        self.estado = estado
        self.cd = cd
        self.data = data
        self.valor = valor
        self.tons = tons
        self.valor_por_ton = valor / tons if tons else 0
        self.faturamento = faturamento
        self.fat_dev_c_mot = fat_dev_c_mot
        self.fat_dev_s_mot = fat_dev_s_mot
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'estado': self.estado,
            'cd': self.cd,
            'data': self.data.strftime('%Y-%m-%d'),
            'valor': self.valor,
            'tons': self.tons,
            'valor_por_ton': self.valor_por_ton,
            'faturamento': self.faturamento,
            'fat_dev_c_mot': self.fat_dev_c_mot,
            'fat_dev_s_mot': self.fat_dev_s_mot
        }


class Regiao(db.Model):
    __tablename__ = 'regiao'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cd = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    mes = db.Column(db.Integer)  # Calculado da data
    ano = db.Column(db.Integer)  # Calculado da data
    regiao = db.Column(db.String(100), nullable=False)
    tons = db.Column(db.Float)
    tons_dev_c_mot = db.Column(db.Float)
    tons_dev_s_mot = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tipo, estado, cd, data, regiao, tons=None, 
                 tons_dev_c_mot=None, tons_dev_s_mot=None):
        self.tipo = tipo
        self.estado = estado
        self.cd = cd
        self.data = data
        self.mes = data.month
        self.ano = data.year
        self.regiao = regiao
        self.tons = tons
        self.tons_dev_c_mot = tons_dev_c_mot
        self.tons_dev_s_mot = tons_dev_s_mot
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'estado': self.estado,
            'cd': self.cd,
            'data': self.data.strftime('%Y-%m-%d'),
            'mes': self.mes,
            'ano': self.ano,
            'regiao': self.regiao,
            'tons': self.tons,
            'tons_dev_c_mot': self.tons_dev_c_mot,
            'tons_dev_s_mot': self.tons_dev_s_mot
        }


class Entregas(db.Model):
    __tablename__ = 'entregas'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cd = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    mes = db.Column(db.Integer)  # Calculado da data
    ano = db.Column(db.Integer)  # Calculado da data
    regiao = db.Column(db.String(100), nullable=False)
    entregas = db.Column(db.Float)
    ent_dev_c_mot = db.Column(db.Float)
    ent_dev_s_mot = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tipo, estado, cd, data, regiao, entregas=None, 
                 ent_dev_c_mot=None, ent_dev_s_mot=None):
        self.tipo = tipo
        self.estado = estado
        self.cd = cd
        self.data = data
        self.mes = data.month
        self.ano = data.year
        self.regiao = regiao
        self.entregas = entregas
        self.ent_dev_c_mot = ent_dev_c_mot
        self.ent_dev_s_mot = ent_dev_s_mot
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'estado': self.estado,
            'cd': self.cd,
            'data': self.data.strftime('%Y-%m-%d'),
            'mes': self.mes,
            'ano': self.ano,
            'regiao': self.regiao,
            'entregas': self.entregas,
            'ent_dev_c_mot': self.ent_dev_c_mot,
            'ent_dev_s_mot': self.ent_dev_s_mot
        }


class KmRodado(db.Model):
    __tablename__ = 'km_rodado'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cd = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    km_rodado = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tipo, estado, cd, data, km_rodado):
        self.tipo = tipo
        self.estado = estado
        self.cd = cd
        self.data = data
        self.km_rodado = km_rodado
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'estado': self.estado,
            'cd': self.cd,
            'data': self.data.strftime('%Y-%m-%d'),
            'km_rodado': self.km_rodado
        }


class Ocupacao(db.Model):
    __tablename__ = 'ocupacao'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cd = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    ocupacao = db.Column(db.Float, nullable=False)  # Percentual (0-100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tipo, estado, cd, data, ocupacao):
        self.tipo = tipo
        self.estado = estado
        self.cd = cd
        self.data = data
        self.ocupacao = ocupacao
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'estado': self.estado,
            'cd': self.cd,
            'data': self.data.strftime('%Y-%m-%d'),
            'ocupacao': self.ocupacao
        }
