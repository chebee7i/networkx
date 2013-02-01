"""
Module implementing restricted APIs based on graph types.

"""
_graph_types = set(['graph', 'multigraph', 'digraph', 'multidigraph'])

class MockModule(object):
    """
    A mock module.

    """
    def __init__(self, name):
        self._name = name

        # We distinguish between a module which mocks a real module and one
        # which is just a mock module.
        import networkx
        try:
            # The mock module mocks a real module.
            self._module = eval(name)
        except (AttributeError, NameError):
            # This mock module does not mock a real module.
            self._module = None

    def __repr__(self):
        if self._module is None:
            msg = '<MockModule {0}>'
        else:
            msg = '<MockModule for {0}>'
        return msg.format(self._name)

    def _register(self, func):
        """
        Register `func` with this module.

        This will recursively create new mock modules if necessary.

        """
        modname = func.__module__

        # Ignore the top level module ('networkx').
        modnames = modname.split('.')[1:]
        current_module = self
        for i, modname in enumerate(modnames):
            try:
                current_module = getattr(current_module, modname)
            except AttributeError:
                name = '.'.join(['networkx'] + modnames[:i+1])
                new_module = MockModule(name)
                setattr(current_module, modname, new_module)
                current_module = new_module
        else:
            setattr(current_module, func.__name__, func)

def register(*graph_types):
    """
    Decorator to register a function as usable for the specified graph types.

    Parameters
    ----------
    graph_types : str
        One or more graph types. Acceptable types are: 'graph', 'multigraph',
        'digraph', 'multidigraph'.

    Returns
    -------
    func : function
        The original function with a new attribute 'graph_types', a set which
        contains the acceptable graph types.

    """
    import networkx as nx
    graph_types = set(graph_types)

    # Make sure only known graph types are included.
    unknown_types = graph_types - _graph_types
    if unknown_types:
        msg = 'Invalid graph types: {0}'.format(unknown_types)
        raise nx.NetworkXError(msg)

    # Create the decorator (without arguments) and return it.
    def decorator(func):
        # Register this function in the appropriate mock modules.
        cmd = '{0!s}_only._register'
        for graph_type in graph_types:
            eval(cmd.format(graph_type))(func)

        # Store the applicable graph types as a function attribute.
        func.graph_types = graph_types

        return func

    return decorator

# Create mock modules for APIs restricted by graph type.
_g = globals()
for graph_type in _graph_types:
    _g[graph_type + '_only'] = MockModule(graph_type)
del graph_type

