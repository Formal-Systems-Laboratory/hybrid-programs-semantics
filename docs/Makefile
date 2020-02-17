.PHONY := clean open

constraint_synthesis.pdf : constraint_synthesis.tex
	pdflatex constraint_synthesis

open : constraint_synthesis.pdf
	open constraint_synthesis.pdf



clean :
	rm -f constraint_synthesis.pdf constraint_synthesis.aux constraint_synthesis.fdb_latexmk constraint_synthesis.fls constraint_synthesis.log

