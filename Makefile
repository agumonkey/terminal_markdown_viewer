clean:
	find . -type f -iname "*~" -delete
	find . -type f -iname "#*" -delete
	# find . -type d -iname "__pycache__" -delete

todo:
	@echo listing TOFIX, WAT, ... things to do
	@grep -E -R '@(WAT|TOFIX|TODO)'
