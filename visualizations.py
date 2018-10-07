from plotly.graph_objs import Bar, Histogram, Layout, Heatmap
from plotly.tools import FigureFactory
from operator import attrgetter

#========================================
# Bar Plots
#========================================

def barLayout(title):
    return Layout(
        xaxis=dict(
            title=title,
            titlefont=dict(
                family='Times New Roman, serif',
                size=18,
                color='lightgrey'
            ),
            showticklabels=True,
            #tick0=0,
            #dtick=1,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=8,
                color='black'
            )
        ),
        yaxis=dict(
            type='category',
            titlefont=dict(
                family='Times New Roman, serif',
                size=18,
                color='lightgrey'
            ),
            showticklabels=True,
            tick0=0,
            dtick=1,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=8,
                color='black'
            )
        )
    )

def horizontalPlot(xValues, yValues, title=None):
    data = [
        Bar(
            x = xValues,
            y = yValues,
            orientation = 'h',
        )
    ]
    
    return {'data':data, 'layout':barLayout(title)} 

def characterLinePlot(play):
    data = sorted([(character.lines(), character.name) for character in play.characters])
    lines, names = zip(*data)
    return horizontalPlot(lines, names, "lines")

def characterSpeechPlot(play):
    data = sorted([(len(character.speeches), character.name) for character in play.characters])
    speeches, names = zip(*data)
    return horizontalPlot(speeches, names, "speeches")

def characterScenePlot(play):
    data = sorted([(len(character.scenes), character.name) for character in play.characters])
    scenes, names = zip(*data)
    return horizontalPlot(scenes, names, "scenes")

#========================================
# Character heat maps
#========================================
def isInScene(character, scene):
    return int(character in scene.characters)

def linesPerScene(character, scene):
    characterSpeeches = [speech for speech in scene.speeches if speech.character is character]
    return sum(map(len, characterSpeeches))

def heatMap(x, y, z, title=None):
    #colorscale = [[0, 'rgb(250,250,250)'], [1, 'rgb(255, 153, 0)']]
    colorscale = [[0, 'rgb(250,250,250)'], [1, 'rgb(0, 150, 255)']]
    
    data = [
        Heatmap(
            x=x,
            y=y,
            z=z,
            colorscale=colorscale,
            colorbar = dict(outlinewidth=0, outlinecolor='#cfcfcf'),            
        )
    ]

    defaultAxis = dict( type='category',
                        showticklabels=True,
                        tickfont=dict(
                            family='Old Standard TT, serif',
                            size=8,
                            color='black'
                        ),
                    )
    
    topAxis = defaultAxis.copy()
    topAxis.update( dict(side='top') )
    
    bottomAxis = defaultAxis.copy()
    bottomAxis.update( dict(side='bottom', overlaying='x') )

    layout = Layout(
        xaxis = topAxis,
        xaxis2 = bottomAxis,
        yaxis = defaultAxis,
        title = title
    )
    
    return {'data': data, 'layout': layout}


def characterMap(play, metric=isInScene):
    
    characters = sorted(play.characters, key=lambda c: len(c.scenes))

    # for the horizontal axis
    sceneNames = sorted(['%d.%d' % (scene.act.number, scene.number) for scene in play.scenes])
    
    # for the vertical axis
    characterNames = [character.name for character in characters]
    
    # for the value axis
    intensities = [[metric(character, scene) for scene in play.scenes] 
                   for character in characters]

    return heatMap(sceneNames, characterNames, intensities)

def metrics(play):
    
    numScenes = len(play.scenes)
    #characters = sorted(play.characters, key=lambda c: len(c.lines()))

    results = []
    for character in play.characters:
        characterScenes = len(character.scenes)
        characterName = character.name
        characterLines = character.lines()
        results.append('%s,%s,%s' % (characterName, characterLines, characterScenes))

    return '\n'.join(results)

def characterPairingsMap(play):
    characters = sorted(play.characters, key=lambda c: len(c.scenes))
    pairings = {}
    for character in characters:
        pairings[character] = {c:0 for c in characters}
        for scene in character.scenes:
            for other in scene.characters:
                if other is not character:
                    pairings[character][other] += 1

    names = [c.name for c in characters]
    intensities = [[pairings[c][o] for o in reversed(characters)] for c in characters]
    return heatMap(list(reversed(names)), names, intensities)
    
    