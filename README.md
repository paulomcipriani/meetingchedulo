# Sistema de Escala

Este é um sistema para gerenciamento de escalas com interface gráfica, permitindo o cadastro de designações, pessoas e datas especiais, além da geração automática de escalas em PDF.

## Funcionalidades

- Cadastro de designações (cargos/funções)
- Cadastro de pessoas e suas designações
- Cadastro de datas especiais (eventos, feriados, etc.)
- Geração automática de escala em PDF
- Interface gráfica amigável
- Executável standalone (não requer Python instalado)

## Requisitos

Para desenvolvimento:
- Python 3.6 ou superior
- Bibliotecas Python listadas em requirements.txt

Para uso:
- Windows: Nenhum requisito adicional (usar o executável)
- Linux/Mac: Python 3.6 ou superior e bibliotecas necessárias

## Instalação

### Usuários Windows (Forma mais fácil)
1. Baixe o arquivo "Sistema de Escala.exe" da pasta dist
2. Execute o arquivo baixado
3. Pronto! O programa está instalado e pronto para uso

### Desenvolvedores (Para modificar o código)
1. Clone ou baixe este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Usando o Executável (Windows)
- Simplesmente clique duas vezes no arquivo "Sistema de Escala.exe"

### Usando o Código Fonte
Para iniciar o programa com interface gráfica:
```bash
python escala_gui.py
```

Para iniciar o programa em modo console:
```bash
python escala.py
```

## Criando o Executável

Se você fez modificações no código e precisa gerar um novo executável:

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o script de build:
```bash
python build_exe.py
```

3. O executável será criado na pasta `dist` com o nome "Sistema de Escala.exe"

## Interface Gráfica

A interface gráfica possui quatro abas principais:

1. **Designações**: Cadastro e gerenciamento de designações/cargos
2. **Pessoas**: Cadastro de pessoas e suas designações
3. **Datas Especiais**: Cadastro de eventos e datas especiais
4. **Gerar Escala**: Geração da escala em PDF

## Arquivos

- `escala_gui.py`: Interface gráfica do sistema
- `escala.py`: Lógica principal do sistema
- `dados.json`: Arquivo de dados (criado automaticamente)
- `build_exe.py`: Script para gerar o executável
- `Sistema de Escala.exe`: Executável do programa (após build) 