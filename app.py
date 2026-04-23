import os
import html
import numpy as np

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


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


def aplicar_busca_textual(df: pd.DataFrame, consulta: str) -> pd.DataFrame:
    consulta = (consulta or "").strip().lower()
    if not consulta:
        return df

    termos = [t for t in consulta.split() if t.strip()]
    if not termos:
        return df

    df_busca = df.copy()
    df_busca["_texto_busca"] = (
        df_busca["titulo"].fillna("").astype(str) + " "
        + df_busca["resumo"].fillna("").astype(str) + " "
        + df_busca["texto_completo"].fillna("").astype(str) + " "
        + df_busca["fonte"].fillna("").astype(str) + " "
        + df_busca["categoria_publica"].fillna("").astype(str)
    ).str.lower()

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
    padding: 4px 8px;
    border-radius: 999px;
    background: #eef2ff;
    color: #3730a3;
    font-size: 0.8rem;
    margin-right: 6px;
    margin-bottom: 6px;
}
.overlay-badge-tecnica {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    background: #f3f4f6;
    color: #4b5563;
    font-size: 0.8rem;
    margin-right: 6px;
    margin-bottom: 6px;
}
div[data-testid="stButton"] > button.tile-open {
    width: 100%;
    min-height: 2.25rem;
    margin-top: 0 !important;
    margin-bottom: 14px !important;
    border-radius: 0 0 12px 12px;
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
else:
    data_mais_recente = "—"

total_noticias = len(df_noticias)
total_entidades = len(df_entidades)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Notícias na janela atual", total_noticias)
m2.metric("Total no banco", total_banco)
m3.metric("Entidades", total_entidades)
m4.metric("Última coleta (Brasil)", data_mais_recente)

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
                "Categorias públicas",
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
                    options=["Linha única", "Por categoria pública", "Por portal", "Alertas adaptativos", "Alertas por categoria pública"],
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

                elif modo_linha == "Alertas por categoria pública":
                    if granularidade != "Diária":
                        st.info("Os alertas por categoria pública estão habilitados apenas para a granularidade diária.")
                    else:
                        categorias_disp = sorted(
                            [c for c in df_tempo["categoria_publica"].dropna().astype(str).unique().tolist() if c.strip()]
                        )

                        categorias_sel = st.multiselect(
                            "Selecione as categorias para comparar",
                            options=categorias_disp,
                            default=categorias_disp[:3] if len(categorias_disp) >= 3 else categorias_disp,
                            key="categorias_alerta_timeline",
                            placeholder="Selecione categorias públicas"
                        )

                        if not categorias_sel:
                            st.info("Selecione ao menos uma categoria pública.")
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

                    elif modo_linha == "Por categoria pública":
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
                        elif modo_linha == "Por categoria pública":
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
            title="Distribuição das notícias por categoria pública"
        )
        fig_cat.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(
            fig_cat,
            use_container_width=True,
            key="plot_categorias_publicas"
        )

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

