# rede_viaria.py
from local import Local, calcular_distancia_geografica
from typing import Optional, List, Tuple, Dict

# --- Algoritmos de Ordenação ---

def insertion_sort_locais(lista_locais: List[Local]) -> List[Local]:
    """Ordena uma lista de Locais por designação (alfabética) usando Insertion Sort.
       Complexidade: O(N^2) pior caso, O(N) melhor caso.
    """
    locais_ordenados = list(lista_locais) # Cria cópia para não modificar original
    for i in range(1, len(locais_ordenados)):
        chave = locais_ordenados[i]
        j = i - 1
        # Compara designações ignorando maiúsculas/minúsculas
        while j >= 0 and chave.designacao.lower() < locais_ordenados[j].designacao.lower():
            locais_ordenados[j + 1] = locais_ordenados[j]
            j -= 1
        locais_ordenados[j + 1] = chave
    return locais_ordenados

def merge_sort_trocos(lista_trocos: List[Tuple[str, str, int]], descending=True) -> List[Tuple[str, str, int]]:
    """Ordena uma lista de troços (loc1, loc2, veiculos) por número de veículos
       usando Merge Sort.
       Complexidade: O(N log N).
    """
    if len(lista_trocos) <= 1:
        return lista_trocos

    meio = len(lista_trocos) // 2
    esquerda = merge_sort_trocos(lista_trocos[:meio], descending)
    direita = merge_sort_trocos(lista_trocos[meio:], descending)

    return merge_trocos(esquerda, direita, descending)

def merge_trocos(esquerda: List[Tuple[str, str, int]], direita: List[Tuple[str, str, int]], descending=True) -> List[Tuple[str, str, int]]:
    """Função auxiliar para o Merge Sort."""
    resultado = []
    idx_esquerda, idx_direita = 0, 0

    while idx_esquerda < len(esquerda) and idx_direita < len(direita):
        # Comparação baseada no número de veículos (índice 2 da tupla)
        comparacao = esquerda[idx_esquerda][2] > direita[idx_direita][2] if descending else esquerda[idx_esquerda][2] < direita[idx_direita][2]
        if comparacao:
            resultado.append(esquerda[idx_esquerda])
            idx_esquerda += 1
        else:
            resultado.append(direita[idx_direita])
            idx_direita += 1

    resultado.extend(esquerda[idx_esquerda:])
    resultado.extend(direita[idx_direita:])
    return resultado


# --- Classe Principal ---

