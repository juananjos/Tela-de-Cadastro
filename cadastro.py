import PySimpleGUI as sg
import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

conexao = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
) #Conexão com o banco de dados

cursor = conexao.cursor() #Cursor para realizar operações no BD

sg.theme('reddit')   #Tema do layout da janela

janela_cadastro= [ #Definição dos elementos da janela de cadastro
    [sg.Text('Email'),sg.Input(key='email')],
    [sg.Text('Senha'),sg.Input(key='senha', password_char='*')],
    [sg.Text('Confirmação senha'),sg.Input(key='confirmar_senha', password_char='*')],
    [sg.Button('Cadastrar')]
] 


def verificar_email(email): #Verifica se o email já existe no banco de dados
    email = email.lower()
    cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")
    return cursor.fetchone() is not None

def verificar_login(email, senha, confirmar_senha): #Verifica se a senha e email estão válidos
    email = email.lower()
    if "@" in email and ".com" in email:
        if any(char.isalpha() for char in senha) and any(char.isdigit() for char in senha) and len(senha) >= 8:
            if confirmar_senha == senha:
                if not verificar_email(email):
                    return True, None
                else:
                    return False, "Email já está em uso. Por favor, escolha outro."
            else:
                return False, "As senhas não coincidem."
        else:
            return False, "Senha inválida."
    else:
        return False, "Email inválido."
    
def criar_hash_senha(senha): #Criptografa a senha 
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    
janela = sg.Window('Cadastro', layout = janela_cadastro)


while True: 
    event, values = janela.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Cadastrar':
        email = values['email'].lower()
        valido, mensagem_erro = verificar_login(values['email'], values['senha'], values['confirmar_senha']) 
        
        if valido:
            sg.popup_non_blocking('Cadastro efetuado com sucesso!')
            hash_senha = criar_hash_senha(values['senha'])
            comando = "INSERT INTO usuarios (email, senha) VALUES (%s, %s)"
            cursor.execute(comando, (values["email"], hash_senha.decode("utf-8")))

            conexao.commit()
        else:
            sg.popup_non_blocking(mensagem_erro)
   

janela.close()
