# OpenAIPtoCSV Converter for LitteNavMap

Author: Detlev Hoffmann (info at gunduran.de)

With this small Python program you could download reporting points from  [OpenAIP](https://www.openaip.net) and create csv files that could be imported into [LittleNavMap](https://albar965.github.io/littlenavmap.html).

These userpoints will then be shown as waypoints and the airport is a tag. If the reporting point is a compulsatory (mandatory) reporting point it is also indicated.

Installation:

1. Please have Pyhton 3.x installed [Python.org](https://www.python.org/)
2. Create a folder in a place you like (e.g. e:\tools\converter)
3. unpack the openaiptocsv.zip file to this folder
4. check if python is installed correctly open a terminal (Windows cmd) and type `python --version`
> As we need to access google storage services, we need to install this package from google using the pip command. 

Two ways:
* Directly into the current python environment ==> not recommended, but ok
* Create a virtual python environment ==> recommended and easy

> Prepare a virtual environment

* `cd your folder` e.g. cd e:\tools\converter
* `python -m venv env` this create a new virtual envitonment in the folder "env"
* `.\env\scripts\activate` this activates the environment, prompt should change to "(env) folder...". 
* If you are running the commands in windows powershell, you need to use `.\env\scripts\activate.ps1` and potentially need to allow the execution of such scripts via `set-executionpolicy RemoteSigned -Scope CurrentUser`

**Remember to activate the environment always before running the commands** 

> Now wheter in the virtual environment or in the global python installation. In a terminal (Windows cmd)

* `pip install --upgrade google-cloud-storage`

Now we are ready to start the program

`python openaiptocsv.py --help` (will show you the help)

> Normal use cases:

`python openaiptocsv.py -d de` Downloads from Google Storage the needed files for de = Germany

`python openaiptocsv.py -da` Downloads all available countries

`python openaiptocsv.py -w de` creates the csv file for all German airports

`python openaiptocsv.py -i EDDK -c de` creates the points for Cologne

>Standard folders

`\openAIP_files\` ==> Storage for the downloaded files

`\Userpoints\` ==> created user points 

>Version history:

1.0 - Inital version
1.1 - updated readme.md