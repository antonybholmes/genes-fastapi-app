pwd=`pwd`
name=`basename ${pwd}`

docker run -p 9000:9000 -d --name ${name} --network host ${name} 
