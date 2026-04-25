import os
import html
import numpy as np

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import re


FUSO_BRASIL = "America/Sao_Paulo"

st.set_page_config(
    page_title="Agregador de notícias sobre preconceitos e discursos de ódio",
    layout="wide"
)


def get_db_url() -> str:
    secrets_dict = {}
    try:
        secrets_dict = st.secrets.to_dict()
    except Exception:
        secrets_dict = {}

    if "SUPABASE_DB_URL" in secrets_dict:
        return secrets_dict["SUPABASE_DB_URL"]

    env_url = os.getenv("SUPABASE_DB_URL", "").strip()
    if env_url:
        return env_url

    raise RuntimeError("SUPABASE_DB_URL não configurada.")


@st.cache_resource
def get_engine():
    return create_engine(
        get_db_url(),
        pool_pre_ping=True,
        poolclass=NullPool,
    )


def _build_noticias_query(periodo_sql: str, limite: int):
    if periodo_sql == "tudo":
        query = text("""
            SELECT *
            FROM noticias
            ORDER BY data_coleta DESC
            LIMIT :limite
        """)
        params = {"limite": int(limite)}
    else:
        query = text(f"""
            SELECT *
            FROM noticias
            WHERE data_coleta >= NOW() - INTERVAL '{periodo_sql}'
            ORDER BY data_coleta DESC
            LIMIT :limite
        """)
        params = {"limite": int(limite)}
    return query, params


@st.cache_data(ttl=60)
def carregar_dados(periodo_sql: str, limite: int):
    try:
        query_noticias, params = _build_noticias_query(periodo_sql, limite)
        with get_engine().connect() as conn:
            df_noticias = pd.read_sql(query_noticias, conn, params=params)
            df_entidades = pd.read_sql(
                text("""
                    SELECT e.*
                    FROM entidades e
                    INNER JOIN (
                        SELECT id
                        FROM noticias
                        {where_clause}
                        ORDER BY data_coleta DESC
                        LIMIT :limite
                    ) n ON e.noticia_id = n.id
                """.format(
                    where_clause="" if periodo_sql == "tudo" else f"WHERE data_coleta >= NOW() - INTERVAL '{periodo_sql}'"
                )),
                conn,
                params={"limite": int(limite)}
            )
            df_total = pd.read_sql(text("SELECT COUNT(*) AS total FROM noticias"), conn)
        total_banco = int(df_total.iloc[0]["total"]) if not df_total.empty else 0
        return df_noticias, df_entidades, total_banco, None
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), 0, str(e)


def safe_text(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    return html.escape(str(value))


def formatar_data_curta(value, somente_data: bool = False) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    try:
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return "—"

        if getattr(ts, "tzinfo", None) is None:
            ts = ts.tz_localize("UTC")

        ts = ts.tz_convert(FUSO_BRASIL)

        if somente_data:
            return ts.strftime("%Y-%m-%d")
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)

def texto_para_html_paragrafos(texto: str) -> str:
    if not texto:
        return ""

    texto_limpo = str(texto).replace("\r\n", "\n").replace("\r", "\n").strip()

    # divide em blocos/parágrafos por uma ou mais linhas em branco
    paragrafos = re.split(r"\n\s*\n+", texto_limpo)

    paragrafos_html = []
    for p in paragrafos:
        p_limpo = safe_text(p.strip()).replace("\n", " ")
        if p_limpo:
            paragrafos_html.append(f"<p>{p_limpo}</p>")

    return "".join(paragrafos_html)

def categorizar_publicamente(row) -> str:
    titulo = str(row.get("titulo", "") or "").lower()
    resumo = str(row.get("resumo", "") or "").lower()
    texto_completo = str(row.get("texto_completo", "") or "").lower()
    texto = f"{titulo} {resumo} {texto_completo}"

    def tem(*termos):
        return any(t in texto for t in termos)

    if tem(
        "racismo", "racista", "injuria racial", "injúria racial",
        "ofensa racista", "discriminacao racial", "discriminação racial",
        "negro", "negra", "pretos", "pretas", "população negra", "populacao negra",
        "cotas raciais"
    ):
        return "Racismo e discriminação racial"

    if tem(
        "misoginia", "misóginia", "machismo", "sexismo",
        "violencia contra a mulher", "violência contra a mulher",
        "violencia contra mulheres", "violência contra mulheres",
        "feminicidio", "feminicídio"
    ):
        return "Gênero, misoginia e violência contra mulheres"

    if tem(
        "homofobia", "transfobia", "lgbtfobia", "lgbt", "lgbtqia",
        "travesti", "travestis", "gay", "gays", "lésbica", "lesbica",
        "bissexual", "não-binário", "nao-binario", "mulher trans", "homem trans",
        "pessoa trans"
    ):
        return "LGBTQIA+ e LGBTfobia"

    if tem(
        "intolerancia religiosa", "intolerância religiosa",
        "terreiro", "terreiros", "candomble", "candomblé", "umbanda",
        "mesquita", "sinagoga", "templo", "hijab", "ataque a terreiro"
    ):
        return "Intolerância religiosa"

    if tem(
        "xenofobia", "xenófobia", "imigrante", "imigrantes",
        "migrante", "migrantes", "refugiado", "refugiados",
        "migração", "migracao"
    ):
        return "Xenofobia, migração e refúgio"

    if tem(
        "indigena", "indígena", "indigenas", "indígenas",
        "quilombola", "quilombolas", "povos originarios", "povos originários",
        "demarcacao", "demarcação", "terras indígenas", "terras indigenas",
        "comunidades tradicionais", "comunidade tradicional"
    ):
        return "Povos indígenas, quilombolas e comunidades tradicionais"

    if tem(
        "capacitismo", "capacitista", "pessoa com deficiência",
        "pessoa com deficiencia", "pcd", "autista", "autistas",
        "deficiente", "deficiência", "deficiencia"
    ):
        return "Capacitismo e deficiência"

    if tem(
        "futebol", "torcida", "torcedor", "torcedores", "estadio", "estádio",
        "jogador", "jogadora", "clube", "campeonato",
        "show", "espetaculo", "espetáculo", "musica", "música",
        "teatro", "cinema", "samba", "funk", "rap", "hip hop",
        "cultura popular", "festa popular", "lazer popular"
    ):
        return "Esporte, cultura e lazer com discriminação"

    if tem(
        "justiça", "justica", "tribunal", "stf", "stj",
        "direitos humanos", "ministério público", "ministerio publico",
        "projeto de lei", "política pública", "politica publica",
        "ações afirmativas", "acoes afirmativas", "lei de cotas"
    ):
        return "Direitos, justiça e políticas públicas"

    return "Estigma, exclusão e conflitos sociais"



# ============================================================
# Camada analítica adicional: representatividade e enquadramentos
# Mantém o banco intacto. Tudo é inferido em tempo de execução.
# ============================================================

def _texto_longo_row(row) -> str:
    partes = []
    for col in ["titulo", "resumo", "texto_completo", "fonte", "categoria_publica", "classificacao", "criterio_filtro"]:
        if col in row.index:
            valor = row.get(col, "")
            if valor is not None and not (isinstance(valor, float) and pd.isna(valor)):
                partes.append(str(valor))
    return " ".join(partes).lower()


