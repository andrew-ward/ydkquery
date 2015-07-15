Library = {}
def register(name):
	def decorate(f):
		Library[name] = f
		return f
	return decorate

@register('or')
def log_and(visitor, card, left, right):
	if left.accept(visitor, card):
		return True
	else:
		return right.accept(visitor, card)

@register('and')
def log_and(visitor, card, left, right):
	if left.accept(visitor, card):
		return right.accept(visitor, card)
	else:
		return False

@register('not')
def log_and(visitor, card, right):
	right = right.accept(visitor, card)
	if right == None:
		return None
	else:
		return not right.accept(visitor, card)

@register('>')
def cmp_gt(visitor, card, left, right):
	left = left.accept(visitor, card)
	right = right.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return left > right

@register('<')
def cmp_lt(visitor, card, left, right):
	left = left.accept(visitor, card)
	right = right.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return left < right

@register('>=')
def cmp_gte(visitor, card, left, right):
	left = left.accept(visitor, card)
	right = right.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return left >= right

@register('<=')
def cmp_lte(visitor, card, left, right):
	left = left.accept(visitor, card)
	right = right.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return left <= right

@register('=')
def cmp_eq(visitor, card, left, right):
	left = left.accept(visitor, card)
	right = right.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return left == right

@register('!=')
def cmp_neq(visitor, card, left, right):
	left = left.accept(visitor, card)
	right = right.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return left != right

@register('contains')
def str_contains(visitor, card, left, right):
	right = right.accept(visitor, card)
	left = left.accept(visitor, card)
	if left == None or right == None:
		return None
	else:
		return right in left

@register('any')
def hand_any(visitor, hand, arg):
	for card in hand:
		result = arg.accept(visitor, card)
		if result == None:
			continue
		elif result == True:
			return True
	return False

@register('all')
def hand_all(visitor, hand, arg):
	for card in hand:
		result = arg.accept(visitor, card)
		if result == None:
			continue
		elif result == False:
			return False
	return True
