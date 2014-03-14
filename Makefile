.PHONY: serve clean

pycon-2014.slides.html: pycon-2014.ipynb
	ipython nbconvert --RevealHelpTransformer.url_prefix=reveal.js --to slides pycon-2014.ipynb

serve: pycon-2014.slides.html
	python -m SimpleHTTPServer

clean:
	rm -rf pycon-2014.slides.html
