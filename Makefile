.PHONY: serve clean

pycon-2014.slides.html: pycon-2014.ipynb
	ipython nbconvert --RevealHelpTransformer.url_prefix=reveal.js --to slides --template reveal.tpl pycon-2014.ipynb

clean:
	rm -rf pycon-2014.slides.html
