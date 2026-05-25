# garimpo

Script Python para encontrar palavras válidas em jogos como **Termo**, **Soletra** e similares. Configure letras permitidas, obrigatórias e proibidas — o script garimpeia o dicionário e devolve apenas as palavras que encaixam.

## Uso

```bash
python3 search.py
```

O resultado é gravado em `results.txt` a cada execução.

## Exemplos de uso nos jogos

**Termo** (Wordle em português): você já sabe que a palavra tem 5 letras, contém A e R, e não tem E nem S.

```json
{
  "mode": "blacklist",
  "letters":          [],
  "mandatory":        ["A", "R"],
  "prohibited":       ["E", "S"],
  "quantity_letters": [5],
  "pattern":          ""
}
```

**Termo com posições**: você descobriu que a 2ª letra é A e a 4ª é U (tiles verdes).

```json
{
  "mode": "blacklist",
  "letters":          [],
  "mandatory":        ["A", "U"],
  "prohibited":       ["E", "S"],
  "quantity_letters": [5],
  "pattern":          "_A_U_"
}
```

**Soletra**: o painel mostra as letras disponíveis (ex: U, G, A, D, B, I, L) e uma letra central obrigatória (ex: A).

```json
{
  "mode": "whitelist",
  "letters":          ["U", "G", "D", "B", "I", "L"],
  "mandatory":        ["A"],
  "prohibited":       [],
  "quantity_letters": [4, 5, 6, 7]
}
```

## Configuração

Edite `src/rules.json` antes de rodar o script.

### Campos

| Campo | Tipo | Descrição |
|---|---|---|
| `mode` | string | `"whitelist"` ou `"blacklist"`. Padrão: `"whitelist"` |
| `letters` | string[] | Pool de letras de referência |
| `mandatory` | string[] | Letras que **devem** aparecer na palavra |
| `prohibited` | string[] | Letras bloqueadas (modo blacklist). Aceita `"*"` como curinga |
| `quantity_letters` | number[] | Tamanhos de palavra aceitos (contando só letras, sem acentos) |
| `pattern` | string | Posições fixas da palavra. Letras = posição certa (tile verde), `_` = livre. Ex: `"_A_U_"` → A na pos 2, U na pos 4 |

### Modos

**`mode: "whitelist"`** — apenas as letras em `letters` + `mandatory` podem aparecer. O campo `prohibited` é ignorado.

**`mode: "blacklist"`** — `prohibited` define o que é bloqueado; todo o resto é livre.

| `prohibited` | Efeito |
|---|---|
| `[]` | Nada bloqueado — qualquer letra pode aparecer |
| `["Z", "X"]` | Apenas Z e X são bloqueados |
| `["*"]` | Tudo fora de `letters` é bloqueado (mesmo efeito do whitelist) |

### Normalização

As letras são comparadas sem acento e em maiúsculo. `"á"`, `"À"` e `"A"` são tratados como `A`. Hífens, pontos e outros caracteres não-alfabéticos são ignorados na contagem de letras.

## Estrutura

```
garimpo/
├── search.py        # script principal
├── results.txt      # saída gerada pelo script
└── src/
    ├── palavras.txt # dicionário (uma palavra por linha)
    └── rules.json   # regras de busca
```
