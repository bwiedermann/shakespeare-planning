import pandas as pd
import numpy as np
import xarray as xr


def isInScene(character, scene):
    return character in scene.characters


def speechesInScene(character, scene):
    return [speech for speech in scene.speeches if speech.character is character]


def speechesPerScene(character, scene):
    characterSpeeches = speechesInScene(character, scene)
    return len(characterSpeeches)


def linesPerScene(character, scene):
    characterSpeeches = speechesInScene(character, scene)
    return sum(map(len, characterSpeeches))


def wordsPerScene(character, scene):
    characterSpeeches = speechesInScene(character, scene)
    return sum(map(lambda s: len(s.words), characterSpeeches))


def characterTable(play):
    characters = sorted(list(play.characters), key=lambda c: c.name)
    character_names = [character.name for character in characters]

    def get_data(extractor):
        return [extractor(character) for character in characters]

    character_data = pd.DataFrame(index=character_names)
    character_data['# of scenes'] = get_data(lambda c: c.numScenes)
    character_data['# of speeches'] = get_data(lambda c: c.numSpeeches)
    character_data['# of lines'] = get_data(lambda c: c.numLines)
    character_data['# of words'] = get_data(lambda c: c.numWords)
    return character_data


def playTable(play):
    scenes = play.scenes
    scene_names = [str(scene) for scene in scenes]
    characters = sorted(list(play.characters), key=lambda c: c.name)
    character_names = [character.name for character in characters]

    def get_data(extractor):
        return [[extractor(character, scene)
                 for scene in scenes]
                for character in characters]

    array = xr.Dataset(
        {"appearances": (('character', 'scene'), get_data(isInScene))},
        coords={
            'character': character_names,
            'scene': scene_names,
            'speeches': (('character', 'scene'), get_data(speechesPerScene)),
            'lines': (('character', 'scene'), get_data(linesPerScene)),
            'words': (('character', 'scene'), get_data(wordsPerScene))
        }
    )

    return array.to_dataframe()
