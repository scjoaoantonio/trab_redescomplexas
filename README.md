# Redes Complexas - Análise de redes no Instagram

Este projeto é uma ferramenta automatizada para coletar seguidores de perfis do Instagram e criar uma rede visual dos relacionamentos entre esses perfis. Ele permite analisar centralidade e detecção de comunidades dentro da rede de seguidores utilizando técnicas de redes complexas.

## Funcionalidades

1. **Raspagem de Seguidores do Instagram**: Coleta os seguidores de uma lista de perfis do Instagram.
2. **Construção de Redes**: Cria uma rede dos seguidores coletados, onde os nós representam usuários e as arestas representam relações de seguimento.
3. **Análise de Redes**: Calcula a centralidade de grau e detecta comunidades dentro da rede.
4. **Visualização de Redes**: Gera uma visualização gráfica da rede de seguidores.

## Requisitos

- **Python 3.6+**
- **Google Chrome**
- **Bibliotecas Python**:
  - `selenium`
  - `networkx`
  - `community` (Louvain)
  - `matplotlib`
  - `webdriver_manager`

## Instalação

1. **Clone este repositório**:
   ```bash
   git clone https://github.com/scjoaoantonio/trab_redescomplexas.git
   cd trab_redescomplexas
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

   *Obs: Certifique-se de ter o Google Chrome instalado e atualizado.*

## Uso

1. **Executando o Script**:
   Execute o script principal `app.py`:
   ```bash
   python app.py
   ```

2. **Login no Instagram**:
   O script solicitará que você insira seu nome de usuário e senha do Instagram. Essas credenciais serão salvas em um arquivo `login.txt` para uso futuro.

3. **Coleta de Seguidores**:
   Você será solicitado a inserir os nomes de usuários (@s) dos perfis do Instagram dos quais deseja coletar seguidores, separados por vírgulas. Além disso, deve especificar o número de seguidores a coletar (recomendado entre 100 e 2000).

4. **Construção e Análise da Rede**:
   Após a coleta, o script construirá uma rede a partir dos dados coletados e realizará a análise, incluindo o cálculo da centralidade de grau e a detecção de comunidades.

5. **Visualização da Rede**:
   Uma visualização gráfica da rede será exibida, mostrando as conexões entre os seguidores e os perfis coletados.

## Exemplos de Uso

- **Análise de Influenciadores**: Coletar dados de seguidores de influenciadores no Instagram para entender suas comunidades.
- **Marketing Digital**: Visualizar e analisar as redes de seguidores para identificar nichos e comunidades específicas.
- **Pesquisa Acadêmica**: Estudar a topologia das redes sociais e a dinâmica de comunidades em plataformas online.

## Considerações de Privacidade

Este script armazena as credenciais de login em um arquivo de texto simples (`login.txt`). Certifique-se de manter este arquivo seguro e evite compartilhá-lo.

## Problemas Conhecidos

- **Limites do Instagram**: O Instagram pode impor restrições temporárias se muitas solicitações forem feitas em um curto período de tempo. Use este script de forma responsável.

- **Mudanças na Interface do Instagram**: Se o Instagram alterar sua interface, as seleções de elementos podem falhar. Nesses casos, ajustes no código serão necessários.
