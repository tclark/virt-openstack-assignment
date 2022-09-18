# virt-openstack-assignment
__OpenStack SDK assignment for ID720 paper__

Your assignment is to write a Python script to control a set of 
OpenStack resources. This repository contains a file, assignment.py
that provides the top level structure of the program you will write.
In particular, it is invoked with one argument that is one of
"create", "run", "stop", "destroy", or "status". The actions to 
be taken for each argument are

## To Do List

1. __*create*:__
  Create the following resources in OpenStack
     - [x] A network named "\<username\>-net" with a subnet, 192.168.50.0/24
     - [x] A router named "\<username\>-rtr" with interfaces joining the network
    above with public-net
     - [x] A floating IP address
     - [x] Three servers
       - image: ubuntu-minimal-22.04-x86_64
       - flavour: c1.c1r1
       - names: \<username\>-web, \<username\>-app, \<username\>-db
     - [x] security-group: assignment2 (You do not need to create this)
  - [x] Assign the floating IP to the web server.
  - [x] If any of the resources above already exist when the script is run, then they 
  should not be recreated.
2. __*run*:__
   - [x] Start the three servers created above. 
   - [x] If any of them do not exist, print an error message. 
   - [x] If any of the them are already running, do not restart them or otherwise change their state.
3. __*stop*:__
   - [x] Stop the three servers. 
   - [x] If any are not running, then leave them in that state. 
   - [x] If any do not exist, display an error message.
4. __*destroy*:__ 
   - [x] Remove all of the resources created by the create action. 
   - [x] If any of the resources do not exist, ignore them and destroy whatever ones do.
5. __*status*:__ 
   - [x] Print a status report on each of the three servers indcating each servers state and their IP addresses if they have addresses assigned.

Your submitted assignment must use the assignment.py file. If you want to include other files in your project, place them in the same directory as assignment.py. If you use any modules not in the Python standard library, you must include a requirements.txt file. Your program will be marked using Python 3.6.8 (the version used in our lab virtualenvs).

To do this assignment, fork this repository and commit your work to your forked version. Submit your assignment by sending a pull request to the original repository on or before the due date.          
