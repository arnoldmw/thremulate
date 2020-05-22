# Thremulate

Thremulate is a light weight adversary emulation application grounded on the MITRE [ATT&CK™](https://attack.mitre.org/) framework.
Thremulate's server and agent are totally platform independent. Therefore, you can execute over 140 adversarial techniques on Windows, Linux and MacOS operating systems without a hitch.

> Thremulate is currently undergoing quality assurance to fix bugs. 
Therefore not all adversary techniques will work as expected. 
It will soon be production ready :ok_hand:. Keep checking for its v1.0.0 release.


## Why should I use Thremulate?
- **Security Assessments for All:** 
Organizations that may not have full time red team personnel or a substantial IT security budget can leverage the power of this software to test their defenses.
- **Security Monitoring Effectiveness:**
Security personnel should validate their continuous and network security monitoring measure's effectiveness at preventing and detecting adversarial presence on the end-points or network. Thremulate helps you do this with utmost ease. Run an adversarial technique and confirm if its execution is prevented or detected as malicious.
- **Raise Information Security Awareness:**
The lead author created Thremulate to raise awareness about cyber threats out there in the wild inclined on compromising and/or destroying digital infrastructure. Thremulate is a spot-on example of how we can use Cyber Threat Intelligence (CTI) to reinforce our defenses. 

## Features
1. Responsive Web GUI
2. Authentication and Authorization
3. Multi-user for team collaboration
4. Analytics dashboard
![Dashboard](screenshots/dashboard.png)
5. Living Off the Land techniques.
6. Fileless attack techniques.
7. Modular design and easily extendable application and many other features.
## Use Cases

1. Adversary emulation
2. IT Security classes
3. Forensics classes
4. Purple Team engagements
## Major requirement
- Python 3.5.3 or later

## Rule of Engagement

> **"ALWAYS OBTAIN WRITTEN PERMISSION FROM THE DULY AUTHORISED PERSON FOR THIS KIND OF ACTIVITY WHENEVER YOU ARE WORKING WITH INFRASTRUCTURE YOU DO NOT PERSONALLY OWN , OTHERWISE HAVE A COUPLE OF RESUMES AND DEFENCE LAWYERS READY"** 
>  *'The First Rule of Offensive Security',Mwesigwa Arnold  .*

## Installation

Start by cloning this repository.
```
git clone https://github.com/arnoldmw/thremulate.git 
```
Install the requirements for the project. It is recommended to create a new virtual environment for every project.
```python
pip install -r requirements.txt
```
Start the sever
```python
python server.py
```

## Getting Started

* [Running Your First Adversary Emulation with Thremulate](docs/Quick_Start.md)


## Contributing

This project is open to contributions. Guidelines for contributing can be found in the [CONTRIBUTING](CONTRIBUTING.md) file.


## Code of Conduct

In order to have a more open and welcoming community,the maintainers of this repository adhere to a
[code of conduct](docs/CODE_OF_CONDUCT.md).

## Author

1. [Arnold Mwesigwa](https://github.com/arnoldmw) (Maintainer/Author)

## License

See the [LICENSE](LICENSE.txt) file for more details.

## Acknowledgements

- [ATT&CK](https://attack.mitre.org/)
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
- All the threat actors whose techniques I have implemented, I am (un)grateful.

## Support

Encountering problems? Open up an issue.

Got a private comment? Send an email to thremulate@gmail.com. (It is not fun running SIFT(forensic workstation) 
every time I read email. So keep it clean :wink:) 