import simpy
import random
from copy import deepcopy

# Variables
RANDOM_SEED = 42
NUM_RECEPTIONIST = 1  # Number of receptionists available
WRITE_TIME = 2      # Minutes it takes to write a name tag
G_ENTER= 4       # Guest enters with a delay of 1 to 7 minutes
SIM_TIME = 80    # Simulation time in minutes
INITIAL_GUESTS = 2 #inital number of guests

SERVING_DRINK = 2 # Time taken to serve drink
PICKING_FOOD = 4 # Time taken to pick a food
DRINKING = 5 # Time taken to drink
EATING = 10 # Time taken to eat
DRINK_TABLES = 2 # Total Drink tables available
FOOD_TABLES = 2 # Total Food tables available
WALKING_TIME= 1 # Time to reach the food table
food_ready_at = 20 # Time the Food is being served at 
NO_OF_GUESTS = 5


guest_interaction_time = 3 # Time taken by a guest to talk to another guest
hostToGuestInteractionTime = 3 # Time taken by host to talk to a guest
num_of_conversations = 1 # how many people can talk to one individual
 


class Gathering(object):
    def __init__(self, env, num_receptionists, writetime, drink_tables, food_tables):
        self.env = env
        self.receptionist = simpy.Resource(env, num_receptionists)
        self.drink_tables = simpy.Resource(env, drink_tables)
        self.food_tables = simpy.Resource(env, food_tables)

    def write(self, guest):
        print("Time %d: Receptionist starts writing the name tag of %s" %(self.env.now, guest))
        yield self.env.timeout(WRITE_TIME)
        print("Time %d: Receptionist gives the name tag to %s." %(self.env.now, guest))

    def walk(self,guest):
        print('Time %d: %s started walking to drink table' % (self.env.now, guest))
        yield self.env.timeout(WALKING_TIME)
        print('Time %d: %s reached the drink table' % (self.env.now, guest))

    def walkToFoodTable(self,guest):
        print('Time %d: %s started walking to food table' % (self.env.now, guest))
        yield self.env.timeout(WALKING_TIME)
        print('Time %d: %s reached the food table' % (self.env.now, guest))

    def serve_drink(self,guest):
        print('Time %d: %s started pouring drink' % (self.env.now, guest))
        yield self.env.timeout(SERVING_DRINK)
        print('Time %d: %s finished pouring drink' % (self.env.now, guest))

    def serve_food(self,guest):
        print('Time %d: %s started picking food from the table' % (self.env.now, guest))
        yield self.env.timeout(PICKING_FOOD)
        print('Time %d: %s finished picking food' % (self.env.now, guest))

    def drink(self, guest):
        print('Time %d: %s started drinking' % (self.env.now, guest))
        yield self.env.timeout(random.randint(DRINKING-3,DRINKING+3))
        print('Time %d: %s finished drinking' % (self.env.now, guest))

    def eatFood(self, guest):
        print('Time %d: %s started eating' % (self.env.now, guest))
        yield self.env.timeout(random.randint(EATING-3,EATING+3))
        print('Time %d: %s finished eating' % (self.env.now, guest))


