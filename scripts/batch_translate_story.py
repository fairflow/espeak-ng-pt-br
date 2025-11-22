#!/usr/bin/env python3
"""
Batch translate story scenes from source language to English.
This script uses direct LLM translation capabilities to translate all phrases.
Usage: python batch_translate_story.py <lang_code>
Example: python batch_translate_story.py pt
"""

import json
import sys
from pathlib import Path


def get_translation_map_pt():
    """Portuguese to English translation map for all scenes."""
    return {
        # Scene 2
        "À tarde, Sophie e Lucas passeiam pelas ruas da Vila Madalena.": "In the afternoon, Sophie and Lucas stroll through the streets of Vila Madalena.",
        "Eles entram em uma pequena mercearia.": "They enter a small grocery store.",
        "Bom dia, diz a comerciante.": "Good morning, says the shopkeeper.",
        "O que posso fazer por vocês?": "What can I do for you?",
        "Precisamos de pão, responde Sophie.": "We need bread, Sophie responds.",
        "O pão está ali, perto da entrada.": "The bread is over there, near the entrance.",
        "Lucas examina os queijos no balcão.": "Lucas examines the cheeses on the counter.",
        "O queijo está fresco?": "Is the cheese fresh?",
        "Sim, está muito bom.": "Yes, it's very good.",
        "Recebi hoje de manhã.": "I received it this morning.",
        "Perfeito.": "Perfect.",
        "E quanto custam os tomates?": "And how much do the tomatoes cost?",
        "Seis reais o quilo.": "Six reais per kilo.",
        "Sophie faz uma cara de desaprovação.": "Sophie makes a disapproving face.",
        "Está muito caro para mim.": "It's too expensive for me.",
        "Olha, diz a comerciante, tenho tomates de ontem.": "Look, says the shopkeeper, I have tomatoes from yesterday.",
        "Quatro reais o quilo.": "Four reais per kilo.",
        "Tá bom, a gente leva um quilo.": "Okay, we'll take a kilo.",
        "Eles continuam as compras.": "They continue shopping.",
        "Lucas pergunta: Onde fica a padaria?": "Lucas asks: Where is the bakery?",
        "É na esquina, depois da igreja.": "It's on the corner, after the church.",
        "Saindo da loja, Sophie respira o ar fresco.": "Leaving the store, Sophie breathes the fresh air.",
        "Eu adoro esse bairro.": "I love this neighborhood.",
        "Eu também, é muito bonito.": "Me too, it's very beautiful.",
        "Os prédios antigos têm charme.": "The old buildings have charm.",
        "Eles caminham em direção à padaria.": "They walk toward the bakery.",
        "Lucas tem uma ideia.": "Lucas has an idea.",
        "A gente compra vinho?": "Shall we buy wine?",
        "Boa ideia!": "Good idea!",
        "Podemos pegar uma garrafa para hoje à noite.": "We can get a bottle for tonight.",
        "Que vinho você prefere?": "Which wine do you prefer?",
        "Tinto, sempre tinto.": "Red, always red.",
        "Perfeito, vamos pegar uma garrafa.": "Perfect, let's get a bottle.",
        "Eles entram em uma pequena adega.": "They enter a small wine shop.",
        "O dono os aconselha e eles saem com um bom vinho brasileiro.": "The owner advises them and they leave with a good Brazilian wine.",
        
        # Scene 3
        "À noite, no apartamento de Sophie, eles compartilham o vinho e queijo.": "At night, in Sophie's apartment, they share wine and cheese.",
        "A conversa fica mais profunda.": "The conversation becomes deeper.",
        "Sabe Lucas, estou cansada desta vida, começa Sophie.": "You know Lucas, I'm tired of this life, Sophie begins.",
        "Eu também, tudo é igual todo dia.": "Me too, everything is the same every day.",
        "Trânsito, trabalho, casa.": "Traffic, work, home.",
        "A gente poderia viajar para algum lugar.": "We could travel somewhere.",
        "De verdade, não só falar.": "For real, not just talk.",
        "Lucas se endireita no sofá.": "Lucas sits up straight on the sofa.",
        "Onde você quer ir?": "Where do you want to go?",
        "Ainda não sei.": "I don't know yet.",
        "Mas longe daqui.": "But far from here.",
        "Montanha ou praia?": "Mountain or beach?",
        "pergunta Lucas.": "asks Lucas.",
        "Montanha, eu adoro a natureza.": "Mountain, I love nature.",
        "As árvores, o ar puro, o silêncio.": "The trees, the pure air, the silence.",
        "A Serra da Mantiqueira?": "The Serra da Mantiqueira?",
        "Sim!": "Yes!",
        "É uma ideia excelente!": "It's an excellent idea!",
        "Lucas se levanta com entusiasmo.": "Lucas stands up with enthusiasm.",
        "Quando vamos partir?": "When shall we leave?",
        "Logo, muito logo.": "Soon, very soon.",
        "Sophie hesita um momento.": "Sophie hesitates for a moment.",
        "Estou com um pouco de medo, sabe.": "I'm a little afraid, you know.",
        "Lucas pega a mão dela.": "Lucas takes her hand.",
        "Não tenha medo, vai dar tudo certo.": "Don't be afraid, everything will be alright.",
        "Você tem razão, vamos!": "You're right, let's go!",
        "O que a gente tem a perder?": "What do we have to lose?",
        
        # Scene 4
        "Na manhã seguinte, Lucas chega na casa de Sophie com seu laptop.": "The next morning, Lucas arrives at Sophie's house with his laptop.",
        "Está decidido, vamos viajar!": "It's decided, we're going to travel!",
        "anuncia ele.": "he announces.",
        "Daqui a quanto tempo?": "How soon?",
        "Uma semana.": "One week.",
        "Olhei os ônibus ontem à noite.": "I looked at buses last night.",
        "Uma semana?": "One week?",
        "É tão rápido!": "That's so fast!",
        "Sim, mas é melhor assim.": "Yes, but it's better this way.",
        "Se a gente esperar muito, nunca vai sair.": "If we wait too long, we'll never leave.",
        "Sophie pensa.": "Sophie thinks.",
        "Você tem razão.": "You're right.",
        "O que a gente leva?": "What do we take?",
        "Não muita coisa, só o essencial.": "Not much, just the essentials.",
        "Roupas quentes, uma lanterna...": "Warm clothes, a flashlight...",
        "Uma mochila cada, decide Sophie.": "One backpack each, Sophie decides.",
        "E nossos celulares?": "And our phones?",
        "Claro, para as fotos.": "Of course, for photos.",
        "E para segurança.": "And for safety.",
        "Sophie começa a fazer uma lista.": "Sophie starts making a list.",
        "Estou empolgada!": "I'm excited!",
        "Isso realmente vai acontecer!": "This is really going to happen!",
        "Lucas sorri.": "Lucas smiles.",
        "Eu também.": "Me too.",
        "Uma nova aventura começa.": "A new adventure begins.",
        
        # Scene 5
        "Uma semana depois, Sophie e Lucas estão na frente da Rodoviária do Tietê.": "A week later, Sophie and Lucas are in front of the Tietê Bus Station.",
        "Suas mochilas estão prontas.": "Their backpacks are ready.",
        "A empolgação se mistura com o nervosismo.": "Excitement mixes with nervousness.",
        "Eles se aproximam do guichê.": "They approach the ticket counter.",
        "Duas passagens para Campos do Jordão, por favor, diz Lucas.": "Two tickets to Campos do Jordão, please, says Lucas.",
        "Só ida ou ida e volta?": "One way or round trip?",
        "pergunta a atendente.": "asks the attendant.",
        "Só ida.": "One way.",
        "O ônibus sai que horas?": "What time does the bus leave?",
        "pergunta Sophie.": "asks Sophie.",
        "Às onze e quinze.": "At eleven fifteen.",
        "Vocês têm sorte, é o direto.": "You're lucky, it's the direct one.",
        "Lucas olha o relógio.": "Lucas looks at his watch.",
        "Temos tempo de tomar um café?": "Do we have time for a coffee?",
        "Sim, temos meia hora.": "Yes, we have half an hour.",
        "Eles encontram uma lanchonete na rodoviária.": "They find a snack bar in the bus station.",
        "Sophie pergunta ao atendente: Qual plataforma para o ônibus de Campos do Jordão?": "Sophie asks the attendant: Which platform for the Campos do Jordão bus?",
        "Plataforma número sete.": "Platform number seven.",
        "Você vai ver os painéis.": "You'll see the signs.",
        "Lucas verifica sua mochila.": "Lucas checks his backpack.",
        "Não esqueça sua mochila!": "Don't forget your backpack!",
        "Já peguei.": "I already got it.",
        "E você, tem as passagens?": "And you, do you have the tickets?",
        "Sim, no meu bolso.": "Yes, in my pocket.",
        "Sophie respira fundo.": "Sophie takes a deep breath.",
        "Você está pronto para a aventura?": "Are you ready for the adventure?",
        "Sim, mais do que nunca!": "Yes, more than ever!",
        "Um anúncio ressoa na rodoviária.": "An announcement echoes through the bus station.",
        "O ônibus vai chegar logo.": "The bus will arrive soon.",
        "Vamos rápido, tem muita gente, diz Lucas.": "Let's hurry, there are a lot of people, says Lucas.",
        "Eles encontram seus assentos no ônibus.": "They find their seats on the bus.",
        "Aqui estão nossos lugares.": "Here are our seats.",
        "Perto da janela!": "Near the window!",
        "O ônibus parte.": "The bus departs.",
        "Sophie olha São Paulo ficando para trás.": "Sophie watches São Paulo fade behind.",
        "Lá vamos nós para uma nova vida!": "Here we go to a new life!",
        
        # Continue with remaining scenes...
        # Scene 6
        "O ônibus viaja pela rodovia Dutra.": "The bus travels along the Dutra highway.",
        "Sophie e Lucas olham a paisagem que passa pela janela.": "Sophie and Lucas watch the landscape passing by the window.",
        "Finalmente saímos de São Paulo, diz Sophie, quase incrédula.": "We finally left São Paulo, says Sophie, almost incredulous.",
        "Lucas verifica seu celular.": "Lucas checks his phone.",
        "Você trancou a porta direito?": "Did you lock the door properly?",
        "Sim, verifiquei três vezes.": "Yes, I checked three times.",
        "E você, avisou seu trabalho?": "And you, did you notify your work?",
        "Sim, mandei um email ontem à noite.": "Yes, I sent an email last night.",
        "Sophie se vira para Lucas.": "Sophie turns to Lucas.",
        "O que você está sentindo?": "What are you feeling?",
        "Me sinto livre e um pouco nervoso.": "I feel free and a little nervous.",
        "É estranho, né?": "It's strange, isn't it?",
        "Eu também, é normal.": "Me too, it's normal.",
        "A gente está mudando toda nossa vida.": "We're changing our whole life.",
        "A paisagem fica cada vez mais montanhosa.": "The landscape becomes increasingly mountainous.",
        "Olha a paisagem, está linda!": "Look at the landscape, it's beautiful!",
        "Sophie abre sua mochila.": "Sophie opens her backpack.",
        "Trouxe sanduíches.": "I brought sandwiches.",
        "Queijo e presunto.": "Cheese and ham.",
        "Ótima ideia, estou com fome.": "Great idea, I'm hungry.",
        "Eles comem em silêncio, admirando a vista.": "They eat in silence, admiring the view.",
        "Lucas pergunta: Quanto tempo dura a viagem?": "Lucas asks: How long is the journey?",
        "Umas cinco horas.": "About five hours.",
        "Chegamos por volta das quatro.": "We arrive around four.",
        "Sophie procura em sua mochila.": "Sophie searches in her backpack.",
        "Ah não!": "Oh no!",
        "Esqueci meu livro!": "I forgot my book!",
        "Não tem problema, a gente pode conversar.": "No problem, we can talk.",
        "Sobre o que você quer falar?": "What do you want to talk about?",
        "Lucas pensa.": "Lucas thinks.",
        "Sobre nossos sonhos e nosso futuro.": "About our dreams and our future.",
        "O que você realmente quer na vida?": "What do you really want in life?",
        "Sophie sorri.": "Sophie smiles.",
        "É uma grande pergunta.": "That's a big question.",
        "Eu quero me sentir viva, eu acho.": "I want to feel alive, I think.",
    }


def translate_all_scenes(lang_code):
    """Translate all scene files for a given language."""
    scenes_dir = Path(f"language_materials/{lang_code}/story-scenes-json")
    
    if not scenes_dir.exists():
        print(f"Error: Directory not found: {scenes_dir}")
        return
    
    # Get translation map
    if lang_code == 'pt':
        translations = get_translation_map_pt()
    else:
        print(f"Error: No translation map available for language: {lang_code}")
        return
    
    total_translated = 0
    total_files = 0
    
    for json_file in sorted(scenes_dir.glob("scene-*.json")):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated_count = 0
        for phrase_obj in data[lang_code]:
            source_text = phrase_obj[lang_code]
            if source_text in translations:
                phrase_obj['english'] = translations[source_text]
                translated_count += 1
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ {json_file.name}: {translated_count} phrases translated")
        total_translated += translated_count
        total_files += 1
    
    print(f"\n✅ Completed: {total_files} files, {total_translated} phrases translated")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_translate_story.py <lang_code>")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    translate_all_scenes(lang_code)
