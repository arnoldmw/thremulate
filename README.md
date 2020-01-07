# Thremulate

Mwesigwa Arnold 2020.

Thremulate is a light weight adversary emulation application grounded on the MITRE [ATT&CK™](https://attack.mitre.org/) framework.
Thremulate's server and agent are totally platform independent. Therefore, you can execute over 140 adversarial techniques on Windows, Linux and MacOS operating systems without a hitch.

## Why should I use Thremulate?

## Philosophy

- **Security Assessments for All**
Organizations that may not have full time red team personnel or IT security budget constraints or irregular security assessments can leverage the power of this software to test their defenses.
- **Security Monitoring Effectiveness**
Security personnel should validate their continuous and/or network security monitoring measures effectiveness at preventing and/or detecting adversarial behavior on the end-points or network. Thremulate helps you do this with utmost ease. Run an adversarial technique and confirm if it is prevented or detected as malicious.
- **Raise Information Security Awareness**
The lead author created Thremulate to raise awareness about cyber threats out there in the wild (unknown) inclined on compromising and/or destroying digital infrastructure. Thremulate is a spot-on example of how we can use threat intelligence to reinforce our defenses. 

## Features
1. Responsive Web GUI
2. Authentication and Authorization
3. Multi-user for team collaboration
4. Analytics dashboard
![Screen](screenshots/dashboard.png)
5. Living Off the Land techniques
6. Fileless attack techniques
7. Very modular and easily extendable application plus many other features.
## Use Cases

1. Adversary emulation
2. IT Security classes
3. Forensics classes
4. Threat hunting games
## Major requirement
- Python 3.5.3 or later

## Rules of Engagement

**"ALWAYS OBTAIN WRITTEN PERMISSION FROM THE AUTHORISED PERSON FOR THIS KIND OF ACTIVITY WHENEVER YOU ARE WORKING WITH INFRASTRUCTURE YOU DO NOT PERSONALLY OWN , OTHERWISE HAVE A COUPLE OF RESUMES OR CVS READY"**

 *'The First Rule of Offensive Security', Mwesigwa Arnold.*

## Installation

Start by cloning this repository.
```
git clone https://github.com/infosecone/thremulate.git 
```
Install the requirements for the project. It is recommended to create a virtual environment for every project.
```python
pip install -r requirements.txt
```
Start the sever
```python
python main.py
```

## Getting Started

* [Running Your First Adversary Emulation with Thremulate](docs/quick_start.md)
* The Complete [list of all supported adversarial techniques](art/atomics/index.md) and the [ATT&CK Matrix](art/atomics/matrix.md)
  - Windows [Tests](art/atomics/windows-index.md) and [Matrix](art/atomics/windows-matrix.md)
  - MacOS [Tests](art/atomics/macos-index.md) and [Matrix](art/atomics/macos-matrix.md)
  - Linux [Tests](art/atomics/linux-index.md) and [Matrix](art/atomics/linux-matrix.md)
* Do you prefer the ATT&CK Navigator? Check out the [coverage layer](art/atomics/art_navigator_layer.json)

## Contributing

This project is open to contributions. For major changes please open an issue first to discuss what
you would like to change.
Guidelines for contributing can be found in the [CONTRIBUTING](CONTRIBUTING.md) file.


## Code of Conduct

In order to have a more open and welcoming community,the maintainers of this repository adhere to a
[code of conduct](CODE_OF_CONDUCT.md).

## Author

1. Mwesigwa Arnold (Lead Maintainer/Author)

## License
Apache License 2.0. 
See the [LICENSE](LICENSE.txt) file for more details.

## Acknowledgements
- [ATT&CK](https://attack.mitre.org/)
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
- All the threat actors out there whose techniques I have used. I am (un)grateful.

## Support

Having problems? Or a comment? 

Phish me an [email](thremulate@gmail.com). (Reminder. It's not fun firing up a fortified VM every time with SIFT(forensic workstation) on standby just to read email) 