import requests
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# ============================================================
# CONFIGURAÇÕES ROBUSTAS
# ============================================================

CHROME_OPTIONS = Options()
# CHROME_OPTIONS.add_argument('--headless=new')  # Mantenha comentado para ver o navegador
CHROME_OPTIONS.add_argument('--no-sandbox')
CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')
CHROME_OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])
CHROME_OPTIONS.add_experimental_option('useAutomationExtension', False)
CHROME_OPTIONS.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
CHROME_OPTIONS.add_argument('--start-maximized')

# ============================================================
# FUNÇÕES AUXILIARES ROBUSTAS
# ============================================================

def criar_pasta_segura(nome_pasta):
    """Cria pasta com tratamento de erro robusto"""
    try:
        if not os.path.exists(nome_pasta):
            os.makedirs(nome_pasta)
            print(f"✅ Pasta '{nome_pasta}' criada")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar pasta '{nome_pasta}': {e}")
        return False

def limpar_nome_arquivo(nome):
    """Remove caracteres inválidos para nome de arquivo"""
    caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in caracteres_invalidos:
        nome = nome.replace(char, '_')
    return nome[:100]  # Limita tamanho

def baixar_imagem_super_robusta(url, nome_arquivo):
    """Baixa imagem com tratamento completo de erros"""
    try:
        # Garante que a pasta existe
        pasta = os.path.dirname(nome_arquivo)
        if not criar_pasta_segura(pasta):
            return False
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        }
        
        # Se for LinkedIn, adiciona referer
        if 'linkedin.com' in url:
            headers['Referer'] = 'https://www.linkedin.com/'
        
        resposta = requests.get(url, headers=headers, timeout=20, stream=True)
        
        if resposta.status_code == 200:
            # Verifica se é realmente uma imagem
            content_type = resposta.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"    ⚠️  URL não é uma imagem: {content_type}")
                return False
            
            with open(nome_arquivo, 'wb') as arquivo:
                for chunk in resposta.iter_content(1024):
                    arquivo.write(chunk)
            
            # Verifica se o arquivo foi criado e tem tamanho razoável
            if os.path.exists(nome_arquivo):
                tamanho = os.path.getsize(nome_arquivo)
                if tamanho > 500:  # Pelo menos 500 bytes
                    print(f"    ✅ Imagem salva: {nome_arquivo} ({tamanho} bytes)")
                    return True
                else:
                    os.remove(nome_arquivo)
                    print(f"    ⚠️  Arquivo muito pequeno: {tamanho} bytes")
                    return False
            return False
        else:
            print(f"    ❌ Erro HTTP {resposta.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ Erro ao baixar imagem: {e}")
        return False

def extrair_username_github(url):
    """Extrai username de URL do GitHub de forma robusta"""
    if not url:
        return None
    
    try:
        url_limpa = url.strip().replace('https://', '').replace('http://', '')
        partes = url_limpa.split('/')
        
        for parte in partes:
            if parte and parte not in ['', 'github.com']:
                return parte
        return None
    except:
        return None

def baixar_foto_github_super(url_github, nome_pessoa):
    """Baixa foto do GitHub com múltiplas tentativas"""
    try:
        if not url_github or not url_github.startswith('http'):
            return False
            
        username = extrair_username_github(url_github)
        if not username:
            print(f"    ❌ Não foi possível extrair username do GitHub")
            return False
        
        # Nome do arquivo seguro
        nome_seguro = limpar_nome_arquivo(nome_pessoa.replace(' ', '_'))
        nome_arquivo = f"fotos/{nome_seguro}_github.jpg"
        
        # Múltiplas URLs para tentar
        urls_tentativas = [
            f"https://avatars.githubusercontent.com/{username}?size=400",
            f"https://avatars.githubusercontent.com/{username}",
            f"https://github.com/{username}.png?size=400",
            f"https://github.com/{username}.png",
        ]
        
        for i, url_foto in enumerate(urls_tentativas, 1):
            print(f"    🔄 Tentativa {i}/4 GitHub: {username}")
            if baixar_imagem_super_robusta(url_foto, nome_arquivo):
                return True
            time.sleep(1)  # Pausa entre tentativas
        
        return False
        
    except Exception as e:
        print(f"    ❌ Erro GitHub: {e}")
        return False

