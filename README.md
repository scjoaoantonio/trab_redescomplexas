# Instagram User Network Analysis

Este projeto utiliza dados de comentários de uma postagem do Instagram para construir e analisar uma rede de usuários mencionados. A rede é gerada com base em co-ocorrências de menções (@) nos comentários, permitindo a análise de centralidade, identificação de comunidades e visualização da estrutura da rede.

## Funcionalidades

- **Extração de Comentários**: Extrai todos os comentários de uma postagem específica no Instagram.
- **Identificação de Menções**: Identifica todos os usuários mencionados nos comentários.
- **Construção de Rede**: Cria uma rede de co-ocorrências onde os nós representam usuários e as arestas indicam menções conjuntas em comentários.
- **Análise de Centralidade**: Calcula a centralidade de intermediação (betweenness centrality) para identificar usuários influentes na rede.
- **Detecção de Comunidades**: Identifica comunidades de usuários com base em modularidade.
- **Visualização da Rede**: Gera um gráfico da rede de usuários.

## Requisitos

- Python 3.x
- Bibliotecas Python:
  - `instaloader`
  - `networkx`
  - `matplotlib`
  - `tqdm`
  - `re`

Para instalar as bibliotecas necessárias, você pode usar:

```bash
pip install instaloader networkx matplotlib tqdm
```

## Configuração

1. **Clonar o Repositório**:

   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Adicionar Credenciais do Instagram**:

   Crie um arquivo `login.py` no diretório raiz do projeto e adicione suas credenciais do Instagram:

   ```python
   USER = 'seu_usuario'
   PASSWORD = 'sua_senha'
   ```

   **Nota**: O arquivo `login.py` está adicionado ao `.gitignore` para evitar que suas credenciais sejam publicadas no GitHub.

3. **Executar o Script**:

   Execute o script principal para gerar a análise de rede:

   ```bash
   python main.py
   ```

   **Nota**: Certifique-se de alterar `POST_URL` no código para a URL da postagem do Instagram que você deseja analisar.

## Exemplo de Saída

- **Informações da Rede**: Número de nós, arestas e top 5 usuários por centralidade.
- **Comunidades**: Lista de comunidades identificadas.
- **Visualização**: Gráfico da rede mostrando as conexões entre os usuários.