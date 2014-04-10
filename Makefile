.PHONY: serve clean
SOURCES=images custom.css reveal.js

pycon-2014.slides.html: pycon-2014.ipynb
	ipython nbconvert --RevealHelpTransformer.url_prefix=reveal.js --to slides --template reveal.tpl pycon-2014.ipynb

clean:
	rm -rf pycon-2014.slides.html

gh-pages:
	make clean || true
	make pycon-2014.slides.html
	mv pycon-2014.slides.html index.html
	git checkout gh-pages
	git checkout master $(SOURCES)
	git reset HEAD
	git add -A
	git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" #&& git push origin gh-pages
	git checkout master
