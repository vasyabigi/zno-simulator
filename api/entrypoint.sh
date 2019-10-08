#!/bin/bash

exec gunicorn app -b 0.0.0.0