if st.session_state.noticia_id_aberta is not None and not df_noticias.empty:
    selecionada = df_noticias[df_noticias["id"] == st.session_state.noticia_id_aberta]
    entidades_rel = pd.DataFrame()

    if not df_entidades.empty:
        entidades_rel = df_entidades[
            df_entidades["noticia_id"] == st.session_state.noticia_id_aberta
        ].copy()

    if not selecionada.empty:
        row = selecionada.iloc[0]

        st.markdown(
            """
            <style>
            .overlay-backdrop {
                position: fixed;
                inset: 0;
                background: rgba(17, 24, 39, 0.52);
                z-index: 999990;
                pointer-events: none;
            }

            .overlay-anchor {
                position: relative;
                z-index: 999991;
            }

            .overlay-shell {
                max-width: 1080px;
                margin: 0 auto 24px auto;
                background: #ffffff;
                border-radius: 18px;
                box-shadow: 0 18px 50px rgba(0,0,0,0.28);
                border: 1px solid #e5e7eb;
                overflow: hidden;
            }

            .overlay-shell-inner {
                padding: 22px 24px 24px 24px;
            }

            .overlay-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 18px;
                margin-bottom: 8px;
            }

            .overlay-header-left {
                min-width: 0;
                flex: 1;
            }

            .overlay-meta-fake {
                color: #4b5563;
                font-size: 0.95rem;
                margin-bottom: 10px;
            }

            .overlay-title-fake {
                color: #111827;
                font-size: 1.45rem;
                line-height: 1.35;
                font-weight: 700;
                margin-bottom: 14px;
            }

            .overlay-body-wrap {
                max-height: 72vh;
                overflow-y: auto;
                padding-right: 4px;
            }

            .overlay-body-wrap::-webkit-scrollbar {
                width: 10px;
            }

            .overlay-body-wrap::-webkit-scrollbar-thumb {
                background: #c7cdd6;
                border-radius: 999px;
            }

            .overlay-body-wrap::-webkit-scrollbar-track {
                background: #eef2f7;
                border-radius: 999px;
            }

            .overlay-floating-note {
                color: #6b7280;
                font-size: 0.84rem;
                margin-bottom: 8px;
            }

            .overlay-close-area {
                min-width: 120px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="overlay-backdrop"></div>', unsafe_allow_html=True)
        st.markdown('<div class="overlay-anchor" id="overlay-noticia-anchor">', unsafe_allow_html=True)

        container_overlay = st.container(border=False)
        with container_overlay:
            st.markdown('<div class="overlay-shell"><div class="overlay-shell-inner">', unsafe_allow_html=True)

            topo_esq, topo_dir = st.columns([8, 1.3], vertical_alignment="top")

            with topo_esq:
                st.markdown(
                    f"""
                    <div class="overlay-meta-fake">
                        {safe_text(row["fonte"])} · {safe_text(formatar_data_curta(row["data_coleta"]))}
                    </div>
                    <div class="overlay-title-fake">
                        {safe_text(row["titulo"])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with topo_dir:
                st.markdown('<div class="overlay-close-area">', unsafe_allow_html=True)
                if st.button("Fechar", key=f"fechar_overlay_{int(row['id'])}", use_container_width=True):
                    fechar_noticia()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            badges = []
            if "categoria_publica" in row.index and pd.notna(row["categoria_publica"]):
                badges.append(f'<span class="overlay-badge">{safe_text(row["categoria_publica"])}</span>')

            if "classificacao" in row.index and pd.notna(row["classificacao"]):
                badges.append(f'<span class="overlay-badge-tecnica">triagem: {safe_text(row["classificacao"])}</span>')

            if "criterio_filtro" in row.index and pd.notna(row["criterio_filtro"]):
                badges.append(f'<span class="overlay-badge-tecnica">critério: {safe_text(row["criterio_filtro"])}</span>')

            if "score_relevancia" in row.index and pd.notna(row["score_relevancia"]):
                try:
                    badges.append(f'<span class="overlay-badge-tecnica">score {float(row["score_relevancia"]):.3f}</span>')
                except Exception:
                    pass

            if "impacto" in row.index and pd.notna(row["impacto"]):
                badges.append(f'<span class="overlay-badge-tecnica">impacto {int(row["impacto"])}</span>')

            st.markdown("".join(badges), unsafe_allow_html=True)
            st.markdown('<div class="overlay-body-wrap">', unsafe_allow_html=True)

            texto_completo = None
            resumo = None
            url_fonte = None

            if "texto_completo" in row.index and pd.notna(row["texto_completo"]):
                texto_completo = str(row["texto_completo"]).strip()
            if "resumo" in row.index and pd.notna(row["resumo"]):
                resumo = str(row["resumo"]).strip()
            if "url_fonte" in row.index and pd.notna(row["url_fonte"]):
                url_fonte = str(row["url_fonte"]).strip()

            st.subheader("Texto da notícia")
            if texto_completo:
                st.markdown(texto_completo.replace("\n", "\n\n"))
            elif resumo:
                st.markdown(resumo)
                st.info("O banco tem apenas resumo para este item. O texto completo não foi capturado nesta coleta.")
            else:
                st.info("Este registro não tem texto completo armazenado. Para itens antigos, isso é esperado até uma nova coleta com o pipeline atualizado.")

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
                    if col in row.index:
                        value = row[col]
                        if col == "data_coleta" and not pd.isna(value):
                            meta[col] = formatar_data_curta(value)
                        else:
                            meta[col] = "—" if pd.isna(value) else value
                st.json(meta)

                st.markdown("**Entidades relacionadas**")
                if not entidades_rel.empty:
                    entidades_rel_ordenadas = entidades_rel.sort_values(by="tipo")
                    st.dataframe(
                        entidades_rel_ordenadas[["texto", "tipo"]].rename(
                            columns={"texto": "Entidade", "tipo": "Tipo"}
                        ),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.write("Nenhuma entidade extraída para este item.")

            st.markdown('</div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <script>
            const anchor = window.parent.document.getElementById("overlay-noticia-anchor");
            if (anchor) {
                anchor.scrollIntoView({behavior: "smooth", block: "start"});
            }
            </script>
            """,
            unsafe_allow_html=True
        )