import requests
import csv
import os
import time

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def criar_pasta(nome):
    """Cria pasta se não existir"""
    if not os.path.exists(nome):
        os.makedirs(nome)


def extrair_username_github(url):
    """Extrai username de URL do GitHub"""
    # https://github.com/username -> username
    partes = url.replace('https://', '').replace('http://', '').split('/')
    if len(partes) >= 2:
        return partes[1]
    return None


def baixar_imagem(url, nome_arquivo):
    """Baixa imagem de uma URL e salva em disco"""
    try:
        # Faz download da imagem
        resposta = requests.get(url, timeout=10)
        
        # Verifica se deu certo
        if resposta.status_code != 200:
            return False
        
        # Salva no arquivo
        with open(nome_arquivo, 'wb') as arquivo:
            arquivo.write(resposta.content)
        
        return True
        
    except:
        return False


# ============================================================
# FUNÇÕES DE DOWNLOAD POR PLATAFORMA
# ============================================================

def baixar_foto_github(url_github, nome_pessoa):
    """Baixa foto do perfil do GitHub"""
    # Extrai username da URL
    username = extrair_username_github(url_github)
    if not username:
        return False
    
    # URL da foto do GitHub
    url_foto = f"https://avatars.githubusercontent.com/{username}"
    
    # Nome do arquivo
    nome_arquivo = f"fotos/{nome_pessoa.replace(' ', '_')}.jpg"
    
    # Baixa e retorna resultado
    return baixar_imagem(url_foto, nome_arquivo)


def baixar_foto_linkedin(url_linkedin, nome_pessoa):
    """Tenta baixar foto do LinkedIn (pode não funcionar sempre)"""
    try:
        # Acessa a página
        resposta = requests.get(url_linkedin, timeout=10)
        if resposta.status_code != 200:
            return False
        
        # Procura pela meta tag com a imagem
        if 'og:image' in resposta.text:
            inicio = resposta.text.find('og:image" content="') + 19
            fim = resposta.text.find('"', inicio)
            url_foto = resposta.text[inicio:fim]
            
            # Verifica se é uma foto válida (não é o logo padrão)
            if 'static' not in url_foto and 'sharing' not in url_foto:
                nome_arquivo = f"fotos/{nome_pessoa.replace(' ', '_')}.jpg"
                return baixar_imagem(url_foto, nome_arquivo)
        
        return False
        
    except:
        return False


# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================

def processar_csv():
    """Lê CSV e baixa todas as fotos"""
    
    # Cria pasta de fotos
    criar_pasta('fotos')
    
    # Lista para resultados
    resultados = []
    
    # Lê arquivo CSV
    with open('pessoas.csv', 'r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        pessoas = list(leitor)
    
    print(f"Total de pessoas: {len(pessoas)}\n")
    
    # Processa cada pessoa
    for pessoa in pessoas:
        nome = pessoa['nome']
        linkedin = pessoa['linkedin']
        github = pessoa['github']
        
        print(f"Processando: {nome}")
        
        sucesso = False
        origem = "nenhum"
        
        # Tenta LinkedIn primeiro
        if linkedin and linkedin != 'none':
            if baixar_foto_linkedin(linkedin, nome):
                sucesso = True
                origem = "linkedin"
                print(f"  ✓ Foto baixada do LinkedIn")
        
        # Se falhou, tenta GitHub
        if not sucesso and github and github != 'none':
            if baixar_foto_github(github, nome):
                sucesso = True
                origem = "github"
                print(f"  ✓ Foto baixada do GitHub")
        
        # Se nada funcionou
        if not sucesso:
            print(f"  ✗ Nenhuma foto encontrada")
        
        # Guarda resultado
        resultados.append({
            'nome': nome,
            'origem': origem,
            'sucesso': 'sim' if sucesso else 'nao'
        })
        
        # Pausa de 1 segundo entre requisições
        time.sleep(1)
    
    # Salva resultados em CSV
    with open('resultado.csv', 'w', newline='', encoding='utf-8') as arquivo:
        campos = ['nome', 'origem', 'sucesso']
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)
    
    # Mostra resumo
    total_sucesso = sum(1 for r in resultados if r['sucesso'] == 'sim')
    print(f"\nConcluído: {total_sucesso}/{len(resultados)} fotos baixadas")
    print("Resultados salvos em: resultado.csv")


# ============================================================
# CRIAR ARQUIVO DE EXEMPLO
# ============================================================

def criar_csv_exemplo():
    """Cria arquivo CSV de exemplo"""
    dados = [
        {'nome': 'Pessoa 1', 'linkedin': 'https://linkedin.com/in/exemplo1', 'github': 'https://github.com/exemplo1'},
        {'nome': 'Pessoa 2', 'linkedin': 'https://linkedin.com/in/exemplo2', 'github': 'https://github.com/exemplo2'},
        {'nome': 'Pessoa 3', 'linkedin': 'none', 'github': 'https://github.com/exemplo3'}
    ]
    
    with open('pessoas.csv', 'w', newline='', encoding='utf-8') as arquivo:
        campos = ['nome', 'linkedin', 'github']
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(dados)
    
    print("Arquivo 'pessoas.csv' criado com dados de exemplo")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("DOWNLOAD DE FOTOS DE PERFIL")
    print("=" * 50)
    print()
    
    # Se não existir CSV, cria exemplo
    if not os.path.exists('pessoas.csv'):
        print("Arquivo 'pessoas.csv' não encontrado.")
        criar_csv_exemplo()
        print()
    
    # Processa o CSV
    processar_csv()