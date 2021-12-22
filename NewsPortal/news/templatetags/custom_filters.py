from django import template

register = template.Library()

@register.filter(name='censor')
def censor(text):
	stop_words = ['хуй', 'ебан', 'ебат', 'хуев', 'пизд', 'бляд'] # и всё в таком духе

	for stop in stop_words:
		while stop in text.lower():
			ind = (text.lower()).index(stop)
			text = text[0 : ind + 1] + '...' + text[(ind + len(stop)):]

	return text