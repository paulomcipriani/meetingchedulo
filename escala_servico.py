import random
from collections import defaultdict
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta

print("O arquivo será salvo em:", os.getcwd())

ARQUIVO_DADOS = 'dados_servico.json'
cargos = []
pessoas = {}
datas_especiais = {} 

def carregar_dados():
    global cargos, pessoas, datas_especiais
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            cargos = dados.get('designações', [])
            pessoas = dados.get('pessoas', {})
            datas_especiais = dados.get('datas_especiais', {})
    except FileNotFoundError:
        cargos = []
        pessoas = {}
        datas_especiais = {}
        salvar_dados()  # Criar arquivo inicial
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        cargos = []
        pessoas = {}
        datas_especiais = {}
        salvar_dados()  # Criar arquivo inicial

def salvar_dados():
    try:
        dados = {
            'designações': cargos,
            'pessoas': pessoas,
            'datas_especiais': datas_especiais
        }
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

def cadastrar_data_especial():
    while True:
        try:
            data_str = input("Digite a data do evento (DD/MM): ")
            ano_atual = datetime.now().year
            data_str_completa = f"{data_str}/{ano_atual}"
            data = datetime.strptime(data_str_completa, "%d/%m/%Y")
            
            data_key = data.strftime("%d/%m")
            
            evento = input("Digite a descrição do evento: ").strip()
            if evento:
                datas_especiais[data_key] = evento
                salvar_dados()
                print("Evento cadastrado com sucesso!")
                break
            else:
                print("A descrição do evento não pode estar vazia.")
        except ValueError:
            print("Data inválida. Use o formato DD/MM (exemplo: 20/06)")

def editar_data_especial():
    if not datas_especiais:
        print("Não há datas especiais cadastradas.")
        return
    
    print("\n--- DATAS ESPECIAIS CADASTRADAS ---")
    for data, evento in datas_especiais.items():
        print(f"{data}: {evento}")
    
    data_str = input("\nDigite a data que deseja editar (DD/MM): ").strip()
    if data_str in datas_especiais:
        novo_evento = input("Digite a nova descrição do evento: ").strip()
        if novo_evento:
            datas_especiais[data_str] = novo_evento
            salvar_dados()
            print("Evento atualizado com sucesso!")
        else:
            print("A descrição do evento não pode estar vazia.")
    else:
        print("Data não encontrada.")

def excluir_data_especial():
    if not datas_especiais:
        print("Não há datas especiais cadastradas.")
        return
    
    print("\n--- DATAS ESPECIAIS CADASTRADAS ---")
    for data, evento in datas_especiais.items():
        print(f"{data}: {evento}")
    
    data_str = input("\nDigite a data que deseja excluir (DD/MM): ").strip()
    if data_str in datas_especiais:
        confirmacao = input(f"Tem certeza que deseja excluir o evento de {data_str}? (s/n): ").lower()
        if confirmacao == 's':
            del datas_especiais[data_str]
            salvar_dados()
            print("Evento excluído com sucesso!")
    else:
        print("Data não encontrada.")

def listar_datas_especiais():
    if not datas_especiais:
        print("Não há datas especiais cadastradas.")
        return
    
    print("\n--- DATAS ESPECIAIS ---")
    for data, evento in sorted(datas_especiais.items()):
        print(f"{data}: {evento}")

def verificar_evento_especial(inicio, fim):
    """Verifica se há algum evento especial no intervalo de datas"""
    data_atual = inicio
    while data_atual <= fim:
        data_str = data_atual.strftime("%d/%m")
        if data_str in datas_especiais:
            return datas_especiais[data_str]
        data_atual += timedelta(days=1)
    return None

def menu():
    carregar_dados()
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Cadastrar designação")
        print("2. Cadastrar pessoa")
        print("3. Editar pessoa")
        print("4. Excluir designação")
        print("5. Excluir pessoa")
        print("6. Visualizar designações")
        print("7. Visualizar pessoas")
        print("8. Gerar escala")
        print("9. Cadastrar data especial")
        print("10. Editar data especial")
        print("11. Excluir data especial")
        print("12. Listar datas especiais")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            cadastrar_cargo()
        elif opcao == '2':
            cadastrar_pessoa()
        elif opcao == '3':
            editar_pessoa()
        elif opcao == '4':
            excluir_cargo()
        elif opcao == '5':
            excluir_pessoa()
        elif opcao == '6':
            listar_cargos()
        elif opcao == '7':
            listar_pessoas()
        elif opcao == '8':
            gerar_escala()
        elif opcao == '9':
            cadastrar_data_especial()
        elif opcao == '10':
            editar_data_especial()
        elif opcao == '11':
            excluir_data_especial()
        elif opcao == '12':
            listar_datas_especiais()
        elif opcao == '0':
            salvar_dados()
            break
        else:
            print("Opção inválida.")

