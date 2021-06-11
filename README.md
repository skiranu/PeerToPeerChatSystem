# p2p-chat
This program will implement distributed chat on virtual ring topology network.
Furthermore this program will implement Chang-Roberts algorithm for leader election and Laport's timestamp to achieve full ordering of messages.

Features:
  - Nodes can freely join into existing ring, based on information about one node (IP:port). First node will join with itself into ring.
  - Ring will recover from unexpected disconnect of one node at the time.
  - One node will be elected as central authority (leader), all messages will be then passed through leader.
  - Leader will be elected using Chang-Roberts algorithm.
  - Encryption of messages.
  
## How to setup the environment
1. Create virtual environment using: `python3 -m venv env`
2. Activate virtual environment: `. env/bin/activate`
3. Install dependencies: `python3 -m pip install -r requirements.txt`

## How to run the application
1. Activate the environment
2. In the directory where chat.py is placed, run the command 'python3 chat.py' 

## login to application
Currently these users, password have the access to login 
1. abhay, test
2. susmith, test
3. tharun, test

## startnode dialog
Choose a name for the node (use same one as the login) and set the IP address and port number. If it is the first node, there is no need to connect it to another node. For subsequent nodes, connect it to one of the existing nodes in the network. 

To send encrypted messages, click the load key button and choose the keys.cfg file in the folder. The keys for abhay, susmith and tharun have been added in the keys.cfg file. To test new users, their names and keys also need to be added to the keys.cfg file.

## chat window
After creating two or more nodes, click the 'select online users' to display the available users. Then the user can be selected and a message can be sent to that user. 
If the key has been loaded, then the encrypted checkbox should be clicked before sending the message. 
A broadcast message can be sent by sending a message without selecting any user. 
The log for each node is visible in the log tab where one can check the underlying communication betweeen the nodes.
