# DoclingTaxaBO

Conversão de Monografias em PDF para JSON Estruturado seguindo o padrão Darwin Core (DwC).

## Visão Geral

DoclingTaxaBO processa monografias científicas sobre fauna e flora em formato PDF, extraindo informações taxonômicas, morfológicas e ecológicas em documentos JSON estruturados armazenados no MongoDB. O sistema segue o padrão de dados de biodiversidade Darwin Core (DwC) com extensões para descrições detalhadas de espécies.

## Sobre o Projeto Docling

### O que é Docling?

**Docling** é uma biblioteca de código aberto desenvolvida pela IBM Research Zurich e hospedada pela LF AI & Data Foundation, especializada em processamento inteligente de documentos para aplicações de Inteligência Artificial Generativa.

### Problemas que Resolve

1. **Complexidade na Extração de PDFs**: PDFs científicos contêm layouts complexos, tabelas, imagens e hierarquias de seções que são difíceis de processar com ferramentas tradicionais.

2. **Diversidade de Formatos**: Necessidade de processar diferentes tipos de documentos (PDF, DOCX, PPTX, imagens) com uma única ferramenta.

3. **Preparação para IA**: Documentos precisam ser convertidos em formatos estruturados (JSON, Markdown) para uso em sistemas de IA, RAG (Retrieval-Augmented Generation) e análise semântica.

4. **OCR e Documentos Digitalizados**: PDFs escaneados requerem reconhecimento óptico de caracteres (OCR) integrado para extração de texto.

5. **Privacidade de Dados**: Processamento local de documentos sensíveis sem necessidade de envio para serviços externos.

### Como Funciona

O Docling utiliza **modelos de linguagem visual (Visual Language Models)** como o GraniteDocling para entender a estrutura do documento:

1. **Análise de Layout**: Identifica cabeçalhos, parágrafos, tabelas, figuras e hierarquia de seções
2. **Ordem de Leitura**: Determina a sequência lógica do conteúdo (importante para documentos de múltiplas colunas)
3. **Extração de Tabelas**: Reconhece e estrutura tabelas complexas preservando relações entre células
4. **OCR Integrado**: Processa PDFs escaneados ou imagens com reconhecimento de texto
5. **Exportação Estruturada**: Converte para formatos padronizados (JSON, Markdown) mantendo a semântica

### Por que Usamos Docling neste Projeto?

No **DoclingTaxaBO**, aproveitamos o Docling para:

- **Extrair hierarquias taxonômicas** (Reino → Filo → Classe → Ordem → Família → Gênero → Espécie) preservando a estrutura original
- **Identificar seções específicas** como "Morfologia", "Distribuição Geográfica", "Material Examinado"
- **Processar tabelas** de caracteres diagnósticos e dados morfométricos
- **Suportar PDFs antigos digitalizados** de monografias históricas usando OCR
- **Preparar dados para IA** em formato compatível com o padrão Darwin Core para integração com sistemas de biodiversidade

### Tecnologias Docling

- **Python**: Interface simples via CLI e API
- **Modelos de IA**: Visual Language Models (VLMs) para compreensão de layout
- **Integrações**: LangChain, LlamaIndex para aplicações de IA
- **Aceleração**: Suporte MLX para processamento eficiente
- **Código Aberto**: Licença MIT, comunidade ativa no GitHub

## Funcionalidades

- 🔬 **Conformidade Darwin Core**: Saída segue padrão internacional de dados de biodiversidade
- 📄 **Processamento de PDF**: Suporta PDFs baseados em texto e digitalizados (OCR) usando Docling
- 🗂️ **Extração Estruturada**: Morfologia, ecologia, fenologia, distribuição e caracteres diagnósticos
- 🌿 **Foco em Nível de Espécie**: Extrai apenas descrições de nível de espécie (exclui Família/Gênero)
- 🚫 **Filtragem Inteligente**: Exclui automaticamente chaves de identificação
- 📊 **Armazenamento MongoDB**: Armazena dados taxonômicos hierárquicos com validação
- 🔄 **Processamento em Lote**: Processa diretórios inteiros com relatório de progresso
- ✅ **Resiliência a Erros**: Continua processamento em caso de falhas individuais

