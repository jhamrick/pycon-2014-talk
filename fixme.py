# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------
# Copyright (c) 2013 - Damián Avila
#
# Distributed under the terms of the Modified BSD License.
#
# A little snippet to fix @media print issue printing slides from IPython
#-----------------------------------------------------------------------------

import io
import re

notebook = 'pycon-2014.ipynb'
path = notebook[:-6] + '.slides.html'
flag = u'@media print{*{text-shadow:none !important;color:#000 !important'

with io.open(path, 'r') as in_file:
    data = in_file.readlines()
    for i, line in enumerate(data):
        if line[:64] == flag:
            data[i] = data[i].replace('color:#000 !important;', '')
        data[i] = re.sub('data-fragment-index="[0-9]+"', "", data[i])
        data[i] = re.sub('class="[0-9]+"', "", data[i])
        data[i] = data[i].replace('class="fragment', 'class="')
        data[i] = data[i].replace('class=""', '')

with io.open(path, 'w') as out_file:
    out_file.writelines(data)

print "You can now print your slides"
