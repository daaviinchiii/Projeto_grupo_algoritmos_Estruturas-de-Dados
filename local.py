# local.py
import math

class Local:
    """Representa um local na rede viária municipal."""
    MAX_PALAVRAS_CHAVE = 6

    def __init__(self, designacao: str, freguesia: str, coords_gps: tuple[float, float],
                 palavras_chave: list[str] | None = None, url: str | None = None):
        if not designacao:
            raise ValueError("Designação não pode ser vazia.")
        if not freguesia:
            raise ValueError("Freguesia não pode ser vazia.")
        if not isinstance(coords_gps, tuple) or len(coords_gps) != 2 or \
           not all(isinstance(c, (int, float)) for c in coords_gps):
            raise ValueError("Coordenadas GPS devem ser uma tupla de dois números (latitude, longitude).")

        self.designacao = designacao
        self.freguesia = freguesia
        self.coords_gps = coords_gps # (latitude, longitude)
        self.url = url

        if palavras_chave is None:
            self.palavras_chave = set()
        else:
            if len(palavras_chave) > self.MAX_PALAVRAS_CHAVE:
                raise ValueError(f"Número máximo de palavras-chave é {self.MAX_PALAVRAS_CHAVE}.")
            # Usar set para garantir unicidade e facilitar pesquisa
            self.palavras_chave = set(pc.lower() for pc in palavras_chave if pc)

    def adicionar_palavra_chave(self, palavra: str):
        if len(self.palavras_chave) < self.MAX_PALAVRAS_CHAVE:
            if palavra and isinstance(palavra, str):
                self.palavras_chave.add(palavra.lower())
            else:
                print("Aviso: Palavra-chave inválida ignorada.")
        else:
            print(f"Aviso: Limite de {self.MAX_PALAVRAS_CHAVE} palavras-chave atingido.")

    def remover_palavra_chave(self, palavra: str):
        self.palavras_chave.discard(palavra.lower())

    def __str__(self):
        palavras = ', '.join(sorted(list(self.palavras_chave))) if self.palavras_chave else "Nenhuma"
        url_str = self.url if self.url else "Nenhum"
        return (f"Local: {self.designacao}\n"
                f"  Freguesia: {self.freguesia}\n"
                f"  Coordenadas GPS: {self.coords_gps}\n"
                f"  Palavras-chave: {palavras}\n"
                f"  URL: {url_str}")

    def __repr__(self):
        return f"Local(designacao='{self.designacao}')"

    def __lt__(self, other):
        # Para permitir ordenação por designação
        if isinstance(other, Local):
            return self.designacao.lower() < other.designacao.lower()
        return NotImplemented

    def __eq__(self, other):
         # Para permitir comparação por designação (útil em sets/dicts)
        if isinstance(other, Local):
            return self.designacao.lower() == other.designacao.lower()
        return NotImplemented

    def __hash__(self):
        # Necessário se usar Local como chave de dicionário ou em sets
        return hash(self.designacao.lower())

# --- Funções Auxiliares ---
def calcular_distancia_geografica(coords1: tuple[float, float], coords2: tuple[float, float]) -> float:
    """Calcula a distância Haversine entre duas coordenadas GPS em km."""
    R = 6371.0  # Raio da Terra em km

    lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
    lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distancia = R * c
    return distancia