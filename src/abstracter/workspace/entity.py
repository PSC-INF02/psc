

class Entity:
    '''
    Represents an entity in the text,
    as in an actual being in the real world that we've seen in the text.
    it contains :
    * a name
    * a list of the attributes that reference to it
    * a list of references where the entity is referred to in the text,
        under the norm (paragraphNumber, wordNumber)
    '''

    def __init__(self, name=None, attributes=None, references=None):
        '''
        Initianalises an entity. All arguments but the name are optional.
        @param name the name of the entity
        @param attributes a list of the attribute applying to the entity
        @param references a list of places
            where that entity is referred to in the text
        @returns an entity ready to be pushed in the workspace !
        '''

        self.name = name
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = []
        if references:
            self.references = references
        else:
            self.references = []

    def add_attribute(self, attributeID):
        '''
        Adds An attribute object to the attributes list
        @param attributeID the ID of the attribute to add
        '''

        self.attributes.append(attributeID)

    def add_reference(self, reference):
        '''
        Adds another reference to the references list
        @param reference a reference tuple :
            (paragraphNumber, beginWordNumber, endWordNumber)
        '''

        self.references.append(reference)

    def get_attributes(self):
        '''
        @returns attributes of the entity as a list
        '''

        return self.attributes

    def remove_attribute(self, attribute):
        '''
        Removes an attribute from the entity.
        @param attribute Attribute to remove.
        '''

        self.attributes.remove(attribute)
