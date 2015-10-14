# USAGE: docker run -d -i -p 8080:8080 IMAGE 

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
RUN git clone https://github.com/highslide-software/highcharts.com.git ~/highcharts.com
RUN mv ~/highcharts.com/exporting-server/java/highcharts-export /srv/highcharts-export

# BUILD A .WAR FILE
RUN cd /srv/highcharts-export/ && mvn install 
RUN cd /srv/highcharts-export/highcharts-export-web/ && mvn clean package

# MOVE TO APP SERVER
RUN cp /srv/highcharts-export/highcharts-export-web/target/highcharts-export-web.war  /usr/local/tomcat/webapps/

CMD ["catalina.sh","run"]