DICIONARIOS_EIXOS = {
    "Racismo e discriminação racial": ["racismo", "racista", "injúria racial", "injuria racial", "discriminação racial", "discriminacao racial", "ofensa racista", "branquitude", "cotas raciais", "ação afirmativa", "acoes afirmativas", "negro", "negra", "pretos", "pretas", "população negra", "populacao negra"],
    "Gênero, misoginia e violência contra mulheres": ["misoginia", "misóginia", "machismo", "sexismo", "feminicídio", "feminicidio", "violência contra a mulher", "violencia contra a mulher", "violência contra mulheres", "assédio", "assedio", "igualdade de gênero", "violência doméstica", "violencia domestica"],
    "LGBTQIA+ e LGBTfobia": ["homofobia", "transfobia", "lgbtfobia", "lgbt", "lgbtqia", "travesti", "travestis", "gay", "gays", "lésbica", "lesbica", "bissexual", "não-binário", "nao-binario", "mulher trans", "homem trans", "pessoa trans", "identidade de gênero", "orientação sexual"],
    "Intolerância religiosa e racismo religioso": ["intolerância religiosa", "intolerancia religiosa", "racismo religioso", "terreiro", "terreiros", "candomblé", "candomble", "umbanda", "orixá", "orixa", "mesquita", "sinagoga", "islamofobia", "antissemitismo", "ataque a terreiro"],
    "Xenofobia, migração e refúgio": ["xenofobia", "xenófobia", "imigrante", "imigrantes", "migrante", "migrantes", "refugiado", "refugiados", "refugiada", "refugiadas", "migração", "migracao", "venezuelano", "venezuelana", "haitiano", "haitiana", "boliviano", "boliviana"],
    "Povos indígenas, quilombolas e comunidades tradicionais": ["indígena", "indigena", "indígenas", "indigenas", "povos originários", "povos originarios", "quilombola", "quilombolas", "comunidades tradicionais", "comunidade tradicional", "demarcação", "demarcacao", "terra indígena", "terras indígenas", "yanomami", "guarani", "kaiowá", "kaiowa"],
    "Capacitismo e deficiência": ["capacitismo", "capacitista", "pessoa com deficiência", "pessoa com deficiencia", "pessoas com deficiência", "pessoas com deficiencia", "pcd", "deficiência", "deficiencia", "autismo", "autista", "autistas", "neurodivergente", "acessibilidade"],
    "Preconceito regional e territorial": ["preconceito regional", "nordestino", "nordestina", "nordestinos", "nordestinas", "xenofobia contra nordestinos", "sotaque", "sertanejo", "sertaneja", "amazônida", "amazonida", "ribeirinho", "ribeirinha", "periferia", "favela", "comunidade"],
    "Classe social, pobreza e desigualdade": ["pobreza", "pobre", "pobres", "desigualdade social", "classe social", "morador de rua", "população em situação de rua", "populacao em situacao de rua", "sem-teto", "sem teto", "trabalho escravo", "trabalho análogo", "trabalho analogo"],
    "Etarismo, infância, juventude e envelhecimento": ["etarismo", "idoso", "idosa", "idosos", "idosas", "velhice", "envelhecimento", "criança", "crianca", "adolescente", "adolescentes", "juventude", "jovens"],
    "Corpo, aparência e estigma estético": ["gordofobia", "obesidade", "obeso", "obesa", "aparência", "aparencia", "padrão de beleza", "padrao de beleza", "corpo", "estética", "estetica"],
}


DICIONARIOS_ENQUADRAMENTO = {
    "Grupo como ameaça": ["ameaça", "ameaca", "risco", "perigo", "invasão", "invasao", "desordem", "baderna", "radical", "extremista", "terror", "terrorismo", "crise migratória", "crise migratoria"],
    "Grupo criminalizado": ["crime", "criminoso", "criminosa", "suspeito", "suspeita", "prisão", "prisao", "preso", "presa", "tráfico", "trafico", "roubo", "furto", "facção", "faccao", "violência", "violencia"],
    "Grupo como vítima": ["vítima", "vitima", "vítimas", "vitimas", "agredido", "agredida", "ataque", "atacado", "atacada", "ameaçado", "ameaçada", "morto", "morta", "ferido", "ferida", "denuncia", "denúncia"],
    "Sujeito de direitos": ["direitos", "direitos humanos", "igualdade", "cidadania", "proteção", "protecao", "garantia", "política pública", "politica publica", "ação afirmativa", "acoes afirmativas", "lei", "estatuto"],
    "Agência política e resistência": ["protesto", "manifestação", "manifestacao", "mobilização", "mobilizacao", "movimento", "resistência", "resistencia", "liderança", "lideranca", "organização", "organizacao", "coletivo", "marcha"],
    "Exotização ou folclorização": ["exótico", "exotico", "tribal", "folclore", "folclórico", "folclorico", "curioso", "curiosidade", "tradição exótica", "tradicao exotica"],
    "Linguagem moralizante": ["família", "familia", "bons costumes", "ideologia", "imoral", "moral", "vergonha", "decadência", "decadencia", "degeneração", "degeneracao", "doutrinação", "doutrinacao"],
    "Linguagem estrutural": ["estrutura", "estrutural", "desigualdade", "histórico", "historico", "colonial", "colonialismo", "institucional", "sistêmico", "sistemico", "reparação", "reparacao", "vulnerabilidade"],
    "Invisibilização ou apagamento": ["invisível", "invisivel", "invisibilidade", "apagamento", "silenciamento", "exclusão", "exclusao", "marginalizado", "marginalizada", "subnotificação", "subnotificacao"],
}


TIPOS_FONTES_POR_NOME = {
    "midia_identitaria_direitos": ["alma_preta", "geledes", "genero_e_numero", "agencia_patricia_galvao", "catarinas", "midia_india", "apib", "cimi", "conaq", "casa1", "correio_nago", "rioonwatch", "agencia_mural", "periferia_em_movimento", "voz_das_comunidades"],
    "jornalismo_investigativo": ["agencia_publica", "the_intercept", "ponte", "reporter_brasil", "de_olho_nos_ruralistas", "nexo"],
    "fact_checking": ["lupa", "aos_fatos", "comprova", "boatos", "verifica"],
    "fonte_publica_institucional": ["senado", "camara", "gov", "stf", "stj", "tse", "agu", "mpf", "conass", "agencia_brasil", "ebc"],
    "midia_religiosa": ["gospel", "cristao", "guiame", "cnbb", "vatican", "pleno_news"],
    "midia_internacional_lusofona": ["bbc", "dw", "rfi", "france24", "euronews", "onu", "voa", "publico_pt", "observador_pt", "angola", "mocambique", "rtp_africa"],
    "midia_regional": ["_ac", "_al", "_am", "_ap", "_ba", "_ce", "_df", "_es", "_go", "_ma", "_mg", "_ms", "_mt", "_pa", "_pb", "_pe", "_pi", "_pr", "_rj", "_rn", "_ro", "_rr", "_rs", "_sc", "_se", "_sp", "_to"],
}


REGIOES_POR_SIGLA = {
    "_ac": "Norte", "_am": "Norte", "_ap": "Norte", "_pa": "Norte", "_ro": "Norte", "_rr": "Norte", "_to": "Norte",
    "_al": "Nordeste", "_ba": "Nordeste", "_ce": "Nordeste", "_ma": "Nordeste", "_pb": "Nordeste", "_pe": "Nordeste", "_pi": "Nordeste", "_rn": "Nordeste", "_se": "Nordeste",
    "_df": "Centro-Oeste", "_go": "Centro-Oeste", "_ms": "Centro-Oeste", "_mt": "Centro-Oeste",
    "_es": "Sudeste", "_mg": "Sudeste", "_rj": "Sudeste", "_sp": "Sudeste",
    "_pr": "Sul", "_rs": "Sul", "_sc": "Sul",
}


PESO_TIPO_FONTE = {
    "midia_nacional_generalista": 1.00,
    "midia_regional": 1.15,
    "midia_identitaria_direitos": 1.35,
    "jornalismo_investigativo": 1.25,
    "fonte_publica_institucional": 1.00,
    "fact_checking": 1.15,
    "midia_religiosa": 1.05,
    "midia_internacional_lusofona": 0.90,
    "outra": 1.00,
}


def _fonte_normalizada(fonte) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", str(fonte or "").lower()).strip("_")


def inferir_tipo_fonte(fonte: str) -> str:
    f = _fonte_normalizada(fonte)
    for tipo, marcadores in TIPOS_FONTES_POR_NOME.items():
        if any(m in f for m in marcadores):
            return tipo
    return "midia_nacional_generalista"


def inferir_regiao_fonte(fonte: str) -> str:
    f = _fonte_normalizada(fonte)
    for sigla, regiao in REGIOES_POR_SIGLA.items():
        if sigla in f or f.endswith(sigla.strip("_")):
            return regiao
    if any(m in f for m in ["bbc", "dw", "rfi", "france24", "euronews", "onu", "voa", "publico_pt", "observador_pt"]):
        return "Internacional"
    return "Nacional/sem região explícita"


def classificar_por_dicionario(texto: str, dicionario: dict, fallback: str = "Não classificado") -> str:
    encontrados = []
    for rotulo, termos in dicionario.items():
        if any(t.lower() in texto for t in termos):
            encontrados.append(rotulo)
    if not encontrados:
        return fallback
    return "; ".join(encontrados)


def classificar_eixos_preconceito(row) -> str:
    texto = _texto_longo_row(row)
    eixos = classificar_por_dicionario(texto, DICIONARIOS_EIXOS, fallback="Outros/inespecífico")
    if eixos == "Outros/inespecífico" and "categoria_publica" in row.index and pd.notna(row.get("categoria_publica")):
        return str(row.get("categoria_publica"))
    return eixos


def classificar_enquadramentos(row) -> str:
    texto = _texto_longo_row(row)
    return classificar_por_dicionario(texto, DICIONARIOS_ENQUADRAMENTO, fallback="Enquadramento não identificado")


