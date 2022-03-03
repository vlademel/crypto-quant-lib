# incrypt
Crypto trading library

LOGGING INTO EC2 INSTANCE

In order to login to the ec2 instance you will need to run the following code:
    
    ssh -i "C:\Users\Vlad\Desktop\Current Projects\ec2\market_listener.pem" ec2-user@ec2-35-177-10-25.eu-west-2.compute.amazonaws.com
The stuff between the quotation marks is the location of the cert for that instance, the stuff coming after the quotation marks is the name of the instance itself.


CLONING TO EC2 INSTANCE

Generate ssh keys on local machine as in the following link:

  https://stackoverflow.com/questions/19596974/ec2-how-to-clone-git-repository.

Instead of copying over the .pub file, do this with the private key and use the command (In the EC2 Linux terminal):
    
    $ chmod 600 [keyname]
    

SETTING UP BOTO3

Incrypt uses boto3 to send trades and information to DynamoDB. In order to set this up you need to run the following commands to install AWS CLI:

    $ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    $ sudo apt install unzip
    $ unzip awscliv2.zip
    $ sudo ./aws/install
  
Once AWS CLI has been installed, you will need to configure the keys using 

    aws configre
    
And enter the relevant keys.

INSTALLING

First thing's first - install python3 as ec2 (at time of writing) only comes with python 2. Run the following command:

    sudo yum install python3 -y

Then you should install pip, this will allow you to install the various Python packages

    sudo yum -y install python3-pip
    
Once you have installed pip3 you will then need to install rust as cryptography (a dependency of one of the dependencies) requires it.

    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

Next, navigate to where the requirements.txt file is located and install using the following command

    pip3 install -r requirements.txt
    
You can also use the setup.py file to install too.

RUNNING A SCRIPT

    https://stackoverflow.com/questions/47823240/keep-running-a-python-script-on-aws-ec2-even-if-cli-session-is-closed/47823620
    
You will need to launch a seperate window within the instance as in the above link.