def cadastrar_cargo():
    nome = input("Nome da designação: ").strip()
    if nome and nome not in cargos:
        cargos.append(nome)
        salvar_dados()
        print("Designação cadastrada.")
    else:
        print("Designação já existe ou inválida.")

def cadastrar_pessoa():
    if not cargos:
        print("Cadastre ao menos uma designação antes de adicionar pessoas.")
        return
    nome = input("Nome da pessoa: ").strip()
    if not nome:
        print("Nome inválido.")
        return
    print("Selecione as designações da pessoa (separadas por vírgula):")
    for i, cargo in enumerate(cargos):
        print(f"{i + 1}. {cargo}")
    indices = input("Designações: ").split(',')
    selecionados = set()
    for idx in indices:
        try:
            selecionados.add(cargos[int(idx) - 1])
        except:
            pass
    if not selecionados:
        print("É necessário selecionar ao menos uma designação.")
        return
    pessoas[nome] = list(selecionados)
    salvar_dados()
    print("Pessoa cadastrada com sucesso.")

def editar_pessoa():
    nome = input("Nome da pessoa a editar: ").strip()
    if nome not in pessoas:
        print("Pessoa não encontrada.")
        return
    novo_nome = input("Novo nome (pressione Enter para manter o atual): ").strip()
    if novo_nome:
        pessoas[novo_nome] = pessoas.pop(nome)
        nome = novo_nome
    print("Cargos atuais:", pessoas[nome])
    print("Deseja atualizar as designações? (s/n)")
    if input().lower() == 's':
        print("Selecione os novos cargos:")
        for i, cargo in enumerate(cargos):
            print(f"{i + 1}. {cargo}")
        indices = input("Cargos: ").split(',')
        selecionados = set()
        for idx in indices:
            try:
                selecionados.add(cargos[int(idx) - 1])
            except:
                pass
        if selecionados:
            pessoas[nome] = list(selecionados)
        else:
            print("Nenhuma designação selecionada. Mantida as designações anteriores.")
    salvar_dados()

def excluir_cargo():
    nome = input("Nome da designação a excluir: ").strip()
    if nome in cargos:
        cargos.remove(nome)
        for p in list(pessoas):
            if nome in pessoas[p]:
                pessoas[p].remove(nome)
                if not pessoas[p]:
                    print(f"{p} ficou sem designação e será desconsiderado na escala.")
        salvar_dados()
        print("Designação excluída.")
    else:
        print("Designação não encontrada.")

def excluir_pessoa():
    nome = input("Nome da pessoa a excluir: ").strip()
    if nome in pessoas:
        del pessoas[nome]
        salvar_dados()
        print("Pessoa excluída com sucesso.")
    else:
        print("Pessoa não encontrada.")

def listar_cargos():
    print("\n--- DESIGNAÇÕES ---")
    for c in cargos:
        print("-", c)

def listar_pessoas():
    print("\n--- PESSOAS ---")
    for nome, lista_cargos in pessoas.items():
        status = "(SEM DESIGNAÇÃO!)" if not lista_cargos else ""
        print(f"{nome} - Designações: {', '.join(lista_cargos)} {status}")

def obter_data_inicial():
    while True:
        try:
            data_str = input("Digite a data inicial (DD/MM): ")
            ano_atual = datetime.now().year
            data_str_completa = f"{data_str}/{ano_atual}"
            data = datetime.strptime(data_str_completa, "%d/%m/%Y")
            return data
        except ValueError:
            print("Data inválida. Use o formato DD/MM (exemplo: 02/06)")

def gerar_intervalo_datas(data_inicial, num_semanas):
    intervalos = []
    for i in range(num_semanas):
        inicio = data_inicial + timedelta(days=i*7)
        fim = inicio + timedelta(days=6)
        intervalos.append((inicio, fim))
    return intervalos

def formatar_intervalo_data(inicio, fim):
    return f"{inicio.strftime('%d/%m')} a {fim.strftime('%d/%m')}"

