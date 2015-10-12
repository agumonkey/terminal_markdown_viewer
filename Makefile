clean:
	find . -type f -iname "*~" -delete
	find . -type f -iname "#*" -delete
	# find . -type d -iname "__pycache__" -delete
