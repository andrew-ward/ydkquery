import ygo
from lxml import html

def load(url):
	if isinstance(url, int) or url.isdigit():
		url = 'http://yugiohtopdecks.com/deck/{}'.format(url)
	text = ygo.core.compat.get_html(url)
	tree = html.fromstring(text)

	byline_section = tree.xpath('//body/div/div/div[@class="large-5 columns"]/div/div[@class="large-12 columns panel"]')
	title = tree.xpath('//body/div/div/div[@class="large-5 columns"]/div/div[@class="large-12 columns panel"]/h3/b')[0].text.strip()
	author = tree.xpath('//body/div/div/div[@class="large-5 columns"]/div/div[@class="large-12 columns panel"]/p/a')[0].text.strip()

	sections = tree.xpath('//body/div/div/div[@class="large-6 columns"]')
	main_deck_div = sections[0]
	other_deck_div = sections[1]
	
	
	main_deck = ygo.core.deck.YugiohSet()
	card_tags = main_deck_div.find('div').find('ul').findall('li')
	for card in card_tags:
		name = card.find('a').text.strip()
		count = int(card.find('b').text.strip()[0])
		ygocard = ygo.search.find(name)
		main_deck.add_card(ygocard, count)
	
	section_divs = other_deck_div.find('div').findall('ul')
	extra_deck_card_tags = section_divs[0].findall('li')
	side_deck_card_tags = section_divs[1].findall('li')

	side_deck = ygo.core.deck.YugiohSet()
	for card in extra_deck_card_tags:
		name = card.find('a').text.strip()
		count = int(card.find('b').text.strip()[0])
		ygocard = ygo.search.find(name)
		side_deck.add_card(ygocard, count)
		
	extra_deck = ygo.core.deck.YugiohSet()
	for card in side_deck_card_tags:
		name = card.find('a').text.strip()
		count = int(card.find('b').text.strip()[0])
		ygocard = ygo.search.find(name)
		extra_deck.add_card(ygocard, count)
	return ygo.core.deck.YugiohDeck(title, author, main_deck, side_deck, extra_deck)

if __name__ == '__main__':
	result = load(4652)
	print result.as_markdown()