def gerar_pdf_escala(escala, nome_arquivo='escala.pdf'):
    doc = SimpleDocTemplate(
        nome_arquivo,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=30
    )
    elementos = []
    
    # Definir cores personalizadas
    cor_borda = colors.HexColor('#999898')
    cor_cabecalho = colors.HexColor('#d9d9d9')
    cor_titulo = colors.HexColor('#4a6da7')
    cor_evento = colors.HexColor('#FFEB9C')  
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,  
        spaceAfter=0,
        textColor=colors.white,  
        leading=20
    )
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,  
        spaceAfter=0,
        textColor=colors.white,  
        leading=5
    )
    
    # Estilo para o cabeçalho da tabela
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=8.5,
        alignment=1,
        textColor=colors.black,
        leading=10
    )

    # Estilo para a coluna Semana
    week_style = ParagraphStyle(
        'WeekStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        textColor=colors.black,
        leading=12
    )
    
    # Criar título com fundo colorido
    titulo = Paragraph("<b>Congregação Coqueiros</b>", titulo_style)
    titulo_table = Table([[titulo]], colWidths=[doc.width])
    titulo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), cor_titulo),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(titulo_table)
    
    # Criar subtítulo com fundo colorido
    subtitulo = Paragraph("<b>Designações de serviço para as reuniões</b>", subtitulo_style)
    subtitulo_table = Table([[subtitulo]], colWidths=[doc.width])
    subtitulo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), cor_titulo),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elementos.append(subtitulo_table)
    elementos.append(Spacer(1, 5))
    
    # Preparar dados para a tabela
    dados_tabela = []
    # Cabeçalho
    cabecalho = [Paragraph("<b>Período</b>", header_style)] + [Paragraph(f"<b>{cargo}</b>", header_style) for cargo in cargos]
    dados_tabela.append(cabecalho)
    
    # Lista para armazenar as linhas que contêm eventos especiais
    linhas_eventos = []
    linha_atual = 1  
    
    for linha in escala:
        if 'evento_especial' in linha:
            # Linha de evento especial
            evento_style = ParagraphStyle(
                'EventoStyle',
                parent=styles['Normal'],
                fontSize=9,
                alignment=1,
                textColor=colors.black,
                leading=12
            )
            # Primeira coluna é o período, as demais serão mescladas
            dados = [
                Paragraph(f"<b>{linha['intervalo']}</b>", week_style),
                Paragraph(f"<b>{linha['evento_especial']}</b>", evento_style)
            ] + [''] * (len(cargos) - 1)
            dados_tabela.append(dados)
            # Guardar o índice desta linha para mesclar depois
            linhas_eventos.append(linha_atual)
        else:
            # Linha normal da escala
            dados = [Paragraph(f"<b>{linha['intervalo']}</b>", week_style)] + [linha.get(c, '-') for c in cargos]
            dados_tabela.append(dados)
        linha_atual += 1

    # Calcular larguras das colunas
    largura_disponivel = doc.width
    num_colunas = len(cabecalho)
    
    # Primeira coluna (Período) um pouco maior para acomodar as datas
    larguras_colunas = [largura_disponivel * 0.12]  # 12% para coluna Período
    largura_restante = largura_disponivel * 0.88
    largura_por_coluna = largura_restante / (num_colunas - 1)
    larguras_colunas.extend([largura_por_coluna] * (num_colunas - 1))
    
    # Criar tabela com larguras específicas e altura da primeira linha maior
    tabela = Table(dados_tabela, colWidths=larguras_colunas, rowHeights=[40] + [25] * (len(dados_tabela)-1))
    
    # Estilo da tabela
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), cor_cabecalho),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        # Ajustar padding do cabeçalho
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, 0), 2),
        ('RIGHTPADDING', (0, 0), (-1, 0), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        # Definir grade com nova cor e espessura
        ('GRID', (0, 0), (-1, -1), 0.5, cor_borda),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Ajustar padding das células de conteúdo
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('LEFTPADDING', (0, 1), (-1, -1), 2),
        ('RIGHTPADDING', (0, 1), (-1, -1), 2),
        # Permitir quebra de linha no cabeçalho
        ('WORDWRAP', (0, 0), (-1, 0), True),
        # Garantir que a primeira coluna (Semana) use a fonte em negrito
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        # Mudar a cor do texto do cabeçalho para preto
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ])

    # Adicionar mesclagem para as linhas com eventos especiais
    for linha in linhas_eventos:
        # Mesclar todas as células após a primeira coluna
        estilo.add('SPAN', (1, linha), (-1, linha))
        # Ajustar o alinhamento vertical para a célula mesclada
        estilo.add('VALIGN', (1, linha), (-1, linha), 'MIDDLE')
        # Adicionar cor de fundo amarela para toda a linha
        estilo.add('BACKGROUND', (0, linha), (-1, linha), cor_evento)
    
    tabela.setStyle(estilo)
    
    elementos.append(tabela)
    doc.build(elementos)
    print(f"\nEscala gerada com sucesso! Arquivo salvo como '{nome_arquivo}'")

