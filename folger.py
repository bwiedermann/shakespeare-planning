import os, itertools, re
from collections import defaultdict
from operator import itemgetter, attrgetter
from play import *

ACT_SPLIT    = re.compile(r'ACT\s+\d+')
SCENE_SPLIT  = re.compile(r'Scene\s+\d+')
BUSINESS_RE  = re.compile(r'((,\s+)?\[.+?\])|(^\[.*$)|(^[^\[]+\])$', re.MULTILINE)
MARKUP_RE    = re.compile(r'=+') 
SPEECH_RE    = re.compile(r'^([A-Z][A-Z\']+[ ]?[A-Z]+\s+)', re.MULTILINE)
CHARACTER_RE = re.compile(r'^[A-Z][A-Z\']+[ ]?[A-Z]+')

def makeNumberedSplit(text, splitter, hasFrontMatter=True):
    '''returns a dictionary of {number : text}'''
    
    splits = splitter.split(text)
    
    # get rid of front-matter, if necessary
    if (hasFrontMatter):
        splits = splits[1:]
    
    # return a dictionary, with numbers as keys
    return {i: split for i, split in enumerate(splits, start=1)}

def play2acts(text):
    '''returns a dictionary of {actNumber : text}'''
    return makeNumberedSplit(text, ACT_SPLIT)

def act2scenes(text):
    '''returns a dictionary of {sceneNumber : text}'''
    return makeNumberedSplit(text, SCENE_SPLIT)

def scene2speeches(text, act, scene):
    # remove business
    text = BUSINESS_RE.sub('', text)

    # remove markup
    text = MARKUP_RE.sub('', text)

    # remove empty lines
    text = os.linesep.join([s for s in text.splitlines() if s])

    # split into speeches
    speeches = [part for part in SPEECH_RE.split(text) if part]
    names = [name.strip() for name in speeches[0::2]]    
    lines = speeches[1::2]
    
    # check for errors: all the names should match the character RE
    if not all(CHARACTER_RE.match(name) is not None for name in names):
        raise ValueError('Bad formatting in %d.%d: %s' % (act.number, scene.number, str(names)))
    
    # make characters
    characters = map(Character, names)

    # make speeches
    speeches = []
    lineNumber = 1  # line numbers reset at scene breaks
    for character, line in zip(characters, lines):
        newSpeech = Speech(character, act, scene, lineNumber, line)
        speeches.append(newSpeech)
        lineNumber += len(newSpeech.lines)
        
    return speeches

def processText(title, text):
    play = Play(title)

    # parse the text into acts
    actTexts = play2acts(text)
    for actNumber, actText in actTexts.items():
        act = Act(actNumber)
        play.addAct(act)

        # parse the act into scenes
        sceneTexts = act2scenes(actText)
        for sceneNumber, sceneText in sceneTexts.items():
            scene = Scene(sceneNumber)
            scene.act = act
            act.addScene(scene)
            
            # parse the scene into speeches
            speeches = scene2speeches(sceneText, act, scene)
            for speech in speeches:
                character = speech.character
                character.addSpeech(speech)
                scene.addSpeech(speech)
                scene.addCharacter(character)
                act.addCharacter(character)
                play.addCharacter(character)
    
    return play