# ============================================================
# SELENIUM ROBUSTO
# ============================================================

def inicializar_selenium_robusto():
    """Inicializa Selenium com tratamento de erro robusto"""
    try:
        print("🚀 Inicializando navegador...")
        driver = webdriver.Chrome(options=CHROME_OPTIONS)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        print("✅ Navegador inicializado com sucesso")
        return driver
    except Exception as e:
        print(f"❌ Erro ao inicializar Selenium: {e}")
        print("💡 Soluções possíveis:")
        print("   1. Baixe o ChromeDriver em: https://chromedriver.chromium.org/")
        print("   2. Ou instale: pip install webdriver-manager")
        return None

def verificar_sessao_ativa(driver):
    """Verifica se a sessão do Selenium ainda está ativa"""
    try:
        driver.current_url
        return True
    except WebDriverException:
        return False

def fazer_login_linkedin_robusto(driver):
    """Faz login manual com verificações robustas"""
    print("\n🔐 INSTRUÇÕES DE LOGIN NO LINKEDIN:")
    print("   =========================================")
    print("   1. O navegador abrirá na página de login")
    print("   2. Faça login MANUALMENTE com sua conta")
    print("   3. Após login completo, VOLTE para este terminal")
    print("   4. Pressione ENTER para continuar o script")
    print("   =========================================\n")
    
    try:
        driver.get("https://www.linkedin.com/login")
        print("✅ Página de login carregada")
        
        input("   ⏳ Após fazer login, pressione ENTER aqui... ")
        
        # Verificações de login bem-sucedido
        time.sleep(3)
        current_url = driver.current_url
        
        if "feed" in current_url or "in/" in current_url:
            print("✅ Login confirmado! Continuando...")
            return True
        else:
            print("⚠️  Não foi possível confirmar login automaticamente, mas continuando...")
            return True
            
    except Exception as e:
        print(f"⚠️  Erro durante login: {e}")
        return False

def deslogar_linkedin_seguro(driver):
    """Tenta deslogar do LinkedIn de forma segura"""
    if not verificar_sessao_ativa(driver):
        print("   ⚠️  Navegador já fechado, pulando logout")
        return
    
    try:
        print("   🔓 Tentando deslogar do LinkedIn...")
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(3)
        
        # Tenta encontrar e clicar no menu de perfil
        selectors_menu = [
            "button.global-nav__primary-link-me-menu-trigger",
            "button[data-test-global-nav-link='me']",
            "img.global-nav__me-photo"
        ]
        
        for selector in selectors_menu:
            try:
                menu = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                menu.click()
                time.sleep(2)
                break
            except:
                continue
        
        # Tenta encontrar e clicar em "Sair"
        selectors_sair = [
            "a[data-test-name='logout']",
            "a[href*='logout']",
            "button[data-test-name='logout']"
        ]
        
        for selector in selectors_sair:
            try:
                sair = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                sair.click()
                time.sleep(3)
                print("   ✅ Deslogado com sucesso!")
                return
            except:
                continue
                
        print("   ⚠️  Não foi possível encontrar botão de logout")
        
    except Exception as e:
        print(f"   ⚠️  Erro durante logout: {e}")

# ============================================================
# DOWNLOAD LINKEDIN COM SELENIUM
# ============================================================

