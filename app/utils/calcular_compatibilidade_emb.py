from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def calcular_compatibilidade_emb(requisitos, experiencia_completa, limiar_alto=0.6, limiar_baixo=0.3):
    """
    Avalia compatibilidade semântica entre requisitos e perfil do candidato.
    Retorna pontuação média e listas de requisitos mais e menos compatíveis.
    """

    requisitos_lista = [r.strip() for r in requisitos.split("\n") if r.strip()]
    emb_experiencia = model.encode(experiencia_completa, convert_to_tensor=True)

    resultados = []
    for requisito in requisitos_lista:
        emb_requisito = model.encode(requisito, convert_to_tensor=True)
        score = util.cos_sim(emb_requisito, emb_experiencia).item()
        resultados.append((requisito, score))

    # Pontuação média
    media_score = sum(score for _, score in resultados) / len(resultados) if resultados else 0
    compatibilidade = round(media_score * 100, 2)

    # Requisitos mais e menos compatíveis
    mais_compativeis = [r for r, s in resultados if s > limiar_alto]
    menos_compativeis = [r for r, s in resultados if s < limiar_baixo]

    return {
        "score": compatibilidade,
        "mais_compativeis": mais_compativeis,
        "menos_compativeis": menos_compativeis
    }