# Thremulate
https://github.com/infosecone/thremulate.git<br>
Mwesigwa Arnold 2020.

Thremulate is a light weight adversary emulation application based on the MITRE ATT&CK repository.<br>
Thremulate's server and agent are totally platform independent.
Therefore you can execute over 140 adversarial techniques on Windows, Linux and 
MacOS operating systems without a hitch.<br>
Thremulate's server and agent run on any platform without further configurations. 
## Philosophy
- **Security Assessments for All**<br>
Organisations that may not have full time red team personnel or IT security budget constraints 
or irregular security assessments can leverage the power of this software to test their defenses.
- **Continuous Monitoring Effectiveness**<br>
Security personnel ought to effortlessly validate their continuous monitoring 
 measures effectiveness at preventing or detecting adversarial behavior on the network or end points. 
- **Raise IT security Awareness**<br>
This project was created to raise awareness about the threats out there in the world
 willing to compromise and/or destroy digital infrastructure and how we can use threat 
 intelligence to bolster our defenses. 

## Features
1. Responsive Web GUI
2. Authentication and Authorization
3. Multi-user
4. Dashboard
![Screen](screenshots/dashboard.png)
5. Living Off the Land techniques
6. Fileless attack techniques
7. Easily extendable application... etc.
## Use Cases
1. Adversary emulation
2. Network Security classes
3. Forensics classes
4. Threat hunting
## Major requirement
Python 3.5.3 or later
## Installation
Start by cloning this repository.
```
git clone https://github.com/infosecone/thremulate.git 
```
Install the requirements for the project. It is recommended to create a virtual environment for this project.
```
pip install -r requirements.txt
```
Start the sever
```
python main.py
```

## Getting Started
* [Getting Started With Thremulate](docs/quick_start.md)
* View the Complete [list of availale adversarial techniques](art/atomics/index.md) and the [ATT&CK Matrix](art/atomics/matrix.md)
  - Windows [Tests](art/atomics/windows-index.md) and [Matrix](art/atomics/windows-matrix.md)
  - macOS [Tests](art/atomics/macos-index.md) and [Matrix](art/atomics/macos-matrix.md)
  - Linux [Tests](art/atomics/linux-index.md) and [Matrix](art/atomics/linux-matrix.md)
* Using ATT&CK Navigator? Check out our [coverage layer](art/atomics/art_navigator_layer.json)
## Contributing
This project is open to contributions. For major changes please open an issue first to discuss what
you would like to change.<br>
Guidelines for contributing can be found in the [CONTRIBUTING](CONTRIBUTING.md) file.


## Code of Conduct

In order to have a more open and welcoming community,the maintainers of this repository adhere to a
[code of conduct](CODE_OF_CONDUCT.md).

## Authors
1. Mwesigwa Arnold (Lead Maintainer/Author)

## License
Apache License 2.0 <br>
See the [LICENSE](LICENSE.txt) file.

## Acknowledgements
[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)<br>
[ATT&CK](https://)


##Support
