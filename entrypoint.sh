#!/bin/sh

sh ./wait-for mongo:27017

# sh ./wait-for rabbit:5672

# sh ./wait-for redis:6379

exec "$@"