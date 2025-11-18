import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from urllib.parse import urlparse

def criar_pasta_se_nao_existir(nome_pasta):
    """
    Cria uma pasta se ela não existir
    """
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
        print(f"✅ Pasta '{nome_pasta}' criada com sucesso!")

def obter_user_agent():
    """
    Retorna um User-Agent realista para evitar bloqueios
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

def baixar_foto_linkedin(url_linkedin, nome_pessoa):
    """
    Tenta baixar a foto do perfil do LinkedIn
    Retorna (sucesso, caminho_arquivo, origem) ou (False, None, None) em caso de erro
    """
    try:
        print(f"🔍 Tentando acessar LinkedIn de {nome_pessoa}...")
        
        # Fazer requisição para o LinkedIn
        headers = obter_user_agent()
        response = requests.get(url_linkedin, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar LinkedIn: Status {response.status_code}")
            return False, None, None
        
        # Parse do HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Estratégia 1: Procurar pela tag meta com a imagem do perfil
        meta_imagem = soup.find('meta', property='og:image')
        if meta_imagem and meta_imagem.get('content'):
            url_imagem = meta_imagem['content']
            # Verificar se é uma imagem válida (não a imagem padrão)
            if 'sharing' not in url_imagem and 'static' not in url_imagem:
                print(f"📸 Foto do LinkedIn encontrada: {url_imagem}")
                return baixar_imagem(url_imagem, nome_pessoa, 'linkedin')
        
        # Estratégia 2: Procurar por elementos de imagem específicos
        img_perfil = soup.find('img', {'class': ['pv-top-card-profile-picture__image', 'evi-image', 'profile-photo-edit__preview']})
        if img_perfil and img_perfil.get('src'):
            url_imagem = img_perfil['src']
            if 'sharing' not in url_imagem and 'static' not in url_imagem:
                print(f"📸 Foto do LinkedIn encontrada: {url_imagem}")
                return baixar_imagem(url_imagem, nome_pessoa, 'linkedin')
        
        print("ℹ️  Nenhuma foto encontrada no LinkedIn")
        return False, None, None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com LinkedIn: {e}")
        return False, None, None
    except Exception as e:
        print(f"❌ Erro inesperado no LinkedIn: {e}")
        return False, None, None

def baixar_foto_github(url_github, nome_pessoa):
    """
    Tenta baixar a foto do perfil do GitHub
    Retorna (sucesso, caminho_arquivo, origem) ou (False, None, None) em caso de erro
    """
    try:
        print(f"🔍 Tentando acessar GitHub de {nome_pessoa}...")
        
        # Extrair username do URL do GitHub
        parsed_url = urlparse(url_github)
        caminho = parsed_url.path.strip('/')
        if '/' in caminho:
            username = caminho.split('/')[0]
        else:
            username = caminho
        
        if not username:
            print("❌ Não foi possível extrair username do GitHub")
            return False, None, None
        
        # URL do avatar do GitHub
        url_avatar = f"https://avatars.githubusercontent.com/{username}"
        
        print(f"📸 Tentando baixar avatar do GitHub: {url_avatar}")
        return baixar_imagem(url_avatar, nome_pessoa, 'github')
        
    except Exception as e:
        print(f"❌ Erro ao baixar foto do GitHub: {e}")
        return False, None, None

def baixar_imagem(url_imagem, nome_pessoa, origem):
    """
    Baixa a imagem da URL e salva no disco
    Retorna (sucesso, caminho_arquivo, origem)
    """
    try:
        headers = obter_user_agent()
        response = requests.get(url_imagem, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erro ao baixar imagem: Status {response.status_code}")
            return False, None, None
        
        # Verificar se é realmente uma imagem
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"❌ URL não é uma imagem: {content_type}")
            return False, None, None
        
        # Criar nome do arquivo seguro (sem caracteres especiais)
        nome_arquivo = f"{nome_pessoa.replace(' ', '_').replace('/', '_')}.jpg"
        caminho_arquivo = os.path.join('fotos', nome_arquivo)
        
        # Salvar imagem
        with open(caminho_arquivo, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Foto salva: {caminho_arquivo}")
        return True, caminho_arquivo, origem
        
    except Exception as e:
        print(f"❌ Erro ao baixar imagem: {e}")
        return False, None, None

def processar_pessoas():
    """
    Função principal que processa todas as pessoas do CSV
    """
    # Criar pasta de fotos
    criar_pasta_se_nao_existir('fotos')
    
    # Lista para armazenar resultados
    resultados = []
    
    try:
        # Ler arquivo CSV
        with open('pessoas.csv', 'r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            pessoas = list(leitor)
        
        print(f"📊 Encontradas {len(pessoas)} pessoas para processar")
        
        for pessoa in pessoas:
            nome = pessoa['nome']
            linkedin = pessoa['linkedin'].strip()
            github = pessoa['github'].strip()
            
            print(f"\n{'='*50}")
            print(f"👤 Processando: {nome}")
            print(f"🔗 LinkedIn: {linkedin}")
            print(f"🐙 GitHub: {github}")
            
            sucesso = False
            caminho_arquivo = None
            origem = None
            
            # Tentar LinkedIn primeiro
            if linkedin and linkedin.lower() != 'none':
                sucesso, caminho_arquivo, origem = baixar_foto_linkedin(linkedin, nome)
            
            # Se LinkedIn falhou, tentar GitHub
            if not sucesso and github and github.lower() != 'none':
                sucesso, caminho_arquivo, origem = baixar_foto_github(github, nome)
            
            # Registrar resultado
            if sucesso:
                resultados.append({
                    'nome': nome,
                    'origem_foto': origem,
                    'arquivo': caminho_arquivo
                })
                print(f"✅ {nome}: Foto baixada do {origem.upper()}")
            else:
                resultados.append({
                    'nome': nome,
                    'origem_foto': 'nenhum',
                    'arquivo': 'none'
                })
                print(f"❌ {nome}: Nenhuma foto encontrada")
            
            # Pequena pausa para evitar bloqueios
            time.sleep(1)
        
        # Salvar resultados em CSV
        with open('resultado.csv', 'w', newline='', encoding='utf-8') as arquivo:
            campos = ['nome', 'origem_foto', 'arquivo']
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            
            escritor.writeheader()
            for resultado in resultados:
                escritor.writerow(resultado)
        
        print(f"\n🎉 Processamento concluído!")
        print(f"📁 Fotos salvas em: fotos/")
        print(f"📊 Relatório salvo em: resultado.csv")
        
        # Estatísticas
        sucessos = sum(1 for r in resultados if r['origem_foto'] != 'nenhum')
        print(f"📈 Estatísticas: {sucessos}/{len(resultados)} fotos baixadas com sucesso")
        
    except FileNotFoundError:
        print("❌ Erro: Arquivo 'pessoas.csv' não encontrado!")
        print("💡 Certifique-se de que o arquivo existe no mesmo diretório do script")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def criar_exemplo_csv():
    """
    Cria um arquivo CSV de exemplo com 3 pessoas fictícias
    """
    dados_exemplo = [
        {'nome': 'Ana Silva', 'linkedin': 'https://www.linkedin.com/in/ana-silva-exemplo', 'github': 'https://github.com/anaxsilva'},
        {'nome': 'Carlos Santos', 'linkedin': 'https://www.linkedin.com/in/carlos-santos-exemplo', 'github': 'https://github.com/carlossantos'},
        {'nome': 'Maria Oliveira', 'linkedin': 'https://www.linkedin.com/in/maria-oliveira-exemplo', 'github': 'https://github.com/mariaoliveira'}
    ]
    
    with open('pessoas.csv', 'w', newline='', encoding='utf-8') as arquivo:
        campos = ['nome', 'linkedin', 'github']
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        
        escritor.writeheader()
        for pessoa in dados_exemplo:
            escritor.writerow(pessoa)
    
    print("📝 Arquivo 'pessoas.csv' de exemplo criado com sucesso!")
    print("💡 Você pode editar este arquivo com os dados reais que deseja processar")

if __name__ == "__main__":
    print("🚀 Iniciando Script de Download de Fotos de Perfil")
    print("=" * 60)
    
    # Verificar se o arquivo CSV existe
    if not os.path.exists('pessoas.csv'):
        print("ℹ️  Arquivo 'pessoas.csv' não encontrado.")
        criar_exemplo_csv()
    
    # Executar o processamento
    processar_pessoas()