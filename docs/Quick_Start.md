## Quick Start

Ready to run your first Thremulate adversary emulation? Thremulate agents can run locally or remotely. This example runs locally. To run this example using a remote Thremulate server, replace localhost with the IP address of the remote Thremulate server.
## 1. What should I start with?

- Start the Thremulate server first.

```
python main.py
```

- Open your favorite browser and navigate to **https://localhost:8000**.  Login with **admin@thremulate.com** as the email and **password** as the password.

   ```
   https:\\localhost:8000
   username: admin@thremulate.com
   password: password
   ```
   ## NOTE: Invalid SSL certificate warnings.
   
   Thremulate's SSL certificate is self signed and is therefore not in the trusted root certificates. Browsers will warn you that 'Your connection is not private' or a similar message.The script that created the Thremulate's SSL certificate is in the certificate folder. You are free to generate your own certificate. Otherwise add Thremulate's default certificate as an exception in Firefox and Safari or click 'Advanced' and then click 'Proceed to localhost (unsafe)' for the Google Chrome browser.

## 2. I have logged into the Thremulate server. How can I get the Agent to the target computer?

   These are some of the ways of getting the agent to the target computer.

   - The Home page of an authenticated user has platform specific commands that download an agent to a target computer that executes them. Copy and paste them in the bash or command prompt or powershell terminal. For best results use a terminal or console with Administrative privileges on the target computer. Ensure the Thremulate server IP is the correct one in the deployment commands otherwise correct it as you paste the commands.
   - Transfer the Agent for the corresponding test platform using external storage media or FTP or any other viable means. The Agent lives in the **agents** folder found in the Thremulate root. Windows Agents are labelled win_agent.exe, Linux Agents are labelled lin_agent.exe. and MacOS Agents are labelled mac_agent.exe.

## 3. The Agent is on the test computer. What next?

If you pasted the commands into the terminal to get the agent, the agent was automatically downloaded and started for you.

Otherwise run the agent via command line while passing the IP address of the Thremulate server. Navigate to the location of the agent.

   ```
   win-agent.exe -s [SERVER_IP]
   example: win-agent.exe -s localhost
   ```

## 5. Upon running the Agent, it said it has registered. I am ready to Thremulate. Great!!

- On the computer running ther server, in the browser navigate to the https://localhost:8000/agents. This leads you to a page which shows all the agents that have registered with the server.

- A random name was given to your Agent. You can change it later by clicking on the Edit button with the 'Update Agent' tooltip. Access tooltips by hovering over the buttons. To assign an agent techniques to execute, click on the 'Play' button with the 'Assign techniques' tooltip. 

- The ATT&CK Matrix with all the techniques for appropriate for that agent is presented. To assign an agent a technique, click on the technique.

<img src="..\screenshots\matrix.png" alt="Screen" />

- You can view or modify the execution parameters of the technique before assigning it an agent.

  >**NOTE: A technique may multiple tests for better coverage. A win for you :smiley:.**

<img src="..\screenshots\assign_technique.png" alt="Screen" />

- Wait for the agent to execute the assigned techniques. The Agent by default checks for new techniques assignments every 5 seconds. This can later be changed to any value when starting the Agent.



## 6. Agent says it executed TXXXX:X. How do I know that the agent really executed TXXXX:X ?

- One more time on the computer running ther server, in the browser navigate to the https://localhost:8000/agents. Click on the Information button with the 'More information' tooltip.

- This will show you all the techniques associated with that Agent and their respective analysis.You can delete the output of a particular technique test for the Agent to re-run it or even remove the technique test from the Agent.
- If you wish to view output from the Agent, click on the name of the technique test.

<img src="..\screenshots\agent_details.png" alt="Screen" />



## 7. And that is your first adversary emulation with Thremulate. Congratulations!!

Have a peek at your insightful dashboard to view your progress and run more techniques if the charts are not putting a smile on your face. Happy Thremulating.

I'd appreciate a sentence or two of feedback. Thanks in advance.

<img src="..\screenshots\dashboard.png" alt="Screen" />