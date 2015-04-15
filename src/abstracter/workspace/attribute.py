

class Attribute:
    '''
    @class Attribute
    @brief Represents an attribute to an entity.
    Since an attribute is generally associated to only one entity and 
    entities have a list of attributes, an attribute will only consist in :
    * A name, which will essentially be a concept for the attribute. "Captain", for instance.
    * A logical modifier (such as "not" for "not captain", no other example at the moment)
    '''

    def __init__(self, name, modifier=None):
        '''
        Creates an instance of the object, ready to be added to an entity or pushed in the workspace.
        @param name Title for the attribute
        @param modifier An optional logical modifier for the title.
        '''

        self.name = name
        if modifier:
            self.modifier = modifier

    def modify(self, modifier):
        '''
        Amends the modifier of the attribute. Assuming an attribute can have
        at most one modifier, it erases the previous one.
        @param modifier new modifier)
        '''
        self.modifier = modifier
