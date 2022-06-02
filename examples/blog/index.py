from datetime import date
import os

# This function must return a dict
def generate_model(ctx):
	articles = []
	for file in os.listdir('articles'):
		if not file.endswith('.dr'):
			continue
		res = ctx.resolve('articles/' + file)
		articles.append({
			'title': res.meta()['title'],
			'author': res.meta().get('author'),
			'date': res.meta()['date'],
			'href': res.path_output()
		})
	articles.sort(key=lambda a: date.fromisoformat(a['date']))
	return {'articles': articles}