class RedeViaria:
    """Gere a rede viária municipal como um grafo."""

    def __init__(self):
        # Dicionário para acesso rápido aos objetos Local pela designação
        self.locais: Dict[str, Local] = {}
        # Lista de Adjacência: {designacao_origem: {designacao_destino: {'distancia': float, 'media_veiculos': int}}}
        self.adj: Dict[str, Dict[str, Dict]] = {}

    # --- RF01: Gerir Rede ---

    def adicionar_local(self, local: Local) -> bool:
        """Adiciona um novo local à rede."""
        if local.designacao in self.locais:
            print(f"Erro: Local com designação '{local.designacao}' já existe.")
            return False
        self.locais[local.designacao] = local
        self.adj[local.designacao] = {} # Adiciona entrada na lista de adjacência
        print(f"Local '{local.designacao}' adicionado com sucesso.")
        return True

    def remover_local(self, designacao: str) -> bool:
        """Remove um local e todos os troços ligados a ele."""
        if designacao not in self.locais:
            print(f"Erro: Local '{designacao}' não encontrado.")
            return False

        # Remover troços que ligam a este local a partir de outros locais
        vizinhos_a_remover = list(self.adj.get(designacao, {}).keys()) # Cópia das chaves
        for vizinho in vizinhos_a_remover:
            if vizinho in self.adj and designacao in self.adj[vizinho]:
                del self.adj[vizinho][designacao]

        # Remover o local da lista de adjacência e do dicionário de locais
        if designacao in self.adj:
            del self.adj[designacao]
        del self.locais[designacao]

        print(f"Local '{designacao}' e troços associados removidos com sucesso.")
        return True

    def consultar_local(self, designacao: str) -> Optional[Local]:
        """Consulta os detalhes de um local pela designação."""
        local = self.locais.get(designacao)
        if not local:
            print(f"Local '{designacao}' não encontrado.")
        return local

    def listar_todos_locais(self) -> List[Local]:
        """Retorna uma lista de todos os locais na rede."""
        return list(self.locais.values())

    def adicionar_troco(self, desig1: str, desig2: str, distancia: float, media_veiculos: int) -> bool:
        """Adiciona um troço (ligação) entre dois locais."""
        if desig1 not in self.locais or desig2 not in self.locais:
            print("Erro: Um ou ambos os locais não existem na rede.")
            return False
        if desig1 == desig2:
            print("Erro: Não pode adicionar um troço de um local para ele mesmo.")
            return False
        if media_veiculos < 0:
             print("Erro: Média de veículos não pode ser negativa.")
             return False

        local1 = self.locais[desig1]
        local2 = self.locais[desig2]
        distancia_geo = calcular_distancia_geografica(local1.coords_gps, local2.coords_gps)

        if distancia < distancia_geo:
            print(f"Erro: Distância do troço ({distancia:.2f} km) não pode ser inferior "
                  f"à distância geográfica ({distancia_geo:.2f} km).")
            return False

        # Adiciona ligação nos dois sentidos (grafo não direcionado)
        dados_troco = {'distancia': distancia, 'media_veiculos': media_veiculos}
        self.adj.setdefault(desig1, {})[desig2] = dados_troco
        self.adj.setdefault(desig2, {})[desig1] = dados_troco

        print(f"Troço entre '{desig1}' e '{desig2}' adicionado/atualizado com sucesso.")
        return True

    def remover_troco(self, desig1: str, desig2: str) -> bool:
        """Remove um troço entre dois locais."""
        removido = False
        if desig1 in self.adj and desig2 in self.adj[desig1]:
            del self.adj[desig1][desig2]
            removido = True
        if desig2 in self.adj and desig1 in self.adj[desig2]:
            del self.adj[desig2][desig1]
            removido = True

        if removido:
            print(f"Troço entre '{desig1}' e '{desig2}' removido com sucesso.")
            return True
        else:
            print(f"Erro: Troço entre '{desig1}' e '{desig2}' não encontrado.")
            return False

    def consultar_troco(self, desig1: str, desig2: str) -> Optional[Dict]:
        """Consulta os detalhes de um troço entre dois locais."""
        if desig1 in self.adj and desig2 in self.adj[desig1]:
            return self.adj[desig1][desig2]
        elif desig2 in self.adj and desig1 in self.adj[desig2]:
             return self.adj[desig2][desig1] # Grafo não direcionado
        else:
            print(f"Troço entre '{desig1}' e '{desig2}' não encontrado.")
            return None

    def listar_todos_trocos(self) -> List[Tuple[str, str, Dict]]:
        """Retorna uma lista de todos os troços únicos na rede."""
        trocos = []
        visitados = set() # Para evitar duplicados (A->B e B->A)
        for origem, vizinhos in self.adj.items():
            for destino, dados in vizinhos.items():
                # Adiciona apenas uma vez (ex: A-B e não B-A também)
                par = tuple(sorted((origem, destino)))
                if par not in visitados:
                    trocos.append((origem, destino, dados))
                    visitados.add(par)
        return trocos

    # --- RF02: Pesquisar Locais ---

    def pesquisar_locais(self, designacao: Optional[str] = None,
                         freguesia: Optional[str] = None,
                         palavra_chave: Optional[str] = None,
                         ponto_gps: Optional[Tuple[float, float]] = None,
                         raio_km: float = 5.0) -> List[Local]:
        """Pesquisa locais por múltiplos critérios."""
        resultados = list(self.locais.values()) # Começa com todos

        if designacao:
            resultados = [loc for loc in resultados if designacao.lower() in loc.designacao.lower()]
        if freguesia:
            resultados = [loc for loc in resultados if freguesia.lower() == loc.freguesia.lower()]
        if palavra_chave:
            resultados = [loc for loc in resultados if palavra_chave.lower() in loc.palavras_chave]
        if ponto_gps:
            try:
                resultados = [loc for loc in resultados
                              if calcular_distancia_geografica(ponto_gps, loc.coords_gps) <= raio_km]
            except Exception as e:
                print(f"Erro ao calcular proximidade: {e}")
                # Pode retornar lista vazia ou a filtrada até agora
                return []

        # Ordenar resultados por designação usando Insertion Sort (O(N) melhor caso)
        resultados_ordenados = insertion_sort_locais(resultados)

        return resultados_ordenados

    # --- RF03: Consultar Troços por Circulação ---

    def consultar_trocos_mais_circulacao(self) -> List[Tuple[str, str, int]]:
        """Consulta os troços ordenados por maior circulação de veículos."""
        trocos_unicos_com_veiculos = []
        visitados = set()
        for origem, vizinhos in self.adj.items():
            for destino, dados in vizinhos.items():
                par = tuple(sorted((origem, destino)))
                if par not in visitados:
                    trocos_unicos_com_veiculos.append((origem, destino, dados['media_veiculos']))
                    visitados.add(par)

        # Ordenar por 'media_veiculos' decrescente usando Merge Sort (O(N log N))
        trocos_ordenados = merge_sort_trocos(trocos_unicos_com_veiculos, descending=True)

        return trocos_ordenados