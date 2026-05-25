#!/usr/bin/env python3
import json
import re
import unicodedata
from pathlib import Path
from dataclasses import dataclass, field

SRC = Path(__file__).parent / "src"
OUTPUT = Path(__file__).parent / "results.txt"


@dataclass(frozen=True)
class CompiledRules:
    """
    Guarda as regras já processadas como conjuntos imutáveis (frozenset).
    Isso evita recriar os conjuntos a cada palavra verificada.

    Campos:
      pool                — letras de referência (letters + mandatory juntos)
      mandatory           — letras que DEVEM aparecer na palavra
      prohibited          — letras bloqueadas (usado no modo blacklist)
      quantities          — tamanhos de palavra aceitos (contagem só de letras)
      mode                — "whitelist" ou "blacklist"
      wildcard_prohibited — True quando prohibited contém "*"
    """
    pool: frozenset[str]
    mandatory: frozenset[str]
    prohibited: frozenset[str]
    quantities: frozenset[int]
    mode: str
    wildcard_prohibited: bool
    _non_alpha: re.Pattern = field(default=re.compile(r"[^A-Z]"), compare=False)

    def normalize(self, word: str) -> str:
        """
        Prepara a palavra para comparação:
          1. Converte para maiúsculas
          2. Remove acentos (á → A, ê → E, etc.)
          3. Remove tudo que não é letra (hífens, pontos, espaços)
        Exemplo: "pá-de-cal" → "PADECAL"
        """
        stripped = "".join(
            c for c in unicodedata.normalize("NFD", word.upper())
            if unicodedata.category(c) != "Mn"
        )
        return self._non_alpha.sub("", stripped)

    def matches(self, word: str) -> bool:
        """
        Verifica se a palavra satisfaz todas as regras.

        Modo whitelist:
          — Todas as letras precisam estar em `pool` (letters + mandatory).
          — O campo `prohibited` é ignorado nesse modo.

        Modo blacklist:
          — Qualquer letra é permitida, EXCETO as que estão em `prohibited`.
          — Se `prohibited` contém "*", bloqueia tudo fora de `letters`.
          — Se `prohibited` está vazio, nenhuma letra é bloqueada.

        Em ambos os modos:
          — O tamanho da palavra (só letras) precisa estar em `quantity_letters`.
          — Todas as letras de `mandatory` precisam aparecer.
        """
        letters = self.normalize(word)
        if not letters:
            return False

        # Checa tamanho primeiro — operação O(1), descarte rápido
        if self.quantities and len(letters) not in self.quantities:
            return False

        letter_set = frozenset(letters)

        if self.mode == "whitelist":
            # Todas as letras da palavra precisam estar no pool
            if self.pool and not letter_set.issubset(self.pool):
                return False
        else:
            # Blacklist: verifica o que está explicitamente bloqueado
            if self.wildcard_prohibited:
                # "*" em prohibited → bloqueia tudo fora de letters
                if not letter_set.issubset(self.pool):
                    return False
            elif letter_set & self.prohibited:
                return False

        # As letras obrigatórias todas precisam aparecer na palavra
        if not self.mandatory.issubset(letter_set):
            return False

        return True


def compile_rules(path: Path) -> CompiledRules:
    """
    Lê o rules.json e converte cada lista em frozenset.

    `pool` é a união de letters + mandatory porque ambas são letras de referência
    — a diferença é que mandatory exige presença, letters apenas define o conjunto.

    Se prohibited contém "*", o wildcard é separado do restante da lista
    para que a lógica de matches possa tratá-lo de forma especial.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    letters = frozenset(raw.get("letters", []))
    mandatory = frozenset(raw.get("mandatory", []))
    prohibited_raw = raw.get("prohibited", [])
    wildcard = "*" in prohibited_raw
    return CompiledRules(
        pool=letters | mandatory,
        mandatory=mandatory,
        prohibited=frozenset(p for p in prohibited_raw if p != "*"),
        quantities=frozenset(raw.get("quantity_letters", [])),
        mode=raw.get("mode", "whitelist"),
        wildcard_prohibited=wildcard,
    )


def main():
    """
    Ponto de entrada: carrega as regras, percorre o dicionário linha a linha
    e grava as palavras que passam no filtro em results.txt.
    """
    rules = compile_rules(SRC / "rules.json")

    results = []
    with open(SRC / "palavras.txt", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word and rules.matches(word):
                results.append(word)

    OUTPUT.write_text("\n".join(results) + f"\n\n{len(results)} palavra(s) encontrada(s).\n", encoding="utf-8")
    print(f"{len(results)} palavra(s) encontrada(s). → {OUTPUT}")


if __name__ == "__main__":
    main()
