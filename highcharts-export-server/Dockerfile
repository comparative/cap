FROM tomcat:7-jre7

ENV DEBIAN_FRONTEND noninteractive

# INSTALL JDK
RUN apt-get update && apt-get install -y default-jdk

# INSTALL MAVEN2
RUN apt-get update &&  apt-get install -y apt-utils && apt-get install -y maven2

# INSTALL PHANTOM JS
RUN apt-get install -y build-essential chrpath libssl-dev libxft-dev
RUN apt-get install libfreetype6 libfreetype6-dev
RUN apt-get install libfontconfig1 libfontconfig1-dev

RUN cd ~
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
RUN tar xvjf phantomjs-1.9.8-linux-x86_64.tar.bz2
RUN mv phantomjs-1.9.8-linux-x86_64 /usr/local/share
RUN ln -sf /usr/local/share/phantomjs-1.9.8-linux-x86_64/bin/phantomjs /usr/local/bin

# INSTALL GIT
RUN apt-get install -y git-core

# DOWNLOAD EXPORT SERVER FROM GITHUB
RUN git clone https://github.com/highcharts/highcharts-export-server.git && cd highcharts-export-server && git checkout 0c831a080
RUN mv ./highcharts-export-server/java/highcharts-export /srv/highcharts-export

# BUILD A .WAR FILE
RUN cd /srv/highcharts-export/ && mvn install 
RUN cd /srv/highcharts-export/highcharts-export-web/ && mvn clean package

# MOVE TO APP SERVER
RUN cp /srv/highcharts-export/highcharts-export-web/target/highcharts-export-web.war  /usr/local/tomcat/webapps/

# USE PORT 80
RUN cd /usr/local/tomcat/conf && cat server.xml | sed s/8080/80/g > server_80.xml && mv server_80.xml server.xml

EXPOSE 80

CMD ["catalina.sh","run"]