class BroadcastPipe(object):
    """A Broadcast pipe that allows one process to send messages to many.

    This construct is useful when message consumers are running at
    different rates than message generators and provides an event
    buffering to the consuming processes.

    The parameters are used to create a new
    :class:`~simpy.resources.store.Store` instance each time
    :meth:`get_output_conn()` is called.

    """
    def __init__(self, env, capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.pipes = []

    def put(self, value):
        """Broadcast a *value* to all receivers."""
        if not self.pipes:
            raise RuntimeError('There are no output pipes.')
        events = [store.put(value) for store in self.pipes]
        return self.env.all_of(events)  # Condition event for all "events"

    def get_output_conn(self):
        """Get a new output connection for this broadcast pipe.

        The return value is a :class:`~simpy.resources.store.Store`.

        """
        pipe = simpy.Store(self.env, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe

class Host(object):
    def __init__(self, env, name, food_ready, out_pipe, hostToGuestInteractionTime, num_of_conversations):
        self.env = env
        self.name = name
        self.food_ready = food_ready
        self.out_pipe = out_pipe
        self.hostToGuestInteractionTime = hostToGuestInteractionTime
        self.conversation = simpy.PriorityResource(env, capacity=num_of_conversations)
        self.guests = []
        self.guests_notified = False
        self.timeSpentTalking = 0

    def run(self):
        self.process = self.env.process(self.actions())

    def setGuests(self, guests):
        self.guests = guests

    def getGuests(self):
        return self.guests

    def addGuest(self, guest):
        #print "adding %s to host list" % guest.name
        self.guests.append(guest)

    def removeGuest(self, guest):
        self.guests.remove(guest)

    def actions(self):
        while True:
            if self.guests:
                if(self.env.now >= self.food_ready and not self.guests_notified):
                    msg = (env.now, '%s says food is being served' % (self.name))
                    self.out_pipe.put(msg)
                    self.guests_notified = True
                guest = self.guests[random.randint(0, len(self.guests)-1)]
                with guest.conversation.request(priority = 1) as req1:
                    start = env.now
                    event0 = self.env.timeout(1, value='busy')
                    ret = yield req1 | event0
                    if event0 not in ret:
                        with self.conversation.request(priority = 0) as req2:
                            event1 = self.env.timeout(1, value='busy')
                            ret = yield req2 | event1
                            if event1 not in ret:
                                print "Time %d: HOST started conversation with %s" % (self.env.now, guest.name)
                                randomNumber = random.randint(0, 2)
                                yield self.env.timeout(self.hostToGuestInteractionTime+randomNumber)
                                self.timeSpentTalking += self.hostToGuestInteractionTime+randomNumber
                                guest.timeSpentTalking += self.hostToGuestInteractionTime+randomNumber
                                print "Time %d: HOST ended conversation with %s" % (self.env.now, guest.name)
            yield self.env.timeout(2)

         

class Guest(object):
    def __init__(self, env, host, gathering, name, in_pipe, guest_interaction_time, num_of_conversations, max_hunger):
        self.env = env
        self.host = host
        self.gathering = gathering
        self.name = name
        self.in_pipe = in_pipe
        self.guest_interaction_time = guest_interaction_time
        self.conversation = simpy.PriorityResource(env, capacity=num_of_conversations)
        self.food_ready = False
        self.hunger = 0
        self.max_hunger = max_hunger
        self.ate_food = False
        self.waiting_time = 1
        self.timeSpentTalking = 0
        

    def setGuests(self, guests):
        self.guests = guests

    def getGuests(self):
        return self.guests

    # not required
    def setHost(self, host):
        self.host = host

    def run(self):
        self.process = env.process(self.actions())

    def actions(self):

        # Receive NameTag  -- All Guests should be arriving before 6:30 pm
        print('Time %d: %s arrives at the reception desk' % (self.env.now, self.name))
        with self.gathering.receptionist.request() as request:
            yield request
            yield self.env.process(self.gathering.write(self.name))
            print('Time %d: %s leaves the reception desk' % (self.env.now, self.name))
            

        # Collect Drink and Drink it
        with self.gathering.drink_tables.request() as request:
            yield request
            yield self.env.process(self.gathering.walk(self.name))
            yield self.env.process(self.gathering.serve_drink(self.name))

            print('Time %d: %s leaves the drink table' % (self.env.now, self.name))
            
        # add this guest to host's list
        self.host.addGuest(self)
        yield self.env.process(self.gathering.drink(self.name))
        
        while True:
            yield self.env.timeout(random.randint(0, 8))
            self.hunger = self.env.now
            if (self.hunger >= self.max_hunger and not self.ate_food):
                yield self.in_pipe.get()
                print "Time %d: %s started eating food" % (self.env.now, self.name)
                yield self.env.process(self.gathering.walkToFoodTable(self.name))
                with self.gathering.food_tables.request() as request:
                    yield request
                    yield self.env.process(self.gathering.serve_food(self.name))
                yield self.env.process(self.gathering.eatFood(self.name))
                self.ate_food = True

            self.guests = self.host.getGuests()[:]
            self.guests.remove(self)
            if self.guests:
                randnum = random.random()
                if (randnum < 0.7):
                    guest = self.guests[random.randint(0, len(self.guests)-1)]
                    with guest.conversation.request(priority = 1) as req1:
                        start = self.env.now
                        event0 = self.env.timeout(self.waiting_time, value='busy')
                        ret = yield req1 | event0
                        if event0 not in ret:
                            with self.conversation.request(priority = 0) as req2:
                                event1 = self.env.timeout(self.waiting_time, value='busy')
                                ret = yield req2 | event1
                                if event1 not in ret:
                                    print "Time %d: %s started conversation with %s " % (self.env.now, self.name, guest.name)
                                    randomNumber = random.randint(0, 2)
                                    yield self.env.timeout(self.guest_interaction_time+randomNumber)
                                    self.timeSpentTalking += self.guest_interaction_time+randomNumber
                                    guest.timeSpentTalking += self.guest_interaction_time+randomNumber
                                    print "Time %d: %s ended conversation with %s " % (self.env.now, self.name, guest.name)
                else:
                    with self.host.conversation.request(priority = 1) as req1:
                        start = self.env.now
                        event0 = self.env.timeout(self.waiting_time, value='busy')
                        ret = yield req1 | event0
                        if event0 not in ret:
                            with self.conversation.request(priority = 0) as req2:
                                event1 = self.env.timeout(self.waiting_time, value='busy')
                                ret = yield req2 | event1
                                if event1 not in ret:
                                    print "Time %d: %s started conversation with HOST" % (self.env.now, self.name)
                                    randomNumber = random.randint(0, 2)
                                    yield self.env.timeout(self.guest_interaction_time+randomNumber)
                                    self.timeSpentTalking += self.guest_interaction_time+randomNumber
                                    self.host.timeSpentTalking += self.guest_interaction_time+randomNumber
                                    print "Time %d: %s ended conversation with HOST" % (self.env.now, self.name)
            """
            leaveParty = random.random()
            if leaveParty > 0.9:
                self.host.removeGuest(self)
                self.env.exit()
            """
            
        
            

# Setup and start the simulation
print('*******************************')
print('Gathering starts')
print('*******************************')

random.seed()  # This helps reproducing the results
#env = simpy.Environment()
env=simpy.rt.RealtimeEnvironment(initial_time=0,factor=0.5,strict=True)
speech_pipe = BroadcastPipe(env)
#guests = []

def setup(env, host, num_receptionists, writetime, g_enter, drink_tables, food_tables):
    """Create a gathering, a number of initial guests and keep creating guests
    approx. every ``g_enter`` minutes."""
    
    host.run()

    # Create the gathering
    gathering = Gathering(env, num_receptionists, writetime, drink_tables, food_tables)


    # Create 2 initial guest
    for i in range(INITIAL_GUESTS):
        max_hunger = random.randint(20, 30)
        guest = (Guest(env, host, gathering, "Guest %d" % i, speech_pipe.get_output_conn(), guest_interaction_time, num_of_conversations, max_hunger))
        guest.run()

    # Create more guests while the simulation is running
    i = INITIAL_GUESTS
    while i<NO_OF_GUESTS:
        yield env.timeout(random.randint(g_enter-3, g_enter+3))
        max_hunger = random.randint(20, 30)
        guest = (Guest(env, host, gathering, "Guest %d" % i, speech_pipe.get_output_conn(), guest_interaction_time, num_of_conversations, max_hunger))
        guest.run()
        i += 1


host = (Host(env, "HOST", food_ready_at, speech_pipe, hostToGuestInteractionTime, num_of_conversations))
env.process(setup(env, host, NUM_RECEPTIONIST, WRITE_TIME, G_ENTER, DRINK_TABLES, FOOD_TABLES))

env.run(until=SIM_TIME)


print ''
print ''
print '*************'
print 'RESULTS'
print '*************'
print 'TIME SPENT INTERACTING'
print 'Host - %d' % host.timeSpentTalking
for i in host.getGuests():
    print '%s - %s' % (i.name, i.timeSpentTalking)