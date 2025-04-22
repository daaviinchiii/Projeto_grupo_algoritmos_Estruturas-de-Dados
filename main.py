from typing import Optional, Tuple, List, Dict # Adicionar esta linha
from rede_viaria import RedeViaria, Local, calcular_distancia_geografica
from rede_viaria import RedeViaria, Local, calcular_distancia_geografica

def obter_coordenadas() -> Optional[Tuple[float, float]]:
    while True:
        try:
            lat_str = input("  Latitude (-90 a 90): ")
            if not lat_str: return None
            lat = float(lat_str)
            if not -90 <= lat <= 90:
                raise ValueError("Latitude fora do intervalo.")

            lon_str = input("  Longitude (-180 a 180): ")
            if not lon_str: return None
            lon = float(lon_str)
            if not -180 <= lon <= 180:
                raise ValueError("Longitude fora do intervalo.")
            return (lat, lon)
        except ValueError as e:
            print(f"  Erro: Entrada inválida. {e}. Tente novamente ou deixe em branco para cancelar.")

def obter_palavras_chave() -> List[str]:
    """Auxiliar para obter palavras-chave do utilizador."""
    palavras = []
    print(f"  Insira até {Local.MAX_PALAVRAS_CHAVE} palavras-chave (uma por linha, enter vazio para terminar):")
    while len(palavras) < Local.MAX_PALAVRAS_CHAVE:
        palavra = input(f"  Palavra {len(palavras) + 1}: ").strip()
        if not palavra:
            break
        palavras.append(palavra)
    return palavras

