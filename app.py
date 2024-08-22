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

TIMEOUT = 15

# Função para salvar mensagens em um arquivo de log
def log_message(message):
    if not os.path.exists('output'):
        os.makedirs('output')
    with open('output/log.txt', 'a') as f:
        f.write(message + "\n")

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
        log_message("[Info] - O Instagram não exigiu a aceitação de cookies desta vez.")

    log_message("[Info] - Fazendo login...")
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
    WebDriverWait(bot, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers/')]"))).click()
    time.sleep(3.5)
    log_message(f"[Info] - Coletando os seguidores de {usuario}...")
    bot.get(f'https://www.instagram.com/{usuario}/followers/mutualFirst')
    time.sleep(3.5)
    log_message(f"[Info] - Acessando seguidores mútuos de {usuario}...")
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

    log_message(f"[Info] - Salvando seguidores de {usuario}...")
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
def view_network(G, selected_users=None, save_fig=False):
    centralidade = nx.degree_centrality(G)
    betweenness = centralidade_betweenness(G)
    closeness = centralidade_closeness(G)
    
    particao = community_louvain.best_partition(G)
    pos = nx.spring_layout(G, seed=42)
    comunidades = set(particao.values())
    cores = list(mcolors.CSS4_COLORS.values())[:len(comunidades)]
    mapa_cores = {com: cor for com, cor in zip(comunidades, cores)}
    tamanho_nos = [v * 5000 for v in centralidade.values()]
    
    plt.figure(figsize=(14, 14))
    
    # Desenhar as arestas primeiro para ficar em segundo plano
    nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
    
    # Desenhar os nós das comunidades (fundo)
    nx.draw_networkx_nodes(
        G, pos, node_color=[mapa_cores[particao[node]] for node in G.nodes()],
        node_size=tamanho_nos, alpha=0.9
    )
    
    # Destacar os nós selecionados
    if selected_users:
        selected_nodes = [node for node in G.nodes() if node in selected_users]
        nx.draw_networkx_nodes(
            G, pos, nodelist=selected_nodes, node_color='red',
            node_size=[tamanho_nos[G.nodes().index(node)] * 1.5 for node in selected_nodes],
            edgecolors='black', linewidths=2.5, alpha=1
        )
    
    # Desenhar os rótulos dos nós por último para sobrepor tudo
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')
    
    # Legenda para as comunidades
    for com in comunidades:
        plt.scatter([], [], color=mapa_cores[com], label=f'Comunidade {com + 1}')
    
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, loc='best')
    plt.title("Rede de Seguidores do Instagram", size=15)
    plt.axis('off')

    try:
        if save_fig:
            if not os.path.exists('output'):
                os.makedirs('output')
            plt.savefig('output/network_visualization.png')
            log_message("[Info] - Network visualization saved to 'output/network_visualization.png'")
        else:
            plt.show()
    except KeyboardInterrupt:
        log_message("[Info] - Visualization interrupted by the user.")
    
    return centralidade, betweenness, closeness, particao


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
        f.write("\nCoeficiente de clustering:\n")
        for node, coef in clustering.items():
            f.write(f"{node}: {coef:.4f}\n")
    
    log_message("[Info] - Análise descritiva salva em 'output/analise_descritiva.txt'")

# Função para calcular a centralidade de betweenness
def centralidade_betweenness(G):
    return nx.betweenness_centrality(G)

# Função para calcular a centralidade de closeness
def centralidade_closeness(G):
    return nx.closeness_centrality(G)

# # Função para plotar a distribuição de graus
# def plot_distribution(G):
#     degrees = [G.degree(n) for n in G.nodes()]
#     plt.figure(figsize=(10, 6))
#     plt.hist(degrees, bins=30, color='blue', alpha=0.7)
#     plt.title("Distribuição de Graus")
#     plt.xlabel("Grau")
#     plt.ylabel("Frequência")
#     plt.show()

