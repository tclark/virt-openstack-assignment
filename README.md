# virt-openstack-assignment
OpenStack SDK assignment for ID720 paper

Your assignment is to write a Python script to control a set of 
OpenStack resources. This repository contains a file, assignment.py
that provides the top level structure of the program you will write.
In particular, it is invoked with one argument that is one of
"create", "run", "stop", "destroy", or "status". The actions to 
be taken for each argument are

*create*: Create the following resources in OpenStack
  - A network named "\<username\>-net" with a subnet, 192.168.50.0/24
  - A router named "\<username\>-rtr" with interfaces joining the network
    above with public-net
  - A floating IP address
  - Three servers
     - image: ubuntu-minimal-22.04-x86_64
     - flavour: c1.c1r1
     - names: \<username\>-web, \<username\>-app, \<username\>-db
     - security-group: assignment2 (You do not need to create this)
  Assign the floating IP to the web server.
  If any of the resources above already exisit when the script is run, then they 
  should not be recreated.

*run*: Start the three servers created above. If any of them do not exist, 
print an error message. If any of the them are already running, do not restart
them or otherwise change their state.

*stop*: Stop the three servers. If any are not running, then leave them in
that state. If any do not exist, display an error message.

*destroy*: Remove all of the resources created by the create action. If any
of the resources do not exisit, ignore them and destroy whatever ones do.

*status*: Print a status report on each of the three servers indcating
each servers state and their IP addresses if they have addresses assigned.

Your submitted assignment must use the assignment.py file. If you want to 
include other files in your project, place them in the same directory as assignment.py.
If you use any modules not in the Python standard library, you must include a
requirements.txt file. Your program will be marked using Python 3.6.8 (the version
used in our lab virtualenvs).

To do this assignment, fork this repository and commit your work to your forked
version. Submit your assignment by sending a pull request to the original repository
on or before the due date.          
