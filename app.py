from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import random
import os 
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

#Pega a variável de ambiente e converte para json
FB_KEY = json.loads(os.getenv('CONFIG_FIREBASE'))

cred = credentials.Certificate(FB_KEY)
firebase_admin.initialize_app(cred)

#Conectando com o firestore da Firebase
db = firestore.client()

#*Rota principal de teste*
@app.route('/', methods = ['GET'])
def index():
    return 'API está ligada!'

#Rota método GET, charada aleatória
@app.route('/charadas', methods=['GET'])
def charada_aleatoria():
    charadas = []
    lista = db.collection('charadas').stream()
    for item in lista:
        charadas.append(item.to_dict()) #Transforma em dicionário cada charada do firebase

    if charadas:
        return jsonify(random.choice(charadas)), 200
    
    else:
        return jsonify({'Mensagem': 'Erro! Nenhuma charada encontrada.'}), 404

#Rota método GET, charada por ID
@app.route('/charadas/<id>', methods=['GET'])
def busca(id):
    doc_ref = db.collection('charadas').document(id) #Aponta este documento
    doc = doc_ref.get().to_dict() #Pega o que tem dentro do documento

    if doc:
        return jsonify(doc), 200
    
    else: 
        return jsonify({'mensagem': 'Erro! Charada não encontrada.'})
    
#Rota método POST, adicionar charada
@app.route('/charadas', methods=['POST'])
def adicionar_charada():
    dados = request.json

    if "pergunta" not in dados or "resposta" not in dados:
        return jsonify({'mensagem': 'Erro! Campos pergunta e resposta são obrigatórios'}), 400
    
    #Contador
    contador_ref = db.collection('controle_id').document('contador')
    contador_doc = contador_ref.get().to_dict()
    ultimo_id = contador_doc.get('id')
    novo_id = int(ultimo_id) + 1
    contador_ref.update({'id': novo_id})

    db.collection('charadas').document(str(novo_id)).set({
        "id": novo_id,
        "pergunta": dados['pergunta'],
        "resposta": dados['resposta']

    })

    return jsonify({'mensagem': 'Charada cadastrada com sucesso!'}), 201

#Rota metódo PUT, alterar charadas 
@app.route('/charadas/<id>', methods=['PUT'])
def alterar_charada(id):
    dados = request.json

    if "pergunta" not in dados or "resposta" not in dados:
        return jsonify({'mensagem': 'Erro! Campos pergunta e resposta são obrigatórios'}), 400
    
    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update({
            "pergunta": dados['pergunta'],
            "reposta": dados['resposta']
        })
        return jsonify({'mensagem': 'Charada alterada com sucesso!'}), 200
    
    else:
        return jsonify({'mensagem': 'Erro! Charada não encontrada'}), 404

#Rota método DELETE, deletar charada
@app.route('/charadas/<id>', methods=['DELETE'])
def excluir_charada(id):
    doc_ref = db.collection('charadas').document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({'mensagem': 'Erro! Charada não encontrada.'}), 404

    doc_ref.delete()
    return jsonify({'mensagem': 'Charada excluída com sucesso!'})

if __name__ == '__main__':
    app.run()