# Função principal para visualização da rede
def view_network(G, save_fig=False):
    # Centralidade (Grau)
    centralidade = nx.degree_centrality(G)
    
    # Centralidade de Betweenness e Closeness
    betweenness = centralidade_betweenness(G)
    closeness = centralidade_closeness(G)
    
    # Detectando as comunidades
    particao = community_louvain.best_partition(G)
    
    # Ajuste de layout usando spring_layout para espaçar bem os nós
    pos = nx.spring_layout(G, seed=42, k=0.1, iterations=50)
    
    # Comunidades
    comunidades = set(particao.values())
    cores = list(mcolors.CSS4_COLORS.values())[:len(comunidades)]
    mapa_cores = {com: cor for com, cor in zip(comunidades, cores)}
    
    # Tamanho dos nós proporcional à centralidade de grau
    tamanho_nos = [v * 7000 for v in centralidade.values()]
    
    plt.figure(figsize=(16, 16))
    
    # Desenho das arestas
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', width=0.5)
    
    # Desenho dos nós (comunidades)
    nx.draw_networkx_nodes(
        G, pos, node_color=[mapa_cores[particao[node]] for node in G.nodes()],
        node_size=tamanho_nos, alpha=0.9
    )
    
    # Desenho dos rótulos dos nós
    nx.draw_networkx_labels(G, pos, font_size=9, font_color='black')
    
    # Legenda para as comunidades
    for com in comunidades:
        plt.scatter([], [], color=mapa_cores[com], label=f'Comunidade {com + 1}')
    
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, loc='best')
    plt.title("Rede de Seguidores do Instagram", size=15)
    plt.axis('off')
    
    try:
        if save_fig:
            if not os.path.exists('output'):
                os.makedirs('output')
            plt.savefig('output/network_visualization.png', dpi=300)
            log_message("[Info] - Network visualization saved to 'output/network_visualization.png'")
        else:
            plt.show()
    except KeyboardInterrupt:
        log_message("[Info] - Visualization interrupted by the user.")
    
    return centralidade, betweenness, closeness, particao

# Função principal
if __name__ == '__main__':
    TIMEOUT = 15
    usuarios = scrape()
    G = network(usuarios)
    centralidade, betweenness, closeness, particao = view_network(G, save_fig=True)
    analise_descritiva(G)
    
    # Exemplo de escrita de centralidade em log
    log_message("Centralidade de Grau dos usuários:")
    for usuario, cent in centralidade.items():
        log_message(f"{usuario}: {cent:.4f}")
    
    # Exemplo de escrita de betweenness em log
    log_message("Centralidade de Betweenness dos usuários:")
    for usuario, bet in betweenness.items():
        log_message(f"{usuario}: {bet:.4f}")
    
    # Exemplo de escrita de closeness em log
    log_message("Centralidade de Closeness dos usuários:")
    for usuario, close in closeness.items():
        log_message(f"{usuario}: {close:.4f}")


# Função principal
if __name__ == '__main__':
    TIMEOUT = 15
    usuarios = scrape()
    G = network(usuarios)
    centralidade, betweenness, closeness, particao = view_network(G, save_fig=True)  # Adicione save_fig=True para salvar a imagem
    # plot_distribution(G)
    analise_descritiva(G)
    
    # Exemplo de escrita de centralidade em log
    log_message("Centralidade de Grau dos usuários:")
    for usuario, cent in centralidade.items():
        log_message(f"{usuario}: {cent:.4f}")
    
    # Exemplo de escrita de betweenness em log
    log_message("Centralidade de Betweenness dos usuários:")
    for usuario, bet in betweenness.items():
        log_message(f"{usuario}: {bet:.4f}")
    
    # Exemplo de escrita de closeness em log
    log_message("Centralidade de Closeness dos usuários:")
    for usuario, close in closeness.items():
        log_message(f"{usuario}: {close:.4f}")
