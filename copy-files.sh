printf "Deleting all contents in the folder: artifact \n"
rm -r artifact/*
printf "copy started all contents in the folder: artifact \n"

cp -r .elasticbeanstalk .platform .ebextensions artifact
cp -r pages artifact/
cp InputText.py utils.py artifact/
cp Procfile artifact/
cp requirements.txt artifact/
cp -r libs artifact/
find . -type d -name "__pycache__" -exec rm -rf {} +
printf "copy completed all contents in the folder: artifact \n"

cd artifact
zip -r artifact.zip .elasticbeanstalk .platform .ebextensions *
mv artifact.zip ../