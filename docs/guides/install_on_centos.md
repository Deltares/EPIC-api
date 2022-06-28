# Installing on a CentOs machine:
In this section you will find the steps to follow in order to install the latest Python and SQLite versions in a CentOs machine. These steps are a summarized walk-through from the references listed in the [references section](#references).

## Preparation
In order to ensure the installation happens correctly it is better to first download, compile and install SQLite3, this way we guarantee the follow-up [installation of Python](#installing-python-39) will pick up said latest version.

* Do a system update:
```bash
sudo yum -y install epel-release
sudo yum -y update
```
* Reboot server:
```bash
sudo reboot
```
* Install required packages (needed for both SQLite and Python):
```bash 
sudo yum -y install wget
sudo yum groupinstall "Development Tools" -y
```

## Installing PostgreSQL 
> Supported from versions EPPIC-api v.1.*

We will install PostgreSQL directly from CentOS repositories. To do so follow these steps once you are logged in your server.
* Install PostgreSQL:
```bash
sudo yum install postgresql11-server
```
<!-- * Make sure the psycopg2 pre-requirements are met:

        sudo yum install postgresql-libs
        sudo yum install postgresql-devel -->

* Initialize the Database
```bash
sudo /usr/pgsql-11/bin/postgresql-11-setup initdb
```
* Start the database
```bash
sudo systemctl start postgresql-11
sudo systemctl enable postgresql-11
```

Installation is complete, however we are still not ready to use the database server. We can now proceed with its configuration.

### PostgreSQL setup
Now we need to create the (empty) database to be used by the API, as well as to set a user and a password to access to it. Keep in mind a default user `postgres` has been added to our linux system. For this guide we will be using the following settings:

```
User: postgres
Password: postgres
Database: epic_db
``` 
* Set a password for our 'postgres' user.
```bash
sudo -u postgres psql
\password
```
* Create the database for the EPIC api. We will be using the name 'epic_db' across this guide.
```bash
sudo -u postgres createdb epic_db
```
We can now connect to `epic_db` with user `postgres`. Keep in mind you will need to specify this in the `epic_core/settings.py` file.

__Note__: We have found out some issues with the `pga_hba.conf` file when connecting with the database. A working solution is to modify the file fron `ident` to `md5`. We fixed this based on the following [reference](https://stackoverflow.com/a/64596782).

## Installing Python 3.9

* Install required specific packages:
```bash
sudo yum install openssl-devel libffi-devel bzip2-devel -y
```
* Export the libraries to ensure the [latest SQLite3](#installing-sqlite3) installed version gets picked up:
```bash
export LD_LIBRARY_PATH="/usr/local/lib/"
alias sqlite3="/usr/local/bin/sqlite3"
```
* Download source code:
```bash
cd /opt
mkdir python39 && cd python39
wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
tar xvf Python-3.9.10.tgz
cd Python-3.9.10
```
* Build and install:
```bash
./configure --enable-optimizations
sudo make altinstall
```

* Verify installation:
```bash
python3 --version
```
> Python 3.9.10
```bash        
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```
> 3.38.5

If the latest step does not return at least that value you may need to recompile and install python ensuring the libraries are correctly exported as described in previous steps.

## Installing Poetry:

* Install package under latest python3 library:

```bash        
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"
```

* Verify installation:
       
```bash
poetry --version
```
> Poetry version 1.1.13


## Appendix
### Invoking the libraries:
To ensure everything gets picked up correctly you can execute the following command lines:
```bash
export LD_LIBRARY_PATH="/usr/local/lib/"
PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
```
In addition, poetry might require this extra step:
```bash
export PATH="/root/.local/bin:$PATH"
```

### References:
* SQLite3:
    * [Installing Latest SQLite3](https://www.hostnextra.com/kb/how-to-install-sqlite3-on-centos-7/)
    * https://www.sqlite.org/2022/sqlite-autoconf-3380500.tar.gz
    > It might be good to replace the previous version of sqlite by moving it to a bak directory and renaming the latest one to the ‘sqlite3’. Taking over future invocations.
* PostgreSQL:
    * [Installing PostgreSQL 11 on CentOs]((https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-7))
* Python 3.9:
    * [Installing latest Python on CentOs](https://computingforgeeks.com/install-latest-python-on-centos-linux/)
    > It is also possible replacing the previous python3 version, as with SQLite3, moving the python 3.6 to a backup directory (python3.6.bak), this way the alias gets picked up always.
* (Extra) [Poetry official installer](https://python-poetry.org/docs/master/#installing-with-the-official-installer)
