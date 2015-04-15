

class Event:
    '''
    @class Event
    Represents an event, or a change, related in the text that we have somehow
    managed to find and want to push in the workspace. It contains:
    * An entity or attribute of origin (before the change)
    * An entity or attribute of destination (after the change)
    * A list of other events that this one is linked to. The links are labeled
    with the nature of the relationship between the two events (sameTime, consequence, etc.)
    '''

    def __init__(self, origin, destination, events=None):
        '''
        Creates an event, ready to be pushed in the workspace.
        @param origin Attribute or Entity before the change.
        @param destination Attribute or Entity after the change.
        @param events An optional list of other events this one is linked to
        '''

        self.origin = origin
        self.destination = destination

        if events:
            self.events = events

    def add_event(self, event):
        '''
        Adds an event linked to this one.
        @param event A tuple like (relationship, event_object) to link with this one
        '''
        self.events.append(event)

    def remove_event(self, event):
        '''
        Deletes the link between this event and another, whatever the relationship was.
        @param event The event to be separated from this one
        '''

        for e in self.events:
            if e[1] == event:
                self.events.remove(e)

