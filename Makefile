.PHONY: serve clean pdf
SOURCES=images custom.css reveal.js

pycon-2014.slides.html: pycon-2014.ipynb reveal.tpl
	ipython nbconvert --RevealHelpTransformer.url_prefix=reveal.js --to slides --template reveal.tpl pycon-2014.ipynb

pdf: pycon-2014.slides.html fixme.py
	python fixme.py

clean:
	rm -rf pycon-2014.slides.html

gh-pages:
	make clean || true
	make pycon-2014.slides.html
	git checkout gh-pages
	git checkout master $(SOURCES)
	git reset HEAD
	mv pycon-2014.slides.html index.html
	git add -A
	git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages
	git checkout master
