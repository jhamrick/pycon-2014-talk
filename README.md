# Games for Science: Creating interactive psychology experiments in Python with Panda3D

Jessica Hamrick  
Peter Battaglia

## Description

Have you ever wanted to play video games while also contributing to
science? In psychology experiments developed by myself and Peter
Battaglia, participants are immersed in an interactive 3D world which
is experimentally well-controlled, yet also extremely fun. This talk
will explain how we created these "game-like" experiments in Python
using the Panda3D video game engine.

## Abstract

How do you create a psychology experiment which is engaging and
enjoyable for participants, yet also well-controlled by scientific
standards? In this talk, I will present several real experiments
developed by myself and my colleague Peter Battaglia which immerse
participants in a rich, 3D environment. Using Python, our experiments
simulate a semi-realistic world and present a level of interactivity
similar to that found in popular physics-based video games such as
Angry Birds.

To create such "game-like" experiments, we use the Panda3D video game
engine. Panda3D exposes the ability to capture key presses, track the
mouse, display text, simulate physics, and render 3D graphics, all
with the level of precision required by a well-controlled
experiment. Furthermore, because Panda3D uses Python, it integrates
well with powerful tools such as NumPy and SciPy. The result is that
code involved in running behavioral experiments can be reused for
model simulations and data analysis.

During this talk, audience members will be able to collectively
participate in demos of our experiments. After each demo, I will walk
through the steps that were necessary to create the experiment,
emphasizing both where there are differences between implementing an
interactive experiment versus an actual video game, and how the
experiments fit within a larger theme of Python in science.


## Generating and viewing slides

The slides are saved in the form of an IPython notebook, in
`pycon-2014.ipynb`. To convert them to HTML slides, you can simply
type `make`, which will generate `pycon-2014.slides.html`.

To serve these slides locally, you can run the command `make
serve`. They will then be accessible from the URL
`http://localhost:8000/pycon-2014.slides.html`.
