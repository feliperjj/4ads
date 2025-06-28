# SGE - Sistema de Gerenciamento de Estoque

Um sistema de gerenciamento de estoque (SGE) desktop robusto e intuitivo, desenvolvido em Python utilizando Tkinter para a interface gráfica e SQLite para o gerenciamento de dados. O objetivo principal do SGE é otimizar o controle de inventário, produtos, fornecedores e movimentações, oferecendo uma visão clara e organizada do seu estoque.

## Funcionalidades Chave

O SGE foi projetado com as seguintes capacidades para atender às necessidades de controle de estoque:

* **Gestão Completa de Produtos:**
    * **CRUD de Produtos:** Adicione, edite, visualize e exclua informações de produtos facilmente.
    * **Detalhamento do Produto:** Cada produto possui código, nome, preço de custo, preço de venda, quantidade em estoque e uma quantidade mínima para alerta.
    * **Alertas de Estoque Baixo:** Receba notificações visuais automáticas quando a quantidade de um produto atingir ou ficar abaixo do seu limite mínimo.
    * **Pesquisa Rápida:** Encontre produtos rapidamente através de uma barra de pesquisa global na tela principal, filtrando por nome ou código.
    * **Ordenação de Produtos:** Organize a visualização da sua lista de produtos clicando nos cabeçalhos das colunas (ID, Código, Nome, Quantidade, etc.) para ordenar de forma ascendente ou descendente.

* **Controle Abrangente de Movimentações:**
    * **Registro Flexível:** Registre entradas, saídas, devoluções (de cliente ou para fornecedor) e ajustes de estoque.
    * **Histórico Detalhado:** Acesse um histórico completo de todas as movimentações, incluindo tipo, quantidade, data/hora, observações, o fornecedor envolvido (para entradas e devoluções a fornecedor) e o usuário responsável.
    * **Filtros Avançados no Histórico:** Filtre o histórico por produto, tipo de movimentação e um intervalo de datas específico para análises precisas.

* **Gerenciamento Eficiente de Fornecedores:**
    * **Cadastro Completo:** Mantenha um registro detalhado de seus fornecedores, incluindo nome, contato, endereço, CNPJ e email.
    * **CRUD de Fornecedores:** Adicione, edite e exclua informações de fornecedores conforme necessário.
    * **Histórico de Compras por Fornecedor:** Visualize um histórico específico de movimentações de entrada e devolução de fornecedor associadas a cada fornecedor.
    * **Busca de Fornecedores:** Localize fornecedores rapidamente através de um campo de busca integrado na tela de gerenciamento.

* **Relatórios e Análises de Vendas:**
    * **Produtos Mais Vendidos:** Identifique quais produtos têm maior saída em um determinado período.
    * **Vendas por Período:** Obtenha uma lista detalhada de todas as vendas (saídas) dentro de um intervalo de datas, com informações de produto, quantidade e valor total da venda.
    * **Valor Total de Vendas:** Calcule o faturamento bruto das vendas para o período selecionado.

* **Segurança e Rastreabilidade:**
    * **Sistema de Login:** Acesso protegido por autenticação de usuário.
    * **Níveis de Permissão:** Controle o acesso a funcionalidades específicas com base em perfis de usuário (administrador e operador).
    * **Gerenciamento de Usuários:** Administradores podem adicionar, editar e remover usuários do sistema.
    * **Auditoria de Ações:** Todas as operações críticas são registradas, fornecendo um histórico completo de quem fez o quê e quando, crucial para a segurança e conformidade.
    * **Visualização de Auditoria:** Administradores podem consultar o histórico detalhado de todas as ações no sistema.

* **Personalização da Interface (UI/UX):**
    * **Temas Visuais:** Escolha entre diferentes temas de interface para personalizar a aparência do sistema de acordo com sua preferência.
    * **Exportação de Dados:** Exporte listas de produtos e históricos de movimentações para arquivos CSV, facilitando a integração com outras ferramentas ou para fins de backup.

## Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **Tkinter:** Biblioteca padrão do Python para desenvolvimento de interfaces gráficas.
* **SQLite:** Banco de dados leve e embarcado para armazenamento de dados.

## Como Rodar o Projeto

Siga os passos abaixo para configurar e executar o SGE em sua máquina local:

1.  **Pré-requisitos:**
    * Certifique-se de ter o **Python 3.x** instalado. Você pode baixá-lo em [python.org](https://www.python.org/).
    * As bibliotecas `tkinter` (geralmente já inclusa com a instalação padrão do Python) e `hashlib` (nativa do Python) são utilizadas.

2.  **Clone o Repositório:**
    Abra seu terminal ou prompt de comando e clone o projeto para sua máquina:
    ```bash
    git clone (https://github.com/feliperjj/4ads)
    cd NomeDoSeuRepositorio
    ```


3.  **Execute o Aplicativo:**
    Dentro do diretório clonado, execute o arquivo `main.py`:
    ```bash
    python main.py
    ```

    * **Primeira Execução:** Na primeira vez que você rodar o aplicativo, um arquivo de banco de dados chamado `estoque.db` será criado automaticamente no diretório raiz do projeto.
    * **Usuário Administrador Padrão:** Um usuário administrador padrão será configurado para facilitar o acesso inicial:
        * **Username:** `admin`
        * **Senha:** `admin`
        * **Atenção:** É **altamente recomendável** que você altere a senha do usuário `admin` imediatamente após o primeiro login por questões de segurança. Você pode fazer isso na tela "Gerenciar Usuários" (acessível pelo menu "Sistema" após o login).