def enriquecer_dataframe_analitico(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "fonte" in out.columns:
        out["tipo_fonte"] = out["fonte"].apply(inferir_tipo_fonte)
        out["regiao_fonte"] = out["fonte"].apply(inferir_regiao_fonte)
        out["peso_tipo_fonte"] = out["tipo_fonte"].map(PESO_TIPO_FONTE).fillna(1.0)
    else:
        out["tipo_fonte"] = "outra"
        out["regiao_fonte"] = "Não informado"
        out["peso_tipo_fonte"] = 1.0
    out["eixos_preconceito"] = out.apply(classificar_eixos_preconceito, axis=1)
    out["enquadramentos"] = out.apply(classificar_enquadramentos, axis=1)
    return out


def explodir_lista_semicolon(df: pd.DataFrame, coluna: str, nome_saida: str) -> pd.DataFrame:
    if df.empty or coluna not in df.columns:
        return pd.DataFrame(columns=[nome_saida])
    tmp = df[[coluna]].copy()
    tmp[coluna] = tmp[coluna].fillna("Não informado").astype(str).str.split(";")
    tmp = tmp.explode(coluna)
    tmp[coluna] = tmp[coluna].astype(str).str.strip()
    tmp.loc[tmp[coluna] == "", coluna] = "Não informado"
    return tmp.rename(columns={coluna: nome_saida})


def filtrar_coluna_multivalor(df: pd.DataFrame, coluna: str, selecionados: list) -> pd.DataFrame:
    if not selecionados or coluna not in df.columns:
        return df
    selecionados = [str(x).strip() for x in selecionados if str(x).strip()]
    if not selecionados:
        return df
    padrao = "|".join(re.escape(x) for x in selecionados)
    return df[df[coluna].fillna("").astype(str).str.contains(padrao, case=False, regex=True, na=False)]


def calcular_hhi(series: pd.Series) -> float:
    if series is None or series.empty:
        return np.nan
    proporcoes = series.value_counts(normalize=True)
    if proporcoes.empty:
        return np.nan
    return float((proporcoes ** 2).sum())


def interpretar_hhi(hhi: float) -> str:
    if pd.isna(hhi):
        return "Não calculado"
    if hhi < 0.10:
        return "baixa concentração"
    if hhi < 0.18:
        return "concentração moderada"
    return "alta concentração"


def gerar_sintese_rodada(df: pd.DataFrame) -> str:
    if df.empty:
        return "Não há registros no recorte atual."
    total = len(df)
    hhi = calcular_hhi(df["fonte"]) if "fonte" in df.columns else np.nan
    tipo_top = df["tipo_fonte"].value_counts().idxmax() if "tipo_fonte" in df.columns and not df["tipo_fonte"].empty else "não identificado"
    eixo_df = explodir_lista_semicolon(df, "eixos_preconceito", "Eixo")
    enquad_df = explodir_lista_semicolon(df, "enquadramentos", "Enquadramento")
    eixo_top = eixo_df["Eixo"].value_counts().idxmax() if not eixo_df.empty else "não identificado"
    enquad_top = enquad_df["Enquadramento"].value_counts().idxmax() if not enquad_df.empty else "não identificado"
    hhi_txt = "não calculado" if pd.isna(hhi) else f"{hhi:.3f}"
    return (
        f"No recorte atual, há {total} notícias carregadas. "
        f"O tipo de fonte mais frequente é '{tipo_top}'. "
        f"O eixo temático mais recorrente é '{eixo_top}' e o enquadramento mais frequente é '{enquad_top}'. "
        f"O índice HHI por fonte é {hhi_txt}, indicando {interpretar_hhi(hhi)} da coleta."
    )

def aplicar_busca_textual(df: pd.DataFrame, consulta: str) -> pd.DataFrame:
    consulta = (consulta or "").strip().lower()
    if not consulta:
        return df

    termos = [t for t in consulta.split() if t.strip()]
    if not termos:
        return df

    df_busca = df.copy()
    colunas_texto = [
        "titulo", "resumo", "texto_completo", "fonte", "categoria_publica",
        "eixos_preconceito", "enquadramentos", "tipo_fonte", "regiao_fonte",
        "classificacao", "criterio_filtro"
    ]
    existentes = [c for c in colunas_texto if c in df_busca.columns]
    if not existentes:
        return df_busca

    df_busca["_texto_busca"] = ""
    for col in existentes:
        df_busca["_texto_busca"] = df_busca["_texto_busca"] + " " + df_busca[col].fillna("").astype(str)
    df_busca["_texto_busca"] = df_busca["_texto_busca"].str.lower()

    mascara = pd.Series(True, index=df_busca.index)
    for termo in termos:
        mascara = mascara & df_busca["_texto_busca"].str.contains(termo, regex=False, na=False)

    return df_busca[mascara].drop(columns=["_texto_busca"])

def preparar_serie_alerta_total(df_base: pd.DataFrame) -> pd.DataFrame:
    df_aux = df_base.copy()
    df_aux["data_plot"] = pd.to_datetime(df_aux["data_coleta"], errors="coerce")
    df_aux = df_aux.dropna(subset=["data_plot"])

    if df_aux.empty:
        return pd.DataFrame()

    if getattr(df_aux["data_plot"].dt, "tz", None) is None:
        df_aux["data_plot"] = df_aux["data_plot"].dt.tz_localize("UTC")

    df_aux["data_plot"] = df_aux["data_plot"].dt.tz_convert(FUSO_BRASIL).dt.normalize()

    serie = (
        df_aux.groupby("data_plot")
        .size()
        .rename("Quantidade")
        .reset_index()
        .sort_values("data_plot")
    )

    if serie.empty:
        return serie

    intervalo = pd.date_range(
        start=serie["data_plot"].min(),
        end=serie["data_plot"].max(),
        freq="D",
        tz=serie["data_plot"].dt.tz
    )

    serie = (
        serie.set_index("data_plot")
        .reindex(intervalo, fill_value=0)
        .rename_axis("data_plot")
        .reset_index()
    )

    serie["weekday"] = serie["data_plot"].dt.dayofweek
    serie["data_str"] = serie["data_plot"].dt.strftime("%Y-%m-%d")
    return serie


def _media_ponderada(valores: list[float]) -> float:
    if len(valores) == 0:
        return np.nan
    pesos = np.linspace(1.0, 2.0, num=len(valores))
    return float(np.average(valores, weights=pesos))


def _mad_robusto(x: np.ndarray) -> float:
    if len(x) == 0:
        return np.nan
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return float(1.4826 * mad)


def calcular_alertas_adaptativos(serie: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = serie.copy().sort_values("data_plot").reset_index(drop=True)
    n = len(df)

    meta = {
        "modelo": "insuficiente",
        "descricao": "Série ainda insuficiente para estimar padrão esperado com estabilidade.",
        "pontos_validos": n,
        "ativo": False
    }

    if n < 14:
        df["esperado"] = np.nan
        df["limite_superior"] = np.nan
        df["limite_inferior"] = np.nan
        df["alerta"] = False
        return df, meta

    y = df["Quantidade"].astype(float)

    if 14 <= n < 30:
        esperado = y.shift(1).rolling(7, min_periods=5).mean()
        sigma = y.shift(1).rolling(7, min_periods=5).std(ddof=0).fillna(0)
        modelo = "Média móvel 7 dias"
        descricao = "Modelo inicial com média móvel e dispersão recente."
    elif 30 <= n < 90:
        rolling_mean = y.shift(1).rolling(14, min_periods=7).mean()
        same_weekday = []
        for i in range(n):
            prev = df.iloc[:i]
            prev_same = prev.loc[prev["weekday"] == df.loc[i, "weekday"], "Quantidade"].tail(4).tolist()
            same_weekday.append(np.mean(prev_same) if len(prev_same) >= 2 else np.nan)
        same_weekday = pd.Series(same_weekday, index=df.index)
        esperado = 0.55 * same_weekday.fillna(rolling_mean) + 0.45 * rolling_mean.fillna(same_weekday)
        sigma_roll = y.shift(1).rolling(14, min_periods=7).std(ddof=0)
        sigma = pd.concat(
            [
                sigma_roll,
                np.sqrt(np.maximum(esperado, 1))
            ],
            axis=1
        ).max(axis=1)
        modelo = "Híbrido móvel + sazonalidade semanal"
        descricao = "Combina tendência recente com padrão por dia da semana."
    else:
        rolling_mean = y.shift(1).rolling(21, min_periods=10).mean()
        same_weekday_ew = []
        for i in range(n):
            prev = df.iloc[:i]
            prev_same = prev.loc[prev["weekday"] == df.loc[i, "weekday"], "Quantidade"].tail(8).tolist()
            same_weekday_ew.append(_media_ponderada(prev_same) if len(prev_same) >= 3 else np.nan)
        same_weekday_ew = pd.Series(same_weekday_ew, index=df.index)

        esperado = 0.60 * same_weekday_ew.fillna(rolling_mean) + 0.40 * rolling_mean.fillna(same_weekday_ew)

        erro_prev = (y.shift(1) - esperado.shift(1)).abs()
        sigma_rob = erro_prev.rolling(28, min_periods=10).apply(_mad_robusto, raw=True)
        sigma_fallback = pd.concat(
            [
                y.shift(1).rolling(21, min_periods=10).std(ddof=0),
                np.sqrt(np.maximum(esperado, 1))
            ],
            axis=1
        ).max(axis=1)

        sigma = sigma_rob.fillna(sigma_fallback)
        modelo = "Robusto sazonal adaptativo"
        descricao = "Combina tendência recente, sazonalidade semanal e banda robusta por erro absoluto."

    limite_superior = esperado + 2.0 * sigma
    limite_inferior = (esperado - 2.0 * sigma).clip(lower=0)

    df["esperado"] = esperado
    df["limite_superior"] = limite_superior
    df["limite_inferior"] = limite_inferior
    df["alerta"] = (df["Quantidade"] > df["limite_superior"]) & df["limite_superior"].notna()

    meta = {
        "modelo": modelo,
        "descricao": descricao,
        "pontos_validos": n,
        "ativo": True
    }
    return df, meta


def plotar_alertas_adaptativos(df_alerta: pd.DataFrame, meta: dict):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_alerta["data_str"],
        y=df_alerta["limite_superior"],
        mode="lines",
        name="Limite superior esperado",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=df_alerta["data_str"],
        y=df_alerta["esperado"],
        mode="lines",
        name="Linha esperada"
    ))

    fig.add_trace(go.Scatter(
        x=df_alerta["data_str"],
        y=df_alerta["Quantidade"],
        mode="lines+markers",
        name="Observado"
    ))

    df_alert = df_alerta[df_alerta["alerta"]].copy()
    if not df_alert.empty:
        fig.add_trace(go.Scatter(
            x=df_alert["data_str"],
            y=df_alert["Quantidade"],
            mode="markers",
            name="Alertas",
            marker=dict(size=10, symbol="circle-open")
        ))

    fig.update_layout(
        title=f"Alertas adaptativos — {meta['modelo']}",
        xaxis_title="Data",
        yaxis_title="Número de notícias",
        hovermode="x unified"
    )
    fig.update_xaxes(type="category", tickangle=-45)
    fig.update_yaxes(dtick=1, tickformat="d")
    return fig


