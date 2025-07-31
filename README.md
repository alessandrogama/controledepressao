# Sistema de Monitoramento de Pacientes

Sistema desktop em Python para cadastro e monitoramento de pacientes, com armazenamento local usando SQLite e interface gráfica feita com Tkinter. Permite registrar pacientes, cadastrar medidas vitais (peso, pressão arterial, pulsação, temperatura), e visualizar histórico e gráficos de evolução.

---

## Funcionalidades

- Cadastro de pacientes com dados pessoais (nome, data de nascimento, CPF, cartão SUS, telefone, email)
- Listagem de pacientes com atualização dinâmica
- Visualização do histórico de medidas por paciente em tabela e gráficos de evolução (peso, pressão sistólica e diastólica)
- Interface gráfica intuitiva feita com Tkinter e gráficos usando Matplotlib
- Armazenamento local de dados usando SQLite

---

## Estrutura do Projeto

- `dashboard.py`: Tela principal com listagem de pacientes e ações (medir, editar, histórico)
- `cadastropaciente.py`: Tela para cadastro de novos pacientes
- `medidor.py`: Tela para registrar medidas vitais para um paciente (abrir a partir do dashboard)
- `historicoPaciente.py`: Tela que mostra o histórico de medidas com gráficos para um paciente
- `medidor.sqlite`: Banco de dados SQLite com tabelas `paciente`, `endereco` e `medida`

---

## Dependências

- Python 3.11.9
- Tkinter 
- Matplotlib 
- SQLite3 
- Outras bibliotecas recomendadas:
  - pandas
  - Pillow

Instale as principais dependências via pip:

```bash
pip install matplotlib pandas pillow
