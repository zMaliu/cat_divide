# -*- coding: utf-8 -*-
import multiprocessing

bind = "127.0.0.1:5001"
workers = 4
worker_class = "gevent"
threads = 2
max_requests = 1000
timeout = 120
graceful_timeout = 30
accesslog = "/var/log/yunhumeng/access.log"
errorlog = "/var/log/yunhumeng/error.log"
loglevel = "info"
proc_name = "yunhumeng_backend"
daemon = False
chdir = "/var/www/yunhumeng/backend"
preload_app = True
