# MIRA! Project-

MIRA! is a framework designed to ensure seamless service migration of network service instance(s) between two IaaSs (VMs, Clouds, Datacenters) based on the CRIU project. MIRA! Provides several modules that guarantee the success and integrity of the requested migration service. It is primarily designed to support ultra-low latency type of service.


#Cloud1 & Cloud2 --> VM1 & VM2-


1.Host specification:

Distributor ID:	Ubuntu
Description:	Ubuntu 16.04.2 LTS
Release:	16.04
Codename:	xenial
kernel version: 4.8.8-040808-lowlatency

It’s not mandatory to follow this specification any Linux kernel up to 4.0 can do the job.



2.Container engine:

In our case we are using system level container in order to get the flexibility of running a Linux machine with less overhead and a fast boot up time, so our container engine is LXC.


	2,1.Dependencies:

	sudo apt-get install build-essential automake autoconf pkg-config docbook2x libapparmor-dev libselinux1-dev libcgmanager-dev libpython3-dev python3-dev libcap-dev python3-setuptools debootstrap libtool automake bridge-utils

	2,2.lxc installation:
	
	sudo apt-get update
	sudo apt-get install lxc

3.Migration tool:

	3,1.Dependencies:

	sudo apt-get install --no-install-recommends git build-essential libprotobuf-dev libprotobuf-c0-dev protobuf-c-compiler protobuf-compiler python-protobuf libnl-3-dev libpth-dev pkg-config libcap-dev asciidoc libnet-dev xmlto asciidoc

	3,2.CRIU installation:
	
	sudo apt-get install git
	sudo git clone http://github.com//xemul/criu/releases/tag/v3.6  #last available v3.6
	cd criu #or criu number of version 
	sudo make
	sudo make install
	sudo reboot

4.Network tool:
	
	4,1.Ovs installation:
    
	sudo apt-get install openvswitch-switch
    
#ONOS-

1.download from :https://wiki.onosproject.org/display/ONOS/Downloads

2.
sudo apt-get install software-properties-common -y && \
sudo add-apt-repository ppa:webupd8team/java -y && \
sudo apt-get update && \
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections && \
sudo apt-get install oracle-java8-installer oracle-java8-set-default -y	

4.
env | grep JAVA_HOME ## just to verify that there is java home

5.
unzip onos:
tar -xvzf onos_version.tar.gz

6.
cd onos_version

7.
bin/onos-service start
