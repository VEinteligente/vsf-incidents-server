from plugins.views import PluginTableView


class DemoTableView(PluginTableView):
    titles = ['flags', 'id', 'input']


def hola_hola():
    print 'esto es una prueba exitosa'
    return True


def chao_chao():
    print "WOOOOOOOOOOOOOOHOOOOOOOOOOOOOOO------------"
    return False
