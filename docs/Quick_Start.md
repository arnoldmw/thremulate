## Quick Start

Ready to run your first Thremulate adversary emulation? Thremulate agents can run locally or remotely. This example runs locally.
## 1. What should I start with?

- Start the Thremulate server first.

```
python main.py
```

- Open your favorite browser on the computer running the Thremulate server and navigate to **https://localhost:8000**. Login with **admin@thremulate.com** as the username and **password** as the password.

   ```
   http:\\localhost:8000
   username: admin@thremulate.com
   password: password
   ```
   ## NOTE: Invalid SSL certificate warnings.
   
   Thremulate's SSL certificate is self signed and therefore not trusted by browsers. Browsers will tell you that 'Your connection is not private' or a similar message.The script that created the Thremulate's SSL certificate is in the certificate folder. You can  generate your own certificate. Otherwise add Thremulate's default certificate as an exception in Firefox or click 'Advanced' and then click 'Proceed to localhost (unsafe)' for the Google Chrome browser.

## 2. I have logged into the Thremulate server. How can I get the Agent to the target computer?

   These are the ways of getting the agent to the test computer.

   - The Home page of an authenticated user has platform specific commands that download an agent to a target computer that executes them. Copy and paste them in the bash or command prompt or powershell terminal with Administrative privileges on the target computer.
   - Otherwise one may navigate to http://SERVER_IP:8000/getagent through a browser on the test computer. This automatically downloads the agent to the test machine (drive-by download). SERVER_IP is the IP address of the device running the Thremulate server. In this example that would be http://127.0.0.1:8000/getagent.
   - Transfer the Agent for the corresponding test platform using external storage media or FTP or any other viable means. The Agent lives in the **agents** folder found in the Thremulate root. Windows Agents are labelled win-agent.exe, Linux Agents are labelled lin-agent.exe. and MacOS Agents are labelled mac-agent.exe.

## 3. The Agent is on the test computer. What next?

If you pasted the commands into the terminal to get the agent or navigated to the malicious URL(http://127.0.0.1:8000/getagent) , the agent was automatically downloaded and started for you.

Otherwise run the agent via command line while passing the IP address of the Thremulate server. Navigate to the location of the agent.

   ```
   win-agent.exe -thremulate [SERVER_IP]
   example: win-agent.exe -thremulate 127.0.0.1
   ```

## 5. The Agent says it has registered. I am ready to Thremulate. Great!!

- On the computer running ther server, in the browser navigate to the http://localhost:8000/agents. This leads you to a page which shows all the agents that have phoned back to the server.

- A random name was given to your Agent. You can change it later by clicking on the Edit button with the 'Update Agent' tooltip. Access tooltips by hovering over the buttons. To assign an agent techniques to execute, click on the 'Play' button with the 'Assign techniques' tooltip. 

- The ATT&CK Matrix with all the techniques for appropriate for that agent is presented. To assign an agent a technique, click on the technique.

<img src="..\screenshots\matrix.png" alt="Screen" />



- You can view or modify the execution parameters of the technique before assigning it an agent.

<img src="..\screenshots\assign_technique.png" alt="Screen" />

- Wait for the agent to execute the assigned techniques. The Agent by default checks for new techniques assignments every 5 seconds. This can later be changed to any value.



## 6. Agent says it executed TXXXX:X. How do I know that the agent really executed TXXXX:X ?

- One more time on the computer running ther server, in the browser navigate to the http://localhost:8000/agents. Click on the Information button with the 'More information' tooltip.

- This will show you all the techniques associated with that Agent and their respective analysis.You can delete the analysis of a particular technique and re-run it or even remove the technique from the Agent.
- If you wish to view output from the Agent, click on the name of the technique .

<img src="..\screenshots\agent_details.png" alt="Screen" />



## 7. And that is your first adversary emulation with Thremulate. Congratulation!!

Have a peek at your insightful dashboard to view your progress and run more techniques if the charts are flat. Happy Thremulating.

I'd appreciate a sentence or two of feedback. Thanks in advance.

<img src="..\screenshots\dashboard.png" alt="Screen" />