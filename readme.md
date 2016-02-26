# Comparative Agendas

Comparative Agendas is an online research and analysis tool for for archived sources of policy data.

[http://www.comparativeagendas.net](http://www.comparativeagendas.net)

## Getting Started

```(Example commands are for Ubuntu 14.04 LTS)```

* Install PostgreSQL > 9.4

```wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -```

```sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" >> /etc/apt/sources.list.d/postgresql.list'```

```apt-get update```

```apt-get upgrade```

```apt-get install postgresql-9.4```

* Install Git

```apt-get install git```

* Install Docker

```wget -qO- https://get.docker.com/ | sh```

* Move to web root

```mkdir /var/www```

```cd /var/www```

* Clone this repo

```git clone https://github.com/comparative/cap```

* Move to app root

```cd /var/www/cap```

* Build Docker image

```docker build -t cap:web .```

* Create config file (& edit to fill in your credentials)

```cp /var/www/cap/config_sample.py /var/www/cap/config.py```

* Run Docker container (add-host flag tells the web server your PostgreSQL address)

```docker run --add-host=mypostgres:123.45.67.89 --name="web" -d -p 80:5000  -v /var/www/cap:/var/www/cap cap:web```

* Enter Docker container

```docker exec -it web bash```

* Move to app root

```cd /var/www/cap```

* Create database

```python create_db.py```

* Enter python shell

``` python ```

* Create database tables

```>>> from app import db```

```>>> db.create_all()```


## Deployment

For production you may need to run your own Highcharts Export Server.

These are the instructions:

[http://www.highcharts.com/docs/export-module/setting-up-the-server](http://www.highcharts.com/docs/export-module/setting-up-the-server)

... but you don't need to follow them because this repo contains a Docker image:

```cd /var/www/cap/highcharts-export```

```docker build -t cap:export .```

```docker run --name="export" -d -p 8080:8080 cap:export```

## Built With

* Highcharts
* AngularJS
* Flask
* Celery
* PostgreSQL
* Docker

## Acknowledgments

This software project was made possible by the following groups and institutions:

* The Mannheim Centre for European Social Research (MZES) at the University of Mannheim

* Christoffer Green-Pedersen, Aarhus University through funds from the Danish Social Science Research Council and the Research Foundation at Aarhus University. 

* Media, Movements & Politics at University of Antwerp
 
* University of Southampton

* Ministerio de Ciencia e Innovación (CSO-2012-31214). Convocatoria 2012 del subprograma de Proyectos de Investigación Fundamental no orientada.Title of the project: Interest groups in Spain: Participation in the governmental and parliamentary arenas 

* Faculadade de Ciêcias Sociais e Humanas FCSH 

* Liberal Arts Instructional Technologies (LAITS) at the University of Texas at Austin