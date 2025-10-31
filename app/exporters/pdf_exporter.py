from typing import List, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

from app.core.models import Scene, Character


class PDFExporter:
    def __init__(self, font_name: str = "Helvetica"):
        self.font_name = font_name

    def export_scene(self, scene: Scene, messages: List[Tuple[str, str]], path: str):
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = styles['Title']
        normal = styles['Normal']
        normal.alignment = TA_LEFT

        story.append(Paragraph(scene.title, title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Тема: {scene.topic}", normal))
        story.append(Paragraph(f"Локация: {scene.location}", normal))
        story.append(Paragraph(f"Участники: {', '.join(scene.participants)}", normal))
        story.append(Spacer(1, 12))

        for speaker, content in messages:
            story.append(Paragraph(f"<b>{speaker}:</b> {content}", normal))
            story.append(Spacer(1, 6))

        doc.build(story)

    def export_character(self, character: Character, path: str):
        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = styles['Title']
        normal = styles['Normal']
        normal.alignment = TA_LEFT

        story.append(Paragraph(character.name, title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Фракция: {character.faction}", normal))
        story.append(Spacer(1, 12))

        sections = [
            ("Описание", character.description),
            ("Характер", character.personality),
            ("Манера речи", character.speech_style),
            ("Цели", character.goals),
            ("Связи", character.relationships),
        ]

        for title, content in sections:
            story.append(Paragraph(f"<b>{title}</b>", normal))
            story.append(Paragraph(content or "-", normal))
            story.append(Spacer(1, 8))

        doc.build(story)
