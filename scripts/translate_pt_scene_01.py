#!/usr/bin/env python3
"""
Translate Portuguese story phrases to English in JSON files.
This script will be run by the LLM agent to perform bulk translations.
"""

import json
from pathlib import Path


# Translation mappings for Portuguese to English
TRANSLATIONS = {
    # Scene 1
    "O sol nasce suavemente sobre São Paulo.": "The sun rises gently over São Paulo.",
    "As ruas da Vila Madalena começam a ganhar vida.": "The streets of Vila Madalena begin to come alive.",
    "Sophie Moreira entra em seu café preferido, um lugar acolhedor na esquina da rua Aspicuelta.": "Sophie Moreira enters her favorite café, a cozy place on the corner of Aspicuelta street.",
    "Bom dia Sophie, tudo bem?": "Good morning Sophie, how are you?",
    "pergunta Marco, o garçom que a conhece bem.": "asks Marco, the waiter who knows her well.",
    "Sim, tudo bem obrigada.": "Yes, I'm fine thank you.",
    "E você?": "And you?",
    "responde Sophie com um sorriso cansado.": "Sophie responds with a tired smile.",
    "Tudo certo.": "All good.",
    "O que você vai querer hoje?": "What will you have today?",
    "Um café e um pão na chapa, por favor.": "A coffee and a grilled bread, please.",
    "Sophie senta perto da janela.": "Sophie sits near the window.",
    "Ela observa as pessoas que passam na rua.": "She watches the people passing by on the street.",
    "Alguns minutos depois, Lucas Duarte chega, sua mochila nas costas.": "A few minutes later, Lucas Duarte arrives, his backpack on his back.",
    "Bom dia Lucas!": "Good morning Lucas!",
    "diz Sophie.": "says Sophie.",
    "Você dormiu bem?": "Did you sleep well?",
    "Não, não muito bem.": "No, not very well.",
    "Tive sonhos estranhos.": "I had strange dreams.",
    "Lucas faz o pedido no balcão.": "Lucas orders at the counter.",
    "Um café com leite e um pão de queijo, por favor.": "A coffee with milk and a cheese bread, please.",
    "Ele vem sentar na frente de Sophie.": "He comes to sit across from Sophie.",
    "Marco traz os pedidos.": "Marco brings the orders.",
    "Aqui está para vocês.": "Here you are.",
    "Bom apetite!": "Enjoy your meal!",
    "Obrigado, dizem eles juntos.": "Thank you, they say together.",
    "Lucas olha Sophie atentamente.": "Lucas looks at Sophie attentively.",
    "Você quer açúcar no seu café?": "Do you want sugar in your coffee?",
    "Não obrigada, eu tomo sem açúcar.": "No thank you, I take it without sugar.",
    "Está um dia bonito hoje, observa Lucas olhando pela janela.": "It's a beautiful day today, Lucas observes looking out the window.",
    "Sim, é um dia lindo.": "Yes, it's a lovely day.",
    "Eles bebem o café em silêncio por alguns instantes.": "They drink their coffee in silence for a few moments.",
    "Sophie suspira profundamente.": "Sophie sighs deeply.",
    "Sabe Lucas, a vida é tão monótona aqui.": "You know Lucas, life is so monotonous here.",
    "Concordo com você.": "I agree with you.",
    "Todo dia é igual.": "Every day is the same.",
    "A gente deveria viajar, diz Sophie espontaneamente.": "We should travel, Sophie says spontaneously.",
    "Lucas a olha com surpresa, então um sorriso aparece em seu rosto.": "Lucas looks at her with surprise, then a smile appears on his face.",
    "Você tem razão!": "You're right!",
    "Por que não?": "Why not?"
}


def translate_scene_file(file_path, translations):
    """Translate phrases in a JSON scene file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translated_count = 0
    for phrase_obj in data['pt']:
        pt_text = phrase_obj['pt']
        if pt_text in translations:
            phrase_obj['english'] = translations[pt_text]
            translated_count += 1
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return translated_count


def main():
    scenes_dir = Path("language_materials/pt/story-scenes-json")
    
    total_translated = 0
    for json_file in sorted(scenes_dir.glob("scene-*.json")):
        count = translate_scene_file(json_file, TRANSLATIONS)
        print(f"Translated {count} phrases in {json_file.name}")
        total_translated += count
    
    print(f"\n✓ Total phrases translated: {total_translated}")


if __name__ == "__main__":
    main()
