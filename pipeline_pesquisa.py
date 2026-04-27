"""
pipeline_pesquisa.py — Versão Híbrida com camada temática popular
Ajuste cirúrgico para reabrir futebol, esportes, espetáculo, música,
periferias, artes, festas populares e lazer popular, sem voltar ao ruído amplo.
"""

import os
import csv
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
import unicodedata
import re
import hashlib
from email.utils import parsedate_to_datetime

import psycopg2
import requests
import spacy
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from configuracao_buscas import PORTAIS_CONFIG


def get_db_url() -> str:
    env_url = os.getenv("SUPABASE_DB_URL", "").strip()
    if env_url:
        return env_url
    raise RuntimeError("SUPABASE_DB_URL nao configurada no ambiente.")


DB_URL = get_db_url()

logging.basicConfig(
    filename="pipeline_decisoes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    nlp = spacy.load("pt_core_news_lg")
except Exception as e:
    raise RuntimeError(
        "Modelo spaCy nao encontrado. Execute: python -m spacy download pt_core_news_lg"
    ) from e

REPORTS_DIR = Path("relatorios_pipeline")
REPORTS_DIR.mkdir(exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

from regras_dicionarios import (
    TERMOS_ALVO_SPACY, BLACKLIST_EXATA, BLACKLIST_EDITORIAL, BLACKLIST_FRAGMENTOS,
    BLACKLIST_ESPORTIVA, BLACKLIST_ECONOMICA, BLACKLIST_CULTURAL, BLACKLIST_VIOLENCIA_GENERICA,
    GATILHOS_FORTES, GRUPOS_SOCIAIS, CONTEXTOS_SENSIVEIS, VERBOS_CONFLITO, EXPRESSOES_ESPECIFICAS,
    TEMAS_POPULARES, MARCADORES_SOCIAIS_POPULARES, TEMAS_POPULARES_SENSIVEIS, MARCADORES_POPULARES_ESTRITOS,
    CATEGORIAS_PUBLICAS, ENQUADRAMENTOS_DISCURSIVOS, FONTE_TIPO_REGRAS, REGIAO_FONTE_REGRAS,
    STOPWORDS_CASO
)
import unicodedata

def normalizar_texto(texto: str) -> str:
    """Converte o texto para minúsculas e remove acentos."""
    if not texto:
        return ""
    texto = str(texto).lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Cria vetores individuais para não diluir o sentido semântico (correção da falha do spaCy)
CONCEITOS_ALVO = [nlp(termo) for termo in TERMOS_ALVO_SPACY]

def contem_algum(texto: str, lista_termos) -> bool:
    """Verifica se algum dos termos da lista está contido no texto."""
    if not texto:
        return False
    return any(termo in texto for termo in lista_termos)


## Memória viva do pipeline para aprender com a curadoria humana
VETORES_FALSOS_POSITIVOS = []

def carregar_memoria_falsos_positivos(conn):
    global VETORES_FALSOS_POSITIVOS
    try:
        with conn.cursor() as cur:
            # Busca os últimos 400 lixos rejeitados para manter o pipeline rápido
            cur.execute("""
                SELECT titulo FROM noticias 
                WHERE falso_positivo = TRUE 
                ORDER BY data_coleta DESC LIMIT 400
            """)
            titulos_rejeitados = [row[0] for row in cur.fetchall() if row[0]]

        # Transforma os títulos em vetores para comparação rápida
        VETORES_FALSOS_POSITIVOS = [nlp(normalizar_texto(t)) for t in titulos_rejeitados if t]

        logging.info(f"🧠 Memória de Curadoria Carregada: {len(VETORES_FALSOS_POSITIVOS)} exemplos.")
        print(f"🧠 Pipeline aprendeu com {len(VETORES_FALSOS_POSITIVOS)} falsos positivos do painel.")

    except Exception as e:
        conn.rollback()  # <-- A SALVAÇÃO! Limpa o erro para não travar os portais
        VETORES_FALSOS_POSITIVOS = []
        logging.error(f"Erro ao carregar memória de falsos positivos: {e}")
        print(f"⚠️ Aviso: Não foi possível carregar a memória ({e}). O pipeline seguirá a recolha com as regras padrão.")

def calcular_similaridade_focada(texto: str) -> float:
    """Calcula a similaridade máxima entre o texto e os conceitos alvo individuais."""
    doc_texto = nlp(texto)
    if not doc_texto.has_vector:
        return 0.0

    similaridades = [doc_texto.similarity(conceito) for conceito in CONCEITOS_ALVO if conceito.has_vector]
    return max(similaridades) if similaridades else 0.0


def _texto_analitico(titulo: str = "", resumo: str = "", texto_completo: str = "") -> str:
    return normalizar_texto(f"{titulo or ''} {resumo or ''} {texto_completo or ''}")

def classificar_categoria_publica(titulo: str = "", resumo: str = "", texto_completo: str = "") -> str:
    texto = _texto_analitico(titulo, resumo, texto_completo)
    for categoria, termos in CATEGORIAS_PUBLICAS.items():
        if contem_algum(texto, [normalizar_texto(t) for t in termos]):
            return categoria
    return "Estigma, exclusao e conflitos sociais"

def classificar_eixos_analiticos(titulo: str = "", resumo: str = "", texto_completo: str = "") -> str:
    texto = _texto_analitico(titulo, resumo, texto_completo)
    eixos = [categoria for categoria, termos in CATEGORIAS_PUBLICAS.items() if contem_algum(texto, [normalizar_texto(t) for t in termos])]
    return "; ".join(dict.fromkeys(eixos or ["Estigma, exclusao e conflitos sociais"]))

def classificar_enquadramentos(titulo: str = "", resumo: str = "", texto_completo: str = "") -> str:
    texto = _texto_analitico(titulo, resumo, texto_completo)
    enquadramentos = [nome for nome, termos in ENQUADRAMENTOS_DISCURSIVOS.items() if contem_algum(texto, [normalizar_texto(t) for t in termos])]
    return "; ".join(dict.fromkeys(enquadramentos or ["Enquadramento indeterminado"]))

def inferir_tipo_fonte(nome_fonte: str) -> str:
    f = normalizar_texto(nome_fonte).replace(" ", "_")
    for tipo, marcadores in FONTE_TIPO_REGRAS.items():
        if any(normalizar_texto(m).replace(" ", "_") in f for m in marcadores):
            return tipo
    if re.search(r"_[A-Z]{2}$", nome_fonte or ""):
        return "midia_regional"
    return "midia_nacional_generalista"

def inferir_regiao_fonte(nome_fonte: str) -> str:
    f_original = nome_fonte or ""
    f_norm = normalizar_texto(f_original).replace(" ", "_")
    for regiao, marcadores in REGIAO_FONTE_REGRAS.items():
        for marcador in marcadores:
            if marcador in f_original or normalizar_texto(marcador).replace(" ", "_") in f_norm:
                return regiao
    return "Nacional/Indefinida"

def extrair_palavras_chave_caso(titulo: str, resumo: str = "", limite: int = 10) -> list[str]:
    texto = normalizar_texto(f"{titulo or ''} {resumo or ''}")
    tokens = re.findall(r"[a-z0-9]{4,}", texto)
    tokens = [t for t in tokens if t not in STOPWORDS_CASO]
    return list(dict.fromkeys(tokens))[:limite]

def criar_caso_id(titulo: str, categoria_publica: str, data_referencia: Optional[datetime] = None, resumo: str = "") -> str:
    data_str = data_referencia.strftime("%Y-%m-%d") if isinstance(data_referencia, datetime) else "sem_data"
    palavras = extrair_palavras_chave_caso(titulo, resumo, limite=8)
    base = f"{normalizar_texto(categoria_publica)}|{data_str}|{' '.join(palavras)}"
    return "caso_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

def estimar_similaridade_caso(titulo: str, resumo: str = "") -> float:
    n = len(extrair_palavras_chave_caso(titulo, resumo, limite=12))
    return round(min(1.0, max(0.35, n / 10.0)), 3)


# ============================================================
# Agrupamento real por CASO no pipeline
# ============================================================
TERMOS_GENERICOS_CASO = STOPWORDS_CASO | {
    "racismo", "racista", "racial", "injuria", "injúria", "discriminacao",
    "discriminação", "preconceito", "odio", "ódio", "caso", "casos",
    "contra", "sobre", "apos", "após", "justica", "justiça", "lei",
    "crime", "crimes", "denuncia", "denúncia", "especialistas", "detalham",
    "rigor", "solta", "solto", "preso", "presa", "prisao", "prisão",
    "acusado", "acusada", "vitima", "vítima", "ataque", "ataques",
    "combate", "direitos", "humanos", "brasil"
}


def tokens_para_cluster_caso(titulo: str = "", resumo: str = "", texto_completo: str = "") -> set[str]:
    texto = normalizar_texto(f"{titulo or ''} {resumo or ''}")
    if not texto and texto_completo:
        texto = normalizar_texto(texto_completo[:1200])
    tokens = re.findall(r"[a-z0-9]{3,}", texto)
    return set(t for t in tokens if t not in TERMOS_GENERICOS_CASO)


def similaridade_tokens_caso(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    overlap = inter / max(1, min(len(a), len(b)))
    jaccard = inter / max(1, len(a | b))
    return round(max(overlap, jaccard * 1.5), 3)


def _data_referencia_cluster(data_publicacao, data_coleta):
    dt = data_publicacao or data_coleta
    if isinstance(dt, datetime):
        return dt.date()
    try:
        parsed = parse_data_publicacao(str(dt)) if dt else None
        return parsed.date() if parsed else None
    except Exception:
        return None


def _distancia_dias(d1, d2) -> int:
    if d1 is None or d2 is None:
        return 999999
    return abs((d1 - d2).days)


def _criar_caso_id_cluster(categoria: str, data_ref, tokens: set[str], primeiro_id: int) -> str:
    data_txt = data_ref.isoformat() if data_ref else "sem_data"
    base_tokens = " ".join(sorted(tokens)[:14])
    base = f"{normalizar_texto(categoria)}|{data_txt}|{base_tokens}|{primeiro_id}"
    return "caso_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def reagrupar_casos_por_similaridade(conn, limite: int = 10000, janela_dias: int = 5, limiar: float = 0.38) -> int:
    """Recalcula caso_id por similaridade lexical. Roda no pipeline, não no Streamlit."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, fonte, data_coleta, data_publicacao,
               categoria_publica, resumo, texto_completo
        FROM noticias
        WHERE titulo IS NOT NULL
        ORDER BY COALESCE(data_publicacao, data_coleta), id
        LIMIT %s
    """, (limite,))
    rows = cursor.fetchall()
    if not rows:
        return 0

    clusters = []
    atribuicoes = []

    for row in rows:
        noticia_id, titulo, fonte, data_coleta, data_publicacao, categoria, resumo, texto_completo = row
        categoria = categoria or classificar_categoria_publica(titulo or "", resumo or "", texto_completo or "")
        data_ref = _data_referencia_cluster(data_publicacao, data_coleta)
        tokens = tokens_para_cluster_caso(titulo or "", resumo or "", texto_completo or "")

        melhor_idx = None
        melhor_score = 0.0
        for idx, cl in enumerate(clusters):
            if cl["categoria"] != categoria:
                continue
            if _distancia_dias(data_ref, cl["data_ref"]) > janela_dias:
                continue
            score = similaridade_tokens_caso(tokens, cl["tokens"])
            if score > melhor_score:
                melhor_score = score
                melhor_idx = idx

        if melhor_idx is not None and melhor_score >= limiar:
            cl = clusters[melhor_idx]
            cl["ids"].append(noticia_id)
            cl["tokens"] = set(list(cl["tokens"] | tokens)[:120])
            if data_ref and (cl["data_ref"] is None or data_ref < cl["data_ref"]):
                cl["data_ref"] = data_ref
            atribuicoes.append((noticia_id, melhor_idx, melhor_score))
        else:
            clusters.append({
                "categoria": categoria,
                "data_ref": data_ref,
                "tokens": tokens,
                "ids": [noticia_id],
                "primeiro_id": noticia_id,
            })
            atribuicoes.append((noticia_id, len(clusters) - 1, 1.0))

    caso_ids = {
        idx: _criar_caso_id_cluster(cl["categoria"], cl["data_ref"], cl["tokens"], cl["primeiro_id"])
        for idx, cl in enumerate(clusters)
    }

    atualizados = 0
    for noticia_id, cluster_idx, score in atribuicoes:
        cursor.execute(
            """
            UPDATE noticias
            SET caso_id = %s,
                similaridade_caso = %s
            WHERE id = %s
            """,
            (caso_ids[cluster_idx], float(round(score, 3)), noticia_id),
        )
        atualizados += 1

    conn.commit()
    logging.info(
        "REAGRUPAMENTO_CASOS: %s noticias atualizadas | clusters=%s | janela=%s | limiar=%.3f",
        atualizados, len(clusters), janela_dias, limiar,
    )
    print(f"Reagrupamento de casos: {atualizados} notícias atualizadas em {len(clusters)} casos.")
    return atualizados
def parse_data_publicacao(valor: Optional[str]) -> Optional[datetime]:
    if not valor:
        return None
    bruto = str(valor).strip()
    if not bruto:
        return None
    try:
        dt = parsedate_to_datetime(bruto)
        if dt:
            return dt
    except Exception:
        pass
    try:
        return datetime.fromisoformat(bruto.replace("Z", "+00:00"))
    except Exception:
        pass
    m = re.search(r"(20\d{2}|19\d{2})[-/](\d{1,2})[-/](\d{1,2})", bruto)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except Exception:
            return None
    return None

def extrair_data_publicacao_soup(soup: BeautifulSoup) -> Optional[datetime]:
    for attrs in [{"property":"article:published_time"}, {"property":"og:published_time"}, {"name":"article:published_time"}, {"name":"pubdate"}, {"name":"publishdate"}, {"name":"date"}, {"name":"DC.date.issued"}, {"itemprop":"datePublished"}]:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            dt = parse_data_publicacao(tag.get("content"))
            if dt:
                return dt
    time_tag = soup.find("time")
    if time_tag:
        dt = parse_data_publicacao(time_tag.get("datetime") or time_tag.get_text(" ", strip=True))
        if dt:
            return dt
    for script in soup.find_all("script", type="application/ld+json"):
        txt = script.get_text(" ", strip=True)
        for campo in ["datePublished", "dateCreated", "uploadDate"]:
            m = re.search(rf'"{campo}"\s*:\s*"([^"]+)"', txt)
            if m:
                dt = parse_data_publicacao(m.group(1))
                if dt:
                    return dt
    return None

def gerar_campos_analiticos(titulo: str, fonte: str, resumo: str = "", texto_completo: str = "", data_publicacao: Optional[datetime] = None, data_coleta: Optional[datetime] = None) -> dict:
    categoria = classificar_categoria_publica(titulo, resumo, texto_completo)
    data_ref = data_publicacao or data_coleta
    return {
        "categoria_publica": categoria,
        "eixos_analiticos": classificar_eixos_analiticos(titulo, resumo, texto_completo),
        "enquadramentos": classificar_enquadramentos(titulo, resumo, texto_completo),
        "tipo_fonte": inferir_tipo_fonte(fonte),
        "regiao_fonte": inferir_regiao_fonte(fonte),
        "caso_id": criar_caso_id(titulo, categoria, data_ref, resumo),
        "similaridade_caso": estimar_similaridade_caso(titulo, resumo),
    }


def classificar_titulo(titulo: str) -> tuple:
    t = normalizar_texto(titulo)
    if not t:
        return False, None, 0.0, "vazio"

    if t in BLACKLIST_EXATA:
        return False, None, 0.0, "blacklist_exata"
    if contem_algum(t, BLACKLIST_FRAGMENTOS):
        return False, None, 0.0, "blacklist_fragmento"
    if contem_algum(t, TEMAS_POPULARES_SENSIVEIS) and contem_algum(t, MARCADORES_POPULARES_ESTRITOS):
        return True, "caso_sensivel", 0.86, "tema_popular_estrito"
    if len(t.split()) < 5:
        return False, None, 0.0, "curto"
    if len("".join(c for c in t if c.isalpha())) < 20:
        return False, None, 0.0, "baixo_conteudo"

    tem_gatilho  = contem_algum(t, GATILHOS_FORTES)
    tem_grupo    = contem_algum(t, GRUPOS_SOCIAIS)
    tem_conflito = contem_algum(t, VERBOS_CONFLITO)
    tem_contexto = contem_algum(t, CONTEXTOS_SENSIVEIS)
    tem_expressao = contem_algum(t, EXPRESSOES_ESPECIFICAS)
    tem_tema_popular = contem_algum(t, TEMAS_POPULARES)
    tem_marcador_popular = contem_algum(t, MARCADORES_SOCIAIS_POPULARES)

    if contem_algum(t, BLACKLIST_ESPORTIVA) and not (
        tem_gatilho or
        (tem_contexto and tem_conflito) or
        (tem_tema_popular and tem_marcador_popular)
    ):
        return False, None, 0.0, "ruido_esportivo"

    if contem_algum(t, BLACKLIST_ECONOMICA) and not tem_gatilho:
        return False, None, 0.0, "ruido_economico"

    if contem_algum(t, BLACKLIST_CULTURAL) and not (
        tem_gatilho or
        tem_conflito or
        (tem_tema_popular and tem_marcador_popular)
    ):
        return False, None, 0.0, "ruido_cultural"

    if contem_algum(t, BLACKLIST_VIOLENCIA_GENERICA) and not (tem_gatilho or (tem_grupo and tem_conflito)):
        return False, None, 0.0, "violencia_generica"

    if tem_gatilho:
        return True, "alta_relevancia", 1.0, "gatilho_forte"

    if tem_grupo and tem_conflito:
        return True, "alta_relevancia", 0.95, "grupo+conflito"

    if tem_contexto and tem_conflito:
        return True, "alta_relevancia", 0.92, "contexto+conflito"

    if tem_contexto and tem_grupo and tem_expressao:
        return True, "caso_sensivel", 0.88, "contexto+grupo+expressao"

    if tem_expressao and (tem_grupo or tem_contexto):
        return True, "caso_sensivel", 0.85, "expressao+ancora"

    if tem_tema_popular and tem_marcador_popular:
        return True, "caso_sensivel", 0.86, "tema_popular+marcador_social"

    sim = calcular_similaridade_focada(t)

    if sim == 0.0:
        logging.info("REJEITADO (sem_vetor) - %s", titulo)
        return False, None, 0.0, "sem_vetor"

        # -------------------------------------------------------------
        # 🧠 APRENDIZADO DE MÁQUINA: Bloqueio por Memória de Curadoria
        # -------------------------------------------------------------
        try:
            # Só executa se a variável global existir e não estiver vazia
            if 'VETORES_FALSOS_POSITIVOS' in globals() and VETORES_FALSOS_POSITIVOS:
                doc_t = nlp(t)
                if doc_t.has_vector:
                    sim_com_lixo = [doc_t.similarity(v_lixo) for v_lixo in VETORES_FALSOS_POSITIVOS if
                                    v_lixo.has_vector]

                    if sim_com_lixo and max(sim_com_lixo) >= 0.88:
                        logging.info("REJEITADO (aprendizado_curadoria: %.3f) - %s", max(sim_com_lixo), titulo)
                        return False, None, max(sim_com_lixo), "aprendizado_curadoria"
        except Exception as e:
            logging.error(f"Erro no módulo de aprendizado para o título '{titulo}': {e}")
        # -------------------------------------------------------------

    n_sinais = sum([tem_grupo, tem_conflito, tem_contexto])

    # RÉGUA SUBIU: De 0.63 para 0.73
    if n_sinais >= 2 and sim >= 0.73:
        logging.info("ACEITO (vetor_dois_sinais: %.3f) - %s", sim, titulo)
        return True, "relevancia_contextual", sim, "vetor_dois_sinais"

    # RÉGUA SUBIU: De 0.70 para 0.80
    if n_sinais == 1 and sim >= 0.80:
        logging.info("ACEITO (vetor_um_sinal: %.3f) - %s", sim, titulo)
        return True, "relevancia_contextual", sim, "vetor_um_sinal"

    # RÉGUA SUBIU: De 0.78 para 0.86 (Texto sem sinais precisa ser MUITO óbvio)
    if n_sinais == 0 and sim >= 0.86:
        logging.info("ACEITO (vetor_isolado: %.3f) - %s", sim, titulo)
        return True, "relevancia_contextual", sim, "vetor_isolado"

    # Ajuste no log de "quase aceito" para não poluir o terminal
    if sim >= 0.68:
        logging.info("QUASE_ACEITO (%.3f | sinais=%d) - %s", sim, n_sinais, titulo)

    return False, None, sim, "rejeitado_semantico"


def preparar_banco(conn) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id               BIGSERIAL PRIMARY KEY,
            titulo           TEXT UNIQUE,
            fonte            TEXT,
            data_coleta      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            data_publicacao  TIMESTAMPTZ,
            score_relevancia DOUBLE PRECISION,
            classificacao    TEXT,
            criterio_filtro  TEXT,
            url_fonte        TEXT,
            resumo           TEXT,
            texto_completo   TEXT,
            categoria_publica TEXT,
            eixos_analiticos TEXT,
            enquadramentos   TEXT,
            tipo_fonte       TEXT,
            regiao_fonte     TEXT,
            caso_id          TEXT,
            similaridade_caso DOUBLE PRECISION
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entidades (
            id          BIGSERIAL PRIMARY KEY,
            noticia_id  BIGINT REFERENCES noticias(id) ON DELETE CASCADE,
            texto       TEXT,
            tipo        TEXT
        )
    """)
    for cmd in [
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS score_relevancia DOUBLE PRECISION",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS classificacao TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS criterio_filtro TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS url_fonte TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS resumo TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS texto_completo TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS data_publicacao TIMESTAMPTZ",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS categoria_publica TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS eixos_analiticos TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS enquadramentos TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS tipo_fonte TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS regiao_fonte TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS caso_id TEXT",
        "ALTER TABLE noticias ADD COLUMN IF NOT EXISTS similaridade_caso DOUBLE PRECISION",
    ]:
        cursor.execute(cmd)
    conn.commit()


def extrair_itens_requests(url_base: str, seletor: str) -> list:
    resp = requests.get(url_base, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    itens = []
    for el in soup.select(seletor):
        titulo = el.get_text(" ", strip=True)
        if not titulo:
            continue
        a = el.find("a", href=True)
        if a is None and el.parent is not None:
            a = el.parent if getattr(el.parent, "name", None) == "a" and el.parent.get("href") else el.parent.find("a", href=True)
        url = urljoin(url_base, a.get("href")) if a and a.get("href") else None
        itens.append({"titulo": titulo, "url": url})
    return itens


def extrair_itens_playwright(url_base: str, seletor: str) -> list:
    js = f"""
    () => {{
      const nodes = Array.from(document.querySelectorAll({seletor!r}));
      return nodes.map((el) => {{
        const title = (el.innerText || '').trim();
        let anchor = el.querySelector('a[href]');
        if (!anchor && el.parentElement && el.parentElement.tagName === 'A' && el.parentElement.href) {{
          anchor = el.parentElement;
        }}
        if (!anchor && el.parentElement) {{
          anchor = el.parentElement.querySelector('a[href]');
        }}
        return {{
          titulo: title,
          url: anchor ? anchor.href : null
        }};
      }}).filter(item => item.titulo);
    }}
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url_base, wait_until="domcontentloaded", timeout=60000)
            return page.evaluate(js)
        finally:
            browser.close()


def extrair_itens(cfg: dict) -> list:
    return extrair_itens_requests(cfg["url"], cfg["seletor"]) if cfg["estrategia"] == "requests" else extrair_itens_playwright(cfg["url"], cfg["seletor"])


def extrair_texto_artigo(url: Optional[str]) -> tuple[Optional[str], Optional[str], Optional[datetime]]:
    if not url:
        return None, None, None
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception:
        logging.exception("Falha ao buscar URL do artigo: %s", url)
        return None, None, None

    soup = BeautifulSoup(resp.text, "html.parser")
    data_publicacao = extrair_data_publicacao_soup(soup)
    for bad in soup.select("script, style, noscript, nav, footer, header, aside, form"):
        bad.decompose()

    candidatos = []
    for seletor in ["article p", "main p", "[itemprop='articleBody'] p", ".article-content p", ".content-text p", ".post-content p", ".entry-content p", ".materia-conteudo p", ".noticia-conteudo p"]:
        ps = [p.get_text(" ", strip=True) for p in soup.select(seletor)]
        ps = [p for p in ps if len(p) >= 40]
        if len(ps) >= 3:
            candidatos = ps
            break
    if not candidatos:
        ps = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        candidatos = [p for p in ps if len(p) >= 40]
    if not candidatos:
        return None, None, data_publicacao
    texto = "\n\n".join(candidatos)
    resumo = " ".join(candidatos[:2])[:900]
    return resumo, texto, data_publicacao


def salvar_relatorio_csv(resumos: list[dict], totais: dict) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"resumo_fontes_{ts}.csv"
    fieldnames = [
        "fonte", "extraidos", "filtrados", "alta_relevancia", "relevancia_contextual",
        "caso_sensivel", "inseridos", "duplicados", "erros_db", "taxa_filtragem_pct", "taxa_aproveitamento_pct"
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in resumos:
            writer.writerow(row)
        writer.writerow({})
        writer.writerow({
            "fonte": "TOTAL_GERAL",
            "extraidos": totais["extraidos"],
            "filtrados": totais["filtrados"],
            "alta_relevancia": totais["alta_relevancia"],
            "relevancia_contextual": totais["relevancia_contextual"],
            "caso_sensivel": totais["caso_sensivel"],
            "inseridos": totais["inseridos"],
            "duplicados": totais["duplicados"],
            "erros_db": totais["erros_db"],
            "taxa_filtragem_pct": round((totais["filtrados"] / totais["extraidos"] * 100), 2) if totais["extraidos"] else 0.0,
            "taxa_aproveitamento_pct": round((totais["inseridos"] / totais["filtrados"] * 100), 2) if totais["filtrados"] else 0.0,
        })
    return path



def backfill_campos_analiticos(conn, limite: int = 5000, preencher_data_publicacao: bool = False) -> int:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, fonte, data_coleta, url_fonte, resumo, texto_completo, data_publicacao
        FROM noticias
        WHERE categoria_publica IS NULL
           OR eixos_analiticos IS NULL
           OR enquadramentos IS NULL
           OR tipo_fonte IS NULL
           OR regiao_fonte IS NULL
           OR caso_id IS NULL
           OR similaridade_caso IS NULL
           OR (%s = TRUE AND data_publicacao IS NULL AND url_fonte IS NOT NULL)
        ORDER BY id DESC
        LIMIT %s
    """, (preencher_data_publicacao, limite))
    rows = cursor.fetchall()
    atualizados = 0
    for row in rows:
        noticia_id, titulo, fonte, data_coleta, url_fonte, resumo, texto_completo, data_publicacao_atual = row
        data_publicacao = data_publicacao_atual
        resumo_local = resumo
        texto_local = texto_completo
        if preencher_data_publicacao and not data_publicacao and url_fonte:
            try:
                resumo_extraido, texto_extraido, data_extraida = extrair_texto_artigo(url_fonte)
                data_publicacao = data_extraida or data_publicacao
                resumo_local = resumo_local or resumo_extraido
                texto_local = texto_local or texto_extraido
            except Exception:
                logging.exception("Falha no backfill de data_publicacao: noticia_id=%s", noticia_id)
        campos = gerar_campos_analiticos(titulo or "", fonte or "", resumo_local or "", texto_local or "", data_publicacao, data_coleta)
        cursor.execute("""
            UPDATE noticias
            SET data_publicacao = COALESCE(%s, data_publicacao),
                resumo = COALESCE(resumo, %s),
                texto_completo = COALESCE(texto_completo, %s),
                categoria_publica = %s,
                eixos_analiticos = %s,
                enquadramentos = %s,
                tipo_fonte = %s,
                regiao_fonte = %s,
                caso_id = %s,
                similaridade_caso = %s
            WHERE id = %s
        """, (data_publicacao, resumo_local, texto_local, campos["categoria_publica"], campos["eixos_analiticos"], campos["enquadramentos"], campos["tipo_fonte"], campos["regiao_fonte"], campos["caso_id"], campos["similaridade_caso"], noticia_id))
        atualizados += 1
    conn.commit()
    logging.info("BACKFILL_ANALITICO: %s registros atualizados | preencher_data_publicacao=%s", atualizados, preencher_data_publicacao)
    return atualizados


def coletar_noticias() -> None:
    conn = psycopg2.connect(DB_URL)
    preparar_banco(conn)


    preencher_datas = os.getenv("BACKFILL_DATAS", "0").strip() == "1"
    backfill_limite = int(os.getenv("BACKFILL_LIMITE", "5000"))
    backfill_n = backfill_campos_analiticos(conn, limite=backfill_limite, preencher_data_publicacao=preencher_datas)
    print(f"Backfill analitico: {backfill_n} registros atualizados.")

    if os.getenv("REAGRUPAR_CASOS_INICIO", "1") == "1":
        reagrupar_casos_por_similaridade(
            conn,
            limite=int(os.getenv("CASOS_LIMITE", "10000")),
            janela_dias=int(os.getenv("CASOS_JANELA_DIAS", "5")),
            limiar=float(os.getenv("CASOS_LIMIAR", "0.38")),
        )

    if os.getenv("REAGRUPAR_CASOS_INICIO", "1") == "1":
        reagrupar_casos_por_similaridade(
            conn,
            limite=int(os.getenv("CASOS_LIMITE", "10000")),
            janela_dias=int(os.getenv("CASOS_JANELA_DIAS", "5")),
            limiar=float(os.getenv("CASOS_LIMIAR", "0.38")),
        )

    if os.getenv("BACKFILL_APENAS", "0") == "1":
        conn.close()
        print("BACKFILL_APENAS=1: campos analíticos e casos atualizados; coleta pulada.")
        return

    cursor = conn.cursor()
    fuso_br = timezone(timedelta(hours=-3))

    totais = {
        "portais_ok": 0, "portais_erro": 0, "extraidos": 0, "filtrados": 0,
        "alta_relevancia": 0, "relevancia_contextual": 0, "caso_sensivel": 0,
        "inseridos": 0, "duplicados": 0, "erros_db": 0,
    }
    resumos_fontes = []

    logging.info("Versao v12.2 tematica popular ativa")

    for nome, cfg in PORTAIS_CONFIG.items():
        print(f"Vasculhando {nome}...")
        extraidos = filtrados = inseridos = duplicados = erros_db = 0
        alta = contextual = sensivel = 0

        try:
            itens = extrair_itens(cfg)
            extraidos = len(itens)
            totais["extraidos"] += extraidos
            if itens:
                print(f"  → {len(itens)} títulos encontrados.")
            else:
                print("  → Nenhum título encontrado.")

            for item in itens:
                titulo = (item.get("titulo") or "").strip()
                url = item.get("url")
                if not titulo:
                    continue

                aceito, classificacao, score, criterio = classificar_titulo(titulo)
                if not aceito:
                    continue

                filtrados += 1
                totais["filtrados"] += 1
                if classificacao == "alta_relevancia":
                    alta += 1; totais["alta_relevancia"] += 1
                elif classificacao == "relevancia_contextual":
                    contextual += 1; totais["relevancia_contextual"] += 1
                elif classificacao == "caso_sensivel":
                    sensivel += 1; totais["caso_sensivel"] += 1

                try:
                    resumo, texto_completo, data_publicacao = extrair_texto_artigo(url)
                    data_hora = datetime.now(fuso_br)
                    campos_analiticos = gerar_campos_analiticos(titulo, nome, resumo or "", texto_completo or "", data_publicacao, data_hora)
                    cursor.execute("""
                        INSERT INTO noticias (
                            titulo, fonte, data_coleta, data_publicacao, score_relevancia, classificacao,
                            criterio_filtro, url_fonte, resumo, texto_completo, categoria_publica,
                            eixos_analiticos, enquadramentos, tipo_fonte, regiao_fonte, caso_id, similaridade_caso
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (titulo) DO NOTHING
                        RETURNING id
                    """, (titulo, nome, data_hora, data_publicacao, score, classificacao, criterio, url, resumo, texto_completo, campos_analiticos["categoria_publica"], campos_analiticos["eixos_analiticos"], campos_analiticos["enquadramentos"], campos_analiticos["tipo_fonte"], campos_analiticos["regiao_fonte"], campos_analiticos["caso_id"], campos_analiticos["similaridade_caso"]))
                    row = cursor.fetchone()
                    if row is None:
                        duplicados += 1; totais["duplicados"] += 1
                        conn.commit()
                        continue

                    noticia_id = row[0]
                    doc = nlp(titulo)
                    for ent in doc.ents:
                        if ent.label_ in ["PER", "ORG", "LOC"]:
                            cursor.execute(
                                "INSERT INTO entidades (noticia_id, texto, tipo) VALUES (%s, %s, %s)",
                                (noticia_id, ent.text, ent.label_)
                            )
                    conn.commit()
                    inseridos += 1; totais["inseridos"] += 1
                    logging.info("ACEITO (%s | %.3f | %s) - %s", classificacao, score, criterio, titulo)
                except Exception:
                    conn.rollback()
                    erros_db += 1; totais["erros_db"] += 1
                    logging.exception("ERRO AO SALVAR '%s' (%s)", titulo, nome)

            taxa_filtragem = round((filtrados / extraidos * 100), 2) if extraidos else 0.0
            taxa_aproveitamento = round((inseridos / filtrados * 100), 2) if filtrados else 0.0
            resumo_fonte = {
                "fonte": nome, "extraidos": extraidos, "filtrados": filtrados,
                "alta_relevancia": alta, "relevancia_contextual": contextual, "caso_sensivel": sensivel,
                "inseridos": inseridos, "duplicados": duplicados, "erros_db": erros_db,
                "taxa_filtragem_pct": taxa_filtragem, "taxa_aproveitamento_pct": taxa_aproveitamento,
            }
            resumos_fontes.append(resumo_fonte)
            print(f"[RESUMO {nome}] extraídos={extraidos} | filtrados={filtrados} | alta={alta} | contextual={contextual} | sensivel={sensivel} | inseridos={inseridos} | duplicados={duplicados} | erros_db={erros_db} | taxa_filtragem={taxa_filtragem}% | aproveitamento={taxa_aproveitamento}%")
            totais["portais_ok"] += 1

        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            totais["portais_erro"] += 1
            logging.exception("ERRO NO PORTAL %s", nome)
            print(f"[ERRO] {nome}. Veja o log.")

    if os.getenv("REAGRUPAR_CASOS_FINAL", "1") == "1":
        reagrupar_casos_por_similaridade(
            conn,
            limite=int(os.getenv("CASOS_LIMITE", "10000")),
            janela_dias=int(os.getenv("CASOS_JANELA_DIAS", "5")),
            limiar=float(os.getenv("CASOS_LIMIAR", "0.38")),
        )

    conn.close()
    csv_path = salvar_relatorio_csv(resumos_fontes, totais)
    print("\nResumo geral:")
    print(totais)
    print(f"Relatório por fonte salvo em: {csv_path}")
    logging.info("RESUMO GERAL: %s", totais)
    logging.info("Relatório CSV salvo em: %s", csv_path)


if __name__ == "__main__":
    print("Iniciando pipeline de pesquisa...")
    coletar_noticias()
    print("Coleta concluída! Verifique pipeline_decisoes.log e o CSV em relatorios_pipeline/.")
