# Contributing to Thremulate
Thank you for considering contributing to this project. We are eager to receive your 
contribution. This document details guidelines to follow when contributing to the Thremulate project. 
Changes to this document are welcome too. 

When contributing to this repository, please first discuss the change you wish to make via issue, email or any other method with the owners of the repository before making a change.

## Table of Contents

[1. Project Status](#1-project-status)

[2. Code of Conduct](#2-code-of-conduct)

[3. What should I know before I get started?](#3-what-should-i-know-before-i-get-started)

- [3.1 Thremulate and its modules](#31-thremulate-and-its-modules)

[4. How can I contribute?](#4-how-can-i-contribute)

- [4.1 Reporting Bugs](#41-reporting-bugs)

- [4.2 Suggesting Enhancements](#42-suggesting-enhancements)

- [4.3 Your First Code Contribution](#43-your-first-code-contribution)



## 1. Project Status

This project will be supported as long the maintainers exist.
Anybody willing to contribute to this project as a maintainer or contributor is welcome to do so,
as long as they have the requisite skills and adhere to this project's [code of conduct](CODE_OF_CONDUCT.md).

## 2. Code of Conduct
Please note we have code of [code of conduct](CODE_OF_CONDUCT.md). Kindly follow it in all your interactions with the project.

## 3. What should I know before I get started?

### 3.1 Thremulate and its modules

Thremulate is an open source project built using the python aiohttp web framework. The lead author chose aiohttp because of its light footprint and easy deployment. This project utilises the Model View Template (MVT) design pattern and the Peewee object relational mapper. Data is fetched from an SQLite database due to its easy deployment.

Thremulate is modular in its structure. There is a module for working with agents, campaigns, dashboard, middleware, user management, authentication and authorization. These modules have their respective views in the templates folder.

The modules are briefly described below:

- agent - manages all action implemented by agents. These actions include registering agents, assigning agents tasks, viewing all registered agents, giving an agent a code name, analysing results from an agent and any other agent related functions not mentioned here. Agents automatically register themselves with the server upon running them.
- campaign - handles all the campaign related functions. Campaigns simply group agents basing on the period they were active. Threat actors are known to lauch several 'campaigns' with each campaign having different or similar TTPs from the previous campaign. 
- dashboard - presents an analytical overview of the operations that have taken place on the running instance of the Thremulate project. Multiple database queries are run to obtain the information used in analysis of the operations.
- user_mgt - enables the administrator to manage all the users of a Thremulate project instance.Thremulate was created withcollaborative team usage in mind. Individuals can still user it without any limitations. Each user has access to all abilities of the project. Only the Administrator can add new users.

##  4. How can I contribute?

### 4.1 Reporting Bugs

Writing software without bugs is really challenging. 

- **If you find security vulnerability, kindly do not post it as an issue**. Send me an [email](themulate@gmail.com) with your security findings with the email's subject as 'Security Issue'.
- **Kindly ensure the bug was not already reported** by searching through the Issues.
- **If no issues relates to your bug**, kindly open an issue with a **title, clear description, code sample** (if possible) and any other relevant information you consider useful. Please describe the unexpected behavior that is occurring and what the expected behavior should be.

### 4.2 Suggesting Enhancements

Enhancements or improvements to Threamulate are always welcome on condotion that they add something substantial to the project. This section helps or guides you in submitting requests for improvements or new features. 

### 4.3 Your First Code Contribution

Incase you would like to contribute to Thremulate but do know where to begin from, you can look through the issues section of this project. Hopefully you will find something to work on or you can send me an [email](thremulate@gmail.com) describing how you wish to contribute and I'll get back to you as soon as I can.

- Commit messages

  Your first line should not exceed 72 characters