def baixar_foto_linkedin_com_selenium(url_linkedin, nome_pessoa, driver):
    """Baixa foto do LinkedIn usando Selenium de forma robusta"""
    if not verificar_sessao_ativa(driver):
        print("    ❌ Sessão do navegador fechada")
        return False
        
    try:
        print(f"    🌐 Acessando perfil: {nome_pessoa}")
        
        # Acessa o perfil
        driver.get(url_linkedin)
        time.sleep(5)  # Aguarda carregamento
        
        # Rolagem para carregar elementos
        driver.execute_script("window.scrollTo(0, 300)")
        time.sleep(3)
        
        print("    🔍 Procurando foto de perfil...")
        
        # ESTRATÉGIA 1: Selectors principais
        selectors_principais = [
            "img.pv-top-card-profile-picture__image",
            "img.profile-photo-edit__preview",
            "div.profile-photo-edit__preview img",
            "button.profile-photo-edit__edit-btn img",
        ]
        
        for selector in selectors_principais:
            try:
                elemento = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                src = elemento.get_attribute('src')
                
                if src and src.startswith('http') and 'blank' not in src.lower():
                    print(f"    ✅ Encontrado com: {selector}")
                    nome_seguro = limpar_nome_arquivo(nome_pessoa.replace(' ', '_'))
                    nome_arquivo = f"fotos/{nome_seguro}_linkedin.jpg"
                    
                    # Tenta melhorar a qualidade
                    if 'media.licdn.com' in src:
                        src = src.split('?')[0] + '?size=800x800'
                    
                    return baixar_imagem_super_robusta(src, nome_arquivo)
            except TimeoutException:
                continue
        
        # ESTRATÉGIA 2: Background images
        print("    🔍 Procurando em background images...")
        selectors_background = [
            "div.profile-photo-edit__preview",
            "div.pv-top-card-profile-picture",
        ]
        
        for selector in selectors_background:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, selector)
                style = elemento.get_attribute('style')
                if style and 'background-image' in style:
                    inicio = style.find('url("') + 5
                    fim = style.find('")', inicio)
                    if inicio > 4 and fim > inicio:
                        src = style[inicio:fim]
                        nome_seguro = limpar_nome_arquivo(nome_pessoa.replace(' ', '_'))
                        nome_arquivo = f"fotos/{nome_seguro}_linkedin.jpg"
                        print(f"    ✅ Background image encontrada")
                        return baixar_imagem_super_robusta(src, nome_arquivo)
            except NoSuchElementException:
                continue
        
        print("    ❌ Nenhuma foto encontrada no LinkedIn")
        return False
        
    except Exception as e:
        print(f"    ❌ Erro no LinkedIn: {e}")
        return False

# ============================================================
# PROCESSAMENTO PRINCIPAL SUPER ROBUSTO
# ============================================================

