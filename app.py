import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import networkx as nx
import community as community_louvain
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM

# Função para salvar login
def salvar_login(usuario, senha):
    if not os.path.exists('input'):
        os.makedirs('input')
    with open('input/login.txt', 'w') as arquivo:
        arquivo.write(f"{usuario}\n{senha}")

# Função para carregar login
def load_login():
    if not os.path.exists('input/login.txt'):
        return None

    with open('input/login.txt', 'r') as arquivo:
        linhas = arquivo.readlines()
        if len(linhas) >= 2:
            return linhas[0].strip(), linhas[1].strip()

    return None

# Função para digitar login
def input_login():
    user = input("Digite seu nome de usuário do Instagram: ")
    senha = input("Digite sua senha do Instagram: ")
    salvar_login(user, senha)
    return user, senha

# Função de login no Instagram
def login_instagram(bot, usuario, senha):
    bot.get('https://www.instagram.com/accounts/login/')
    time.sleep(1)

    # Verifica se é necessário aceitar cookies
    try:
        elemento = bot.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        elemento.click()
    except NoSuchElementException:
        print("[Info] - O Instagram não exigiu a aceitação de cookies desta vez.")

    print("[Info] - Fazendo login...")
    input_usuario = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    input_senha = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    input_usuario.clear()
    input_usuario.send_keys(usuario)
    input_senha.clear()
    input_senha.send_keys(senha)

    btn_login = WebDriverWait(bot, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    btn_login.click()
    time.sleep(10)

# Função para pegar os seguidores de um usuário
def scrape_seguidores(bot, usuario, qtd_usuarios):
    bot.get(f'https://www.instagram.com/{usuario}/')
    time.sleep(3.5)
    WebDriverWait(bot, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))).click()
    time.sleep(2)
    print(f"[Info] - Coletando os seguidores de {usuario}...")

    usuarios = set()

    while len(usuarios) < qtd_usuarios:
        seguidores = bot.find_elements(By.XPATH, "//a[contains(@href, '/')]")

        for i in seguidores:
            if i.get_attribute('href'):
                usuarios.add(i.get_attribute('href').split("/")[3])
            else:
                continue

        ActionChains(bot).send_keys(Keys.END).perform()
        time.sleep(1)

    usuarios = list(usuarios)[:qtd_usuarios]  # Limita o número de seguidores ao número desejado

    # Verifica se o diretório 'output' existe, e cria se não existir
    if not os.path.exists('output'):
        os.makedirs('output')

    print(f"[Info] - Salvando seguidores de {usuario}...")
    with open(f'output/{usuario}_seguidores.txt', 'a') as arquivo:
        arquivo.write('\n'.join(usuarios) + "\n")

def load_users(filename):
    with open(filename, 'r') as file:
        usuarios = file.readlines()
    # Remove espaços e quebras de linha de cada linha do arquivo
    usuarios = [usuario.strip() for usuario in usuarios]
    return usuarios

# Função principal de raspagem
def scrape():
    credenciais = load_login()

    if credenciais is None:
        usuario, senha = input_login()
    else:
        usuario, senha = credenciais

    qtd_usuarios = int(input('Quantos seguidores você quer coletar (100-2000 recomendado): '))

    # Carregando os usuários do arquivo txt
    usuarios = load_users('input/usuarios.txt')

    servico = Service()
    opcoes = webdriver.ChromeOptions()
    # opcoes.add_argument("--headless")
    opcoes.add_argument('--no-sandbox')
    opcoes.add_argument("--log-level=3")
    emulacao_mobile = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    opcoes.add_experimental_option("mobileEmulation", emulacao_mobile)

    bot = webdriver.Chrome(service=servico, options=opcoes)
    bot.set_page_load_timeout(15)  # Define o timeout de carregamento da página para 15 segundos

    login_instagram(bot, usuario, senha)

    for usuario in usuarios:
        scrape_seguidores(bot, usuario, qtd_usuarios)

    bot.quit()

    return [f'output/{usuario}_seguidores.txt' for usuario in usuarios]

# Função para construir a rede
def network(arquivos_usuarios):
    G = nx.Graph()

    for arquivo_usuario in arquivos_usuarios:
        with open(arquivo_usuario, 'r') as arquivo:
            seguidores = arquivo.read().splitlines()

        usuario = os.path.basename(arquivo_usuario).replace('_seguidores.txt', '')

        for seguidor in seguidores:
            G.add_edge(usuario, seguidor)

    return G

# Função para analisar e visualizar a rede
def view_network(G):
    # Centralidade de grau
    centralidade = nx.degree_centrality(G)
    
    # Detecção de comunidades
    particao = community_louvain.best_partition(G)
    
    # Posicionamento dos nós
    pos = nx.spring_layout(G, seed=42)  # Usar seed para layout consistente entre execuções
    
    # Cores para as comunidades
    comunidades = set(particao.values())
    cores = list(mcolors.CSS4_COLORS.values())[:len(comunidades)]
    mapa_cores = {com: cor for com, cor in zip(comunidades, cores)}
    
    # Tamanho dos nós baseado na centralidade
    tamanho_nos = [v * 5000 for v in centralidade.values()]  # Escala para o tamanho dos nós
    
    plt.figure(figsize=(14, 14))
    
    # Desenhar a rede com as configurações
    nx.draw_networkx_nodes(
        G, pos, node_color=[mapa_cores[particao[node]] for node in G.nodes()],
        node_size=tamanho_nos, alpha=0.9
    )
    
    # Desenhar as arestas
    nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
    
    # Desenhar os rótulos dos nós
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')
    
    # Legenda para as comunidades
    for com in comunidades:
        plt.scatter([], [], color=mapa_cores[com], label=f'Comunidade {com + 1}')
    
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, loc='best')
    
    # Título da visualização
    plt.title("Rede de Seguidores do Instagram", size=15)
    plt.axis('off')  # Desliga os eixos
    plt.show()

    return centralidade, particao

# Função para calcular e salvar análises descritivas
def analise_descritiva(G):
    # Número de nós e arestas
    n_nos = G.number_of_nodes()
    n_arestas = G.number_of_edges()
    densidade = nx.density(G)
    
    # Distribuição de graus
    distribuicao_graus = dict(nx.degree(G))
    
    # Coeficiente de clustering
    clustering = nx.clustering(G)
    
    # Salvando resultados
    if not os.path.exists('output'):
        os.makedirs('output')
    
    with open('output/analise_descritiva.txt', 'w') as f:
        f.write(f"Número de nós: {n_nos}\n")
        f.write(f"Número de arestas: {n_arestas}\n")
        f.write(f"Densidade da rede: {densidade:.4f}\n")
        f.write("Distribuição de graus:\n")
        for node, degree in distribuicao_graus.items():
            f.write(f"{node}: {degree}\n")
        f.write("Coeficiente de clustering:\n")
        for node, coeff in clustering.items():
            f.write(f"{node}: {coeff:.4f}\n")

# Função principal
if __name__ == '__main__':
    TIMEOUT = 15
    usuarios = scrape()
    
    # Construir a rede
    G = network(usuarios)
    
    # Analisar e visualizar a rede
    centralidade, particao = view_network(G)
    
    # Exemplo de impressão de centralidade
    print("Centralidade de Grau dos usuários:")
    for usuario, cent in centralidade.items():
        print(f"{usuario}: {cent:.4f}")
    
    # Realizar a análise descritiva e salvar os resultados
    analise_descritiva(G)
