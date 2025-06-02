# Sistema de Escalas

Este é um sistema modular para gerenciamento de diferentes tipos de escalas com interface gráfica.

## Módulos Disponíveis

1. **Escala de Serviço e Fim de Semana**
   - Cadastro de designações (cargos/funções)
   - Cadastro de pessoas e suas designações
   - Cadastro de datas especiais (assembleias, congressos, etc.)
   - Edição das pessoas cadastradas e suas designações
   - Geração automática de escala em PDF
   - Interface gráfica amigável

2. **Escala TPL** (Em desenvolvimento)
   - Em breve...

3. **Escala Meio de Semana** (Em desenvolvimento)
   - Em breve...

## Requisitos

Para desenvolvimento:
- Python 3.6 ou superior
- Bibliotecas Python listadas em requirements.txt

Para uso:
- Windows: Nenhum requisito adicional (usar o executável)
- Linux/Mac: Python 3.6 ou superior e bibliotecas necessárias

## Instalação

### Usuários Windows (Forma mais fácil)
1. Faça o download o instalador em: 
2. Execute o arquivo baixado e instale em sua máquina
3. Pronto! O programa está instalado e pronto para uso

### Desenvolvedores (Para modificar o código)
1. Clone ou baixe este repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

### Usando o Código Fonte
Para iniciar o programa:
```bash
python modulo_selector.py
```

## Criando o Executável

Se você fez modificações no código e precisa gerar um novo executável ou recém baixou o código do git e quer gerar um executável:

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o script de build:
```bash
python build_exe.py build
```

3. O executável será criado na pasta `dist` com o nome "Sistema de Escalas.exe", dentro da pasta do sistema.

## Interface Gráfica

O sistema possui uma tela inicial de seleção de módulos, onde você pode escolher qual tipo de escala deseja gerenciar.

### Módulo de Escala de Serviço e Fim de Semana

Este módulo possui três abas principais:

1. **Designações**: Cadastro e gerenciamento de designações/cargos
2. **Pessoas**: Cadastro de pessoas e suas designações
3. **Datas Especiais**: Cadastro de eventos e datas especiais

## Arquivos

- `modulo_selector.py`: Tela inicial de seleção de módulos
- `escala_servico_gui.py`: Interface gráfica do módulo de escala de serviço
- `escala_servico.py`: Lógica principal do módulo de escala de serviço
- `dados_servico.json`: Arquivo de dados para escala de serviço e designações de fim de semana (criado automaticamente)
- `build_exe.py`: Script para gerar o executável
- `Sistema de Escalas.exe`: Executável do programa (após build) 