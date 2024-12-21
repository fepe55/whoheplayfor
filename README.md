# WhoHePlayFor

Who He Play For?

https://whoheplayfor.com/

## Steps to build

You need an external database, you can run one with Docker in testing, with the following command  
`$ docker run -e POSTGRES_USER=whpf -e POSTGRES_DB=whpf -e POSTGRES_PASSWORD=whpf -p 5432:5432 postgres:latest`  
_Important_: We're not using persistent volumes here because it's only for testing, your data will NOT be saved doing it this way

Then build the whpf Docker image with  
`$ docker build . -t whpf`

Rename `env.example` to `env` and edit it accordingly  
`$ cp env.example env`

Run migrations on the container  
`$ docker run --env-file env whpf python manage.py migrate`

Then run initial data  
`$ docker run --env-file env whpf python manage.py startdata`

And update rosters  
`$ docker run --env-file env whpf python manage.py update_rosters`

The usual way takes a long time because it checks that every single player has a valid image file for its face.  
If you don't care about that check, you can skip it by running the script like so:  
`$ docker run --env-file env whpf python manage.py update_rosters --no-faceless-check`

Finally, run the container in daemon mode  
`$ docker run --env-file env -p 8000:8000 -d whpf`

[![Django CI](https://github.com/fepe55/whoheplayfor/actions/workflows/main.yml/badge.svg)](https://github.com/fepe55/whoheplayfor/actions/workflows/main.yml)

[![Coverage](https://codecov.io/gh/fepe55/whoheplayfor/branch/master/graph/badge.svg?token=BBWNJ62AMD)](https://codecov.io/gh/fepe55/whoheplayfor)

[![DeepSource](https://deepsource.io/gh/fepe55/whoheplayfor.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/fepe55/whoheplayfor/?ref=repository-badge)

[![DeepSource](https://deepsource.io/gh/fepe55/whoheplayfor.svg/?label=resolved+issues&show_trend=true)](https://deepsource.io/gh/fepe55/whoheplayfor/?ref=repository-badge)
