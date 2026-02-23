# songrequest-addon

host a webapp to display the current song of the nightbot song-request playlist.
Can be used for 

## installation

run `install.bat`

hopefully everything works without errors :) 

## setup

Create an application in your nightbot setup [here](https://nightbot.tv/settings/connections)  set the redirect-uri to `http://localhost:5000/callback` and save the client-id & client secret for below.

then create a file called `.env`
and insert the following text:
````dotenv
NIGHTBOT_CLIENT_SECRET=<nightbot secret key>
NIGHTBOT_CLIENT_ID=<nightbot client id>
````

where the <placeholders> need to be replaced by the client-id & client secret above.

## obs setup

Add a browser source with url `http://localhost:5000/current-song-page.html` width = 400 & height = 400, then resize the rectangle to your preferred size.

## start

run `start.bat` then go to `http://localhost:5000/current-song` and log in with your twitch account.
