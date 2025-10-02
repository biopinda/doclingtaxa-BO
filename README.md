# DoclingTaxaBO

Conversão de Monografias em PDF para JSON Estruturado seguindo o padrão Darwin Core (DwC).

## Visão Geral

DoclingTaxaBO processa monografias científicas sobre fauna e flora em formato PDF, extraindo informações taxonômicas, morfológicas e ecológicas em documentos JSON estruturados armazenados no MongoDB. O sistema segue o padrão de dados de biodiversidade Darwin Core (DwC) com extensões para descrições detalhadas de espécies.

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
# Copiar template (já configurado com MongoDB de produção)
cp .env.template .env

# Configuração pré-definida para MongoDB de produção:
# MONGODB_URI=mongodb://dwc2json:VLWQ8Bke65L52hfBM635@192.168.1.10:27017/?authSource=admin
# MONGODB_DATABASE=dwc2json
# MONGODB_COLLECTION=monografias
```

### 5. Verificar Conexão MongoDB

```bash
# Testar conexão com MongoDB de produção
mongosh "mongodb://dwc2json:VLWQ8Bke65L52hfBM635@192.168.1.10:27017/?authSource=admin" --eval "db.runCommand({ ping: 1 })"

# Verificar banco de dados e coleção
mongosh "mongodb://dwc2json:VLWQ8Bke65L52hfBM635@192.168.1.10:27017/dwc2json?authSource=admin" --eval "db.monografias.countDocuments({})"
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
doclingtaxaBO process --input-dir /caminho/para/pdfs --mongodb-uri "mongodb://dwc2json:VLWQ8Bke65L52hfBM635@192.168.1.10:27017/?authSource=admin"
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
MongoDB: mongodb://dwc2json@192.168.1.10:27017/dwc2json (coleção: monografias)

[1/5] flora_brazil.pdf ... ✓ (47 espécies, 12.3s)
[2/5] fauna_mammals.pdf ... ✓ (23 espécies, 8.1s)
[3/5] corrupted.pdf ... ✗ (Formato de PDF inválido)
[4/5] empty.pdf ... ⚠ (0 espécies, 2.1s)
[5/5] large_monograph.pdf ... ✓ (156 espécies, 45.7s)

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
    {"path": "monografias/flora_brazil.pdf", "species": 47, "duration": 12.3},
    {"path": "monografias/fauna_mammals.pdf", "species": 23, "duration": 8.1}
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

**Conexão**: `mongodb://dwc2json:VLWQ8Bke65L52hfBM635@192.168.1.10:27017/dwc2json?authSource=admin`

### Consultar por Nome Científico

```javascript
use dwc2json
db.monografias.find({ scientificName: "Handroanthus chrysotrichus" })
```

### Consultar por Família

```javascript
db.monografias.find({ family: "Bignoniaceae" })
```

### Obter Contagem Total de Espécies

```javascript
db.monografias.countDocuments({ taxonRank: "species" })
```

### Encontrar Espécies em Domínio Específico

```javascript
db.monografias.find({
  "distribution.phytogeographicDomains": "Mata Atlântica"
})
```

### Consultar por PDF de Origem

```javascript
db.monografias.find({
  "structuredDescription.sourcePDF.filePath": { $regex: "flora_brazil" }
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
