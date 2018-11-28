"""
ultra.py

Increasingly vivid race reports.

Copyright 2018 Nathan Mifsud <nathan@mifsud.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import codecs
import json
import markovify
import nltk
import random
import re
import time
from num2words import num2words

# Import text to feed the Markov models
with open("barkley.txt", encoding="utf8") as f:
    text_race = f.read()
with open("erowid.txt", encoding="utf8") as f:
    text_trip = f.read()

# Some descriptive variables to add flavour
with open("vars.json", encoding="utf8") as f:
    vars = json.load(f)
athlete = random.choice(vars["athlete"])
race_name = random.choice(vars["race_name"])
race_dist = random.randint(600,1000)
race_adj = random.choice(vars["race_adj"])
race_loc = random.choice(vars["race_loc"])
race_sig = random.choice(vars["race_sig"])
competitors = random.randint(40,120)

# Some internal consistency is better than none
text_race = text_race.replace('Barkley', race_name)

# Use NLTK to improve model quality (https://github.com/jsvine/markovify)
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words
    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

# Build the models
model_race = markovify.Text(text_race)
model_trip = markovify.Text(text_trip)

# Start assembling LaTeX
text = (r'''\documentclass[12pt,titlepage,a4paper]{article}
\usepackage{fontspec}
\setmainfont[Ligatures=TeX]{Equity Text A}
\usepackage{titlesec}
\newcommand{\sectionbreak}{\clearpage}
\usepackage{microtype}
\frenchspacing
\setlength{\parindent}{0in}
\setlength{\parskip}{1em}

\begin{document}

\title{%
    \LARGE{\bfseries{Not Your Average Ultra}}\\\vspace{.5em}
    \large{A report by ''' + athlete + ', winner of the ' + race_name + '—'
+ race_adj + ' ' + str(race_dist) + ' km (' + str(round(race_dist*0.6214))
+ ' mi) trail race set ' + race_loc + r'''}}
\author{https://github.com/nmifsud/ultra}
\date{''' + time.strftime('%d %B %Y') + r'''}
\maketitle''' + '\n\n')

# The race is split into legs, each of whose entries is split into arbitrary
# paragraphs to improve readability
legs = range(1,random.randint(16,24))
headings = random.sample(vars["middle"], len(vars["middle"]))
athletes = random.sample(vars["athlete"], len(vars["athlete"]))
len_chap = [8, 13, 17, 25, 31, 33, 34, 35, 36, 37, 39, 44, 50, 55, 67]
len_para = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 7, 9, 11]
wc = 0

for leg in legs:
    # Select appropriate entry heading
    ord = num2words(leg//2 + (leg % 2 > 0), to='ordinal').capitalize()
    if leg == 1:
        text += r'\section*{' + random.choice(vars["start"]) +'}\n\n'
    elif leg == int(max(legs)/2):
        text += r'\section*{Halfway there}' + '\n\n'
    elif leg == max(legs):
        text += r'\section*{' + random.choice(vars["end"]) +'}\n\n'
    elif leg % 2 != 0 and random.random() > .5:
        text += r'\section*{' + ord + ' day}\n\n'
    elif leg % 2 == 0 and random.random() > .5:
        text += r'\section*{' + ord + ' night}\n\n'
    else:
        text += r'\section*{' + headings.pop() +'}\n\n'

    # A paper-thin veneer of coherent narrative
    half = str(int(round(race_dist/2,-1)))
    dropped = int(round(random.randint(2,round(max(legs)/4))))
    competitors -= dropped
    if leg == 1:
        text += (race_sig + ', signalling the start of the race. '
        + num2words(competitors).capitalize() + ' of us moved off in a pack. ')
    elif leg == 3:
        text += num2words(dropped).capitalize() + ' runners were already gone. '
    elif leg == int(max(legs)/3):
        text += 'Another ' + str(dropped) + ' runners had dropped. '
    elif leg == int(max(legs)/2):
        text += ('I glanced down at my watch. ' + half + '-ish kilometres down, '
        + half + ' to go! ')
    elif leg == max(legs)-1 and competitors > 1:
        text += 'Only ' + str(competitors) + ' others were still in the race. '
    elif leg == max(legs)-1 and competitors == 1:
        text += 'Only ' + athletes.pop() + ' and I were still in the race. '
    elif leg == max(legs)-1 and competitors < 1:
        text += ('I was the only person left with a hope of completing the '
        + race_name + ' this year. ')
    elif leg == max(legs):
        text += ('I could taste the end of this ' + str(int(max(legs)/2))
        + '-day beast ' + race_loc + '. ')

    # This number pair will weight the mixed Markov model for this iteration,
    # initially race reports only, with increasingly stronger trip influences
    div = leg/max(legs)
    if div < .25:
        mix = [1, 0]
    elif .25 <= div <= .5:
        mix = [2-div, 1]
    elif .5 < div < .75:
        mix = [2-div, 1+div]
    elif div >= .75:
        mix = [1, 1+div]

    # Finally, generate the sentences!
    model = markovify.combine([model_race, model_trip], mix)
    chap = []
    for c in range(random.choice(len_chap)):
        for p in range(random.choice(len_para)):
            chap += model.make_sentence() + ' '
        chap = ''.join(chap) + '\n\n'
    text += chap
    wc += len(chap.split())

# Produce the finished report
text += r'\end{document}'
file = 'ultra-' + time.strftime('%y%m%d-%H%M%S') + '.tex'
with codecs.open(file, "w", "utf-8-sig") as t:
    t.write(text)
print('\nGenerated ' + file + ' (' + str(wc) + ' words)')
