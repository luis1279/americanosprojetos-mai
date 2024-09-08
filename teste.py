# # import sqlite3

# # conn = sqlite3.connect('database.db')
# # cursor = conn.cursor()

# # def delete_all_rows(transacoes):
# #     query = f"DELETE FROM {transacoes};"
# #     cursor.execute(query)
# #     print(f"Deleted all rows from {transacoes}")


# # delete_all_rows('transacoes')

# # conn.commit()
# # conn.close()

# # import sqlite3

# # # # Conectando ao banco de dados
# # conn = sqlite3.connect('database.db')
# # cursor = conn.cursor()

# # # cursor.execute('''
# # #     DROP TABLE adicoes;
# # # ''')
# # # cursor.execute('''
# # #     DROP TABLE retiradas;
# # # ''')

# # # Função para clonar uma tabela
# # def clone_table(alunos, adicoes):
# #     # Passo 1: Criar a nova tabela com a mesma estrutura da tabela original
# #     cursor.execute(f'''
# #         CREATE TABLE {adicoes} AS SELECT * FROM {alunos} WHERE 0;
# #     ''')

# #     # Passo 2: Copiar os dados da tabela original para a nova tabela
# #     cursor.execute(f'''
# #         INSERT INTO {adicoes} SELECT * FROM {alunos};
# #     ''')

# #     print(f"Tabela '{alunos}' clonada para '{adicoes}'")

# # # Exemplo: Clonar a tabela 'alunos' para 'alunos_clone'
# # clone_table('alunos', 'adicoes')

# # # Função para clonar uma tabela
# # def clone_table(alunos, retiradas):
# #     # Passo 1: Criar a nova tabela com a mesma estrutura da tabela original
# #     cursor.execute(f'''
# #         CREATE TABLE {retiradas} AS SELECT * FROM {alunos} WHERE 0;
# #     ''')

# #     # Passo 2: Copiar os dados da tabela original para a nova tabela
# #     cursor.execute(f'''
# #         INSERT INTO {retiradas} SELECT * FROM {alunos};
# #     ''')

# #     print(f"Tabela '{alunos}' clonada para '{retiradas}'")

# # # Exemplo: Clonar a tabela 'alunos' para 'alunos_clone'
# # clone_table('alunos', 'retiradas')

# # # Comitando as mudanças e fechando a conexão
# # conn.commit()
# # conn.close()

# # import sqlite3

# # # Conectar ao banco de dados (altere 'database.db' para o caminho do seu banco de dados)
# # conn = sqlite3.connect('database.db')
# # cursor = conn.cursor()

# # # Apagar o valor da célula (definindo como NULL)
# # cursor.execute('UPDATE retiradas SET "Heryco Lemos Queirós" = 0 WHERE id = ?', (1,))

# # # Confirmar as mudanças
# # conn.commit()

# # # Fechar a conexão
# # conn.close()



# # import sqlite3

# # # Conectar ao banco de dados (altere 'database.db' para o caminho do seu banco de dados)
# # conn = sqlite3.connect('database.db')
# # cursor = conn.cursor()

# # # Apagar uma linha específica da tabela
# # cursor.execute('DELETE FROM retiradas WHERE id = ?', (244,))

# # # Confirmar as mudanças
# # conn.commit()

# # # Fechar a conexão
# # conn.close()







# # # Código para alterar o valor de uma determinada célula de uma tabela

# import sqlite3

# # Função para conectar ao banco de dados
# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row  # Para acessar as colunas pelo nome
#     return conn

# # Função para atualizar uma célula específica em três tabelas
# def atualizar_valor_tabelas(tabelas, coluna, novo_valor, condicao_coluna, condicao_valor):
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Loop pelas tabelas para executar a atualização em cada uma delas
#     for tabela in tabelas:
#         query = f'UPDATE {tabela} SET {coluna} = ? WHERE {condicao_coluna} = ?'
#         cursor.execute(query, (novo_valor, condicao_valor))
    
#     # Confirma as mudanças no banco de dados
#     conn.commit()
    
#     # Fecha a conexão
#     conn.close()
#     print(f"Valor atualizado com sucesso nas tabelas: {', '.join(tabelas)}")

# # Exemplo de uso
# # Atualiza a coluna 'saldo' do aluno com id = 1 para o novo valor 100 nas tabelas 'alunos', 'adicoes', e 'retiradas'
#             ######### Atualiza a coluna 'turma' do aluno de 'id' 255. ############
# atualizar_valor_tabelas(['alunos', 'adicoes', 'retiradas'], 'turma', '1A', 'id', 255)

echo "# americanosprojetos" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/herycolemos/americanosprojetos.git
git push -u origin main