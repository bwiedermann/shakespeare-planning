from util import *

# describes relationships that various parts of the play can have
@containsNumberedField('act')
class HasActs(object):
    pass

@containsNumberedField('scene')
class HasScenes(object):
    pass

@containsListField('speech', 'speeches')
class HasSpeeches(object):
    def lines(self):
        return sum(len(speech) for speech in self.speeches)

@containsSetField('character')
class HasCharacters(object):
    def addCharacter(self, character):
        setattr(self, character.name, character)
        super().addCharacter(character)


# describes the parts of the play
class Play(Named, HasCharacters, HasActs):
    @property
    def scenes(self):
        result = []
        for act in self.acts:
            result.extend(act.scenes)
        return result

class Act(Numbered, HasCharacters, HasScenes):
    pass

class Scene(Numbered, HasCharacters, HasSpeeches):
    pass

@registered
class Character(Named, HasSpeeches):
    @property
    def scenes(self):
        return sorted(set([speech.scene for speech in self.speeches]),
                      key = lambda scene: (scene.act.number, scene.number))
    

class Speech(object):
    def __init__(self, character, act, scene, startline=0, text=''):
        self.character = character
        self.act = act
        self.scene = scene
        self.startline = startline
        self.text = text
        self.lines = text.split('\n')
        self.endline = startline + len(self)
        
    def __len__(self):
        return len(self.lines)
    
    def __str__(self):
        output = [self.character]
        for lineNumber, line in enumerate(self.lines):
            actualLineNumber = lineNumber+self.startline
            numberString = str(actualLineNumber) if (actualLineNumber % 10 == 0) else ''
            output.append('{:77}{:>3}'.format(line, numberString))
        return '\n'.join(output)
    
    def __repr__(self):
        return str( (self.character, len(self), self.text, self.startline) )