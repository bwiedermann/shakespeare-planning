from plotly.graph_objs import Bar, Histogram, Layout, Heatmap
from plotly.tools import FigureFactory
from operator import attrgetter
from stats import isInScene, speechesPerScene, linesPerScene, wordsPerScene

# ========================================
# Bar Plots
# ========================================


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
            # tick0=0,
            # dtick=1,
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
            x=xValues,
            y=yValues,
            orientation='h',
        )
    ]

    return {'data': data, 'layout': barLayout(title)}


def characterPlot(play, extractor, title, characters=None):
    if not characters:
        characters = play.characters

    data = sorted([(extractor(character), character.name)
                  for character in characters])
    values, names = zip(*data)
    return horizontalPlot(values, names, title)


def characterLinePlot(play, characters=None):
    return characterPlot(play, lambda c: c.numLines, 'lines', characters)


def characterSpeechPlot(play, characters=None):
    return characterPlot(play, lambda c: c.numSpeeches, 'speeches', characters)


def characterScenePlot(play, characters=None):
    return characterPlot(play, lambda c: c.numScenes, 'scenes', characters)


# ========================================
# Character heat maps
# ========================================

def heatMap(x, y, z, title=None):
    #colorscale = [[0, 'rgb(250,250,250)'], [1, 'rgb(255, 153, 0)']]
    colorscale = [[0, 'rgb(250,250,250)'], [1, 'rgb(0, 150, 255)']]

    data = [
        Heatmap(
            x=x,
            y=y,
            z=z,
            colorscale=colorscale,
            colorbar=dict(outlinewidth=0, outlinecolor='#cfcfcf'),
        )
    ]

    defaultAxis = dict(type='category',
                       showticklabels=True,
                       tickfont=dict(
                            family='Old Standard TT, serif',
                            size=8,
                            color='black'
                       ),
                       )

    topAxis = defaultAxis.copy()
    topAxis.update(dict(side='top'))

    bottomAxis = defaultAxis.copy()
    bottomAxis.update(dict(side='bottom', overlaying='x'))

    layout = Layout(
        xaxis=topAxis,
        xaxis2=bottomAxis,
        yaxis=defaultAxis,
        title=title,
        # height = 200,
    )

    return {'data': data, 'layout': layout}


def characterMap(play, metric=isInScene, characters=None):

    if not characters:
        characters = play.characters

    sortedCharacters = sorted(characters, key=lambda c: len(c.scenes))

    # for the horizontal axis
    sceneNames = sorted(['%d.%d' % (scene.act.number, scene.number)
                        for scene in play.scenes])

    # for the vertical axis
    characterNames = [character.name for character in sortedCharacters]

    # for the value axis
    intensities = [[metric(character, scene) for scene in play.scenes]
                   for character in sortedCharacters]

    return heatMap(sceneNames, characterNames, intensities)

# ========================================
# Character comparison
# ========================================


def characterCompare(play, character1, character2, metric=speechesPerScene):
    c1 = [c for c in play.characters if c.name == character1][0]
    c2 = [c for c in play.characters if c.name == character2][0]

    # for the horizontal axis
    sceneNames = sorted(
        [f'{scene.act.number}.{scene.number}' for scene in play.scenes])

    # for the value axis
    c1Values = [metric(c1, scene) for scene in play.scenes]
    c2Values = [-1*metric(c2, scene) for scene in play.scenes]

    data = [Bar(x=sceneNames, y=c1Values, orientation='v', name=character1.title()),
            Bar(x=sceneNames, y=c2Values, orientation='v', name=character2.title())]

    layout = Layout(barmode='relative', xaxis=dict(type='category'))

    return {'data': data, 'layout': layout}


def characterPairingsMap(play, characters=None):
    if not characters:
        characters = play.characters
    sortedCharacters = sorted(characters, key=lambda c: len(c.scenes))
    pairings = {}
    for character in sortedCharacters:
        pairings[character] = {c: 0 for c in sortedCharacters}
        for scene in character.scenes:
            for other in [c for c in scene.characters if c in sortedCharacters]:
                if other is not character:
                    pairings[character][other] += 1

    names = [c.name for c in sortedCharacters]
    intensities = [[pairings[c][o]
                    for o in reversed(sortedCharacters)] for c in sortedCharacters]
    # return heatMap(list(reversed(names)), [names[-2], names[-3]], [intensities[-2], intensities[-3]])
    return heatMap(list(reversed(names)), names, intensities)
