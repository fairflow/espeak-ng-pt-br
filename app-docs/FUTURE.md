# Future of Miolingo

## Underlying language resources

### Phrase generation

We need to create somehow a better set of provided resources, larger in size and also accurately matched to the claimed difficulty model.

I'm thinking now of how to do this, probably first in French as that's our source language.  I want to the phrases to reflect an engaging narrative rather than being random or amusing or chosen just to cover some basic travelling situations.

So let's create a story about an adventurous couple who set out on a long journey, full of hope and optimism, if a little trepidacious.  They travel to an unfamiliar place and once there face many challenges, get separated and come together again once their individual challenges have been met.

Aucassin et Nicolette is one such story.  It goes back a long long way.  It's about love and heroism.  I don't know how it ends.

There may be Portuguese myths and legends we can draw on.  One route would be to construct a fairly long story, starting in today's rather mundane world, a city-dominated world of cafés and high tech shops, restaurants and bars, pousadas and cheap hotels.  The pair set off from their having been rather unsatifyingly nourished by some sweet pastries and strong but uninspiring coffees.  And so the story goes on!  Sadly this project does not have the luxury of such a story written by me or perhaps even another human.  I plan to delegate this task to an AI.

Next steps are to extract phrases from the narrative, involving a good selection of appropriate adjectives, adverbs, nouns, verbs and the range of different prepositions and pronouns, cases and tenses.  These phrases then need to be analysed for grammatical, lexical and conceptual difficulty and graded into the (rather random) categories A -- D we have chosen for the app.  There should also be progression from phrase to phrase within a given set, for example by including a larger number of unfamiliar phonemes to a foreign language learner, longer sentences or more complex word content.

Or aim is to produce at least 200 phrases,
ideally 1,000 in each language.

### Grammatical training (a later addition?)

The app is primarily conceived of as a language *speaking* assistant, not a grammatical trainer.  But we may well be able to incorporate some elements of this.  Hence the need to have present narrative, future imagining and past events and the telling of past events.

## Migration from Streamlit

This platform has limitations, for example no persistent data, memory restrictions (more so on the free package), limited GUI elements, limitations on languages supported and so on.  This needs to be researched but I anticipate that such limitations will be met if the app starts to take off, as I hope it will.  We need to find out what migration strategies we could adopt.  Can we host a Streamlit library based app on another machine for example?  [Clearly it works on my own machine]

## In-app management requirements

What this means is that we need, at least in the first instance, an admin user account with permission to upload data, check on other users logged in and so on.  Also the logging of users and resources (do we need a separate Streamlit app for this that access the database(s) live to provide admin information)

## Guest mode (no login needed)

What are the basic requirements and safety rails for such a mode (useful at the start for people who want to try the app without having to sign up)?

## Expand CCS "testing" mode

The main issue here is that there are now 2 sources of truth, the CCS-inspired model and the actual app behaviour.  In order to bring them into sync, it is necessary to take the CCS model as primary and to generate the GUI elements from it.  This seems to need metaprogramming (it is a little like a text-based app builder that you often found with early IDEs) because manual code connection is prone to errors.  Does Python have meta-programming perhaps?  I think this is different from eg. C\# reflection.  I have a Mathematica-based implementation of CCS and always wanted to be able to connect a graphical controller to facilitate simulation; from simulation it's a short step to implementation.  This is all in the relevant Mathematica notebooks.

## these are a record of today's thoughts and plans 15/11/2025
