This is an website that allows to load zip files.

The archives should contain a Makefile and the files
inside will be built chosing two different compilers :
```
	- gcc
	- clang
```

Requirements:
```
	- python3
	- flask
	- influxdb
```
Use the following link in order to install and get used with IndluxDB:
	https://www.influxdata.com/blog/getting-started-python-influxdb/

Docker images used for gcc/clang environment:
```
	docker pull gcc
	docker pull rsmmr/clang	
```