def processar_csv_super_robusto():
    """Processa o CSV com máxima robustez"""
    
    # Cria pasta com verificação
    if not criar_pasta_segura('fotos'):
        return
    
    resultados = []
    driver = None
    
    try:
        # Lê o CSV
        with open('pessoas.csv', 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
        
        # Processa cabeçalho
        cabecalho = linhas[0].strip().split(',')
        print(f"📋 Cabeçalho: {cabecalho}")
        
        # Encontra colunas
        indice_nome = next((i for i, c in enumerate(cabecalho) if 'nome' in c.lower()), None)
        indice_linkedin = next((i for i, c in enumerate(cabecalho) if 'linkedin' in c.lower()), None)
        indice_github = next((i for i, c in enumerate(cabecalho) if 'github' in c.lower()), None)
        
        # Processa pessoas
        pessoas = []
        for linha in linhas[1:]:
            if not linha.strip():
                continue
                
            dados = linha.strip().split(',')
            nome = dados[indice_nome] if indice_nome is not None and len(dados) > indice_nome else ""
            linkedin = dados[indice_linkedin] if indice_linkedin is not None and len(dados) > indice_linkedin else ""
            github = dados[indice_github] if indice_github is not None and len(dados) > indice_github else ""
            
            if nome.strip():
                pessoas.append({
                    'nome': nome.strip(),
                    'linkedin': linkedin.strip(),
                    'github': github.strip()
                })
        
        if not pessoas:
            print("❌ Nenhuma pessoa encontrada no CSV")
            return
        
        print(f"👥 {len(pessoas)} pessoas para processar\n")
        
        # INICIALIZA SELENIUM APENAS SE PRECISAR DO LINKEDIN
        precisa_linkedin = any(p['linkedin'].startswith('http') for p in pessoas)
        
        if precisa_linkedin:
            driver = inicializar_selenium_robusto()
            if not driver:
                print("❌ Não foi possível inicializar Selenium. Pulando LinkedIn...")
                precisa_linkedin = False
            else:
                if not fazer_login_linkedin_robusto(driver):
                    print("❌ Problema no login. Pulando LinkedIn...")
                    precisa_linkedin = False
        
        # PROCESSAMENTO DE CADA PESSOA
        for i, pessoa in enumerate(pessoas, 1):
            nome = pessoa['nome']
            linkedin = pessoa['linkedin']
            github = pessoa['github']
            
            print(f"\n🔹 {i}/{len(pessoas)} - {nome}")
            print(f"   📧 LinkedIn: {'Sim' if linkedin.startswith('http') else 'Não'}")
            print(f"   💻 GitHub: {'Sim' if github.startswith('http') else 'Não'}")
            
            sucesso = False
            origem = "nenhum"
            
            # Tenta LinkedIn primeiro (se disponível)
            if not sucesso and precisa_linkedin and linkedin.startswith('http'):
                print("   🎯 Tentando LinkedIn...")
                if baixar_foto_linkedin_com_selenium(linkedin, nome, driver):
                    sucesso = True
                    origem = "linkedin"
                else:
                    print("   ❌ LinkedIn falhou")
            
            # Tenta GitHub (sempre disponível)
            if not sucesso and github.startswith('http'):
                print("   🔄 Tentando GitHub...")
                if baixar_foto_github_super(github, nome):
                    sucesso = True
                    origem = "github"
                else:
                    print("   ❌ GitHub falhou")
            
            # Resultado
            status = "✅" if sucesso else "❌"
            print(f"   {status} Resultado: {origem}")
            
            resultados.append({
                'nome': nome,
                'origem': origem,
                'sucesso': 'sim' if sucesso else 'nao'
            })
            
            # Pausa estratégica
            if i < len(pessoas):
                print("   ⏳ Aguardando 5 segundos...")
                time.sleep(5)
        
        # SALVA RESULTADOS
        try:
            with open('resultado.csv', 'w', newline='', encoding='utf-8') as arquivo:
                campos = ['nome', 'origem', 'sucesso']
                escritor = csv.DictWriter(arquivo, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(resultados)
            print(f"\n📊 Resultados salvos em: resultado.csv")
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
        
        # RESUMO FINAL
        total_sucesso = sum(1 for r in resultados if r['sucesso'] == 'sim')
        print(f"\n🎯 RESUMO FINAL: {total_sucesso}/{len(pessoas)} fotos baixadas")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        # LIMPEZA FINAL
        if driver and verificar_sessao_ativa(driver):
            print("\n🔓 Finalizando sessão...")
            deslogar_linkedin_seguro(driver)
            print("🔄 Fechando navegador...")
            driver.quit()

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("📸 DOWNLOAD DE FOTOS - VERSÃO SUPER ROBUSTA")
    print("=" * 70)
    print()
    
    # Verifica dependências
    try:
        from selenium import webdriver
        print("✅ Selenium disponível")
    except ImportError:
        print("❌ Selenium não instalado")
        print("   Execute: pip install selenium")
        exit(1)
    
    # Verifica arquivo
    if not os.path.exists('pessoas.csv'):
        print("❌ Arquivo 'pessoas.csv' não encontrado")
        print("   Crie um arquivo CSV com colunas: nome,linkedin,github")
        exit(1)
    
    # Executa
    processar_csv_super_robusto()
    
    print("\n✨ Processamento concluído!")