def plotar_alertas_adaptativos_categoria(df_alerta: pd.DataFrame, meta: dict, titulo_categoria: str, ymax: float | None = None):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_alerta["data_str"],
        y=df_alerta["limite_superior"],
        mode="lines",
        name="Limite superior esperado",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=df_alerta["data_str"],
        y=df_alerta["esperado"],
        mode="lines",
        name="Linha esperada"
    ))

    fig.add_trace(go.Scatter(
        x=df_alerta["data_str"],
        y=df_alerta["Quantidade"],
        mode="lines+markers",
        name="Observado"
    ))

    df_alert = df_alerta[df_alerta["alerta"]].copy()
    if not df_alert.empty:
        fig.add_trace(go.Scatter(
            x=df_alert["data_str"],
            y=df_alert["Quantidade"],
            mode="markers",
            name="Alertas",
            marker=dict(size=10, symbol="circle-open")
        ))

    fig.update_layout(
        title=f"{titulo_categoria} — {meta['modelo']}",
        xaxis_title="Data",
        yaxis_title="Número de notícias",
        hovermode="x unified",
        showlegend=True
    )
    fig.update_xaxes(type="category", tickangle=-45)

    if ymax is not None and ymax > 0:
        fig.update_yaxes(range=[0, ymax])

    fig.update_yaxes(dtick=1, tickformat="d")

    return fig


if "noticia_id_aberta" not in st.session_state:
    st.session_state.noticia_id_aberta = None


def abrir_noticia(noticia_id: int):
    st.session_state.noticia_id_aberta = noticia_id


def fechar_noticia():
    st.session_state.noticia_id_aberta = None


css = """
<style>
.card-shell{
    background:#2b3a4a;
    border-radius:12px 12px 0 0;
    padding:12px;
    color:white;
    min-height:190px;
    box-shadow:2px 2px 5px rgba(0,0,0,0.3);
    display:flex;
    flex-direction:column;
}
.card-top{
    background:#1e2933;
    border-radius:6px;
    padding:4px 8px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    font-size:0.74rem;
    margin-bottom:10px;
}
.card-impact-track{
    width:100%;
    height:5px;
    background:rgba(255,255,255,0.10);
    border-radius:999px;
    overflow:hidden;
    margin-bottom:10px;
}
.card-title{
    font-weight:700;
    font-size:1rem;
    line-height:1.35;
    display:-webkit-box;
    -webkit-line-clamp:4;
    -webkit-box-orient:vertical;
    overflow:hidden;
    min-height:calc(1.35em * 4);
}
.card-date{
    font-size:0.74rem;
    color:#b7c0cc;
    margin-top:auto;
    padding-top:10px;
}
.overlay-meta {
    color: #4b5563;
    font-size: 0.95rem;
    margin-bottom: 10px;
}
.overlay-title {
    font-size: 1.35rem;
    line-height: 1.35;
    font-weight: 700;
    margin-bottom: 14px;
}
.overlay-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: #eef2ff;
    color: #3730a3;
    font-size: 0.79rem;
    font-weight: 600;
    margin-right: 7px;
    margin-bottom: 7px;
    border: 1px solid #dbe4ff;
}
.overlay-badge-tecnica {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: #f8fafc;
    color: #475569;
    font-size: 0.78rem;
    margin-right: 7px;
    margin-bottom: 7px;
    border: 1px solid #e2e8f0;
}
div[data-testid="stButton"] > button.tile-open {
    width: 100%;
    min-height: 2.25rem;
    margin-top: 0 !important;
    margin-bottom: 14px !important;
    border-radius: 0 0 12px 12px;
}
div[data-testid="stButton"] > button.botao-fechar-noticia {
    background: #b91c1c;
    color: white;
    border: 1px solid #991b1b;
    font-weight: 600;
}

div[data-testid="stButton"] > button.botao-fechar-noticia:hover {
    background: #991b1b;
    color: white;
    border: 1px solid #7f1d1d;
}

div[data-testid="stButton"] > button[kind="primary"] {
    font-weight: 700;
    border-radius: 10px;
    min-height: 2.5rem;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

col_a, col_b = st.columns([5, 1])
with col_a:
    st.title("Agregador de notícias sobre preconceitos e discursos de ódio")
with col_b:
    if st.button("Atualizar agora", key="btn_atualizar_agregador"):
        st.session_state.noticia_id_aberta = None
        st.cache_data.clear()
        st.rerun()

with st.expander("⚙️ Recorte da consulta ao banco", expanded=True):
    q1, q2 = st.columns([1, 1])

    with q1:
        periodo_consulta_label = st.selectbox(
            "Período-base da consulta",
            options=["Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Últimos 90 dias", "Tudo"],
            index=2,
            key="periodo_consulta_sql"
        )

    mapa_periodo_sql = {
        "Últimos 7 dias": "7 days",
        "Últimos 15 dias": "15 days",
        "Últimos 30 dias": "30 days",
        "Últimos 90 dias": "90 days",
        "Tudo": "tudo"
    }

    with q2:
        limite_consulta_sql = st.selectbox(
            "Limite máximo trazido do banco",
            options=[100, 200, 300, 500, 1000],
            index=2,
            key="limite_consulta_sql"
        )

periodo_sql = mapa_periodo_sql[periodo_consulta_label]
df_noticias, df_entidades, total_banco, erro_db = carregar_dados(periodo_sql, limite_consulta_sql)

if erro_db:
    st.error(f"Erro ao conectar ao Supabase: {erro_db}")

if not df_noticias.empty and "data_coleta" in df_noticias.columns:
    df_noticias["data_coleta_fmt"] = df_noticias["data_coleta"].apply(formatar_data_curta)
    data_mais_recente = formatar_data_curta(df_noticias["data_coleta"].max())
    df_noticias["categoria_publica"] = df_noticias.apply(categorizar_publicamente, axis=1)
    df_noticias = enriquecer_dataframe_analitico(df_noticias)
else:
    data_mais_recente = "—"

total_noticias = len(df_noticias)
total_entidades = len(df_entidades)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Notícias na janela atual", total_noticias)
m2.metric("Total no banco", total_banco)
m3.metric("Entidades", total_entidades)
m4.metric("Última coleta (Brasil)", data_mais_recente)

# =========================
# Painel de acompanhamento no topo
# =========================
if st.session_state.noticia_id_aberta is not None and not df_noticias.empty:
    selecionada_topo = df_noticias[df_noticias["id"] == st.session_state.noticia_id_aberta]
    entidades_rel_topo = pd.DataFrame()

    if not df_entidades.empty:
        entidades_rel_topo = df_entidades[
            df_entidades["noticia_id"] == st.session_state.noticia_id_aberta
        ].copy()

    if not selecionada_topo.empty:
        row_topo = selecionada_topo.iloc[0]

        st.markdown(
            """
            <style>
            .painel-foco {
                background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
                border: 1px solid #d7e2ef;
                border-radius: 20px;
                padding: 26px 28px 24px 28px;
                box-shadow: 0 18px 48px rgba(15, 23, 42, 0.14);
                margin: 14px 0 20px 0;
                position: relative;
                overflow: hidden;
            }

            .painel-foco::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 6px;
                background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
            }

            .painel-foco-meta {
                color: #6b7280;
                font-size: 0.92rem;
                letter-spacing: 0.01em;
                margin-bottom: 12px;
            }

            .painel-foco-titulo {
                color: #0f172a;
                font-size: 1.62rem;
                line-height: 1.32;
                font-weight: 750;
                margin-bottom: 16px;
            }

            .painel-foco-subsecao {
                color: #111827;
                font-size: 1.02rem;
                font-weight: 700;
                margin-top: 18px;
                margin-bottom: 10px;
            }

            .painel-foco-corpo {
                color: #1f2937;
                font-size: 1rem;
                line-height: 1.68;
            }
            .painel-foco-corpo p {
                margin: 0 0 0.75rem 0;
            }

