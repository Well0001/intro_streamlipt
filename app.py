import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import datetime

# Configuração do banco de dados SQLite
engine = create_engine('sqlite:///clientes.db')
Base = declarative_base()


# Definindo o modelo de cliente com SQLAlchemy
class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    data_nascimento = Column(String, nullable=False)
    tipo_cliente = Column(String, nullable=False)
    cpf = Column(String, nullable=True)
    cnpj = Column(String, nullable=True)


# Criando a tabela no banco de dados (se não existir)
Base.metadata.create_all(engine)

# Criando uma sessão com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

# Configurações da pagina
st.set_page_config(
    page_title="Cadastro de Clientes",
    page_icon="🏢",
    layout="wide",
)


# Título da aplicação
st.title('Cadastro de Clientes')

# Coleta de dados
nome = st.text_input("Digite o nome do cliente")
endereco = st.text_input('Digite o endereço')
dt_nasc = str(st.date_input('Escolha a data de nascimento!', value=datetime.date(2000, 1, 1)))
tipo_cliente = st.selectbox('Tipo de cliente (Físico ou Jurídico)', ['PF', 'PJ'])

cpf = ''
cnpj = ''

if tipo_cliente == 'PJ':
    cnpj = st.text_input('Digite o CNPJ')
elif tipo_cliente == 'PF':
    cpf = st.text_input('Digite o CPF')

cadastrar = st.button('Cadastrar')

if cadastrar:
    try:
        # Verifica se CPF ou CNPJ foi preenchido corretamente
        if tipo_cliente == 'PF' and cpf:  # Cliente físico
            novo_cliente = Cliente(
                nome=nome,
                endereco=endereco,
                data_nascimento=dt_nasc,
                tipo_cliente=tipo_cliente,
                cpf=cpf
            )
        elif tipo_cliente == 'PJ' and cnpj:  # Cliente jurídico
            novo_cliente = Cliente(
                nome=nome,
                endereco=endereco,
                data_nascimento=dt_nasc,
                tipo_cliente=tipo_cliente,
                cnpj=cnpj
            )
        else:
            st.error('Por favor, preencha todos os campos obrigatórios!', icon='❌')
            st.stop()

        # Adiciona o novo cliente à sessão e grava no banco de dados
        session.add(novo_cliente)
        session.commit()

        st.success('Cadastro realizado com sucesso!', icon='✅')

    except Exception as e:
        session.rollback()  # Reverter caso de erro
        st.error(f'Ocorreu um erro ao tentar cadastrar: {e}', icon='❌')

# Exibir todos os clientes cadastrados em formato de tabela
st.header('Clientes cadastrados')

# Consulta todos os clientes do banco de dados
clientes = session.query(Cliente).all()

# Transformar os resultados da query em um DataFrame do Pandas
clientes_data = []
for cliente in clientes:
    clientes_data.append({
        'Nome': cliente.nome,
        'Endereço': cliente.endereco,
        'Data de Nascimento': cliente.data_nascimento,
        'Tipo': cliente.tipo_cliente,
        'CPF/CNPJ': cliente.cpf or cliente.cnpj
    })

# Criar o DataFrame com os dados dos clientes (sem o campo ID)
df_clientes = pd.DataFrame(clientes_data)

# Alternador para mostrar ou esconder a lista de clientes
if 'show_clients' not in st.session_state:
    st.session_state.show_clients = False

# Altera a label do botão com base no estado atual
button_label = 'Ocultar Clientes' if st.session_state.show_clients else 'Mostrar Clientes'
toggle_button = st.button(button_label, key='toggle_button')

if toggle_button:
    st.session_state.show_clients = not st.session_state.show_clients
    st.rerun()

if st.session_state.show_clients:
    if not df_clientes.empty:
        st.dataframe(df_clientes)  # Exibir a tabela de clientes
    else:
        st.write("Nenhum cliente cadastrado ainda.")
else:
    pass
