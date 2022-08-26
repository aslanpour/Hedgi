config={}
config['governors'] = 'ond1emand'
govs={0: 'ondemand', 1: 'ondemand', 2: 'ondemand', 3: 'ondemand'}

a = True if True in [True if config['governors'] != governor else False for core, governor in govs.items()] else False

print(a)