def menu_gerir_rede(rede: RedeViaria):
    """Sub-menu para RF01."""
    while True:
        print("\n--- Gerir Rede Viária ---")
        print("1. Adicionar Local")
        print("2. Remover Local")
        print("3. Consultar Local")
        print("4. Listar Todos os Locais")
        print("5. Adicionar Troço")
        print("6. Remover Troço")
        print("7. Consultar Troço")
        print("8. Listar Todos os Troços")
        print("0. Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            print("\n-- Adicionar Novo Local --")
            designacao = input("Designação: ").strip()
            freguesia = input("Freguesia: ").strip()
            coords = obter_coordenadas()
            if not designacao or not freguesia or coords is None:
                print("Adição cancelada (dados obrigatórios em falta).")
                continue
            palavras = obter_palavras_chave()
            url = input("URL (opcional): ").strip() or None
            try:
                novo_local = Local(designacao, freguesia, coords, palavras, url)
                rede.adicionar_local(novo_local)
            except ValueError as e:
                print(f"Erro ao criar local: {e}")

        elif opcao == '2':
            designacao = input("Designação do local a remover: ").strip()
            if designacao:
                rede.remover_local(designacao)
            else:
                print("Designação inválida.")

        elif opcao == '3':
            designacao = input("Designação do local a consultar: ").strip()
            if designacao:
                local = rede.consultar_local(designacao)
                if local:
                    print("\n-- Detalhes do Local --")
                    print(local)
            else:
                print("Designação inválida.")

        elif opcao == '4':
            print("\n-- Lista de Locais --")
            locais = rede.listar_todos_locais()
            if not locais:
                print("Nenhum local na rede.")
            else:
                # Ordena alfabeticamente para exibição consistente
                locais_ordenados = sorted(locais, key=lambda loc: loc.designacao.lower())
                for i, local in enumerate(locais_ordenados):
                    print(f"{i+1}. {local.designacao} ({local.freguesia})")

        elif opcao == '5':
            print("\n-- Adicionar Novo Troço --")
            desig1 = input("Designação do Local 1: ").strip()
            desig2 = input("Designação do Local 2: ").strip()
            try:
                dist_str = input("Distância (km): ")
                dist = float(dist_str)
                veic_str = input("Média diária de veículos: ")
                veic = int(veic_str)
                if dist < 0: raise ValueError("Distância não pode ser negativa.")
                if veic < 0: raise ValueError("Média de veículos não pode ser negativa.")

                if desig1 and desig2:
                     rede.adicionar_troco(desig1, desig2, dist, veic)
                else:
                    print("Designações inválidas.")
            except ValueError as e:
                print(f"Erro: Entrada inválida. {e}")

        elif opcao == '6':
            desig1 = input("Designação do Local 1 do troço: ").strip()
            desig2 = input("Designação do Local 2 do troço: ").strip()
            if desig1 and desig2:
                 rede.remover_troco(desig1, desig2)
            else:
                print("Designações inválidas.")

        elif opcao == '7':
            desig1 = input("Designação do Local 1 do troço: ").strip()
            desig2 = input("Designação do Local 2 do troço: ").strip()
            if desig1 and desig2:
                dados_troco = rede.consultar_troco(desig1, desig2)
                if dados_troco:
                    print("\n-- Detalhes do Troço --")
                    print(f"  Ligação: {desig1} <-> {desig2}")
                    print(f"  Distância: {dados_troco['distancia']:.2f} km")
                    print(f"  Média Veículos/Dia: {dados_troco['media_veiculos']}")
            else:
                print("Designações inválidas.")

        elif opcao == '8':
             print("\n-- Lista de Troços --")
             trocos = rede.listar_todos_trocos()
             if not trocos:
                 print("Nenhum troço na rede.")
             else:
                 # Ordena para exibição consistente
                 trocos_ordenados = sorted(trocos, key=lambda t: (t[0].lower(), t[1].lower()))
                 for i, (o, d, dados) in enumerate(trocos_ordenados):
                     print(f"{i+1}. {o} <-> {d} (Dist: {dados['distancia']:.2f} km, Veículos: {dados['media_veiculos']})")

        elif opcao == '0':
            break
        else:
            print("Opção inválida.")

def menu_pesquisar_locais(rede: RedeViaria):
    """Sub-menu para RF02."""
    print("\n--- Pesquisar Locais ---")
    designacao = input("Designação (deixe em branco para ignorar): ").strip() or None
    freguesia = input("Freguesia (deixe em branco para ignorar): ").strip() or None
    palavra_chave = input("Palavra-chave (deixe em branco para ignorar): ").strip() or None
    ponto_gps = None
    raio_km = 5.0 # Padrão

    usar_proximidade = input("Pesquisar por proximidade a um ponto GPS? (s/N): ").strip().lower()
    if usar_proximidade == 's':
        print("Insira as coordenadas do ponto de referência:")
        ponto_gps = obter_coordenadas()
        if ponto_gps:
            try:
                raio_str = input(f"Raio máximo de busca em km (padrão {raio_km}): ").strip()
                if raio_str:
                    raio_km = float(raio_str)
                    if raio_km < 0: raise ValueError("Raio não pode ser negativo.")
            except ValueError as e:
                 print(f"Raio inválido, usando padrão {raio_km} km. Erro: {e}")
                 raio_km = 5.0
        else:
            print("Coordenadas inválidas, pesquisa por proximidade ignorada.")

    if not designacao and not freguesia and not palavra_chave and not ponto_gps:
        print("Nenhum critério de pesquisa fornecido.")
        return

    resultados = rede.pesquisar_locais(designacao, freguesia, palavra_chave, ponto_gps, raio_km)

    print("\n-- Resultados da Pesquisa (Ordenados por Designação) --")
    if not resultados:
        print("Nenhum local encontrado com esses critérios.")
    else:
        for i, local in enumerate(resultados):
            # Formato de exibição customizável
            print(f"\n{i+1}. {local.designacao}")
            print(f"   Freguesia: {local.freguesia}")
            print(f"   Coords: {local.coords_gps}")
            if palavra_chave and palavra_chave.lower() in local.palavras_chave:
                 print(f"   *Contém palavra-chave '{palavra_chave}'")
            if ponto_gps:
                 dist = calcular_distancia_geografica(ponto_gps, local.coords_gps)
                 print(f"   *Distância ao ponto: {dist:.2f} km")

def menu_consultar_trocos(rede: RedeViaria):
    """Sub-menu para RF03."""
    print("\n--- Consultar Troços com Mais Circulação ---")
    trocos_ordenados = rede.consultar_trocos_mais_circulacao()

    if not trocos_ordenados:
        print("Nenhum troço encontrado na rede.")
    else:
        print("(Ordenado por média de veículos diários - decrescente)")
        for i, (loc1, loc2, veiculos) in enumerate(trocos_ordenados):
            # Consultar detalhes completos do troço para obter distância
            dados_troco = rede.consultar_troco(loc1, loc2)
            distancia = dados_troco['distancia'] if dados_troco else "N/A"
            print(f"{i+1}. {loc1} <-> {loc2}")
            print(f"   Média Veículos/Dia: {veiculos}")
            print(f"   Distância: {distancia:.2f} km" if isinstance(distancia, float) else f"   Distância: {distancia}")


def main():
    """Função principal da aplicação."""
    rede = RedeViaria()

    # Exemplo: Adicionar alguns dados iniciais (opcional)
    try:
        loc1 = Local("Câmara Municipal", "Sé", (41.1455, -8.6109), ["governo", "centro"], "http://cm-porto.pt")
        loc2 = Local("Estádio do Dragão", "Campanhã", (41.1618, -8.5839), ["futebol", "porto", "desporto"])
        loc3 = Local("Casa da Música", "Boavista", (41.1584, -8.6307), ["concerto", "cultura", "arquitetura"])
        loc4 = Local("Jardim Botânico", "Lordelo do Ouro", (41.1544, -8.6456), ["parque", "natureza", "plantas"])

        rede.adicionar_local(loc1)
        rede.adicionar_local(loc2)
        rede.adicionar_local(loc3)
        rede.adicionar_local(loc4)

        rede.adicionar_troco("Câmara Municipal", "Casa da Música", 2.5, 15000)
        rede.adicionar_troco("Câmara Municipal", "Estádio do Dragão", 4.0, 20000)
        rede.adicionar_troco("Casa da Música", "Jardim Botânico", 1.8, 8000)
        rede.adicionar_troco("Estádio do Dragão", "Casa da Música", 5.1, 12000) # Maior que geo-dist

    except ValueError as e:
        print(f"Erro ao inicializar dados de exemplo: {e}")
    except Exception as e:
         print(f"Erro inesperado na inicialização: {e}")


    while True:
        print("\n===== Simulador de Rede Viária Municipal =====")
        print("1. Gerir Rede Viária (RF01)")
        print("2. Pesquisar Locais (RF02)")
        print("3. Consultar Troços por Circulação (RF03)")
        print("0. Sair")
        print("============================================")

        opcao_principal = input("Escolha uma opção: ")

        if opcao_principal == '1':
            menu_gerir_rede(rede)
        elif opcao_principal == '2':
            menu_pesquisar_locais(rede)
        elif opcao_principal == '3':
            menu_consultar_trocos(rede)
        elif opcao_principal == '0':
            print("A sair da aplicação. Até breve!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()