.painel-foco-corpo p:last-child {
    margin-bottom: 0;
}

            .painel-foco-acoes {
                position: sticky;
                top: 0.5rem;
            }

            .painel-foco-nota {
                color: #6b7280;
                font-size: 0.84rem;
                margin-top: 8px;
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div id="painel-noticia-topo"></div>', unsafe_allow_html=True)

        box1, box2 = st.columns([7, 1.2], vertical_alignment="top")

        with box1:
            st.markdown('<div class="painel-foco">', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="painel-foco-meta">
                    {safe_text(row_topo["fonte"])} · {safe_text(formatar_data_curta(row_topo["data_coleta"]))}
                </div>
                <div class="painel-foco-titulo">
                    {safe_text(row_topo["titulo"])}
                </div>
                """,
                unsafe_allow_html=True
            )

            badges = []
            if "categoria_publica" in row_topo.index and pd.notna(row_topo["categoria_publica"]):
                badges.append(f'<span class="overlay-badge">{safe_text(row_topo["categoria_publica"])}</span>')

            if "classificacao" in row_topo.index and pd.notna(row_topo["classificacao"]):
                badges.append(f'<span class="overlay-badge-tecnica">triagem: {safe_text(row_topo["classificacao"])}</span>')

            if "criterio_filtro" in row_topo.index and pd.notna(row_topo["criterio_filtro"]):
                badges.append(f'<span class="overlay-badge-tecnica">critério: {safe_text(row_topo["criterio_filtro"])}</span>')

            if "score_relevancia" in row_topo.index and pd.notna(row_topo["score_relevancia"]):
                try:
                    badges.append(f'<span class="overlay-badge-tecnica">score {float(row_topo["score_relevancia"]):.3f}</span>')
                except Exception:
                    pass

            if "impacto" in row_topo.index and pd.notna(row_topo["impacto"]):
                badges.append(f'<span class="overlay-badge-tecnica">impacto {int(row_topo["impacto"])}</span>')

            st.markdown("".join(badges), unsafe_allow_html=True)

            texto_completo = None
            resumo = None
            url_fonte = None

            if "texto_completo" in row_topo.index and pd.notna(row_topo["texto_completo"]):
                texto_completo = str(row_topo["texto_completo"]).strip()
            if "resumo" in row_topo.index and pd.notna(row_topo["resumo"]):
                resumo = str(row_topo["resumo"]).strip()
            if "url_fonte" in row_topo.index and pd.notna(row_topo["url_fonte"]):
                url_fonte = str(row_topo["url_fonte"]).strip()

            st.markdown('<div class="painel-foco-subsecao">Texto da notícia</div>', unsafe_allow_html=True)

            if texto_completo:
                texto_html = texto_para_html_paragrafos(texto_completo)
                st.markdown(
                    f'<div class="painel-foco-corpo">{texto_html}</div>',
                    unsafe_allow_html=True
                )
            elif resumo:
                resumo_html = texto_para_html_paragrafos(resumo)
                st.markdown(
                    f'<div class="painel-foco-corpo">{resumo_html}</div>',
                    unsafe_allow_html=True
                )
                st.info("O banco tem apenas resumo para este item. O texto completo não foi capturado nesta coleta.")
            else:
                st.info(
                    "Este registro não tem texto completo armazenado. Para itens antigos, isso é esperado até uma nova coleta com o pipeline atualizado.")

            if url_fonte:
                st.link_button("Abrir fonte original", url_fonte)

            with st.expander("Mostrar metadados"):
                meta_cols = [
                    "id", "fonte", "data_coleta", "categoria_publica",
                    "classificacao", "criterio_filtro", "score_relevancia",
                    "url_fonte", "resumo"
                ]
                meta = {}
                for col in meta_cols:
                    if col in row_topo.index:
                        value = row_topo[col]
                        if col == "data_coleta" and not pd.isna(value):
                            meta[col] = formatar_data_curta(value)
                        else:
                            meta[col] = "—" if pd.isna(value) else value
                st.json(meta)

                st.markdown("**Entidades relacionadas**")
                if not entidades_rel_topo.empty:
                    entidades_rel_ordenadas = entidades_rel_topo.sort_values(by="tipo")
                    st.dataframe(
                        entidades_rel_ordenadas[["texto", "tipo"]].rename(
                            columns={"texto": "Entidade", "tipo": "Tipo"}
                        ),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.write("Nenhuma entidade extraída para este item.")

            st.markdown("---")
            st.markdown('<div style="display:flex;justify-content:flex-end;">', unsafe_allow_html=True)

            col_esp, col_btn = st.columns([6.5, 1.4])
            with col_btn:
                if st.button(
                        "Fechar",
                        key=f"fechar_painel_final_{int(row_topo['id'])}",
                        use_container_width=True,
                        type="primary"
                ):
                    fechar_noticia()
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        with box2:
            st.markdown("<div style='padding-top:4px;'></div>", unsafe_allow_html=True)
            if st.button(
                    "Fechar",
                    key=f"fechar_painel_topo_{int(row_topo['id'])}",
                    use_container_width=True,
                    type="primary"
            ):
                fechar_noticia()
                st.rerun()


            st.markdown('<div class="painel-foco-nota">Painel em foco</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <script>
            const el = window.parent.document.getElementById("painel-noticia-topo");
            if (el) {
                el.scrollIntoView({behavior: "smooth", block: "start"});
            }
            </script>
            """,
            unsafe_allow_html=True
        )

if df_noticias.empty:
    st.warning("Nenhuma notícia encontrada para o recorte atual.")
else:
    peso_entidades = df_entidades["texto"].value_counts().to_dict() if not df_entidades.empty else {}

    def calcular_impacto(noticia_id):
        if df_entidades.empty:
            return 1
        ents = df_entidades[df_entidades["noticia_id"] == noticia_id]["texto"]
        score = 1 + sum(peso_entidades.get(e, 0) for e in ents)
        return max(1, int(score))

    df_noticias["impacto"] = df_noticias["id"].apply(calcular_impacto)
    if "peso_tipo_fonte" in df_noticias.columns:
        df_noticias["impacto_ponderado"] = (df_noticias["impacto"].astype(float) * df_noticias["peso_tipo_fonte"].astype(float)).round(2)
    df_noticias["data_filtro"] = pd.to_datetime(df_noticias["data_coleta"], errors="coerce")

    if not df_noticias["data_filtro"].isna().all():
        if getattr(df_noticias["data_filtro"].dt, "tz", None) is None:
            df_noticias["data_filtro"] = df_noticias["data_filtro"].dt.tz_localize("UTC")
        df_noticias["data_filtro"] = df_noticias["data_filtro"].dt.tz_convert(FUSO_BRASIL)

    with st.expander("🔎 Filtros de exibição", expanded=True):
        f1, f2, f3, f4, f5 = st.columns([1.1, 1.4, 1.2, 0.8, 1.2])

        total_registros = int(len(df_noticias))

        opcoes_quantidade = [30, 60, 90, 120]
        opcoes_quantidade = [x for x in opcoes_quantidade if x < total_registros]
        if total_registros not in opcoes_quantidade and total_registros > 0:
            opcoes_quantidade.append(total_registros)
        opcoes_quantidade = sorted(set(opcoes_quantidade))

        with f1:
            filtro_periodo = st.selectbox(
                "Período",
                ["Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Tudo"],
                index=2,
                key="filtro_periodo_cards"
            )

        with f2:
            busca_textual = st.text_input(
                "Busca textual",
                value="",
                key="busca_textual_cards",
                placeholder="Ex: racismo escola torcida"
            )

        with f3:
            categorias_disponiveis = sorted(
                [x for x in df_noticias["categoria_publica"].dropna().astype(str).unique().tolist() if x.strip()]
            )
            filtro_categorias = st.multiselect(
                "Categorias",
                options=categorias_disponiveis,
                default=[],
                key="filtro_categorias_cards",
                placeholder="Selecione categorias"
            )

        with f4:
            limite_padrao = total_registros if total_registros <= 120 else 120
            index_limite = opcoes_quantidade.index(limite_padrao) if limite_padrao in opcoes_quantidade else max(0, len(opcoes_quantidade) - 1)
            limite_exibicao = st.selectbox(
                "Quantidade",
                opcoes_quantidade,
                index=index_limite,
                key="limite_exibicao_cards"
            )

        with f5:
            fontes_disponiveis_cards = sorted(
                [x for x in df_noticias["fonte"].dropna().astype(str).unique().tolist() if x.strip()]
            )
            filtro_fontes_cards = st.multiselect(
                "Portais",
                options=fontes_disponiveis_cards,
                default=[],
                key="filtro_fontes_cards",
                placeholder="Selecione portais"
            )

        fa1, fa2, fa3 = st.columns([1.4, 1.4, 1.2])
        with fa1:
            eixos_disponiveis = sorted(
                explodir_lista_semicolon(df_noticias, "eixos_preconceito", "Eixo")["Eixo"].dropna().unique().tolist()
            ) if "eixos_preconceito" in df_noticias.columns else []
            filtro_eixos_cards = st.multiselect(
                "Eixos analíticos",
                options=eixos_disponiveis,
                default=[],
                key="filtro_eixos_cards",
                placeholder="Ex: racismo, gênero, xenofobia"
            )

        with fa2:
            enquad_disponiveis = sorted(
                explodir_lista_semicolon(df_noticias, "enquadramentos", "Enquadramento")["Enquadramento"].dropna().unique().tolist()
            ) if "enquadramentos" in df_noticias.columns else []
            filtro_enquadramentos_cards = st.multiselect(
                "Enquadramentos",
                options=enquad_disponiveis,
                default=[],
                key="filtro_enquadramentos_cards",
                placeholder="Ex: ameaça, vítima, direitos"
            )

        with fa3:
            tipos_fonte_disponiveis = sorted(
                [x for x in df_noticias.get("tipo_fonte", pd.Series(dtype=str)).dropna().astype(str).unique().tolist() if x.strip()]
            )
            filtro_tipo_fonte_cards = st.multiselect(
                "Tipo de fonte",
                options=tipos_fonte_disponiveis,
                default=[],
                key="filtro_tipo_fonte_cards",
                placeholder="Selecione tipos"
            )

    df_cards = df_noticias.copy()

    if filtro_periodo != "Tudo" and not df_cards["data_filtro"].isna().all():
        agora_br = pd.Timestamp.now(tz=FUSO_BRASIL)
        dias_map = {
            "Últimos 7 dias": 7,
            "Últimos 15 dias": 15,
            "Últimos 30 dias": 30,
        }
        dias = dias_map.get(filtro_periodo)
        if dias is not None:
            limite_data = agora_br - pd.Timedelta(days=dias)
            df_cards = df_cards[df_cards["data_filtro"] >= limite_data]

    df_cards = aplicar_busca_textual(df_cards, busca_textual)

    if filtro_fontes_cards:
        df_cards = df_cards[df_cards["fonte"].isin(filtro_fontes_cards)]

    if filtro_categorias:
        df_cards = df_cards[df_cards["categoria_publica"].isin(filtro_categorias)]

    df_cards = filtrar_coluna_multivalor(df_cards, "eixos_preconceito", filtro_eixos_cards)
    df_cards = filtrar_coluna_multivalor(df_cards, "enquadramentos", filtro_enquadramentos_cards)

    if filtro_tipo_fonte_cards and "tipo_fonte" in df_cards.columns:
        df_cards = df_cards[df_cards["tipo_fonte"].isin(filtro_tipo_fonte_cards)]

    df_cards_filtrado_sem_limite = df_cards.copy()

    df_cards = df_cards.sort_values(
        by=["impacto", "data_coleta"],
        ascending=[False, False]
    ).head(limite_exibicao)

    if busca_textual.strip():
        st.caption(
            f"Exibindo {len(df_cards)} de {len(df_noticias)} notícias carregadas nesta consulta. "
            f"Busca ativa: “{busca_textual.strip()}”. O banco completo tem {total_banco} registros."
        )
    else:
        st.caption(
            f"Exibindo {len(df_cards)} de {len(df_noticias)} notícias carregadas nesta consulta. "
            f"O banco completo tem {total_banco} registros."
        )

    with st.expander("⬇️ Exportar recorte filtrado", expanded=False):
        st.caption("Exporta o recorte após filtros de período, busca, categoria, eixo, enquadramento, portal e tipo de fonte, antes do limite visual dos cards.")
        colunas_export = [
            c for c in [
                "id", "data_coleta", "fonte", "tipo_fonte", "regiao_fonte", "titulo", "url_fonte",
                "categoria_publica", "eixos_preconceito", "enquadramentos", "classificacao",
                "criterio_filtro", "score_relevancia", "impacto", "impacto_ponderado", "resumo"
            ] if c in df_cards_filtrado_sem_limite.columns
        ]
        df_export = df_cards_filtrado_sem_limite[colunas_export].copy() if colunas_export else df_cards_filtrado_sem_limite.copy()
        st.download_button(
            "Baixar CSV do recorte filtrado",
            data=df_export.to_csv(index=False).encode("utf-8-sig"),
            file_name="recorte_observatorio_preconceitos.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.dataframe(df_export.head(100), use_container_width=True, hide_index=True)

    QTD_COLUNAS = 3
    cols = st.columns(QTD_COLUNAS)

    for pos, (_, row) in enumerate(df_cards.iterrows()):
        impacto_val = int(row["impacto"])
        cor_borda = "#ff4b4b" if impacto_val >= 8 else "#ffb020" if impacto_val >= 4 else "#00d4ff"
        noticia_id = int(row["id"])
        largura_impacto = min(100, impacto_val * 10)

        with cols[pos % QTD_COLUNAS]:
            st.markdown(
                f"""
                <div class="card-shell" style="border-left:5px solid {cor_borda};">
                    <div class="card-top">
                        <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:72%;">{safe_text(row['fonte'])}</span>
                        <span style="color:#ffb020;flex-shrink:0;">&#128293; {impacto_val}</span>
                    </div>
                    <div class="card-impact-track">
                        <div style="width:{largura_impacto}%;height:5px;background:{cor_borda};border-radius:999px;"></div>
                    </div>
                    <div class="card-title">{safe_text(row['titulo'])}</div>
                    <div class="card-date">{safe_text(row.get('data_coleta_fmt', row['data_coleta']))}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.button(
                "Acompanhar notícia",
                key=f"abrir_{noticia_id}",
                on_click=abrir_noticia,
                args=(noticia_id,),
                type="secondary"
            )

    st.markdown(
        """
        <script>
        const buttons = window.parent.document.querySelectorAll('div[data-testid="stButton"] button');
        buttons.forEach(btn => {
          if (btn.innerText.trim() === 'Acompanhar notícia') {
            btn.classList.add('tile-open');
          }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    with st.expander("🕒 Linha do tempo das notícias"):
        df_tempo = df_noticias.copy()
        df_tempo["data_plot"] = pd.to_datetime(df_tempo["data_coleta"], errors="coerce")
        df_tempo = df_tempo.dropna(subset=["data_plot"])

        if not df_tempo.empty:
            if getattr(df_tempo["data_plot"].dt, "tz", None) is None:
                df_tempo["data_plot"] = df_tempo["data_plot"].dt.tz_localize("UTC")
            df_tempo["data_plot"] = df_tempo["data_plot"].dt.tz_convert(FUSO_BRASIL).dt.normalize()

        if df_tempo.empty:
            st.info("Não há datas válidas para montar a linha do tempo.")
        else:
            col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 2])

            with col_ctrl1:
                granularidade = st.selectbox(
                    "Granularidade",
                    options=["Diária", "Semanal", "Mensal"],
                    index=0,
                    key="timeline_granularidade"
                )

            with col_ctrl2:
                modo_linha = st.selectbox(
                    "Modo",
                    options=[
                        "Linha única",
                        "Por categorias",
                        "Por portal",
                        "Alertas adaptativos",
                        "Alertas por categorias"
                    ],
                    index=0,
                    key="timeline_modo"
                )

            with col_ctrl3:
                fontes_disponiveis = sorted(
                    [f for f in df_tempo["fonte"].dropna().unique().tolist() if str(f).strip()]
                )
                filtro_fontes = st.multiselect(
                    "Filtrar portais",
                    options=fontes_disponiveis,
                    default=[],
                    key="timeline_fontes",
                    placeholder="Selecione portais"
                )

            if filtro_fontes:
                df_tempo = df_tempo[df_tempo["fonte"].isin(filtro_fontes)]

            if df_tempo.empty:
                st.info("Os filtros atuais não retornaram notícias.")
            else:
                if modo_linha == "Alertas adaptativos":
                    if granularidade != "Diária":
                        st.info("Os alertas adaptativos estão habilitados apenas para a granularidade diária.")
                    else:
                        serie_alerta = preparar_serie_alerta_total(df_tempo)
                        df_alerta, meta_alerta = calcular_alertas_adaptativos(serie_alerta)

                        if not meta_alerta["ativo"]:
                            st.warning(
                                f"{meta_alerta['descricao']} "
                                f"Atualmente há {meta_alerta['pontos_validos']} pontos diários na série."
                            )
                        else:
                            fig_alerta = plotar_alertas_adaptativos(df_alerta, meta_alerta)
                            st.plotly_chart(
                                fig_alerta,
                                use_container_width=True,
                                key="plot_alertas_adaptativos"
                            )

                            ultimo_valido = df_alerta.dropna(subset=["esperado"]).copy()
                            if not ultimo_valido.empty:
                                ultima = ultimo_valido.iloc[-1]
                                total_alertas = int(df_alerta["alerta"].sum())

                                c1, c2, c3, c4 = st.columns(4)
                                c1.metric("Modelo ativo", meta_alerta["modelo"])
                                c2.metric("Observado mais recente", int(ultima["Quantidade"]))
                                c3.metric("Esperado mais recente", round(float(ultima["esperado"]), 2))
                                c4.metric("Dias em alerta", total_alertas)

                            st.caption(meta_alerta["descricao"])

                            with st.expander("Ver tabela do indicador adaptativo"):
                                tabela_alerta = df_alerta.copy()
                                tabela_alerta["Alerta"] = np.where(tabela_alerta["alerta"], "Sim", "Não")
                                st.dataframe(
                                    tabela_alerta[
                                        ["data_str", "Quantidade", "esperado", "limite_superior", "Alerta"]
                                    ].rename(columns={
                                        "data_str": "Data",
                                        "Quantidade": "Observado",
                                        "esperado": "Esperado",
                                        "limite_superior": "Limite superior"
                                    }),
                                    use_container_width=True,
                                    hide_index=True
                                )

                elif modo_linha == "Alertas por categorias":
                    if granularidade != "Diária":
                        st.info("Os alertas por categoria estão habilitados apenas para a granularidade diária.")
                    else:
                        categorias_disp = sorted(
                            [c for c in df_tempo["categoria_publica"].dropna().astype(str).unique().tolist() if c.strip()]
                        )

                        categorias_sel = st.multiselect(
                            "Selecione as categorias para comparar",
                            options=categorias_disp,
                            default=categorias_disp[:3] if len(categorias_disp) >= 3 else categorias_disp,
                            key="categorias_alerta_timeline",
                            placeholder="Selecione categorias"
                        )

                        if not categorias_sel:
                            st.info("Selecione ao menos uma categorias.")
                        else:
                            resultados = []
                            ymax_global = 0.0

                            for cat in categorias_sel:
                                df_cat = df_tempo[df_tempo["categoria_publica"] == cat].copy()
                                serie_cat = preparar_serie_alerta_total(df_cat)
                                df_alerta_cat, meta_cat = calcular_alertas_adaptativos(serie_cat)

                                if not df_alerta_cat.empty:
                                    max_local = pd.concat(
                                        [
                                            df_alerta_cat["Quantidade"],
                                            df_alerta_cat["limite_superior"].fillna(0)
                                        ],
                                        axis=0
                                    ).max()
                                    ymax_global = max(ymax_global, float(max_local))

                                resultados.append((cat, df_alerta_cat, meta_cat))

                            if ymax_global <= 0:
                                ymax_global = 1.0
                            else:
                                ymax_global *= 1.10

                            resumo_alertas = []

                            for i, (cat, df_alerta_cat, meta_cat) in enumerate(resultados):
                                st.markdown(f"### {cat}")

                                if not meta_cat["ativo"]:
                                    st.warning(
                                        f"{meta_cat['descricao']} "
                                        f"Atualmente há {meta_cat['pontos_validos']} pontos diários para esta categoria."
                                    )
                                    continue

                                fig_cat = plotar_alertas_adaptativos_categoria(
                                    df_alerta_cat,
                                    meta_cat,
                                    titulo_categoria=cat,
                                    ymax=ymax_global
                                )

                                st.plotly_chart(
                                    fig_cat,
                                    use_container_width=True,
                                    key=f"plot_alerta_categoria_{i}_{cat}"
                                )

                                ultimo_valido = df_alerta_cat.dropna(subset=["esperado"]).copy()
                                total_alertas_cat = int(df_alerta_cat["alerta"].sum())

                                if not ultimo_valido.empty:
                                    ultima = ultimo_valido.iloc[-1]
                                    c1, c2, c3, c4 = st.columns(4)
                                    c1.metric("Modelo ativo", meta_cat["modelo"])
                                    c2.metric("Observado mais recente", int(ultima["Quantidade"]))
                                    c3.metric("Esperado mais recente", round(float(ultima["esperado"]), 2))
                                    c4.metric("Dias em alerta", total_alertas_cat)

                                resumo_alertas.append({
                                    "Categoria pública": cat,
                                    "Modelo": meta_cat["modelo"],
                                    "Dias em alerta": total_alertas_cat
                                })

                            if resumo_alertas:
                                with st.expander("Resumo comparativo dos alertas por categoria"):
                                    st.dataframe(
                                        pd.DataFrame(resumo_alertas).sort_values("Dias em alerta", ascending=False),
                                        use_container_width=True,
                                        hide_index=True
                                    )

                else:
                    freq_map = {
                        "Diária": "D",
                        "Semanal": "W-MON",
                        "Mensal": "MS"
                    }
                    freq_escolhida = freq_map[granularidade]

                    def preparar_serie_unica(df_base: pd.DataFrame, freq: str, granularidade_txt: str) -> pd.DataFrame:
                        serie = (
                            df_base
                            .set_index("data_plot")
                            .resample(freq)
                            .size()
                            .rename("Quantidade")
                            .reset_index()
                        )

                        if not serie.empty:
                            intervalo = pd.date_range(
                                start=serie["data_plot"].min(),
                                end=serie["data_plot"].max(),
                                freq=freq
                            )
                            serie = (
                                serie
                                .set_index("data_plot")
                                .reindex(intervalo, fill_value=0)
                                .rename_axis("data_plot")
                                .reset_index()
                            )

                        if granularidade_txt == "Mensal":
                            serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m")
                        else:
                            serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m-%d")

                        return serie

                    def preparar_serie_categoria(df_base: pd.DataFrame, freq: str, coluna: str, nome_coluna: str,
                                                 granularidade_txt: str) -> pd.DataFrame:
                        df_aux = df_base.copy()
                        df_aux[coluna] = df_aux[coluna].fillna("Não informado").astype(str).str.strip()
                        df_aux.loc[df_aux[coluna] == "", coluna] = "Não informado"

                        serie = (
                            df_aux
                            .groupby([pd.Grouper(key="data_plot", freq=freq), coluna])
                            .size()
                            .reset_index(name="Quantidade")
                            .rename(columns={coluna: nome_coluna})
                        )

                        if serie.empty:
                            return serie

                        categorias = sorted(serie[nome_coluna].dropna().unique().tolist())
                        datas = pd.date_range(
                            start=serie["data_plot"].min(),
                            end=serie["data_plot"].max(),
                            freq=freq
                        )

                        grade = pd.MultiIndex.from_product(
                            [datas, categorias],
                            names=["data_plot", nome_coluna]
                        )

                        serie = (
                            serie
                            .set_index(["data_plot", nome_coluna])
                            .reindex(grade, fill_value=0)
                            .reset_index()
                        )

                        if granularidade_txt == "Mensal":
                            serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m")
                        else:
                            serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m-%d")

                        return serie

                    if modo_linha == "Linha única":
                        serie_tempo = preparar_serie_unica(df_tempo, freq_escolhida, granularidade)
                        fig_tempo = px.line(
                            serie_tempo,
                            x="data_str",
                            y="Quantidade",
                            markers=True,
                            title=f"Evolução temporal das notícias ({granularidade.lower()})"
                        )
                        tabela_exibicao = serie_tempo.copy()


                    elif modo_linha == "Por categorias":
                        serie_tempo = preparar_serie_categoria(
                            df_tempo,
                            freq_escolhida,
                            "categoria_publica",
                            "Categoria pública",
                            granularidade
                        )
                        fig_tempo = px.line(
                            serie_tempo,
                            x="data_str",
                            y="Quantidade",
                            color="Categoria pública",
                            markers=True,
                            title=f"Evolução temporal por categoria pública ({granularidade.lower()})"
                        )
                        tabela_exibicao = serie_tempo.copy()

                    else:
                        serie_tempo = preparar_serie_categoria(
                            df_tempo,
                            freq_escolhida,
                            "fonte",
                            "Portal",
                            granularidade
                        )
                        fig_tempo = px.line(
                            serie_tempo,
                            x="data_str",
                            y="Quantidade",
                            color="Portal",
                            markers=True,
                            title=f"Evolução temporal por portal ({granularidade.lower()})"
                        )
                        tabela_exibicao = serie_tempo.copy()

                    fig_tempo.update_layout(
                        xaxis_title="Data",
                        yaxis_title="Número de notícias",
                        hovermode="x unified"
                    )
                    fig_tempo.update_xaxes(type="category", tickangle=-45)
                    fig_tempo.update_yaxes(dtick=1, tickformat="d")

                    st.plotly_chart(
                        fig_tempo,
                        use_container_width=True,
                        key=f"plot_timeline_{granularidade}_{modo_linha}_{'_'.join(filtro_fontes) if filtro_fontes else 'todos'}"
                    )

                    if modo_linha == "Linha única":
                        total_periodo = int(tabela_exibicao["Quantidade"].sum())
                        pico = int(tabela_exibicao["Quantidade"].max()) if not tabela_exibicao.empty else 0
                        periodos_com_registro = int((tabela_exibicao["Quantidade"] > 0).sum())

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Períodos com registro", periodos_com_registro)
                        c2.metric("Pico no período", pico)
                        c3.metric("Total no período", total_periodo)
                    else:
                        total_periodo = int(tabela_exibicao["Quantidade"].sum())
                        pico = int(tabela_exibicao["Quantidade"].max()) if not tabela_exibicao.empty else 0
                        n_series = int(tabela_exibicao.iloc[:, 1].nunique()) if not tabela_exibicao.empty else 0

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Séries exibidas", n_series)
                        c2.metric("Pico em uma série", pico)
                        c3.metric("Total no período", total_periodo)

                    with st.expander("Ver tabela da série temporal"):
                        if modo_linha == "Linha única":
                            st.dataframe(
                                tabela_exibicao[["data_str", "Quantidade"]].rename(columns={"data_str": "Data"}),
                                use_container_width=True,
                                hide_index=True
                            )
                        elif modo_linha == "Por categorias":
                            st.dataframe(
                                tabela_exibicao[["data_str", "Categoria pública", "Quantidade"]].rename(columns={"data_str": "Data"}),
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.dataframe(
                                tabela_exibicao[["data_str", "Portal", "Quantidade"]].rename(columns={"data_str": "Data"}),
                                use_container_width=True,
                                hide_index=True
                            )

    with st.expander("📊 Estatística dos Portais"):
        stats_fonte = df_noticias["fonte"].value_counts().reset_index()
        stats_fonte.columns = ["Portal", "Quantidade"]
        fig = px.bar(
            stats_fonte,
            x="Portal",
            y="Quantidade",
            title="Volume de notícias por fonte"
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="plot_estatistica_portais"
        )

    with st.expander("🏷️ Distribuição por categoria pública"):
        stats_cat = df_noticias["categoria_publica"].value_counts().reset_index()
        stats_cat.columns = ["Categoria pública", "Quantidade"]
        fig_cat = px.bar(
            stats_cat,
            x="Categoria pública",
            y="Quantidade",
            title="Distribuição das notícias por categorias"
        )
        fig_cat.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(
            fig_cat,
            use_container_width=True,
            key="plot_categorias_publicas"
        )

    with st.expander("🧭 Representatividade da coleta", expanded=False):
        st.markdown("**Síntese automática da rodada**")
        st.info(gerar_sintese_rodada(df_noticias))

        hhi_fonte = calcular_hhi(df_noticias["fonte"]) if "fonte" in df_noticias.columns else np.nan
        hhi_tipo = calcular_hhi(df_noticias["tipo_fonte"]) if "tipo_fonte" in df_noticias.columns else np.nan
        n_fontes = int(df_noticias["fonte"].nunique()) if "fonte" in df_noticias.columns else 0
        n_tipos = int(df_noticias["tipo_fonte"].nunique()) if "tipo_fonte" in df_noticias.columns else 0

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Fontes distintas", n_fontes)
        r2.metric("Tipos de fonte", n_tipos)
        r3.metric("HHI por fonte", "—" if pd.isna(hhi_fonte) else f"{hhi_fonte:.3f}")
        r4.metric("Concentração", interpretar_hhi(hhi_fonte))

        c_rep1, c_rep2 = st.columns(2)
        with c_rep1:
            if "tipo_fonte" in df_noticias.columns:
                stats_tipo = df_noticias["tipo_fonte"].value_counts().reset_index()
                stats_tipo.columns = ["Tipo de fonte", "Quantidade"]
                fig_tipo = px.bar(stats_tipo, x="Tipo de fonte", y="Quantidade", title="Distribuição por tipo de fonte")
                fig_tipo.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig_tipo, use_container_width=True, key="plot_tipo_fonte_representatividade")
        with c_rep2:
            if "regiao_fonte" in df_noticias.columns:
                stats_regiao = df_noticias["regiao_fonte"].value_counts().reset_index()
                stats_regiao.columns = ["Região inferida", "Quantidade"]
                fig_regiao = px.bar(stats_regiao, x="Região inferida", y="Quantidade", title="Distribuição por região inferida da fonte")
                fig_regiao.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig_regiao, use_container_width=True, key="plot_regiao_fonte_representatividade")

        with st.expander("Tabela de fontes, tipos e regiões inferidas"):
            if "fonte" in df_noticias.columns:
                cols_tab = [c for c in ["fonte", "tipo_fonte", "regiao_fonte"] if c in df_noticias.columns]
                tab_fontes = df_noticias[cols_tab].drop_duplicates().sort_values(cols_tab).rename(columns={"fonte": "Fonte", "tipo_fonte": "Tipo de fonte", "regiao_fonte": "Região inferida"})
                st.dataframe(tab_fontes, use_container_width=True, hide_index=True)

    with st.expander("🧩 Eixos analíticos e enquadramentos", expanded=False):
        eixos_long = explodir_lista_semicolon(df_noticias, "eixos_preconceito", "Eixo")
        enquad_long = explodir_lista_semicolon(df_noticias, "enquadramentos", "Enquadramento")
        ce1, ce2 = st.columns(2)
        with ce1:
            if not eixos_long.empty:
                stats_eixos = eixos_long["Eixo"].value_counts().reset_index()
                stats_eixos.columns = ["Eixo", "Quantidade"]
                fig_eixos = px.bar(stats_eixos, y="Eixo", x="Quantidade", orientation="h", title="Eixos temáticos de preconceito/estigma")
                fig_eixos.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_eixos, use_container_width=True, key="plot_eixos_preconceito")
            else:
                st.info("Não há eixos temáticos identificados no recorte atual.")
        with ce2:
            if not enquad_long.empty:
                stats_enq = enquad_long["Enquadramento"].value_counts().reset_index()
                stats_enq.columns = ["Enquadramento", "Quantidade"]
                fig_enq = px.bar(stats_enq, y="Enquadramento", x="Quantidade", orientation="h", title="Enquadramentos discursivos")
                fig_enq.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_enq, use_container_width=True, key="plot_enquadramentos")
            else:
                st.info("Não há enquadramentos identificados no recorte atual.")

        if "eixos_preconceito" in df_noticias.columns and "enquadramentos" in df_noticias.columns:
            matriz_base = df_noticias[["id", "eixos_preconceito", "enquadramentos"]].copy()
            matriz_base["Eixo"] = matriz_base["eixos_preconceito"].fillna("Não informado").astype(str).str.split(";")
            matriz_base = matriz_base.explode("Eixo")
            matriz_base["Eixo"] = matriz_base["Eixo"].astype(str).str.strip()
            matriz_base["Enquadramento"] = matriz_base["enquadramentos"].fillna("Não informado").astype(str).str.split(";")
            matriz_base = matriz_base.explode("Enquadramento")
            matriz_base["Enquadramento"] = matriz_base["Enquadramento"].astype(str).str.strip()
            matriz = pd.crosstab(matriz_base["Eixo"], matriz_base["Enquadramento"])
            if not matriz.empty:
                fig_heat = px.imshow(matriz, text_auto=True, aspect="auto", title="Matriz eixo temático × enquadramento discursivo")
                st.plotly_chart(fig_heat, use_container_width=True, key="plot_matriz_eixo_enquadramento")
                with st.expander("Ver tabela da matriz eixo × enquadramento"):
                    st.dataframe(matriz.reset_index(), use_container_width=True, hide_index=True)

    with st.expander("🎯 Temas e personagens (NER)"):
        if not df_entidades.empty:
            stats_temas = df_entidades["texto"].value_counts().head(20).reset_index()
            stats_temas.columns = ["Entidade", "Frequência"]
            fig2 = px.bar(
                stats_temas,
                y="Entidade",
                x="Frequência",
                orientation="h",
                title="Top 20 entidades mais frequentes"
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(
                fig2,
                use_container_width=True,
                key="plot_top_entidades"
            )
        else:
            st.info("Ainda não há entidades extraídas para exibir.")