def gerar_escala():
    if not cargos:
        print("Cadastre designações primeiro.")
        return

    validos = {p: c for p, c in pessoas.items() if c}
    if not validos:
        print("Nenhuma pessoa com designação válida cadastrada.")
        return

    # Obter data inicial
    data_inicial = obter_data_inicial()

    try:
        semanas = int(input("Quantas semanas deseja gerar? "))
        if semanas < 1:
            raise ValueError
    except:
        print("Valor inválido.")
        return

    # Gerar intervalos de datas
    intervalos = gerar_intervalo_datas(data_inicial, semanas)

    escala = []
    uso_pessoa = defaultdict(int)
    uso_pessoa_designacao = defaultdict(lambda: defaultdict(int))

    for inicio, fim in intervalos:
        # Verificar se há evento especial no período
        evento = verificar_evento_especial(inicio, fim)
        if evento:
            # Se houver evento especial, adicionar linha especial
            escala.append({
                'intervalo': formatar_intervalo_data(inicio, fim),
                'evento_especial': evento
            })
            continue

        # Se não houver evento especial, gerar escala normal
        alocados = set()
        linha = {'intervalo': formatar_intervalo_data(inicio, fim)}
        cargos_sorteio = cargos[:]
        random.shuffle(cargos_sorteio)

        for cargo in cargos_sorteio:
            candidatos = [p for p in validos if cargo in validos[p] and p not in alocados]
            if not candidatos:
                linha[cargo] = "-"
                continue
            candidatos.sort(key=lambda x: (uso_pessoa_designacao[x][cargo], uso_pessoa[x]))
            escolhido = candidatos[0]
            linha[cargo] = escolhido
            alocados.add(escolhido)
            uso_pessoa[escolhido] += 1
            uso_pessoa_designacao[escolhido][cargo] += 1

        escala.append(linha)

    gerar_pdf_escala(escala)

def gerar_escala_com_data(data_inicial, semanas, nome_arquivo='escala.pdf'):
    """Gera a escala a partir de uma data específica e número de semanas"""
    if not cargos:
        raise Exception("Cadastre designações primeiro.")

    validos = {p: c for p, c in pessoas.items() if c}
    if not validos:
        raise Exception("Nenhuma pessoa com designação válida cadastrada.")

    # Gerar intervalos de datas
    intervalos = gerar_intervalo_datas(data_inicial, semanas)

    escala = []
    uso_pessoa = defaultdict(int)
    uso_pessoa_designacao = defaultdict(lambda: defaultdict(int))

    for inicio, fim in intervalos:
        # Verificar se há evento especial no período
        evento = verificar_evento_especial(inicio, fim)
        if evento:
            # Se houver evento especial, adicionar linha especial
            escala.append({
                'intervalo': formatar_intervalo_data(inicio, fim),
                'evento_especial': evento
            })
            continue

        # Se não houver evento especial, gerar escala normal
        alocados = set()
        linha = {'intervalo': formatar_intervalo_data(inicio, fim)}
        cargos_sorteio = cargos[:]
        random.shuffle(cargos_sorteio)

        for cargo in cargos_sorteio:
            candidatos = [p for p in validos if cargo in validos[p] and p not in alocados]
            if not candidatos:
                linha[cargo] = "-"
                continue
            candidatos.sort(key=lambda x: (uso_pessoa_designacao[x][cargo], uso_pessoa[x]))
            escolhido = candidatos[0]
            linha[cargo] = escolhido
            alocados.add(escolhido)
            uso_pessoa[escolhido] += 1
            uso_pessoa_designacao[escolhido][cargo] += 1

        escala.append(linha)

    gerar_pdf_escala(escala, nome_arquivo)
    return nome_arquivo

if __name__ == '__main__':
    menu()