## Requisitos

- Python 3.11 ou superior
- MongoDB 5.0+ (local ou remoto)
- 2GB RAM (para processamento de PDF)
- 500MB de espaço em disco (para dependências)

## Instalação

### 1. Clonar Repositório

```bash
git clone https://github.com/biopinda/doclingtaxa-BO.git
cd doclingtaxaBO
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Dependências de produção
pip install -e .

# Dependências de desenvolvimento (inclui ferramentas de teste)
pip install -e ".[dev]"
```

### 4. Configurar Ambiente

```bash
# Copiar template de configuração
cp .env.template .env

# Edite o arquivo .env com suas credenciais MongoDB:
# MONGODB_URI=mongodb://seu_usuario:sua_senha@seu_host:27017/?authSource=admin
# MONGODB_DATABASE=seu_banco
# MONGODB_COLLECTION=sua_colecao
```

### 5. Verificar Conexão MongoDB

```bash
# Testar conexão (substitua com suas credenciais)
mongosh "mongodb://seu_usuario:sua_senha@seu_host:27017/?authSource=admin" --eval "db.runCommand({ ping: 1 })"

# Verificar banco de dados e coleção
mongosh "mongodb://seu_usuario:sua_senha@seu_host:27017/seu_banco?authSource=admin" --eval "db.sua_colecao.countDocuments({})"
```

## Início Rápido

### Processar Diretório de Monografias de Teste

```bash
# Processar monografias do diretório de teste
doclingtaxaBO process --input-dir monografias
```

### Processar Diretório Customizado

```bash
doclingtaxaBO process --input-dir /caminho/para/pdfs
```

### Com URI MongoDB Customizada (se necessário)

```bash
doclingtaxaBO process --input-dir /caminho/para/pdfs --mongodb-uri "mongodb://seu_usuario:sua_senha@seu_host:27017/?authSource=admin"
```

### Formato de Saída JSON

```bash
doclingtaxaBO process --input-dir /caminho/para/pdfs --output-format json > resultados.json
```

### Log Detalhado

```bash
doclingtaxaBO process --input-dir /caminho/para/pdfs --verbose
```

## Uso da CLI

```
doclingtaxaBO process [OPÇÕES]

Opções:
  --input-dir TEXT        Diretório contendo monografias em PDF [obrigatório]
  --mongodb-uri TEXT      String de conexão MongoDB [padrão: do .env]
  --output-format TEXT    Formato de saída: json|human [padrão: human]
  --verbose              Habilitar log de depuração
  --help                 Mostrar esta mensagem e sair
```

## Exemplo de Saída

### Formato Legível

```
Processando PDFs de: monografias
MongoDB: mongodb://usuario@host:27017/banco (coleção: colecao)

[1/5] bignoniaceae.pdf ... ✓ (47 espécies, 12.3s)
[2/5] felidae.pdf ... ✓ (23 espécies, 8.1s)
[3/5] corrupted.pdf ... ✗ (Formato de PDF inválido)
[4/5] empty.pdf ... ⚠ (0 espécies, 2.1s)
[5/5] orchidaceae.pdf ... ✓ (156 espécies, 45.7s)

Resumo:
  Total:     5 arquivos
  Sucesso:   3 arquivos (226 espécies)
  Falha:     1 arquivo
  Avisos:    1 arquivo

Tempo de processamento: 68.2 segundos
```

### Formato JSON

```json
{
  "total_files": 5,
  "succeeded": [
    {"path": "monografias/bignoniaceae.pdf", "species": 47, "duration": 12.3},
    {"path": "monografias/felidae.pdf", "species": 23, "duration": 8.1},
    {"path": "monografias/orchidaceae.pdf", "species": 156, "duration": 45.7}
  ],
  "failed": [
    {"path": "monografias/corrupted.pdf", "error": "Formato de PDF inválido"}
  ],
  "processing_time_seconds": 68.2
}
```

