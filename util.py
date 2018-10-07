from operator import attrgetter

def containsField(kind, adder, name, pluralName):
    '''A class decorator to inject a given field name of a given field type'''

    def classWrapper(cls):
        class Wrapper(cls):
            def __init__(self):
                super().__init__()                
                setattr(self, pluralName, kind())  # initialize the field value
        # inject a method that adds something to the field's value
        setattr(Wrapper, 'add%s' % name.title(), adder)
        return Wrapper

    return classWrapper

def containsSetField(name, pluralName=None):
    '''A class decorator that adds a field of a given name, whose value is a set'''

    if not pluralName:
        pluralName = name + 's'

    def addSetValue(self, value):
        '''A method to add a new value to the set'''
        getattr(self, pluralName).add(value)

    return containsField(set, addSetValue, name, pluralName)

def containsListField(name, pluralName=None):
    '''A class decorator that adds a field of a given name, whose value is a list'''

    if not pluralName:
        pluralName = name + 's'

    def addListValue(self, value):
        '''A method to append a new value to the list'''
        getattr(self, pluralName).append(value)

    return containsField(list, addListValue, name, pluralName)

def containsNumberedField(name, pluralName=None):
    '''A class decorator that adds a field of a given name, whose value is a 
    dictionary, keyed by a number'''

    if not pluralName:
        pluralName = name + 's'    

    hiddenPluralName = '_' + pluralName
    
    def addNumberedValue(self, value):
        '''A method to add / update the numbered field'''
        getattr(self, hiddenPluralName)[value.number] = value
        setattr(self, '%s%d' % (name, value.number), value)
        
    def wrapper(cls):
        
        def allThingsInOrder(self):
            '''A method to return all the fields, in numbered order'''
            return sorted(getattr(self, hiddenPluralName).values(), key=attrgetter('number'))
        
        @containsField(dict, addNumberedValue, name, hiddenPluralName)
        class Wrapper(cls):
            pass
        
        # inject a method that adds a property for the numbered field
        setattr(cls, pluralName, property(fget=allThingsInOrder))
        return Wrapper
    
    return wrapper

class Numbered(object):
    def __init__(self, number):
        self.number = number
        super().__init__()
        
class Named(object):
    def __init__(self, name):
        self.name = name
        super().__init__()
        
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name   
    
def registered(cls, registry={}):
    '''A decorator to register instances of a named class'''
    class Wrapper(cls):
        def __new__(cls, name):
            if name not in registry:
                instance = super().__new__(cls)
                instance._initialized = False
                registry[name] = instance
            return registry[name]
        def __init__(self, name):
            if self._initialized:
                return
            else:
                super().__init__(name)
                self._initialized = True
    return Wrapper
