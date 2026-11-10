from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EmailClassification:
    category: str
    label: str
    should_save: bool = True
    should_delete_from_inbox: bool = False
    mark_as_read: bool = True
    move_to_label: bool = True


class EmailClassifier:
    """Regra inicial de classificação por palavras-chave para MVP."""

    def __init__(self) -> None:
        self.keywords_by_category = {
            "Trabalho": [
                "trabalho", "projeto", "cliente", "contrato", "empresa", "colaborador",
                "orcamento", "acordo", "servico", "financeiro", "sala de reunião",
            ],
            "Processo Seletivo": [
                "recrutamento", "processo seletivo", "vagas", "linkedin", "rh", "talento",
                "candidatura", "entrevista", "seleção", "job", "opportunity",
            ],
            "Faculdade": [
                "universidade", "aluno", "disciplina", "nota", "matricula", "biblioteca",
                "seminario", "professor", "curso", "campus",
            ],
            "Banco": [
                "nubank", "itau", "bradesco", "banco", "bancario", "conta", "cartao",
                "financ", "transferencia", "extrato",
            ],
            "Propaganda": [
                "promoção", "oferta", "desconto", "newsletter", "marketing", "campanha",
                "sorteio", "anuncio", "publicidade",
            ],
        }

    def classify(self, sender_email: str, subject: str, snippet: str | None = None) -> EmailClassification:
        text = " ".join([
            sender_email or "",
            subject or "",
            snippet or "",
        ]).lower()

        for category, keywords in self.keywords_by_category.items():
            if any(keyword.lower() in text for keyword in keywords):
                return EmailClassification(
                    category=category,
                    label=category,
                    should_save=True,
                    should_delete_from_inbox=False,
                    mark_as_read=True,
                    move_to_label=True,
                )

        return EmailClassification(
            category="Outros",
            label="Outros",
            should_save=True,
            should_delete_from_inbox=False,
            mark_as_read=True,
            move_to_label=True,
        )

    def classify_many(self, emails: Iterable[dict]) -> list[EmailClassification]:
        return [self.classify(item.get("sender_email", ""), item.get("subject", ""), item.get("snippet")) for item in emails]
