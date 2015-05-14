# PartySimulation

The objective of our project is to simulate a real world scenario which consists of various human interactions, processes, events and resources.  Thus we have simulated the events and interactions happening in a community gathering event. 

We have observed the human interactions in a community gathering and modeled a social meetup hosted by a single host. The guests arrive to the party randomly and first get their name tags from the reception table.  After getting their nametags they proceed to get drinks. After some time the host announces dinner and the guests proceed towards the buffet randomly to have dinner. For our simulation, we have considered two processes: host and guest and three resources in the form of Receptionist table, Drinks table and Food table.

We have used Simpy package of Python in our project. SimPy is a process-based discrete-event simulation framework based on Python. Simpy's event dispatcher is based on Python’s generators and it can also be used to implement multi-process systems and asynchronous communication as a simulation.

#####Challenges faced:
  1. Modeling one-to-many interaction.
  2. Usage of Priority resource.
  3. Blocking both resources on either side of interaction.
  4. Avoiding deadlocks.
  
#####References:
https://simpy.readthedocs.org/en/latest/

#####Execution Instructions:
  1. Install simpy using this link - https://simpy.readthedocs.org/en/latest/simpy_intro/installation.html
  2. clone the repo and run python simulation.py

#####Screenshots:
![alt tag](https://github.com/udaysagar2177/PartySimulation/blob/master/imgs/a.png)
![alt tag](https://github.com/udaysagar2177/PartySimulation/blob/master/imgs/b.png)
#####...
###Results
#####When we have 3 guests
![alt tag](https://github.com/udaysagar2177/PartySimulation/blob/master/imgs/d.png)
#####When we have 5 guests
![alt tag](https://github.com/udaysagar2177/PartySimulation/blob/master/imgs/c.png)
