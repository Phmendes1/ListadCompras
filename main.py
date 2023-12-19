from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import psycopg2

app = Flask(__name__)

# Configurações do banco de dados
db_config = {
    'host': 'seu_host',
    'database': 'seu_banco_de_dados',
    'user': 'seu_usuario',
    'password': 'sua_senha'
}


@app.route('/', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    # Autenticação do usuário (coloque sua lógica de autenticação aqui)
    if usuario == 'admin' and senha == 'admin123':
      # Configurar a sessão com um identificador de usuário
      # session['usuario_id'] = 1
      return redirect(url_for('pagina_inicio'))

    return render_template('login.html',
                           mensagem='Login inválido. Tente novamente.')

  return render_template('login.html')


# Rota para a página de início após o login bem-sucedido
@app.route('/pagina_inicio')
def pagina_inicio():
  # Verifique se o usuário está autenticado antes de exibir a página de início
  # Exemplo: if 'usuario_id' not in session: return redirect(url_for('login'))
  return render_template('pagina_inicio.html')


# Rota para a página de cadastro
@app.route('/pagina_cadastro', methods=['GET', 'POST'])
def pagina_cadastro():
  if request.method == 'POST':
    try:
      # Conectar ao banco de dados
      connection = psycopg2.connect(**db_config)
      cursor = connection.cursor()

      # Obter dados do formulário
      nome = request.form['nome']
      email = request.form['email']
      cpf = request.form['cpf']
      senha = request.form['senha']

      # Verificar se o usuário já existe
      cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email, ))
      existing_user = cursor.fetchone()

      if existing_user:
        return render_template('pagina_cadastro.html',
                               mensagem='Email já cadastrado. Tente outro.')

      # Inserir novo usuário no banco de dados
      cursor.execute(
          "INSERT INTO usuarios (nome, email, cpf, senha) VALUES (%s, %s, %s, %s)",
          (nome, email, cpf, senha))

      # Commit e fechar a conexão
      connection.commit()
      cursor.close()
      connection.close()

      return redirect(url_for('pagina_inicio'))

    except Exception as e:
      return render_template(
          'cadastro.html',
          mensagem='Erro ao cadastrar usuário. Tente novamente.')

  return render_template('cadastro.html')


# Rota para a página de nova lista
@app.route('/pagina_lista')
def pagina_listaNova():
  return render_template('pagina_lista.html')


# Rota para a página de lista
@app.route('/pagina_lista')
def pagina_lista():
  # Conectar ao banco de dados
  connection = psycopg2.connect(**db_config)
  cursor = connection.cursor()

  # Obter todas as listas do banco de dados
  cursor.execute("SELECT * FROM lista_compras")
  listas = cursor.fetchall()

  # Fechar a conexão
  cursor.close()
  connection.close()

  return render_template('pagina_lista.html', listas=listas)


# Rota para salvar informações da lista no banco de dados
@app.route('/salvar_lista', methods=['POST'])
def salvar_lista():
  try:
    # Conectar ao banco de dados
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    # Obter dados da requisição
    dados_lista = request.get_json()

    # Extrair informações da lista
    nome = dados_lista['nome']
    preco = dados_lista['preco']
    quantidade = dados_lista['quantidade']
    valor_total = dados_lista['valor_total']

    # Inserir dados no banco de dados
    cursor.execute(
        "INSERT INTO lista_compras (nome, preco, quantidade, valor_total) VALUES (%s, %s, %s, %s)",
        (nome, preco, quantidade, valor_total))

    # Commit
    connection.commit()

    # Seção adicional para verificar se o botão "Finalizar" foi clicado
    if dados_lista.get('finalizar_compra'):
      # Adicione sua lógica de finalização aqui
      # Por exemplo, você pode adicionar um registro na tabela 'compras_finalizadas'
      cursor.execute(
          "INSERT INTO compras_finalizadas (nome, preco, quantidade, valor_total) VALUES (%s, %s, %s, %s)",
          (nome, preco, quantidade, valor_total))

      # Commit novamente para salvar a compra finalizada
      connection.commit()

    # Fechar a conexão
    cursor.close()
    connection.close()

    # Redirecionar para a página_inicio.html após salvar com sucesso
    return jsonify({
        'status': 'success',
        'message': 'Lista salva com sucesso',
        'redirect': url_for('pagina_inicio')
    })
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)})


# Rota para fazer logout
@app.route('/logout', methods=['POST', 'GET'])
def logout():
  # Limpar a sessão
  session.clear()

  # Redirecionar p a página de login
  return render_template('login.html')
  #return redirect(url_for('login'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=True)

#if __name__ == '__main__':
#app.run(host='0.0.0.0', port=81, debug=True)
