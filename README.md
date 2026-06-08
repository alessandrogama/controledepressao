# Sistema de Monitoramento de Pacientes

[![Python Version](https://img.shields.io/badge/Python-3.11.9-blue?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite Version](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tkinter](https://img.shields.io/badge/UI-Tkinter-brightgreen)](https://docs.python.org/3/library/tkinter.html)
[![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-orange)](https://matplotlib.org/)

Um sistema desktop modular desenvolvido em Python para o cadastro de pacientes e monitoramento local de dados clínicos (medidas vitais de peso, pressão arterial, pulsação e temperatura). O projeto conta com armazenamento relacional local, geração dinâmica de gráficos de evolução clínica e tratamento estrito de integridade de dados.

---

### Projeto de Aprendizado Pessoal
Este repositório foi desenvolvido com o objetivo de consolidar conhecimentos práticos em Engenharia de Software com Python, abordando tópicos como o desenvolvimento de interfaces gráficas desktop nativas, manipulação de bancos de dados relacionais locais (SQLite), estruturação de arquitetura em camadas (Separation of Concerns) e visualização de dados temporais.

---

## Funcionalidades

*   **Cadastro Consolidado de Pacientes:** 
    *   Formulário de cadastro com máscaras em tempo real no teclado para CPF (`###.###.###-##`) e Data de Nascimento (`##/##/####`).
    *   Validação semântica e matemática de integridade (cálculo de dígitos verificadores de CPF, formato de e-mail por regex e data de nascimento em locais coerentes).
    *   Campo Cartão SUS configurado como opcional com conversão em background para valores nulos (`None`), evitando falhas de integridade únicas no banco de dados.
*   **Aferição e Registro Clínico:**
    *   Painel de medição vinculado a um paciente específico para lançamento de dados clínicos.
    *   Suporte a registro de pressão sistólica/diastólica individualizadas.
*   **Histórico de Evolução com Gráficos:**
    *   Exibição dos registros históricos em uma tabela estruturada (`Treeview`).
    *   Geração dinâmica de gráficos de tendência utilizando a biblioteca Matplotlib para acompanhar a variação do Peso e da Pressão Arterial (Sistólica/Diastólica) ao longo do tempo.
*   **Gerenciamento Automático de Banco de Dados:**
    *   Migrações automáticas em background. Se a base de dados relacional existir com regras antigas, o sistema realiza a transição estrutural de DDL sem perda de dados na inicialização do sistema.

---

## Tecnologias e Dependências

*   **Linguagem Principal:** Python 3.11.9
*   **Interface Gráfica (UI):** Tkinter (Tcl/Tk nativo)
*   **Banco de Dados:** SQLite (`sqlite3`)
*   **Visualização Gráfica:** Matplotlib
*   **Manipulação de Imagens:** Pillow (`PIL`)
*   **Conversão de Dados:** Pandas & Numpy

---

## Destaques de Arquitetura e Engenharia

1.  **Separação de Responsabilidades (SoC):** Toda a lógica DDL e DML de banco de dados foi extraída das janelas de interface e centralizada em `database.py`, facilitando manutenções e futuros testes automatizados.
2.  **Abordagem Orientada a Objetos (OO):** Interfaces secundárias foram encapsuladas em classes Tkinter que herdam ou instanciam janelas `Toplevel` nativas, rodando sob a mesma thread principal, economizando recursos de RAM e anulando conflitos de concorrência com o banco de dados.
3.  **Prevenção de Vazamento de Memória (Memory Leak):** A janela de gráficos de histórico gerencia ativamente a desalocação e limpeza (`fig.clear()`) das figuras geradas do Matplotlib no fechamento da janela (`WM_DELETE_WINDOW`).
4.  **Parsing Otimizado de Datas:** Conversão ágil de strings ISO de data evitando fallbacks lentos por captura de exceções repetidas.

---

## Instalação e Execução

### Pré-requisitos
*   Python 3.11 ou superior instalado.

### Passo a Passo

1.  **Clonar o Repositório:**
    ```bash
    git clone https://github.com/alessandrogama/controledepressao.git
    cd controledepressao
    ```

2.  **Criar e Ativar Ambiente Virtual:**
    *   **Windows (PowerShell):**
        ```powershell
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        ```
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Executar o Painel Principal (Dashboard):**
    ```bash
    python dashboard.py
    ```

---

## Estrutura do Projeto

*   `dashboard.py`: Ponto de entrada do sistema e painel principal de listagem de pacientes.
*   `database.py`: Interface de acesso e migração do banco de dados SQLite.
*   `cadastropaciente.py`: Janela de formulário, máscaras e validações de pacientes.
*   `medidor.py`: Tela de aferição e lançamento de dados clínicos.
*   `historicoPaciente.py`: Histórico textual e renderização gráfica de tendências.
*   `medidor.sqlite`: Arquivo físico de banco de dados relacional.