## Esquema Darwin Core

O sistema armazena dados usando campos padrão Darwin Core (DwC) com extensões:

### Campos DwC Principais

- `scientificName`, `canonicalName`, `scientificNameAuthorship`
- `kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `specificEpithet`
- `higherClassification` (hierarquia delimitada por pipe)
- `distribution` (domínios fitogeográficos, tipos de vegetação, ocorrência)
- `speciesprofile` (forma de vida, habitat/substrato)
- `vernacularname` (nomes comuns com idioma)
- `reference` (citações bibliográficas)

### Extensões (Novos Campos)

- **`structuredDescription`**: Descrições detalhadas de espécies
  - `morphology`: hábito, altura, caules, folhas, flores, frutos, sementes
  - `ecology`: habitat, associados, altitude, solo, luminosidade
  - `phenology`: floração, frutificação, queda de folhas
  - `distribution`: distribuição detalhada com estados, municípios
  - `diagnosticCharacters`: características de identificação chave
  - `uses`: econômico, medicinal, ornamental, ecológico
  - `conservationStatus`: categoria IUCN, critérios, ameaças

- **`processingMetadata`**: Rastreamento de status de extração
  - `status`: completed|partial|failed
  - `extractedSections`: lista de seções analisadas com sucesso
  - `validationWarnings`: problemas não fatais
  - `extractionErrors`: mensagens de erro
  - `processingDuration`: tempo em segundos

## Exemplos de Consultas MongoDB

**Nota**: Substitua os valores de conexão pelos seus próprios.

### Consultar por Nome Científico

```javascript
use seu_banco
db.sua_colecao.find({ scientificName: "Handroanthus chrysotrichus" })
```

### Consultar por Família

```javascript
db.sua_colecao.find({ family: "Bignoniaceae" })
```

### Obter Contagem Total de Espécies

```javascript
db.sua_colecao.countDocuments({ taxonRank: "species" })
```

### Encontrar Espécies em Domínio Específico

```javascript
db.sua_colecao.find({
  "distribution.phytogeographicDomains": "Mata Atlântica"
})
```

### Consultar por PDF de Origem

```javascript
db.sua_colecao.find({
  "structuredDescription.sourcePDF.filePath": { $regex: "bignoniaceae" }
})
```

## Desenvolvimento

### Executar Testes

```bash
# Todos os testes
pytest

# Apenas testes de contrato
pytest -m contract

# Apenas testes de integração
pytest -m integration

# Com relatório de cobertura
pytest --cov=src --cov-report=html
```

### Qualidade de Código

```bash
# Linting
ruff check src/ tests/

# Formatação
black src/ tests/

# Verificação de tipos (se usando mypy)
mypy src/
```

### Estrutura do Projeto

```
doclingtaxaBO/
├── src/
│   ├── models/              # Modelos Pydantic (esquema DwC)
│   ├── extractors/          # Lógica de processamento de PDF
│   ├── storage/             # Persistência MongoDB
│   ├── cli/                 # Interface de linha de comando
│   └── lib/                 # Interface de biblioteca principal
├── tests/
│   ├── contract/            # Testes de conformidade de esquema
│   ├── integration/         # Testes ponta a ponta
│   └── unit/                # Testes de componentes
├── specs/                   # Documentação de design
└── pyproject.toml          # Configuração do projeto
```

## Contribuindo

1. Leia a especificação: `specs/main/spec.md`
2. Siga TDD: Escreva testes primeiro (veja `specs/main/tasks.md`)
3. Garanta conformidade DwC: Valide contra `specs/main/contracts/mongodb-schema-dwc-extended.json`
4. Execute testes e linting antes de commitar
5. Atualize documentação conforme necessário

## Licença

[Adicionar informações de licença]

## Referências

- [Padrão Darwin Core](https://dwc.tdwg.org)
- [Biblioteca Docling](https://github.com/docling-project/docling)
- [Driver Python MongoDB](https://pymongo.readthedocs.io)
- [Documentação Pydantic](https://docs.pydantic.dev)
