import abstracter.util.network as network


class Workspace:
    """
    THE Workspace
    """

    def __init__(self):
        self.network = network.Network()

    def __getitem__(self, id):
        return self.network[id]["syntagm"]

    def items(self):
        for n, d in self.network.nodes_iter():
            if "syntagm" in d:
                yield (n, d["syntagm"])

    def add_node(self, id, node=None, **kwargs):
        id = tuple(id)
        if node is None:
            raise RuntimeError("The node must not be null")
        else:
            self.network.add_node(id, syntagm=node)

            for lbl, dest_id in node.get_relations():
                if dest_id is not None:
                    self.network.add_edge(
                        id, tuple(dest_id), relation_type=lbl
                    )

    def get_node(self, parid, lid):
        return self.network.get_node((parid, lid))


class Syntagm:

    def __init__(self, id, name=None, tags={}, number_children=0):
        self.id = id
        self.name = name
        self.number_children = number_children
        self.tags = tags
        if 'id' in self.tags:
            del self.tags['id']

    def __getitem__(self, id):
        return self.tags[id]

    def add_atribute(self, **kwargs):
        for attr, val in kwargs.items():
            self.tags[attr] = val

    def get_tags(self):
        return self.tags

    def get_relations(self):
        parent = self.id[0:-1]
        sons = [
            ("parent_of", self.id.append(son_id))
            for son_id in range(0, self.number_children - 1)
        ]
        return [("son_of", parent)] + sons

    def set_number_children(self, number):
        self.number_children = number

    def add_tag(self, tag, value):
        self.tags[tag] = value


class Entity(Syntagm):
    '''
    @class Entity
    @brief Represents an entity in the text,
    as in an actual being in the real world that we've seen in the text.
    it contains :
    * a name
    * a list of the attributes that reference to it
    * a list of references where the entity is referred to in the text,
        under the norm (paragraphNumber, wordNumber)
    '''

    def __init__(self, id, name=None, attributes=[], references={}, tags={}):
        '''
        Initialises an entity. All arguments but the name are optional.
        @param name the name of the entity
        @param attributes a list of the attribute applying to the entity
        @param references a list of places
            where that entity is referred to in the text
        @return an entity ready to be pushed in the workspace !
        '''
        super(Entity, self).__init__(id, name, tags=tags)
        self.attributes = attributes
        self.references = references

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
            (beginWordTuple, endWordTuple)
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

    def get_relations(self):
        return (
            super(Entity, self).get_relations() +
            [
                ("has_attribute", attribute) for attribute in self.attributes
            ]
        )


class Attribute(Syntagm):
    '''
    @class Attribute
    @brief Represents an attribute to an entity.
    Since an attribute is generally associated to only one entity and
    entities have a list of attributes, an attribute will only consist in :
    * A name, which will essentially be a concept for the attribute.
        "Captain", for instance.
    * A logical modifier (such as "not" for "not captain",
        no other example at the moment)
    '''

    def __init__(self, id, name, modifier=None, tags={}):
        '''
        Creates an instance of the object,
        ready to be added to an entity or pushed in the workspace.
        @param name Title for the attribute
        @param modifier An optional logical modifier for the title.
        '''

        super(Attribute, self).__init__(id, name, tags=tags)
        if modifier:
            self.modifier = modifier

    def modify(self, modifier):
        '''
        Amends the modifier of the attribute. Assuming an attribute can have
        at most one modifier, it erases the previous one.
        @param modifier new modifier)
        '''
        self.modifier = modifier


class Event(Syntagm):
    '''
    @class Event
    Represents an event, or a change, related in the text that we have somehow
    managed to find and want to push in the workspace. It contains:
    * An entity or attribute of origin (before the change)
    * An entity or attribute of destination (after the change)
    * A list of other events that this one is linked to. The links are labeled
    with the nature of the relationship between the two events
        (sameTime, consequence, etc.)
    '''

    def __init__(self, id, name, origin=None,
                 destinations=[], events=None, tags={}):
        '''
        Creates an event, ready to be pushed in the workspace.
        @param origin Attribute or Entity before the change.
        @param destinations list of Attributes or Entities after the change.
        @param events An optional list of other events this one is linked to
        '''

        super(Event, self).__init__(id, name, tags)
        self.origin = origin
        self.destinations = destinations

        if events:
            self.events = events

    def add_event(self, event):
        '''
        Adds an event linked to this one.
        @param event A tuple like (relationship, event_object)
            to link with this one
        '''
        self.events.append(event)

    def remove_event(self, event):
        '''
        Deletes the link between this event and another,
            whatever the relationship was.
        @param event The event to be separated from this one
        '''

        for e in self.events:
            if e[1] == event:
                self.events.remove(e)

    def get_relations(self):
        return (
            super(Event, self).get_relations() +
            [
                ("dest", destination)
                for destination in self.destinations
            ] +
            [
                ("origin", self.origin)
            ]
            )


class WordGroup(Syntagm):
    pass
