## Quick Start

Ready to run your first Thremulate adversary emulation? Thremulate agents can run locally or remotely. This example runs locally.
## 1. What should I start with?

- Start the Thremulate server first.

```
python main.py
```

- Open the browser of your choice on the computer running the Thremulate server and navigate to **http://localhost:8000**. Login with **admin** as the username and **password** as the password

   ```
   http:\\localhost:8000
   username: admin
   password: password
   ```

## 2. I am done starting the server. How can I get the Agent to the test computer?

   These are the ways of getting the agent to the test computer.

   - The Home page of an authenticated user has platform specific commands that download an agent to a computer that executes them. Copy and paste them in the bash or command prompt or powershell terminal with Administrative privileges. Powershell is preferred for the Windows platform. 
   - Otherwise one may navigate to http://SERVER_IP:8000/getagent through a browser on the test computer. This automatically downloads the agent to the test machine (drive-by download). SERVER_IP is the IP address of the device running the Thremulate server. In this example that would be http://127.0.0.1:8000/getagent.
   - Transfer the Agent for the corresponding test platform using external storage media or FTP or any other viable means. The Agent lives in the **agents** folder found in the Thremulate root. Windows Agents are labelled win-agent.exe, Linux Agents are labelled lin-agent.exe. and MacOS Agents are labelled mac-agent.exe.

## 3. The Agent is on the test computer. What next?

If you pasted the commands into the terminal to get the agent or navigated to the malicious URL(http://127.0.0.1:8000/getagent) , the agent was automatically downloaded and started for you.

Otherwise run the agent via command line while passing the IP address of the Thremulate server. Navigate to the location of the agent.

   ```
   win-agent.exe -thremulate [SERVER_IP]
   example: win-agent.exe -thremulate 127.0.0.1
   ```

## 5. The Agent successfully phoned home to the Thremulate server. I am ready to advermulate. Great!!

- On the computer running ther server, in the browser navigate to the http://localhost:8000/agents or hover over the 'Agents' menu in the naviagtion bar and click View Agents in the dropdown menu. This leads you to a page which shows all the agents that have phoned back to the server.

- A random name was given to your Agent. You can change it later by clicking on the Edit button with the 'Update Agent' tooltip. Access tooltips by hovering over the buttons. To assign an agent techniques to execute, click on the 'Play' button with the 'Assign techniques' tooltip. 

- A web page with all the available techniques for appropriate for that agent's platform are presented. To assign an agent a technique, click on the technique.

- You can view or modify the execution parameters of the technique before assigning it an agent.

  <img src="..\screenshots\view_or_modify_technique.png" alt="Screen" />
  
- Wait for the agent to execute the assigned techniques.

- 