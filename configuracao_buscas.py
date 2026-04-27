"""
Configuração ampliada e curada dos portais de busca — versão expandida.

Mudanças desta versão em relação à anterior:
- Corrigida duplicata: Gazeta_do_Povo (seções 2 e 7 tinham a mesma URL)
- Adicionados ~130 novos portais em 15 novos blocos temáticos
- Novos blocos: agências públicas, fact-checkers, esportes, tecnologia/ciência,
  saúde, agronegócio, trabalho/sindical, jurídico, evangélico/religioso,
  cultura/entretenimento, LGBTQIA+, povos indígenas, meio ambiente/amazônia,
  jornalismo comunitário/periférico, capitais (portais municipais),
  complementos regionais por estado, internacionais ampliados.

Observações:
- seletores CSS podem mudar; revise periodicamente portais com 0 títulos.
- em testes, comente blocos inteiros para rodar em lotes menores.
- URLs marcadas com # [VERIFICAR] indicam portais que podem ter mudado de endereço.
"""

PORTAIS_CONFIG = {

    # ==========================================================
    # 1. GRANDES PORTAIS NACIONAIS
    # ==========================================================
    "G1":               {"url": "https://g1.globo.com/",                "estrategia": "playwright", "seletor": "h2"},
    "Folha_SP":         {"url": "https://www1.folha.uol.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Estadao_SP":       {"url": "https://www.estadao.com.br/",          "estrategia": "playwright", "seletor": "h3"},
    "UOL":              {"url": "https://www.uol.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Metropoles_DF":    {"url": "https://www.metropoles.com/",          "estrategia": "playwright", "seletor": "h2"},
    "CNN_Brasil":       {"url": "https://www.cnnbrasil.com.br/",        "estrategia": "playwright", "seletor": "h2"},
    "R7":               {"url": "https://noticias.r7.com/",             "estrategia": "playwright", "seletor": "h3"},
    "SBT_News":         {"url": "https://sbtnews.sbt.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Band":             {"url": "https://www.band.uol.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Terra":            {"url": "https://www.terra.com.br/noticias/",   "estrategia": "playwright", "seletor": "h2"},
    "IG":               {"url": "https://ig.com.br/",                   "estrategia": "playwright", "seletor": "h2"},
    "MSN_Brasil":       {"url": "https://www.msn.com/pt-br/noticias",   "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 2. POLÍTICA / OPINIÃO / ESPECTRO EDITORIAL
    # ==========================================================
    "Poder360":             {"url": "https://www.poder360.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Congresso_em_Foco":    {"url": "https://congressoemfoco.uol.com.br/",       "estrategia": "playwright", "seletor": "h3"},
    "Carta_Capital":        {"url": "https://www.cartacapital.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Revista_Forum":        {"url": "https://revistaforum.com.br/",              "estrategia": "requests",   "seletor": "h2"},
    "Veja":                 {"url": "https://veja.abril.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Brasil_de_Fato":       {"url": "https://www.brasildefato.com.br/",          "estrategia": "requests",   "seletor": "h3"},
    "Gazeta_do_Povo":       {"url": "https://www.gazetadopovo.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "O_Antagonista":        {"url": "https://oantagonista.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Piauí_Revista":        {"url": "https://piaui.folha.uol.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Brasil_247":           {"url": "https://brasil247.com/",                    "estrategia": "playwright", "seletor": "h2"},
    "Crusoé":               {"url": "https://crusoe.com.br/",                    "estrategia": "playwright", "seletor": "h2"},
    "Diário_do_Brasil":     {"url": "https://diariodobrasil.org/",               "estrategia": "playwright", "seletor": "h2"},
    "Senado_Noticias":      {"url": "https://www12.senado.leg.br/noticias",      "estrategia": "playwright", "seletor": "h2"},
    "Camara_Noticias":      {"url": "https://www.camara.leg.br/noticias/",       "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 3. AGÊNCIAS DE NOTÍCIAS E IMPRENSA PÚBLICA
    # ==========================================================
    "Agencia_Brasil_EBC":   {"url": "https://agenciabrasil.ebc.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Radio_Nacional_EBC":   {"url": "https://radionacional.ebc.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "EBC_Cultura":          {"url": "https://cultura.ebc.com.br/",               "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Senado":       {"url": "https://www12.senado.leg.br/noticias/agencia-senado", "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Camara":       {"url": "https://www.camara.leg.br/noticias/agencia", "estrategia": "playwright", "seletor": "h2"},
    "Gov_BR_Noticias":      {"url": "https://www.gov.br/pt-br/noticias",         "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 4. FACT-CHECKERS E VERIFICAÇÃO
    # ==========================================================
    "Agencia_Lupa":         {"url": "https://lupa.uol.com.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "Aos_Fatos":            {"url": "https://www.aosfatos.org/",                 "estrategia": "playwright", "seletor": "h2"},
    "Estadao_Verifica":     {"url": "https://www.estadao.com.br/estadao-verifica/","estrategia": "playwright", "seletor": "h2"},
    "Folha_Comprova":       {"url": "https://projetocomprova.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Boatos_org":           {"url": "https://www.boatos.org/",                   "estrategia": "requests",   "seletor": "h2"},

    # ==========================================================
    # 5. JORNALISMO INVESTIGATIVO
    # ==========================================================
    "The_Intercept_Brasil":  {"url": "https://theintercept.com/brasil/",         "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Publica":       {"url": "https://apublica.org/",                    "estrategia": "playwright", "seletor": "h2"},
    "Nexo_Jornal":           {"url": "https://www.nexojornal.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Ponte_Jornalismo":      {"url": "https://ponte.org/",                       "estrategia": "playwright", "seletor": "h2"},
    "Pirata_Midia":          {"url": "https://piratamidia.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "De_Olho_nos_Ruralistas":{"url": "https://deolhonosruralistas.com.br/",      "estrategia": "playwright", "seletor": "h2"},
    "Repórter_Brasil":       {"url": "https://reporterbrasil.org.br/",           "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 6. ECONOMIA E NEGÓCIOS
    # ==========================================================
    "Valor_Economico":       {"url": "https://valor.globo.com/",                 "estrategia": "playwright", "seletor": "h2"},
    "Exame":                 {"url": "https://exame.com/",                       "estrategia": "playwright", "seletor": "h2"},
    "InfoMoney":             {"url": "https://www.infomoney.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Seu_Dinheiro":          {"url": "https://www.seudinheiro.com/",             "estrategia": "playwright", "seletor": "h2"},
    "Forbes_Brasil":         {"url": "https://forbes.com.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "Bloomberg_Linea_BR":    {"url": "https://www.bloomberglinea.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "NeoFeed":               {"url": "https://neofeed.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Isto_E_Dinheiro":       {"url": "https://istoedinheiro.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Mercado_e_Consumo":     {"url": "https://mercadoeconsumo.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Brazil_Journal":        {"url": "https://braziljournal.com/",              "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 7. TECNOLOGIA, CIÊNCIA E INOVAÇÃO
    # ==========================================================
    "Tecnoblog":            {"url": "https://tecnoblog.net/",                   "estrategia": "playwright", "seletor": "h2"},
    "Olhar_Digital":        {"url": "https://olhardigital.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Canaltech":            {"url": "https://canaltech.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "TecMundo":             {"url": "https://www.tecmundo.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Convergencia_Digital": {"url": "https://www.convergenciadigital.com.br/",  "estrategia": "playwright", "seletor": "h2"},
    "Fapesp_Agencia":       {"url": "https://agencia.fapesp.br/",               "estrategia": "playwright", "seletor": "h2"},
    "Ciencia_Hoje":         {"url": "https://www.cienciahoje.org.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Jornal_da_USP":        {"url": "https://jornal.usp.br/",                   "estrategia": "playwright", "seletor": "h2"},
    "Jornal_da_UNICAMP":    {"url": "https://www.unicamp.br/unicamp/noticias/", "estrategia": "playwright", "seletor": "h2"},
    "MIT_Tech_Review_BR":   {"url": "https://mittechreview.com.br/",            "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 8. SAÚDE E BEM-ESTAR
    # ==========================================================
    "Saude_Abril":          {"url": "https://saude.abril.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Drauzio_Varella":      {"url": "https://drauziovarella.uol.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Saude_MS":     {"url": "https://www.saude.gov.br/noticias/",       "estrategia": "playwright", "seletor": "h2"},
    "Gazeta_Medica":        {"url": "https://www.gazetamedica.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Saude_Business":       {"url": "https://saudebusiness.com/",               "estrategia": "playwright", "seletor": "h2"},
    "Bio_Foco":             {"url": "https://biofoco.com.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "Conass_Noticias":      {"url": "https://www.conass.org.br/noticias/",      "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 9. AGRONEGÓCIO E CAMPO
    # ==========================================================
    "Canal_Rural":           {"url": "https://www.canalrural.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Noticiasagricolas":     {"url": "https://www.noticiasagricolas.com.br/",   "estrategia": "playwright", "seletor": "h2"},
    "AgroLink":              {"url": "https://www.agrolink.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Globo_Rural":           {"url": "https://revistagloborural.globo.com/",    "estrategia": "playwright", "seletor": "h2"},
    "Rural_Centro_Oeste":    {"url": "https://www.ruralcentrooeste.com.br/",    "estrategia": "playwright", "seletor": "h2"},
    "MSF_Brasil_Campo":      {"url": "https://www.msfbrasil.org.br/noticias/",  "estrategia": "playwright", "seletor": "h2"},
    "Agencia_iE":            {"url": "https://agenciaie.com.br/",               "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 10. TRABALHO, SINDICAL E ECONOMIA SOLIDÁRIA
    # ==========================================================
    "CUT_Brasil":            {"url": "https://www.cut.org.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Força_Sindical":        {"url": "https://fsindical.org.br/",               "estrategia": "playwright", "seletor": "h2"},
    "CTB_Online":            {"url": "https://ctb.org.br/",                     "estrategia": "playwright", "seletor": "h2"},
    "DIEESE_Noticias":       {"url": "https://www.dieese.org.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Rede_Brasil_Atual":     {"url": "https://www.redebrasilatual.com.br/",     "estrategia": "playwright", "seletor": "h2"},
    "Trabalho_Mais":         {"url": "https://trabalhomais.com.br/",            "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 11. JURÍDICO E INSTITUCIONAL
    # ==========================================================
    "Consultor_Juridico":    {"url": "https://www.conjur.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Jota_Info":             {"url": "https://www.jota.info/",                  "estrategia": "playwright", "seletor": "h2"},
    "STF_Noticias":          {"url": "https://portal.stf.jus.br/noticias/",    "estrategia": "playwright", "seletor": "h2"},
    "STJ_Noticias":          {"url": "https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/", "estrategia": "playwright", "seletor": "h2"},
    "TSE_Noticias":          {"url": "https://www.tse.jus.br/comunicacao/noticias", "estrategia": "playwright", "seletor": "h2"},
    "AGU_Noticias":          {"url": "https://www.gov.br/agu/pt-br/comunicacao/noticias", "estrategia": "playwright", "seletor": "h2"},
    "MPF_Noticias":          {"url": "https://www.mpf.mp.br/sala-de-imprensa/noticias-do-mpf", "estrategia": "playwright", "seletor": "h2"},
    "Migalhas":              {"url": "https://www.migalhas.com.br/",            "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 12. IMPRENSA EVANGÉLICA E RELIGIOSA
    # (segmento editorial de grande alcance social no Brasil)
    # ==========================================================
    "Gospel_Mais":           {"url": "https://noticias.gospelmais.com.br/",     "estrategia": "playwright", "seletor": "h2"},
    "Pleno_News":            {"url": "https://www.plenews.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Gospel_Prime":          {"url": "https://www.gospelprime.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Cristao_Hoje":          {"url": "https://www.cristaohoje.com/",            "estrategia": "playwright", "seletor": "h2"},
    "Guiame":                {"url": "https://www.guiame.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "CNBB_Noticias":         {"url": "https://www.cnbb.org.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Vatican_News_PT":       {"url": "https://www.vaticannews.va/pt.html",      "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 13. ESPORTES
    # ==========================================================
    "Globo_Esporte":         {"url": "https://ge.globo.com/",                   "estrategia": "playwright", "seletor": "h2"},
    "UOL_Esporte":           {"url": "https://www.uol.com.br/esporte/",         "estrategia": "playwright", "seletor": "h2"},
    "Lance_Net":             {"url": "https://www.lance.com.br/",               "estrategia": "playwright", "seletor": "h2"},
    "ESPN_Brasil":           {"url": "https://www.espn.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Trivela":               {"url": "https://trivela.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Atletismo_Brasil":      {"url": "https://www.atletismo.org.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Terra_Esportes":        {"url": "https://www.terra.com.br/esportes/",      "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 14. CULTURA, ENTRETENIMENTO E COMPORTAMENTO
    # ==========================================================
    "Catraca_Livre":         {"url": "https://catracalivre.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Hypeness":              {"url": "https://www.hypeness.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Cult":          {"url": "https://revistacult.uol.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Rolling_Stone_BR":      {"url": "https://rollingstone.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Veja_SP_Cultura":       {"url": "https://vejasp.abril.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Portal_Geledés":        {"url": "https://www.geledes.org.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Alma_Preta":            {"url": "https://almapreta.com.br/",               "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Africas":       {"url": "https://agenciaafricas.com/",             "estrategia": "playwright", "seletor": "h2"},
    "Rap_Nacional":          {"url": "https://www.rapnacional.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Noticia_Preta":         {"url": "https://noticiapreta.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Mundo_Negro":           {"url": "https://mundonegro.inf.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Trace_Brasil":          {"url": "https://trace.tv/brasil/",                "estrategia": "playwright", "seletor": "h2"},
    "CEERT":                 {"url": "https://ceert.org.br/noticias",           "estrategia": "playwright", "seletor": "h2"}, # Foco forte em mercado de trabalho e racismo institucional

    # ==========================================================
    # 15. GÊNERO, MULHERES E LGBTQIA+
    # ==========================================================
    "Genero_e_Numero":        {"url": "https://www.generonumero.media/",        "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Patricia_Galvao":{"url": "https://agenciapatriciagalvao.org.br/",  "estrategia": "playwright", "seletor": "h2"},
    "Sempreviva":             {"url": "https://sof.org.br/",                    "estrategia": "playwright", "seletor": "h2"},
    "Portal_Catarinas":       {"url": "https://catarinas.info/",                "estrategia": "playwright", "seletor": "h2"},
    "Gênero_e_Política":      {"url": "https://www.genderandpolitics.com.br/",  "estrategia": "playwright", "seletor": "h2"},  # [VERIFICAR]
    "Mix_Brasil":             {"url": "https://www.mixbrasil.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Alma_Preta_Diversidade": {"url": "https://almapreta.com.br/categoria/diversidade/", "estrategia": "playwright", "seletor": "h2"},
    "Casa1_Noticias":         {"url": "https://www.casaum.org/",                "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 16. POVOS INDÍGENAS E QUILOMBOLAS
    # ==========================================================
    "Cimi_Noticias":          {"url": "https://cimi.org.br/",                   "estrategia": "playwright", "seletor": "h2"},
    "Midia_India":            {"url": "https://midiaindia.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "APIB_Comunicacao":       {"url": "https://apiboficial.org/noticias/",      "estrategia": "playwright", "seletor": "h2"},
    "Instituto_Socioambiental":{"url": "https://www.socioambiental.org/",       "estrategia": "playwright", "seletor": "h2"},
    "Povos_Indigenas_BR":     {"url": "https://pib.socioambiental.org/",        "estrategia": "playwright", "seletor": "h2"},
    "Quilombo_Sempre_Vivo":   {"url": "https://quilombosemprevivo.com.br/",     "estrategia": "playwright", "seletor": "h2"},  # [VERIFICAR]
    "Conaq_Noticias":         {"url": "https://conaq.org.br/",                  "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 17. MEIO AMBIENTE, CLIMA E AMAZÔNIA
    # ==========================================================
    "Amazonia_Real":          {"url": "https://amazoniareal.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "InfoAmazonia":           {"url": "https://infoamazonia.org/",              "estrategia": "playwright", "seletor": "h2"},
    "O_Eco":                  {"url": "https://oeco.org.br/",                   "estrategia": "playwright", "seletor": "h2"},
    "Mongabay_Brasil":        {"url": "https://brasil.mongabay.com/",           "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Amazonia":       {"url": "https://www.agenciaamazonia.com.br/",    "estrategia": "playwright", "seletor": "h2"},
    "Climate_Tracker_BR":     {"url": "https://climatetracker.org/america-latina/", "estrategia": "playwright", "seletor": "h2"},
    "WWF_Brasil":             {"url": "https://www.wwf.org.br/",                "estrategia": "playwright", "seletor": "h2"},
    "ISA_Noticias":           {"url": "https://www.socioambiental.org/noticias/", "estrategia": "playwright", "seletor": "h2"},
    "Observatorio_do_Clima":  {"url": "https://www.oc.eco.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Greenpeace_Brasil":      {"url": "https://www.greenpeace.org/brasil/",     "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 18. JORNALISMO COMUNITÁRIO, PERIFÉRICO E FAVELAS
    # ==========================================================
    "Agencia_Mural":          {"url": "https://www.agenciamural.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Voz_das_Comunidades":    {"url": "https://vozdascomunidades.com.br/",      "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Favelagrafia":   {"url": "https://favelagrafia.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "RioOnWatch":             {"url": "https://www.rioonwatch.org.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Central_Periferica":     {"url": "https://www.centralperiferica.com.br/",  "estrategia": "playwright", "seletor": "h2"},  # [VERIFICAR]
    "Periferia_em_Movimento": {"url": "https://periferiaemmovimento.com.br/",   "estrategia": "playwright", "seletor": "h2"},
    "Correio_Nagô":           {"url": "https://correionago.com.br/",            "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 19. NORTE
    # ==========================================================
    "AC24Horas_AC":           {"url": "https://ac24horas.com/",                 "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Acre":           {"url": "https://agencia.ac.gov.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Diario_do_Amapa_AP":     {"url": "https://www.diariodoamapa.com.br/",      "estrategia": "playwright", "seletor": "h2"},
    "Jornal_do_AP":           {"url": "https://jornaldoap.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "A_Critica_AM":           {"url": "https://www.acritica.com/",              "estrategia": "playwright", "seletor": "h2"},
    "Portal_do_Holanda_AM":   {"url": "https://www.portaldoholanda.com.br/",    "estrategia": "requests",   "seletor": "h3"},
    "Amazonas_Atual":         {"url": "https://amazonasatual.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "O_Liberal_PA":           {"url": "https://www.oliberal.com/",              "estrategia": "playwright", "seletor": "h2"},
    "DOL_PA":                 {"url": "https://dol.com.br/",                   "estrategia": "playwright", "seletor": "h2"},
    "Amazonia_PA":            {"url": "https://amazonia.org.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Diario_do_Para":         {"url": "https://www.diariodopara.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Rondoniagora_RO":        {"url": "https://www.rondoniagora.com/",          "estrategia": "requests",   "seletor": "h2"},
    "JP_News_RO":             {"url": "https://www.jpnews.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Folha_BV_RR":            {"url": "https://folhabv.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Roraima_em_Foco":        {"url": "https://roraimaemfoco.com/",             "estrategia": "playwright", "seletor": "h2"},
    "Jornal_do_Tocantins_TO": {"url": "https://www.jornaldotocantins.com.br/",  "estrategia": "playwright", "seletor": "h2"},
    "T1_Noticias_TO":         {"url": "https://www.t1noticias.com.br/",         "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 20. NORDESTE
    # ==========================================================
    "GazetaWeb_AL":           {"url": "https://www.gazetaweb.com/",             "estrategia": "playwright", "seletor": "h2"},
    "Cada_Minuto_AL":         {"url": "https://www.cadaminuto.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Correio_24H_BA":         {"url": "https://www.correio24horas.com.br/",     "estrategia": "playwright", "seletor": "h2"},
    "A_Tarde_BA":             {"url": "https://atarde.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Bahia_Noticias":         {"url": "https://www.bahianoticias.com.br/",      "estrategia": "playwright", "seletor": "h2"},
    "O_Povo_CE":              {"url": "https://www.opovo.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Diario_do_Nordeste_CE":  {"url": "https://diariodonordeste.verdesmares.com.br/", "estrategia": "playwright", "seletor": "h2"},
    "Ceara_Agora":            {"url": "https://cearaagora.com/",                "estrategia": "playwright", "seletor": "h2"},
    "O_Imparcial_MA":         {"url": "https://oimparcial.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Imirante_MA":            {"url": "https://imirante.com/",                  "estrategia": "playwright", "seletor": "h2"},
    "Jornal_da_Paraiba_PB":   {"url": "https://jornaldaparaiba.com.br/",        "estrategia": "playwright", "seletor": "h2"},
    "Polêmica_Paraíba":       {"url": "https://www.polemicaparaiba.com.br/",    "estrategia": "playwright", "seletor": "h2"},
    "Jornal_do_Commercio_PE": {"url": "https://jc.ne10.uol.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Folha_de_PE":            {"url": "https://www.folhape.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "NE10_PE":                {"url": "https://ne10.uol.com.br/",               "estrategia": "playwright", "seletor": "h2"},
    "Cidade_Verde_PI":        {"url": "https://cidadeverde.com/",               "estrategia": "requests",   "seletor": "h2"},
    "Meio_Norte_PI":          {"url": "https://www.meionorte.com/",             "estrategia": "playwright", "seletor": "h2"},
    "Tribuna_do_Norte_RN":    {"url": "https://www.tribunadonorte.com.br/",     "estrategia": "playwright", "seletor": "h2"},
    "Novo_Jornal_RN":         {"url": "https://novojornal.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Infonet_SE":             {"url": "https://infonet.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Jornal_da_Cidade_SE":    {"url": "https://jornaldacidade.net/",            "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 21. CENTRO-OESTE
    # ==========================================================
    "Correio_Braziliense_DF": {"url": "https://www.correiobraziliense.com.br/",  "estrategia": "playwright", "seletor": "h2"},
    "Jornal_de_Brasilia":     {"url": "https://jornaldebrasilia.com.br/",        "estrategia": "playwright", "seletor": "h2"},
    "Metrópoles_DF":          {"url": "https://www.metropoles.com/",             "estrategia": "playwright", "seletor": "h2"},
    "O_Popular_GO":           {"url": "https://opopular.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Diário_da_Manhã_GO":     {"url": "https://www.dm.com.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "MidiaNews_MT":           {"url": "https://www.midianews.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Olhar_Direto_MT":        {"url": "https://www.olhardireto.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "RDNews_MT":              {"url": "https://rdnews.com.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "Correio_do_Estado_MS":   {"url": "https://correiodoestado.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Campo_Grande_News_MS":   {"url": "https://www.campograndenews.com.br/",     "estrategia": "playwright", "seletor": "h2"},
    "JPnews_MS":              {"url": "https://www.jpnews.com.br/",              "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 22. SUDESTE
    # ==========================================================
    # Espírito Santo
    "A_Gazeta_ES":            {"url": "https://www.agazeta.com.br/",            "estrategia": "playwright", "seletor": "h2"},
    "Folha_Vitoria_ES":       {"url": "https://www.folhavitoria.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Aqui_ES":                {"url": "https://aquies.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    # Minas Gerais
    "Estado_de_Minas_MG":     {"url": "https://www.em.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "O_Tempo_MG":             {"url": "https://www.otempo.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Hoje_em_Dia_MG":         {"url": "https://www.hojeemdia.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Diario_do_Comercio_MG":  {"url": "https://diariodocomercio.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    # Rio de Janeiro
    "O_Globo_RJ":             {"url": "https://oglobo.globo.com/",              "estrategia": "playwright", "seletor": "h2"},
    "Extra_RJ":               {"url": "https://extra.globo.com/",               "estrategia": "playwright", "seletor": "h2"},
    "O_Dia_RJ":               {"url": "https://odia.ig.com.br/",                "estrategia": "playwright", "seletor": "h2"},
    "Meia_Hora_RJ":           {"url": "https://www.meiahora.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Rio_de_Fato":            {"url": "https://www.riodefato.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    # São Paulo — capital e interior
    "Folha_SP":               {"url": "https://www1.folha.uol.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Estadao_SP":             {"url": "https://www.estadao.com.br/",            "estrategia": "playwright", "seletor": "h3"},
    "Agora_SP":               {"url": "https://www.agora.uol.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Diario_Grande_ABC_SP":   {"url": "https://www.dgabc.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "A_Tribuna_SP":           {"url": "https://www.atribuna.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Diario_de_SP":           {"url": "https://www.diariodesaul.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Jornal_de_Ribeirao_SP":  {"url": "https://www.jornalderibeirao.com.br/",   "estrategia": "playwright", "seletor": "h2"},
    "A_Cidade_SP":            {"url": "https://www.acidadeon.com/",             "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 23. SUL
    # ==========================================================
    # Paraná
    "Banda_B_PR":             {"url": "https://www.bandab.com.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Plural_PR":              {"url": "https://www.plural.jor.br/",             "estrategia": "playwright", "seletor": "h2"},
    "Parana_Portal":          {"url": "https://paranaportal.uol.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "G1_PR":                  {"url": "https://g1.globo.com/pr/parana/",        "estrategia": "playwright", "seletor": "h2"},
    # Rio Grande do Sul
    "Zero_Hora_RS":           {"url": "https://gauchazh.clicrbs.com.br/",       "estrategia": "playwright", "seletor": "h2"},
    "Correio_do_Povo_RS":     {"url": "https://www.correiodopovo.com.br/",      "estrategia": "playwright", "seletor": "h2"},
    "Sul21_RS":               {"url": "https://www.sul21.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "RS_Urgente":             {"url": "https://rsurgente.com.br/",              "estrategia": "playwright", "seletor": "h2"},
    "Di_Rio_RS":              {"url": "https://diario.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    # Santa Catarina
    "NSC_Total_SC":           {"url": "https://www.nsctotal.com.br/",           "estrategia": "playwright", "seletor": "h2"},
    "ND_Mais_SC":             {"url": "https://ndmais.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "AN_Capital_SC":          {"url": "https://www.an.com.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Click_Camboriu_SC":      {"url": "https://clickcamboriu.com.br/",          "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 24. INTERNACIONAIS EM PORTUGUÊS
    # ==========================================================
    "BBC_Brasil_UK":          {"url": "https://www.bbc.com/portuguese",         "estrategia": "playwright", "seletor": "h3"},
    "DW_Brasil_GER":          {"url": "https://www.dw.com/pt-br/",             "estrategia": "playwright", "seletor": "h2"},
    "RFI_Brasil_FRA":         {"url": "https://www.rfi.fr/br/",                "estrategia": "playwright", "seletor": "h2"},
    "France24_PT":            {"url": "https://www.france24.com/pt/",           "estrategia": "playwright", "seletor": "h2"},
    "Euronews_PT":            {"url": "https://pt.euronews.com/",               "estrategia": "playwright", "seletor": "h2"},
    "Sputnik_Brasil_RUS":     {"url": "https://sputniknewsbr.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Xinhua_PT_CHN":          {"url": "http://portuguese.xinhuanet.com/",       "estrategia": "playwright", "seletor": "h2"},
    "VOA_Portugues_USA":      {"url": "https://www.voaportugues.com/",          "estrategia": "playwright", "seletor": "h2"},
    "ONU_News_PT":            {"url": "https://news.un.org/pt/",                "estrategia": "playwright", "seletor": "h2"},
    # Portugal
    "Publico_PT":             {"url": "https://www.publico.pt/",                "estrategia": "playwright", "seletor": "h2"},
    "Observador_PT":          {"url": "https://observador.pt/",                 "estrategia": "playwright", "seletor": "h2"},
    "Jornal_de_Negocios_PT":  {"url": "https://www.jornaldenegocios.pt/",       "estrategia": "playwright", "seletor": "h2"},
    "Expresso_PT":            {"url": "https://expresso.pt/",                   "estrategia": "playwright", "seletor": "h2"},
    "Sapo_Noticias_PT":       {"url": "https://noticias.sapo.pt/",              "estrategia": "playwright", "seletor": "h2"},
    "Correio_da_Manha_PT":    {"url": "https://www.cmjornal.pt/",               "estrategia": "playwright", "seletor": "h2"},
    # África de língua portuguesa
    "Jornal_Angola":          {"url": "https://jornaldeangola.ao/",             "estrategia": "playwright", "seletor": "h2"},
    "Verdade_Mocambique":     {"url": "https://www.verdade.co.mz/",             "estrategia": "playwright", "seletor": "h2"},
    "RTP_Africa_PT":          {"url": "https://www.rtp.pt/noticias/africa/",    "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 25. FONTES LATINO-AMERICANAS / IBERO-AMERICANAS
    # ==========================================================
    "El_Pais_Brasil":         {"url": "https://brasil.elpais.com/",             "estrategia": "playwright", "seletor": "h2"},
    "The_Conversation_BR":    {"url": "https://theconversation.com/br",         "estrategia": "playwright", "seletor": "h2"},
    "Opera_Mundi":            {"url": "https://operamundi.uol.com.br/",         "estrategia": "playwright", "seletor": "h2"},
    "Rebelion_ES":            {"url": "https://rebelion.org/",                  "estrategia": "playwright", "seletor": "h2"},
    "Telesur_PT":             {"url": "https://www.telesurenglish.net/",        "estrategia": "playwright", "seletor": "h2"},  # [VERIFICAR versão PT]
    "NACLA_Report":           {"url": "https://nacla.org/",                     "estrategia": "playwright", "seletor": "h2"},
    "CELAG_Analisis":         {"url": "https://www.celag.org/",                 "estrategia": "playwright", "seletor": "h2"},

    # ==========================================================
    # 26. DIREITOS HUMANOS E TERCEIRO SETOR
    # ==========================================================
    "Conectas_DH":            {"url": "https://www.conectas.org/",              "estrategia": "playwright", "seletor": "h2"},
    "Andi_Comunicacao":       {"url": "https://www.andi.org.br/",               "estrategia": "playwright", "seletor": "h2"},
    "IUPERJ_Polis":           {"url": "https://polis.org.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "Imazon_Noticias":        {"url": "https://imazon.org.br/",                 "estrategia": "playwright", "seletor": "h2"},
    "Transparencia_BR":       {"url": "https://www.transparencia.org.br/",      "estrategia": "playwright", "seletor": "h2"},
    "Amnistia_Brasil":        {"url": "https://anistia.org.br/",                "estrategia": "playwright", "seletor": "h2"},
    "HRW_Brasil":             {"url": "https://www.hrw.org/pt/americas/brasil", "estrategia": "playwright", "seletor": "h2"},



# ==========================================================
    # 27. PESSOAS COM DEFICIÊNCIA (PCD), AUTISMO E CAPACITISMO
    # ==========================================================
    "Canal_Autismo":         {"url": "https://www.canalautismo.com.br/",        "estrategia": "playwright", "seletor": "h2"},
    "Inclusive_Cidadania":   {"url": "https://www.inclusive.org.br/",           "estrategia": "playwright", "seletor": "h2"},
    "Vencer_Limites":        {"url": "https://brasil.estadao.com.br/blogs/vencer-limites/", "estrategia": "playwright", "seletor": "h2"}, # Blog focado do Estadão
    "Camara_Inclusao":       {"url": "https://camarainclusao.com.br/noticias/", "estrategia": "playwright", "seletor": "h2"},
    "Guia_de_Rodas":         {"url": "https://guiaderodas.com/blog/",           "estrategia": "playwright", "seletor": "h2"},

# ==========================================================
    # 28. MIGRAÇÃO, REFUGIADOS E COMBATE À XENOFOBIA
    # ==========================================================
    "MigraMundo":            {"url": "https://migramundo.com/",                 "estrategia": "playwright", "seletor": "h2"},
    "ACNUR_Brasil":          {"url": "https://www.acnur.org/portugues/noticias/","estrategia": "playwright", "seletor": "h2"},
    "Caritas_Brasileira":    {"url": "https://caritas.org.br/noticias",         "estrategia": "playwright", "seletor": "h2"},
    "Missao_Paz":            {"url": "https://www.missaonspaz.org/noticias",    "estrategia": "playwright", "seletor": "h2"},

# ==========================================================
    # 29. LONGEVIDADE E COMBATE AO ETARISMO
    # ==========================================================
    "Portal_Envelhecimento": {"url": "https://www.portaldoenvelhecimento.com.br/", "estrategia": "playwright", "seletor": "h2"},
    "Longevidade_Expo":      {"url": "https://longevidade.com.br/noticias/",    "estrategia": "playwright", "seletor": "h2"},
    "A_Terceira_Idade":      {"url": "https://www.aterceiraidade.com/",         "estrategia": "playwright", "seletor": "h2"},

# ==========================================================
    # COMPLEMENTO: GÊNERO, MULHERES, DIVERSIDADE E LGBTQIA+
    # ==========================================================
    "Revista_AzMina":        {"url": "https://azmina.com.br/",                  "estrategia": "playwright", "seletor": "h2"},
    "Nos_Mulheres_Periferia":{"url": "https://nosmulheresdaperiferia.com.br/",  "estrategia": "playwright", "seletor": "h2"},
    "Think_Olga":            {"url": "https://thinkolga.com/blog/",             "estrategia": "playwright", "seletor": "h2"},
    "Agencia_Diadorim":      {"url": "https://adiadorim.org/",                  "estrategia": "playwright", "seletor": "h2"}, # Jornalismo investigativo focado em direitos LGBTQIA+
    "Revista_Hibrida":       {"url": "https://revistahibrida.com.br/",          "estrategia": "playwright", "seletor": "h2"},
    "Observatorio_G":        {"url": "https://observatoriog.com.br/",           "estrategia": "playwright", "seletor": "h2"}, # Focado em cultura pop e LGBTfobia
    "Pop_Plus":              {"url": "https://popplus.com.br/blog/",            "estrategia": "playwright", "seletor": "h2"}, # Foco em representatividade gorda / gordofobia
}
